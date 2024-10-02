from django.db import models

class Wallet(models.Model):
    auth0_user_id = models.CharField(max_length=255, unique=True)  # Almacena el user_id de Auth0
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='CLP')  # Puedes cambiarlo según tus necesidades

    def __str__(self):
        return f'{self.auth0_user_id} Wallet'