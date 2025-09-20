import requests
import os
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class AIService:
    def __init__(self):
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.mock_mode = not self.huggingface_api_key
        self.summarization_model = "facebook/bart-large-cnn"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.summarization_model}"

    async def analyze_document(self, content: str, language: str = "en") -> Dict[str, Any]:
        """Analyze document and return multilingual summary, clauses, risk score, and recommendations"""
        try:
            if self.mock_mode:
                logger.info("Using mock mode - no API key provided")
                return await self._mock_analysis(content, language)

            summary = await self._get_summary(content, language)
            analysis = await self._analyze_content(content, summary, language)
            return analysis

        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return await self._mock_analysis(content, language)

    async def _get_summary(self, content: str, language: str) -> str:
        """Get summary using Hugging Face API with multilingual prompts"""
        if self.mock_mode:
            return await self._get_mock_summary(content, language)

        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
        truncated_content = content[:1500]

        prompts = {
            "en": f"Summarize this legal document in simple, plain English: {truncated_content}",
            "bn": f"এই আইনী দলিলটি সরল, স্পষ্ট বাংলায় সংক্ষিপ্ত করুন: {truncated_content}",
            "hi": f"इस कानूनी दस्तावेज़ को सरल, स्पष्ट हिंदी में संक्षेप में प्रस्तुत करें: {truncated_content}",
            "ta": f"இந்த சட்ட ஆவணத்தை எளிய, தெளிவான தமிழில் சுருக்கவும்: {truncated_content}",
            "te": f"ఈ చట్టపరమైన పత్రాన్ని సరళమైన, స్పష్టమైన తెలుగులో సంగ్రహించండి: {truncated_content}"
        }

        prompt = prompts.get(language, prompts["en"])
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 200, "min_length": 80, "do_sample": False, "temperature": 0.3}
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary_text = result[0].get('summary_text', None)
                    if not summary_text:
                        return await self._get_mock_summary(content, language)
                    return summary_text
                return await self._get_mock_summary(content, language)
            elif response.status_code == 503:
                logger.info("Model loading, retrying in 10s...")
                time.sleep(10)
                return await self._get_summary(content, language)
            else:
                error_msg = response.json().get('error', 'Unknown error')
                logger.error(f"Hugging Face API error: {error_msg}")
                return await self._get_mock_summary(content, language)

        except Exception as e:
            logger.error(f"Hugging Face API call failed: {str(e)}")
            return await self._get_mock_summary(content, language)

    async def _analyze_content(self, content: str, summary: str, language: str) -> Dict[str, Any]:
        """Analyze document content for clauses, risks, and multilingual explanations"""
        clauses = []

        clause_patterns = {
            "indemnification": ["indemnify", "indemnification", "hold harmless", "ক্ষতিপূরণ", "क्षतिपूर्ति", "பழிவாங்கல்", "పరిహారం"],
            "liability": ["liability", "liable", "damages", "compensate", "দায়", "दायित्व", "பொறுப்பு", "బాధ్యత"],
            "termination": ["terminate", "termination", "expire", "cancel", "সমাপ্তি", "समाप्ति", "முடிவு", "ముగింపు"],
            "confidentiality": ["confidential", "non-disclosure", "nda", "secret", "গোপনীয়", "गोपनीय", "ரகசிய", "గోప్య"],
            "payment": ["payment", "fee", "compensation", "price", "পেমেন্ট", "भुगतान", "கட்டணம்", "చెల్లింపు"],
            "warranty": ["warranty", "guarantee", "warrant", "ওয়ারেন্টি", "वारंटी", "உத்தரவாதம்", "వారంటీ"]
        }

        content_lower = content.lower()
        for clause_type, keywords in clause_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                risk_level = self._determine_risk_level(clause_type)
                clauses.append({
                    "type": clause_type,
                    "description": self._get_clause_description(clause_type, language),
                    "risk_level": risk_level,
                    "explanation": self._get_clause_explanation(clause_type, risk_level, language)
                })

        if not clauses:
            clauses.append({
                "type": "general",
                "description": self._get_clause_description("general", language),
                "risk_level": "low",
                "explanation": self._get_clause_explanation("general", "low", language)
            })

        risk_score = self._calculate_risk_score(clauses)
        plain_language = self._create_plain_language(summary, language)

        return {
            "summary": summary,
            "plain_language": plain_language,
            "clauses": clauses,
            "risk_score": risk_score,
            "recommended_actions": self._get_recommended_actions(risk_score, language)
        }

    def _determine_risk_level(self, clause_type: str) -> str:
        mapping = {
            "indemnification": "medium",
            "liability": "medium",
            "confidentiality": "medium",
            "warranty": "low",
            "payment": "low",
            "termination": "low",
            "general": "low"
        }
        return mapping.get(clause_type, "low")

    def _get_clause_description(self, clause_type: str, language: str) -> str:
        descriptions = {
            "indemnification": {
                "en": "This clause requires one party to compensate the other for losses or damages.",
                "bn": "এই ধারাটি অন্য পক্ষকে ক্ষতি বা ক্ষতিপূরণের জন্য ক্ষতিপূরণ দিতে বলে।",
                "hi": "यह खंड एक पक्ष को नुकसान या क्षति के लिए दूसरे पक्ष को मुआवजा देने की आवश्यकता है।",
                "ta": "இந்த விதி, இழப்புகள் அல்லது சேதங்களுக்கு ஒரு தரப்பு மற்ற தரப்புக்கு ஈடுசெய்ய வேண்டும்.",
                "te": "ఈ నిబంధన ఒక పక్షాన్ని నష్టాల కోసం మరొక పక్షానికి పరిహారం చెల్లించడానికి చెప్పిస్తుంది."
            },
            "general": {
                "en": "This appears to be a standard legal agreement.",
                "bn": "এটি একটি মানক আইনী চুক্তি বলে মনে হচ্ছে।",
                "hi": "यह एक मानक कानूनी समझौता प्रतीत होता है।",
                "ta": "இது ஒரு நிலையான சட்ட ஒப்பந்தம் போல் தெரிகிறது.",
                "te": "ఇది ఒక ప్రామాణిక చట్టపరమైన ఒప్పందం."
            }
        }
        return descriptions.get(clause_type, descriptions["general"]).get(language, descriptions["general"]["en"])

    def _get_clause_explanation(self, clause_type: str, risk_level: str, language: str) -> str:
        explanations = {
            "indemnification": {
                "en": "Can create significant financial obligations if things go wrong.",
                "bn": "যদি কিছু ভুল হয় তবে উল্লেখযোগ্য আর্থিক বাধ্যবাধকতা তৈরি করতে পারে।",
                "hi": "यदि कुछ गलत होता है तो महत्वपूर्ण वित्तीय दायित्व बन सकता है।",
                "ta": "விஷயங்கள் தவறாக நடந்தால் கணிசமான நிதி கடமைகளை உருவாக்கும்.",
                "te": "విషయాలు తప్పుగా జరిగితే గణనీయమైన ఆర్థిక బాధ్యతలు ఏర్పడతాయి."
            },
            "general": {
                "en": "Standard legal language that should still be reviewed carefully.",
                "bn": "মানক আইনী ভাষা রয়েছে যা সাবধানে পর্যালোচনা করা উচিত।",
                "hi": "मानक कानूनी भाषा शामिल है जिसकी सावधानीपूर्वक समीक्षा की जानी चाहिए।",
                "ta": "நிலையான சட்ட மொழி, கவனமாக மதிப்பாய்வு செய்யப்பட வேண்டும்.",
                "te": "ప్రామాణిక చట్టపరమైన భాష, జాగ్రత్తగా సమీక్షించాలి."
            }
        }
        base = explanations.get(clause_type, explanations["general"]).get(language, explanations["general"]["en"])
        return f"{risk_level.capitalize()} risk: {base}"

    def _calculate_risk_score(self, clauses: List[Dict[str, Any]]) -> float:
        if not clauses:
            return 0.3
        risk_values = {"low": 0.3, "medium": 0.6, "high": 0.9}
        total = sum(risk_values.get(clause.get("risk_level", "low"), 0.3) for clause in clauses)
        return min(1.0, total / len(clauses))

    def _get_recommended_actions(self, risk_score: float, language: str) -> List[str]:
        recommendations = {
            "en": [
                ["Review the document carefully", "Ensure you understand all obligations", "Clarify ambiguous terms"],
                ["Consider seeking legal advice", "Negotiate unfavorable terms", "Request clarification on specific clauses"],
                ["Strongly recommend consulting a lawyer", "Consider significant changes", "Evaluate whether to proceed"]
            ],
            "bn": [
                ["দলিলটি সাবধানে পর্যালোচনা করুন", "সমস্ত দায়িত্ব বোঝা নিশ্চিত করুন", "অস্পষ্ট শর্ত স্পষ্ট করুন"],
                ["আইনি পরামর্শ নেওয়ার কথা বিবেচনা করুন", "অপ্রিয় শর্ত নিয়ে আলোচনা করুন", "নির্দিষ্ট ধারাগুলি স্পষ্ট করুন"],
                ["আইনজীবীর পরামর্শ নেওয়া শক্তভাবে সুপারিশ করা হয়", "গুরুত্বপূর্ণ পরিবর্তনের কথা বিবেচনা করুন", "চলতে হবে কিনা মূল্যায়ন করুন"]
            ]
        }
        lang = recommendations.get(language, recommendations["en"])
        if risk_score < 0.4:
            return lang[0]
        elif risk_score < 0.7:
            return lang[1]
        else:
            return lang[2]

    def _create_plain_language(self, summary: str, language: str) -> str:
        translations = {
            "en": f"In simple terms: {summary}",
            "bn": f"সহজভাবে বললে: {summary}",
            "hi": f"सरल शब्दों में: {summary}",
            "ta": f"எளிதான முறையில்: {summary}",
            "te": f"సరళమైన పదాలలో: {summary}"
        }
        return translations.get(language, translations["en"])

    async def _mock_analysis(self, content: str, language: str) -> Dict[str, Any]:
        summary = await self._get_mock_summary(content, language)
        plain_language = self._create_plain_language(summary, language)
        clauses = [{
            "type": "general",
            "description": self._get_clause_description("general", language),
            "risk_level": "low",
            "explanation": self._get_clause_explanation("general", "low", language)
        }]
        return {
            "summary": summary,
            "plain_language": plain_language,
            "clauses": clauses,
            "risk_score": 0.3,
            "recommended_actions": self._get_recommended_actions(0.3, language)
        }

    async def _get_mock_summary(self, content: str, language: str) -> str:
        texts = {
            "en": "Mock summary: Legal document could not be analyzed due to missing API key.",
            "bn": "মক সংক্ষিপ্তসার: API কী অনুপস্থিতির কারণে আইনী দলিল বিশ্লেষণ করা যায়নি।",
            "hi": "मॉक सारांश: API कुंजी की कमी के कारण कानूनी दस्तावेज़ का विश्लेषण नहीं किया जा सका।",
            "ta": "மொக் சுருக்கம்: API விசை இல்லை காரணமாக சட்ட ஆவணத்தை பகுப்பாய்வு செய்ய முடியவில்லை.",
            "te": "మాక్ సారాంశం: API కీ అందుబాటులో లేకపోవడం కారణంగా చట్టపరమైన పత్రాన్ని విశ్లేషించలేము."
        }
        return texts.get(language, texts["en"])
