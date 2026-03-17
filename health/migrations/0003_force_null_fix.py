# Generated manually to fix IntegrityErrors in UserProfile
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('health', '0002_alter_searchanalytics_user'), 
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='farm_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='primary_species',
            field=models.CharField(blank=True, choices=[('pigs', 'Porcine (Pigs)'), ('rabbits', 'Leporidae (Rabbits)'), ('mixed', 'Mixed Production')], default='mixed', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='acreage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Farm size in acres', max_digits=5, null=True),
        ),
    ]