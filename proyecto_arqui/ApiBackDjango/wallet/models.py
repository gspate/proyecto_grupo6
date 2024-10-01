from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='CLP')  # Puedes cambiarlo según tus necesidades

    def __str__(self):
        return f'{self.user.username} Wallet'