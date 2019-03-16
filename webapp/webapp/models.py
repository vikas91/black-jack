from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_value = models.FloatField(default=0)

class Table(models.Model):
    min_bet = models.FloatField(default=0)
    player_count = models.IntegerField(default=0)
    
class Round(models.Model):
    player_count = models.IntegerField(default=0)
    dealer_cards = models.CharField(max_length=256)
