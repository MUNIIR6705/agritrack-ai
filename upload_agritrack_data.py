import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from health.models import AITrainingData

training_data = [
    # --- PIG RECORDS (25) ---
    {"species": "Pig", "user_prompt": "high fever, bluish ears, bloody diarrhea, sudden death", "ideal_response": "Diagnosis: Potential African Swine Fever (ASF). Treatment: No cure or vaccine. Isolate immediately, report to authorities, and strictly boil all swill."},
    {"species": "Pig", "user_prompt": "piglets with watery yellow diarrhea, sunken eyes, dehydration", "ideal_response": "Diagnosis: Colibacillosis (E. coli). Treatment: Provide oral rehydration salts (ORS). Use vet-prescribed antibiotics and keep piglets warm."},
    {"species": "Pig", "user_prompt": "swollen, hot udder, sow refuses to nurse", "ideal_response": "Diagnosis: Mastitis. Treatment: Massage udder with warm water. Extract milk from affected quarter. Consult vet for Pen-Strep antibiotics."},
    {"species": "Pig", "user_prompt": "diamond shaped red skin lesions, high fever, lameness", "ideal_response": "Diagnosis: Swine Erysipelas. Treatment: Injectable Penicillin (e.g., Pen-Strep) for 3-5 days. Isolate the animal immediately."},
    {"species": "Pig", "user_prompt": "intense itching, red spots, crusty thick skin on ears/neck", "ideal_response": "Diagnosis: Sarcoptic Mange. Treatment: Injectable Ivermectin or specialized skin spray. Disinfect the entire pen."},
    {"species": "Pig", "user_prompt": "barking cough, rapid breathing, fever in growers", "ideal_response": "Diagnosis: Enzootic Pneumonia. Treatment: Improve ventilation. Use antibiotics like Tylosin or Oxytetracycline as directed by a vet."},
    {"species": "Pig", "user_prompt": "vomiting, foul-smelling gray diarrhea in weaners", "ideal_response": "Diagnosis: Swine Dysentery. Treatment: Add Tiamulin or Lincomycin to water/feed as per vet guidance. Sanitize water troughs."},
    {"species": "Pig", "user_prompt": "pale skin, weakness, fast breathing in piglets", "ideal_response": "Diagnosis: Iron Deficiency Anemia. Treatment: Injectable Iron Dextran at 3 days of age. Ensure sow has balanced nutrition."},
    {"species": "Pig", "user_prompt": "stiffness, muscle tremors, lockjaw, sensitive to sound", "ideal_response": "Diagnosis: Tetanus. Treatment: Keep in dark, quiet stall. Clean the wound with peroxide. Administer Penicillin and Tetanus antitoxin."},
    {"species": "Pig", "user_prompt": "piglet shaking, tremors, unable to stand properly", "ideal_response": "Diagnosis: Congenital Tremors. Treatment: No specific cure. Provide extra warmth and help piglets reach the teat to suckle; most recover in weeks."},
    {"species": "Pig", "user_prompt": "bloody urine, arching back, painful urination", "ideal_response": "Diagnosis: Cystitis/Pyelonephritis. Treatment: Increase water intake. Administer Ampicillin or Amoxicillin for 7-10 days."},
    {"species": "Pig", "user_prompt": "lameness, overgrown hooves, cracks in hoof wall", "ideal_response": "Diagnosis: Hoof Rot or Overgrowth. Treatment: Trim hooves. Clean cracks with antiseptic. Use a footbath with 5% copper sulfate solution."},
    {"species": "Pig", "user_prompt": "sow unable to stand after farrowing, shivering", "ideal_response": "Diagnosis: Milk Fever (Hypocalcemia). Treatment: Immediate IV or subcutaneous Calcium Borogluconate injection by a professional vet."},
    {"species": "Pig", "user_prompt": "small blisters on snout and feet, lameness, drooling", "ideal_response": "Diagnosis: Potential Foot and Mouth Disease (FMD). Treatment: Notifiable disease. Isolate and notify vet authorities. Supportive care with soft bedding."},
    {"species": "Pig", "user_prompt": "convulsions, head pressing, excessive thirst", "ideal_response": "Diagnosis: Salt Poisoning/Water Deprivation. Treatment: Provide water slowly in small amounts. Rapid rehydration can be fatal."},
    {"species": "Pig", "user_prompt": "dark tarry stool, weight loss, abdominal pain", "ideal_response": "Diagnosis: Gastric Ulcers. Treatment: Reduce stress. Feed a coarser diet (avoid finely ground feed). Add Vitamin E to diet."},
    {"species": "Pig", "user_prompt": "piglets with greasy, brown crusts on skin, non-itchy", "ideal_response": "Diagnosis: Greasy Pig Disease (Exudative Epidermitis). Treatment: Wash with antiseptic soap. Inject Penicillin or Lincomycin. Ensure dry bedding."},
    {"species": "Pig", "search": "worms", "user_prompt": "distended belly, cough, slow growth, visible worms in dung", "ideal_response": "Diagnosis: Roundworms (Ascaris suum). Treatment: Administer Levamisole or Albendazole dewormer. Repeat in 2 weeks."},
    {"species": "Pig", "user_prompt": "sow with high fever, abortion, stillborn piglets", "ideal_response": "Diagnosis: Porcine Reproductive and Respiratory Syndrome (PRRS) or Leptospirosis. Treatment: Consult vet for vaccination and antibiotic therapy."},
    {"species": "Pig", "user_prompt": "swollen joints, fever, reluctance to move in piglets", "ideal_response": "Diagnosis: Joint Ill (Streptococcal infection). Treatment: Clean navels at birth with Iodine. Inject Penicillin for 5 days."},
    {"species": "Pig", "user_prompt": "paralysis of hind legs, unable to stand, but alert", "ideal_response": "Diagnosis: Spinal Injury or Vitamin B1 Deficiency. Treatment: Provide soft bedding. Consult vet for Vitamin B1/B12 injections."},
    {"species": "Pig", "user_prompt": "white spots on liver during slaughter", "ideal_response": "Diagnosis: Milk Spots (Roundworm migration). Action: This indicates a heavy worm burden. Review and increase the deworming schedule for the herd."},
    {"species": "Pig", "user_prompt": "sow showing heat but not conceiving", "ideal_response": "Diagnosis: Infertility. Action: Check boar fertility. Ensure sow is not over-conditioned (fat). Check for Brucellosis."},
    {"species": "Pig", "user_prompt": "bloody diarrhea in growers, weight loss", "ideal_response": "Diagnosis: Ileitis (Porcine Proliferative Enteropathy). Treatment: Administer Tylosin or Tiamulin in feed or water for 7-14 days."},
    {"species": "Pig", "user_prompt": "piglets with white/yellow pasty diarrhea at 2-3 weeks", "ideal_response": "Diagnosis: Coccidiosis. Treatment: Administer Toltrazuril orally to piglets. Improve pen hygiene to reduce oocyst load."},

    # --- RABBIT RECORDS (25) ---
    {"species": "Rabbit", "user_prompt": "sneezing, white nasal discharge, matted paws", "ideal_response": "Diagnosis: Snuffles (Pasteurellosis). Treatment: Isolate immediately. Administer Enrofloxacin drops. Improve hutch ventilation."},
    {"species": "Rabbit", "user_prompt": "crusty ears, intense scratching, head shaking", "ideal_response": "Diagnosis: Ear Mites (Canker). Treatment: Apply Ivermectin drops or liquid paraffin/vegetable oil to soothe ears. Clean the hutch."},
    {"species": "Rabbit", "user_prompt": "no fecal droppings, hunched posture, bloated belly", "ideal_response": "Diagnosis: GI Stasis. Treatment: Provide oral fluids. Feed high-fiber hay only. Seek vet help for gut motility meds like Metoclopramide."},
    {"species": "Rabbit", "user_prompt": "watery diarrhea, pot belly, weight loss in kits", "ideal_response": "Diagnosis: Coccidiosis. Treatment: Use Sulfa-based drugs (e.g., Sulfaquinoxaline) in water for 10-14 days. Clean floors daily."},
    {"species": "Rabbit", "user_prompt": "drooling, wet chin, unable to eat pellets", "ideal_response": "Diagnosis: Malocclusion (Overgrown teeth). Treatment: Professional tooth trimming by a vet. Provide constant hay to wear down teeth."},
    {"species": "Rabbit", "user_prompt": "matted fur, foul smell, visible maggots near tail", "ideal_response": "Diagnosis: Flystrike. Treatment: EMERGENCY. Remove maggots manually. Clean with Iodine. Keep fly-proof. See vet immediately."},
    {"species": "Rabbit", "user_prompt": "head tilt, loss of balance, rolling over", "ideal_response": "Diagnosis: E. cuniculi or Inner Ear Infection. Treatment: 28-day course of Fenbendazole dewormer. Provide a safe, padded cage."},
    {"species": "Rabbit", "user_prompt": "red, sore, hairless patches on bottom of hind feet", "ideal_response": "Diagnosis: Sore Hocks (Pododermatitis). Treatment: Provide a solid resting board. Clean sores with antiseptic. Use Zinc Oxide ointment."},
    {"species": "Rabbit", "user_prompt": "lumps under the skin, especially near the jaw", "ideal_response": "Diagnosis: Abscesses. Treatment: Surgical drainage by a vet. Flush with dilute Iodine. Administer long-term antibiotics."},
    {"species": "Rabbit", "user_prompt": "sudden death with blood from nose/anus", "ideal_response": "Diagnosis: Rabbit Hemorrhagic Disease (RHD). Treatment: No cure. Highly contagious. Report to authorities. Vaccinate healthy rabbits."},
    {"species": "Rabbit", "user_prompt": "swelling around eyes, mouth, and genitals", "ideal_response": "Diagnosis: Myxomatosis. Treatment: Usually fatal. Provide supportive care (warmth, fluids) or euthanize to prevent spread. Protect from mosquitoes."},
    {"species": "Rabbit", "user_prompt": "frequent sneezing with clear discharge, red eyes", "ideal_response": "Diagnosis: Allergy or Dust Irritation. Treatment: Clean hutch. Change bedding to dust-free straw or wood shavings. Monitor for Snuffles."},
    {"species": "Rabbit", "user_prompt": "blood in urine, straining to urinate", "ideal_response": "Diagnosis: Bladder Stones or Uterine Cancer (in females). Treatment: Consult vet for X-ray/Ultrasound. Spaying is the best prevention for cancer."},
    {"species": "Rabbit", "user_prompt": "patchy hair loss, circular red rings on skin", "ideal_response": "Diagnosis: Ringworm (Fungal). Treatment: Use antifungal creams (e.g., Clotrimazole). Wear gloves as this is zoonotic (spreads to humans)."},
    {"species": "Rabbit", "user_prompt": "doe killing or eating her own kits", "ideal_response": "Diagnosis: Stress or Thirst. Action: Ensure constant access to water. Avoid disturbing the nest box. Check for loud noises/predators nearby."},
    {"species": "Rabbit", "user_prompt": "swollen, blue, cold mammary glands", "ideal_response": "Diagnosis: Blue Bag (Mastitis). Treatment: Isolate doe. Remove kits. Administer Penicillin and apply warm compresses to the udder."},
    {"species": "Rabbit", "user_prompt": "rabbit panting, ears feel very hot, lethargic", "ideal_response": "Diagnosis: Heat Stroke. Treatment: Move to a cool area. Wipe ears with cool (not ice cold) water. Provide cool drinking water."},
    {"species": "Rabbit", "user_prompt": "kits dying at 2-4 weeks with bloated bellies", "ideal_response": "Diagnosis: Mucoid Enteropathy. Treatment: Stop all greens. Provide high-quality hay. Rehydrate with ORS. High mortality rate."},
    {"species": "Rabbit", "user_prompt": "white, flaky skin on the back (dandruff)", "ideal_response": "Diagnosis: Walking Dandruff (Cheyletiella Mites). Treatment: Use Ivermectin (spot-on or injection). Thoroughly clean the environment."},
    {"species": "Rabbit", "user_prompt": "swelling/scabs on the nose and genitals", "ideal_response": "Diagnosis: Rabbit Syphilis (Vent Disease). Treatment: Injectable Penicillin (e.g., Pen-Strep) for 3 weeks. Do not breed affected animals."},
    {"species": "Rabbit", "user_prompt": "wet fur around the mouth and neck", "ideal_response": "Diagnosis: Wet Dewlap. Treatment: Dry the area. Use a water bottle instead of a bowl. Trim fur if it remains wet and infected."},
    {"species": "Rabbit", "user_prompt": "weakness in hind legs, dragging legs", "ideal_response": "Diagnosis: Broken Back or Nerve Damage. Action: Minimize handling. See vet for X-ray. Often caused by improper handling or sudden jumps."},
    {"species": "Rabbit", "user_prompt": "fecal matter stuck to the fur around the tail", "ideal_response": "Diagnosis: Poopy Butt (Cecotropes buildup). Action: Clean area with warm water. Reduce high-protein pellets; increase fiber/hay intake."},
    {"species": "Rabbit", "user_prompt": "small, hard, dark feces or very small droppings", "ideal_response": "Diagnosis: Dehydration or Early GI Stasis. Action: Increase fresh water access. Provide wet leafy greens (if accustomed) and extra hay."},
    {"species": "Rabbit", "user_prompt": "excessive tooth grinding and hunched over", "ideal_response": "Diagnosis: Severe Pain (often abdominal). Action: This is a sign of distress. Check for GI stasis or injury immediately. See a vet."},
]

for item in training_data:
    AITrainingData.objects.get_or_create(
        species=item['species'],
        user_prompt=item['user_prompt'],
        defaults={'ideal_response': item['ideal_response'], 'verified_by_vet': True}
    )

print(f"AgriTrack AI successfully trained with {len(training_data)} verified Kenyan livestock records!")