import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from health.models import AITrainingData

def seed_expert_data():
    print("🧹 Cleaning database for fresh training...")
    AITrainingData.objects.all().delete()

    data = [
        # --- PIGS ---
        {"species": "Pig", "diagnosis": "Swine Erysipelas", "severity": "High", 
         "symptoms": "diamond shaped skin lesions, high fever, stiff joints, lameness, sudden death",
         "treatment": "Administer Penicillin immediately. Isolate pig. Disinfect pens."},
        {"species": "Pig", "diagnosis": "Coccidiosis", "severity": "Medium", 
         "symptoms": "yellow diarrhea, dehydration, rough hair coat, stunted growth in piglets",
         "treatment": "Provide Toltrazuril or Sulfa drugs. Improve sanitation and keep floors dry."},
        {"species": "Pig", "diagnosis": "Atrophic Rhinitis", "severity": "Medium", 
         "symptoms": "twisted snout, sneezing, nose bleeds, tear staining, shortened upper jaw",
         "treatment": "Improve air quality. Vaccinate the herd. Use prescribed feed medication."},
        
        # --- RABBITS ---
        {"species": "Rabbit", "diagnosis": "Myxomatosis", "severity": "Critical", 
         "symptoms": "swollen eyes, milky eye discharge, lumps on head and ears, fever, lethargy",
         "treatment": "No effective treatment. Provide supportive care (fluids/warmth) or euthanasia to prevent spread."},
        {"species": "Rabbit", "diagnosis": "Ear Canker", "severity": "Low", 
         "symptoms": "crusty ears, brown discharge, head shaking, scratching ears, inflamed canal",
         "treatment": "Clean ears with mineral oil. Apply Ivermectin drops. Disinfect cage."},
        {"species": "Rabbit", "diagnosis": "Vent Disease (Syphilis)", "severity": "Medium", 
         "symptoms": "blisters on genitals, scabs around nose and mouth, swelling, redness",
         "treatment": "Administer Penicillin injections (Vet only). Do not breed until fully cleared."}
    ]

    for entry in data:
        AITrainingData.objects.create(**entry)
    print(f"✅ Loaded {len(data)} expert records.")

if __name__ == "__main__":
    seed_expert_data()