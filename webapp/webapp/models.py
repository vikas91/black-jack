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
    TABLE_STATUS = (
        (0, 'inactive'),
        (1, 'active'),
    )
    min_bet = models.FloatField(default=0)
    player_count = models.IntegerField(default=0)
    table_status = models.IntegerField(choices=TABLE_STATUS, default=0) 
    
    class Meta:
        db_table = 'tables'
        

class TablePlayer(models.Model):
    PLAYER_STATUS = (
        (0, 'inactive'),
        (1, 'active'),
    )
    table_id = models.ForeignKey(Table, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    player_type = models.IntegerField(choices=PLAYER_STATUS, default=0) 
    
    def __str__(self):
        return str(self.table_id) + '-' + str(self.user_id.username)
    
    class Meta:
        unique_together = ('table_id', 'user_id')
        db_table = 'table_players'

       
class Round(models.Model):
    ROUND_STATUS = (
        (0, 'inactive'),
        (1, 'active'),
        (2, 'end'),
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    player_count = models.IntegerField(default=0)
    dealer_cards = models.CharField(max_length=256)
    remaining_cards = models.CharField(max_length=256)
    dealer_count = models.IntegerField(default=0)
    dealer_status = models.IntegerField(default=0)
    round_status = models.IntegerField(choices=ROUND_STATUS, default=0)
    
    def __str__(self):
        return 'Table-' + str(self.table.id) + '-Round-' + str(self.id)
    
    class Meta:
        db_table = 'rounds'


class RoundPlayer(models.Model):
    PLAYER_ROUND_STATUS = (
        (0, 'inactive'),
        (1, 'active'),
        (2, 'busted'),
    )
    
    PLAYER_WIN_STATUS =(
        (0, 'LOST'),
        (1, 'DRAW'),
        (2, 'WON'),
    )
    
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    player_order = models.IntegerField(default=0)
    player_bet = models.FloatField(default=0)
    player_cards = models.CharField(max_length=256)
    player_count = models.IntegerField(default=0)
    player_max_count = models.IntegerField(default=0)
    player_game_status = models.IntegerField(choices=PLAYER_ROUND_STATUS, default=0)
    player_win_status = models.IntegerField(default=0)
    
    def __str__(self):
        return 'Round-' + str(self.round.id) + '-' + str(self.player.username)
    
    class Meta:
        db_table = 'round_players'