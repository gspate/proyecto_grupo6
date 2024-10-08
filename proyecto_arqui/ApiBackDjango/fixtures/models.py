from django.db import models
from django.utils import timezone
import uuid

class Fixture(models.Model):
    fixture_id = models.IntegerField(unique=True)
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
    request_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    fixture = models.ForeignKey('Fixture', on_delete=models.CASCADE)
    # user_id = models.IntegerField()    
    quantity = models.IntegerField()
    datetime = models.DateTimeField(default=timezone.now)
    group_id = models.CharField(max_length=10, null=True, blank=True)
    league_name = models.CharField(max_length=100, default='Unknown League')
    round = models.CharField(max_length=100, default='Regular Season')
    date = models.DateField(default=timezone.now)
    result = models.CharField(max_length=50, default='---')
    deposit_token = models.CharField(max_length=100, blank=True, null=True)
    seller = models.IntegerField(default=0)

    def __str__(self):
        return f"Request {self.request_id} for Fixture {self.fixture.fixture_id} - Group {self.group_id}"

