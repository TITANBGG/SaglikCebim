from sqlalchemy.orm import Session
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_allergies import PatientAllergy
from app.models.test_result import TestResult
from app.models.radiology_image import RadiologyFinding, RadiologyImage
import re

class DiagnosisAgent:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = int(user_id)
        
        # Basit NLP Sözlüğü (Semptom Yakalayıcı)
        self.symptom_dict = {
            "ates": ["ateş", "yaniyor", "sicak"],
            "oksirik": ["öksürük", "öksürüyorum", "balgam"],
            "nefes_darligi": ["nefes", "tıkandım", "nefes alamıyorum"],
            "halsizlik": ["halsiz", "yorgun", "bitkin", "uyku"],
            "bas_agrisi": ["baş", "agriyor", "ağrısı"]
        }
        
        # Uzman Puanlama Tablosu
        self.disease_matrix = {
            "Akut Pnömoni (Zatürre)": {
                "blood": {"WBC": "high", "CRP": "high", "score": 15},
                "xray": {"label": "Pnömoni", "score": 30},
                "symptoms": ["ates", "oksirik", "nefes_darligi"],
                "symptom_score": 10
            },
            "Anemi (Kansızlık)": {
                "blood": {"HGB": "low", "Demir": "low", "score": 20},
                "xray": {"label": "Normal", "score": 0},
                "symptoms": ["halsizlik", "bas_agrisi"],
                "symptom_score": 10
            },
            "Viral Enfeksiyon": {
                "blood": {"CRP": "high", "WBC": "low", "score": 15},
                "xray": {"label": "Normal", "score": 0},
                "symptoms": ["ates", "halsizlik", "bas_agrisi"],
                "symptom_score": 10
            }
        }

    def _extract_symptoms(self, text: str) -> list[str]:
        import difflib
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        found_symptoms = set()
        
        for key, synonyms in self.symptom_dict.items():
            for syn in synonyms:
                # 1. Tam cümle veya alt dize eşleşmesi (Örn: "nefes alamıyorum")
                if syn in text_lower:
                    found_symptoms.add(key)
                    continue
                
                # 2. Bulanık (Fuzzy) eşleşme: Kullanıcı eksik/hatalı yazdıysa (Örn: "atşim", "öksrüyorum")
                if len(syn.split()) == 1: # Sadece tek kelimelik semptomlarda harf hatası aranır
                    matches = difflib.get_close_matches(syn, words, n=1, cutoff=0.6)
                    if matches:
                        found_symptoms.add(key)
                        
        return list(found_symptoms)

    def _get_anamnesis(self):
        profile = self.db.query(PatientProfile).filter(PatientProfile.user_id == self.user_id).first()
        conditions = self.db.query(PatientCondition).filter(PatientCondition.user_id == self.user_id).all()
        allergies = self.db.query(PatientAllergy).filter(PatientAllergy.user_id == self.user_id).all()
        
        cond_str = ", ".join([c.condition_name for c in conditions]) if conditions else "Bilinmeyen kronik hastalık yok"
        alg_str = ", ".join([a.allergen_name for a in allergies]) if allergies else "Bilinmeyen alerji yok"
        age = profile.age if profile and profile.age else "Bilinmiyor"
        
        return {
            "age": age,
            "conditions_text": cond_str,
            "allergies_text": alg_str,
            "conditions": [c.condition_name.lower() for c in conditions],
            "allergies": [a.allergen_name.lower() for a in allergies]
        }

    def analyze(self, current_complaint: str):
        # 1. Semptomları Çıkar
        symptoms = self._extract_symptoms(current_complaint)
        
        # 2. Anamnez Çek
        anamnesis = self._get_anamnesis()
        
        # 3. Son Kan Tahlillerini Çek
        abnormal_tests = self.db.query(TestResult).join(TestResult.report).filter(
            TestResult.report.has(user_id=self.user_id),
            TestResult.status != "normal"
        ).all()
        
        blood_dict = {t.test_name.upper(): t.status for t in abnormal_tests}
        
        # 4. Son Röntgeni Çek
        # Query son RadiologyImage ve ona bagli RadiologyFinding
        latest_image = self.db.query(RadiologyImage).filter(RadiologyImage.user_id == self.user_id).order_by(RadiologyImage.id.desc()).first()
        xray_label = "Normal"
        if latest_image:
            finding = self.db.query(RadiologyFinding).filter(RadiologyFinding.image_id == latest_image.id).first()
            if finding:
                xray_label = finding.finding_type # Veya tr_name
        
        # 5. Puanlama Motoru (Expert System Scoring)
        scores = {}
        for disease, rules in self.disease_matrix.items():
            scores[disease] = 0
            
            # Kan Şartları Puanı
            for test, status in rules["blood"].items():
                if test == "score": continue
                if blood_dict.get(test) == status:
                    scores[disease] += rules["blood"]["score"]
            
            # Röntgen Şartları Puanı
            if xray_label == rules["xray"]["label"]:
                scores[disease] += rules["xray"]["score"]
                
            # Semptom Şartları Puanı
            match_count = sum(1 for s in symptoms if s in rules["symptoms"])
            if match_count > 0:
                scores[disease] += (match_count * rules["symptom_score"])
                
        # En yüksek puanlı teşhisi bul
        best_match = max(scores.items(), key=lambda x: x[1])
        disease_name = best_match[0]
        score = best_match[1]
        
        # 6. Farmakoloji Güvenlik Kontrolü (Pharmacology Agent Firewall)
        warning = ""
        if disease_name == "Akut Pnömoni (Zatürre)":
            if any("penisilin" in alg for alg in anamnesis["allergies"]):
                warning = "⚠️ DİKKAT: Sistem kayıtlarında Penisilin alerjiniz görünmektedir. Olası antibiyotik tedavisinde hekiminize bunu mutlaka hatırlatınız."
        
        # 7. İletişim Ajanı (Template NLG)
        if score > 0:
            template = (
                f"Sistemdeki tıbbi kayıtlarınızı ve şikayetlerinizi analiz ettim.\n\n"
                f"**Anamnez:** {anamnesis['conditions_text']} geçmişiniz göz önüne alındı.\n"
                f"**Bulgular:** Kan tahlilinizdeki sapmalar ve radyolojik görüntünüz ({xray_label}), "
                f"şikayetlerinizle birleştiğinde en güçlü ihtimal olarak **{disease_name}** tablosu tespit edilmiştir.\n\n"
                f"{warning}\n\n"
                f"Lütfen kesin tanı ve tedavi için en kısa sürede bir uzman hekime başvurunuz."
            )
        else:
            template = (
                f"Şikayetlerinizi analiz ettim. Sistemdeki kan tahlilleriniz ve röntgen bulgularınız ile doğrudan eşleşen kritik bir tablo yakalayamadım. "
                f"Yine de şikayetleriniz devam ediyorsa lütfen uzman hekime danışın."
            )

        return {
            "template": template,
            "disease": disease_name if score > 0 else "Belirlenemedi",
            "score": score,
            "symptoms_found": symptoms,
            "blood_matched": [t.test_name for t in abnormal_tests],
            "xray_matched": xray_label,
            "warning": warning
        }
