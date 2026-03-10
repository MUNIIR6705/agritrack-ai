from django.db import models
from django.conf import settings

class Farm(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farm')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    size_acres = models.DecimalField(max_digits=5, decimal_places=2, help_text="Size of farm in acres")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True, null=True) # Click to go to cow/sale

    def __str__(self):
        return f"{self.title} - {self.user.username}"