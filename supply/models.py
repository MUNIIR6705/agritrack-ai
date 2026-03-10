from django.db import models

class Supply(models.Model):
    SUPPLY_TYPES = [
        ('Feed', 'Feed'),
        ('Medicine', 'Medicine'),
        ('Equipment', 'Equipment'),
    ]
    
    name = models.CharField(max_length=100)
    supply_type = models.CharField(max_length=20, choices=SUPPLY_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in kg or units")
    unit = models.CharField(max_length=10, default='kg') # kg, bags, vials
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, help_text="Alert when stock falls below this")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Supplies"

    def is_low(self):
        return self.quantity <= self.min_stock_level

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit} left)"