from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_value = models.FloatField(default=0)
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Table(models.Model):
    min_bet = models.FloatField(default=0)
    player_count = models.IntegerField(default=0)
    
class Round(models.Model):
    player_count = models.IntegerField(default=0)
    dealer_cards = models.CharField(max_length=256)
