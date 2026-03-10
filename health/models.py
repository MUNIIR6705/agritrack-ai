from django.db import models
from django.conf import settings
from animals.models import Animal

# --- 1. SMART AI TRAINING DATA ---
class AITrainingData(models.Model):
    """
    PROPOSAL FEATURE: Classification Engine Training Set.
    Stores expert-verified data to improve diagnostic accuracy.
    """
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
    species = models.CharField(max_length=20)
    query_text = models.TextField()
    found_match = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

# --- 3. ANIMAL HEALTH LOGS (Diagnostic Risk Engine) ---
class HealthRecord(models.Model):
    """
    PROPOSAL FEATURE: Diagnostic Risk Engine.
    Tracks clinical presentations and assigns a system risk score.
    """
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
    
    # New Field for Proactive Alerts logic
    risk_factor = models.IntegerField(default=1, help_text="AI assigned risk 1-10") 
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.uep_code} - {self.diagnosis} ({self.severity})"

# --- 4. WEIGHT TRACKING ---
# Note: You already have this in animals/models.py. 
# Use this only if you need a separate health-specific measurement log.
class WeightRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    date_measured = models.DateField(auto_now_add=True)

# --- 5. SMART FINANCIAL LEDGER (M-Pesa Automated) ---
class FinanceRecord(models.Model):
    """
    PROPOSAL FEATURE: M-Pesa automated billing and financial oversight.
    """
    TRANSACTION_TYPES = [('Income', 'Income'), ('Expense', 'Expense')]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    # New Field: Stores Safaricom's ID to allow automated 'Confirmed' status updates
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "✅" if self.is_confirmed else "⏳"
        return f"{status} {self.transaction_type}: KES {self.amount}"

# --- 6. USER PROFILE (SaaS Identity) ---
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.farm_name} ({self.user.username})"