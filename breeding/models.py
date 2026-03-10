from django.db import models
from animals.models import Animal
from datetime import timedelta, datetime

class BreedingRecord(models.Model):
    mother = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='breeding_records')
    father_tag = models.CharField(max_length=50, blank=True)
    mating_date = models.DateField()
    expected_delivery = models.DateField(blank=True, null=True)
    actual_delivery = models.DateField(blank=True, null=True)
    litter_size = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('Pregnant', 'Pregnant'),
        ('Delivered', 'Delivered'),
        ('Failed', 'Failed')
    ], default='Pregnant')

    def save(self, *args, **kwargs):
        # Ensure mating_date is a date object, not a string
        if isinstance(self.mating_date, str):
            self.mating_date = datetime.strptime(self.mating_date, '%Y-%m-%d').date()

        if not self.expected_delivery:
            # Pigs: 114 days | Rabbits: 31 days
            days = 114 if self.mother.species == 'Pig' else 31
            self.expected_delivery = self.mating_date + timedelta(days=days)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mother.tag_number} - Due: {self.expected_delivery}"