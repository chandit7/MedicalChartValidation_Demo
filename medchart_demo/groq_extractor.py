import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from groq import Groq


class GroqPDFExtractor:
    """
    Intelligent extractor for PDF-derived chart text using Groq.
    Intended for PDF inputs only.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not configured.")
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.cache: Dict[str, Dict[str, Any]] = {}

    def extract_from_text(self, chart_text: str) -> Dict[str, Any]:
        cache_key = self._get_cache_key(chart_text)
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = self._build_extraction_prompt(chart_text)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical chart data extraction expert. "
                        "Extract structured information from medical charts and return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=1200,
        )

        result_text = response.choices[0].message.content or ""
        cleaned = self._clean_json_response(result_text)
        extracted_data = json.loads(cleaned)
        validated = self._validate_extraction(extracted_data)

        self.cache[cache_key] = validated
        return validated

    def _build_extraction_prompt(self, chart_text: str) -> str:
        return f"""
Extract structured information from this medical chart text. Return ONLY valid JSON.

Chart Text:
{chart_text[:6000]}

Return JSON with exactly these keys:
{{
  "member_id": string or null,
  "visit_date": string (YYYY-MM-DD) or null,
  "npi": string or null,
  "icd_codes": array of strings,
  "all_codes": array of strings,
  "hba1c": number or null,
  "lab_date": string (YYYY-MM-DD) or null
}}

Rules:
- Return only JSON
- Use null for missing scalar fields
- Use [] for missing arrays
- Convert dates to YYYY-MM-DD when possible
- Include diagnosis codes in icd_codes and all_codes
- hba1c must be numeric only
"""

    def _clean_json_response(self, response: str) -> str:
        if "```json" in response:
            response = response.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in response:
            response = response.split("```", 1)[1].split("```", 1)[0]
        return response.strip()

    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {
            "member_id": data.get("member_id"),
            "visit_date": self._validate_date(data.get("visit_date")),
            "npi": str(data["npi"]) if data.get("npi") is not None else None,
            "icd_codes": data.get("icd_codes") if isinstance(data.get("icd_codes"), list) else [],
            "all_codes": data.get("all_codes") if isinstance(data.get("all_codes"), list) else [],
            "hba1c": self._validate_hba1c(data.get("hba1c")),
            "lab_date": self._validate_date(data.get("lab_date")),
        }
        return normalized

    def _validate_date(self, date_str: Any) -> Optional[str]:
        if not date_str:
            return None
        if not isinstance(date_str, str):
            date_str = str(date_str)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except (ValueError, TypeError):
            return None

    def _validate_hba1c(self, value: Any) -> Optional[float]:
        if value in (None, ""):
            return None
        try:
            return float(str(value).replace("%", "").strip())
        except (ValueError, TypeError):
            return None

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text[:1000].encode("utf-8")).hexdigest()

# Made with Bob
