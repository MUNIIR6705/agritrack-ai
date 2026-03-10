import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from health.models import AITrainingData

data = [
    {
        "species": "Pig",
        "user_prompt": "high fever, bluish ears, bloody diarrhea, sudden death",
        "ideal_response": "Diagnosis: Potential African Swine Fever (ASF). Treatment: No cure or vaccine exists. Isolate immediately, report to authorities, and strictly boil all swill before feeding."
    },
    {
        "species": "Rabbit",
        "user_prompt": "sneezing, white nasal discharge, matted fur on paws",
        "ideal_response": "Diagnosis: Snuffles (Pasteurellosis). Treatment: Isolate rabbit. Administer Enrofloxacin drops for 3-5 days. Improve hutch ventilation."
    },
    # ... You can add all 20 records here following this format
]

for item in data:
    AITrainingData.objects.get_or_create(
        species=item['species'],
        user_prompt=item['user_prompt'],
        defaults={'ideal_response': item['ideal_response'], 'verified_by_vet': True}
    )

print(f"Successfully uploaded {len(data)} training records to AgriTrack AI!")