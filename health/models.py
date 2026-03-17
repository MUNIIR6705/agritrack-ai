from django.db import models
from django.conf import settings
from animals.models import Animal
from django.utils import timezone
from datetime import timedelta

# --- 1. SMART AI TRAINING DATA ---
class AITrainingData(models.Model):
    """Stores expert-verified data to improve diagnostic accuracy."""
    species = models.CharField(max_length=50, choices=[('Pig', 'Pig'), ('Rabbit', 'Rabbit')])
    symptoms = models.TextField()   
    diagnosis = models.CharField(max_length=255) 
    treatment = models.TextField()
    severity = models.CharField(max_length=50, choices=[
        ('Low', 'Low'), 
        ('Medium', 'Medium'), 
        ('High', 'High'), 
        ('Critical', 'Critical')
    ], default='Medium')
    verified_by_vet = models.BooleanField(default=False)
    date_logged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.species} Training: {self.diagnosis}"


# --- 2. SEARCH & AI ANALYTICS ---
class SearchAnalytics(models.Model):
    """Tracks farmer search behavior for AI optimization."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    species = models.CharField(max_length=20)
    query_text = models.TextField()
    found_match = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


# --- 3. ANIMAL HEALTH LOGS (Diagnostic Risk Engine) ---
class HealthRecord(models.Model):
    """Tracks clinical presentations and assigns a system risk score."""
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    symptoms = models.TextField()
    diagnosis = models.CharField(max_length=255, blank=True)
    treatment = models.TextField()
    severity = models.CharField(max_length=50, choices=[
        ('Low', 'Low'), 
        ('Medium', 'Medium'), 
        ('High', 'High'),
        ('Critical', 'Critical')
    ])
    risk_factor = models.IntegerField(default=1, help_text="AI assigned risk 1-10") 
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tag: {self.animal.tag_number} - {self.diagnosis}"


# --- 4. SMART FINANCIAL LEDGER (M-Pesa Automated) ---
class FinanceRecord(models.Model):
    """Handles automated billing and farm financial oversight."""
    TRANSACTION_TYPES = [('Income', 'Income'), ('Expense', 'Expense')]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        status = "✅" if self.is_confirmed else "⏳"
        return f"{status} {self.transaction_type}: KES {self.amount}"


# --- 5. USER PROFILE (The Identity Node) ---
class UserProfile(models.Model):
    """
    HEALTH APP PROFILE: 
    The Farmer Identity Node with 2FA Security Integration.
    """
    SPECIES_CHOICES = [
        ('pigs', 'Porcine (Pigs)'),
        ('rabbits', 'Leporidae (Rabbits)'),
        ('mixed', 'Mixed Production'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='health_profile'
    )
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    
    farm_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    primary_species = models.CharField(max_length=20, choices=SPECIES_CHOICES, default='mixed')
    acreage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Farm size in acres")
    
    # Cloud Sync Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    # --- SECURITY NODE: EMAIL 2FA ---
    login_token = models.CharField(max_length=6, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.farm_name if self.farm_name else self.user.username} Node"

    @property
    def total_assets(self):
        """Calculates total active livestock owned by this user."""
        return Animal.objects.filter(owner=self.user, status='Active').count()

    @property
    def node_status(self):
        """Returns the readiness level of the profile."""
        invalid_vals = [None, "", "Awaiting Config", "Pending Configuration", "N/A", "Awaiting GPS"]
        if self.farm_name not in invalid_vals and self.location not in invalid_vals:
            return "Verified"
        return "Incomplete"

    @property
    def completion_percentage(self):
        """Calculates profile completion for UI progress bars."""
        fields = [self.farm_name, self.location, self.phone_number, self.bio]
        invalid_vals = [None, "", "Awaiting Config", "Pending Configuration", "N/A", "Awaiting GPS"]
        
        filled = [f for f in fields if f and str(f).strip() not in invalid_vals]
        
        if not fields:
            return 0
        return int((len(filled) / len(fields)) * 100)

    def is_token_valid(self):
        """Checks if the 2FA token is less than 10 minutes old."""
        if not self.token_created_at:
            return False
        return timezone.now() < self.token_created_at + timedelta(minutes=10)