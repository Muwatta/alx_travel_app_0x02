from django.urls import path
from .views import InitiatePaymentAPIView, VerifyPaymentAPIView

urlpatterns = [
    path('api/payments/initiate/', InitiatePaymentAPIView.as_view(), name='initiate-payment'),
    path('api/payments/verify/', VerifyPaymentAPIView.as_view(), name='verify-payment'),
]
