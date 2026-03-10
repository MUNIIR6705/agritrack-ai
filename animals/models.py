from django.db import models
from django.contrib.auth import get_user_model
import qrcode
import uuid
from io import BytesIO
from django.core.files import File

User = get_user_model()

class Animal(models.Model):
    SPECIES_CHOICES = [
        ('Pig', 'Pig'),
        ('Rabbit', 'Rabbit'),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Sold', 'Sold'),
        ('Sick', 'Sick'),
        ('Quarantined', 'Quarantined'),
    ]

    # Physical Identification
    tag_number = models.CharField(max_length=50, unique=True)
    
    # PROPOSAL FEATURE: Unique Electronic Profile (UEP)
    # FINALIZED: Removed null=True. This is now a mandatory unique key.
    uep_code = models.CharField(max_length=50, unique=True, editable=False)
    
    species = models.CharField(max_length=50, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    # QR Code Field for physical-to-digital bridge
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Generate UEP if it doesn't exist
        if not self.uep_code:
            prefix = self.species[:2].upper() if self.species else "AN"
            unique_suffix = uuid.uuid4().hex[:8].upper()
            self.uep_code = f"AT-{prefix}-{unique_suffix}"

        # 2. Generate QR code only if it's missing (Digital Passport)
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Metadata updated for Supply Chain Synchronization traceability
            qr_data = (
                f"AgriTrack AI Digital Passport\n"
                f"UEP: {self.uep_code}\n"
                f"Tag: {self.tag_number}\n"
                f"Species: {self.species}\n"
                f"Status: {self.status}"
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f'qr_{self.uep_code}.png'
            
            # save=False avoids recursive save() calls
            self.qr_code.save(file_name, File(buffer), save=False)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.uep_code} ({self.tag_number})"



class WeightRecord(models.Model):
    animal = models.ForeignKey(
        Animal, 
        on_delete=models.CASCADE, 
        related_name='weight_records'
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        # Using UEP for traceability in weight logs
        return f"{self.animal.uep_code} - {self.weight}kg"