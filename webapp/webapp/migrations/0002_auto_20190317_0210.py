# Generated by Django 2.1.7 on 2019-03-17 02:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TablePlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'table_players',
            },
        ),
        migrations.AlterModelTable(
            name='round',
            table='rounds',
        ),
        migrations.AlterModelTable(
            name='table',
            table='tables',
        ),
        migrations.AddField(
            model_name='tableplayer',
            name='table_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Table'),
        ),
        migrations.AddField(
            model_name='tableplayer',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tableplayer',
            unique_together={('table_id', 'user_id')},
        ),
    ]