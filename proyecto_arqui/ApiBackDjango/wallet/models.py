from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    def __str__(self):
        return f"Wallet for {self.user.username}"