from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import default

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
    
    class Meta:
        db_table = 'tables'
        

class TablePlayer(models.Model):
    table_id = models.ForeignKey(Table, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    player_type = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.table_id) + '-' + str(self.user_id.username)
    
    class Meta:
        unique_together = ('table_id', 'user_id')
        db_table = 'table_players'
       
class Round(models.Model):
    player_count = models.IntegerField(default=0)
    dealer_cards = models.CharField(max_length=256)
    
    class Meta:
        db_table = 'rounds'
