from django.db import models

class Booking(models.Model):
    customer_name = models.CharField(max_length=255)
    email = models.EmailField()
    destination = models.CharField(max_length=255)
    travel_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.customer_name} - {self.destination}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for {self.booking.customer_name} - {self.amount}"
