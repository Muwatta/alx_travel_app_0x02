import os
import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Payment
from .serializers import PaymentSerializer
from .tasks import send_payment_confirmation_email  # celery task
from django.shortcuts import get_object_or_404

CHAPA_BASE = os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')
CHAPA_SECRET = os.getenv('CHAPA_SECRET_KEY')

class InitiatePaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Expect { "booking_id": <id>, "amount": 1000.00, "currency": "ETB" }
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'ETB')

        # fetch booking (adjust import/path as needed)
        booking = get_object_or_404(Booking, id=booking_id)

        # generate merchant tx_ref
        tx_ref = f'booking-{booking.id}-{uuid.uuid4().hex[:8]}'

        # create Payment record (initial)
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=amount,
            currency=currency,
            tx_ref=tx_ref,
            status='pending'
        )

        # Prepare payload for Chapa initialize endpoint (transaction initialize)
        # Use the transaction initialize endpoint (example /transaction/initialize)
        url = f'{CHAPA_BASE}/transaction/initialize'

        payload = {
            "amount": float(amount),
            "currency": currency,
            "email": request.user.email or booking.user.email,
            "first_name": request.user.first_name or '',
            "last_name": request.user.last_name or '',
            "tx_ref": tx_ref,
            # return_url/callback_url — set to your frontend or an endpoint that calls verify
            "callback_url": request.build_absolute_uri(f'/api/payments/verify/?tx_ref={tx_ref}'),
            "return_url": request.build_absolute_uri(f'/bookings/{booking.id}/payment-return/')  # optional
        }

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            payment.status = 'failed'
            payment.metadata = {"error": str(e)}
            payment.save()
            return Response({"detail": "Failed to initiate payment", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        data = resp.json()

        # Save the returned transaction id or response
        payment.metadata = data
        # Some Chapa init flows return data.checkout_url or data.data.checkout_url depending on endpoint
        checkout_url = None
        chapa_tx_id = None
        if isinstance(data, dict):
            # robust parsing
            chapa_tx_id = data.get('data', {}).get('id') or data.get('data', {}).get('transaction_id') or data.get('id')
            checkout_url = data.get('data', {}).get('checkout_url') or data.get('data', {}).get('payment_url') or data.get('data', {}).get('url') or data.get('data', {}).get('link')
        payment.chapa_transaction_id = chapa_tx_id
        payment.save()

        return Response({
            "checkout_url": checkout_url,
            "tx_ref": payment.tx_ref,
            "payment_id": str(payment.id),
            "raw": data
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # callback might be from Chapa

    def get(self, request):
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({"detail": "tx_ref is required"}, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(Payment, tx_ref=tx_ref)

        url = f'{CHAPA_BASE}/transaction/verify/{tx_ref}'
        headers = {"Authorization": f"Bearer {CHAPA_SECRET}"}

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            payment.metadata = {"verify_error": str(e)}
            payment.status = 'failed'
            payment.save()
            return Response({"detail": "verification failed", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        data = resp.json()
        # Parse status robustly: check data['data']['status'] or other paths
        chapa_status = None
        if isinstance(data, dict):
            chapa_status = data.get('data', {}).get('status') or data.get('status')

        # Map chapa outcome to our model
        if chapa_status and chapa_status.lower() in ('success', 'completed', 'paid'):
            payment.status = 'completed'
            # optional: update chapa_transaction_id or metadata
            payment.chapa_transaction_id = payment.chapa_transaction_id or data.get('data', {}).get('id')
            payment.metadata = data
            payment.save()
            # enqueue confirmation email
            send_payment_confirmation_email.delay(payment.id)
            return Response({"detail": "payment verified", "status": payment.status, "raw": data})
        else:
            payment.status = 'failed'
            payment.metadata = data
            payment.save()
            return Response({"detail": "payment not successful", "status": payment.status, "raw": data}, status=status.HTTP_200_OK)
