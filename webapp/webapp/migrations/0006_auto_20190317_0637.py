# Generated by Django 2.1.7 on 2019-03-17 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20190317_0611'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='dealer_status',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='roundplayer',
            name='player_order',
            field=models.IntegerField(default=0),
        ),
    ]