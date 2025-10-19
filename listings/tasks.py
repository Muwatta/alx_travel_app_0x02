from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return False

    subject = f'Payment Confirmation — {payment.tx_ref}'
    body = f'Hello {payment.user.get_full_name() or payment.user.email},\n\n' \
           f'Your payment for booking #{payment.booking.id} has been confirmed.\n' \
           f'Amount: {payment.amount} {payment.currency}\n' \
           f'Reference: {payment.tx_ref}\n\nThank you.'
    send_mail(subject, body, settings.EMAIL_HOST_USER, [payment.user.email])
    return True
