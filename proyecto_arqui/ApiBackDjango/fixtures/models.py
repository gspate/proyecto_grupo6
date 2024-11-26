from django.db import models
from django.utils import timezone
import uuid6


class Fixture(models.Model):
    fixture_id = models.CharField(unique=True, null=False, blank=False)
    referee = models.CharField(max_length=100, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    timestamp = models.IntegerField()
    status_long = models.CharField(max_length=50, null=True, blank=True)
    status_short = models.CharField(max_length=50, null=True, blank=True)
    status_elapsed = models.IntegerField(null=True, blank=True)
    league_id = models.IntegerField(null=True, blank=True)
    league_name = models.CharField(max_length=100, null=True, blank=True)
    league_country = models.CharField(max_length=100, null=True, blank=True)
    league_logo = models.CharField(max_length=255, null=True, blank=True)
    league_flag = models.CharField(max_length=255, null=True, blank=True)
    league_season = models.IntegerField(null=True, blank=True)
    league_round = models.CharField(max_length=100, null=True, blank=True)
    home_team_id = models.IntegerField(null=True, blank=True)
    home_team_name = models.CharField(max_length=100, null=True, blank=True)
    home_team_logo = models.CharField(max_length=255, null=True, blank=True)
    home_team_winner = models.BooleanField(null=True, blank=True)
    away_team_id = models.IntegerField(null=True, blank=True)
    away_team_name = models.CharField(max_length=100, null=True, blank=True)
    away_team_logo = models.CharField(max_length=255, null=True, blank=True)
    away_team_winner = models.BooleanField(null=True, blank=True)
    home_goals = models.IntegerField(null=True, blank=True)
    away_goals = models.IntegerField(null=True, blank=True)
    odds_id = models.IntegerField(null=True, blank=True)
    odds_name = models.CharField(max_length=100, null=True, blank=True)
    odds_home_value = models.FloatField(null=True, blank=True)
    odds_draw_value = models.FloatField(null=True, blank=True)
    odds_away_value = models.FloatField(null=True, blank=True)
    available_bonuses = models.IntegerField(default=40) # 40 bonos per fixture by default
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fixture {self.fixture_id}"


class Bonos(models.Model):
    ESTADOS_BONO = [
        ('pendiente', 'Pendiente de Validación'),
        ('ganado', 'Ganado - Pagado'),
        ('perdido', 'Perdido - No Pagado'),
        ('procesado', 'Procesado - Sin Acción'),
    ]

    request_id = models.UUIDField(unique=True, default=uuid6.uuid6, editable=False)
    fixture_id = models.CharField(null=False, blank=False)
    user_id = models.CharField(null=True, blank=True)
    quantity = models.IntegerField()
    datetime = models.DateTimeField(default=timezone.now)
    group_id = models.CharField(max_length=10, null=True, blank=True)
    league_name = models.CharField(max_length=100, default='Unknown League')
    round = models.CharField(max_length=100, default='Regular Season')
    date = models.DateField(default=timezone.now)
    result = models.CharField(max_length=50, default='---')
    deposit_token = models.CharField(max_length=100, blank=True, null=True)
    datetime = models.CharField(max_length=100, blank=True, null=True)
    wallet = models.BooleanField()
    acierto = models.BooleanField(default=False)
    seller = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=ESTADOS_BONO, default='pendiente')


class User(models.Model):
    user_id = models.CharField(unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    wallet = models.FloatField(default=1000)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.username} ({self.user_id})"


class Recommendation(models.Model):
    user_id = models.CharField(null=False, blank=False)
    fixture_id = models.CharField(null=False, blank=False)
    league_name = models.CharField(max_length=100, null=True, blank=True)
    round = models.CharField(max_length=100, null=True, blank=True)
    benefit_score = models.FloatField()  # Ponderador calculado para la recomendaci贸n
    created_at = models.DateTimeField(auto_now_add=True)


class Auctions(models.Model):
    auction_id = models.UUIDField(editable=False, null=False, blank=False)
    proposal_id = models.CharField(editable=False, blank=True)
    fixture_id = models.CharField(null=False, blank=False)
    league_name = models.CharField(max_length=100, null=False, blank=False)
    round = models.CharField(max_length=100, null=False, blank=False)
    result = models.CharField(max_length=100, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    group_id = models.IntegerField(null=False, blank=False)
    type = models.CharField(max_length=100, null=False, blank=False)
