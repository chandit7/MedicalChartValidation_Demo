import os
import re
from datetime import date

try:
    from groq_extractor import GroqPDFExtractor
except ImportError:
    GroqPDFExtractor = None

# Known ICD-10 codes for validation
KNOWN_ICD = {"Z00.00", "Z12.31", "E11.9", "Z23", "Z79.4", "Z13.1", "E11.65"}

def run_extract_agent(text: str, file_type: str = "txt", use_groq_for_pdf: bool = True, api_key: str | None = None) -> dict:
    """Extract structured data from chart text with PDF-only Groq support."""
    normalized_file_type = (file_type or "txt").lower()
    requested_method = "groq_pdf" if normalized_file_type == "pdf" and use_groq_for_pdf else "regex"

    if normalized_file_type == "pdf" and use_groq_for_pdf and GroqPDFExtractor:
        groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        if groq_api_key:
            try:
                extractor = GroqPDFExtractor(api_key=groq_api_key)
                result = extractor.extract_from_text(text)
                result["icd_codes"] = [c for c in result.get("icd_codes", []) if c in KNOWN_ICD]
                result["all_codes"] = result.get("all_codes", []) or result.get("icd_codes", [])
                result["raw_text"] = text
                result["_extraction_meta"] = {
                    "file_type": "pdf",
                    "method_requested": requested_method,
                    "method_used": "groq_pdf",
                    "llm_attempted": True,
                    "llm_status": "passed",
                    "fallback_used": False,
                    "llm_error": None,
                }
                return result
            except Exception as e:
                fallback_result = _regex_extract_fallback(text)
                fallback_result["_extraction_meta"] = {
                    "file_type": "pdf",
                    "method_requested": requested_method,
                    "method_used": "regex_fallback",
                    "llm_attempted": True,
                    "llm_status": "failed",
                    "fallback_used": True,
                    "llm_error": str(e),
                }
                return fallback_result

        skipped_result = _regex_extract_fallback(text)
        skipped_result["_extraction_meta"] = {
            "file_type": "pdf",
            "method_requested": requested_method,
            "method_used": "regex_pdf",
            "llm_attempted": False,
            "llm_status": "skipped",
            "fallback_used": False,
            "llm_error": None,
        }
        return skipped_result

    regex_result = _regex_extract_fallback(text)
    regex_result["_extraction_meta"] = {
        "file_type": normalized_file_type,
        "method_requested": "regex",
        "method_used": "regex",
        "llm_attempted": False,
        "llm_status": "not_applicable",
        "fallback_used": False,
        "llm_error": None,
    }
    return regex_result

def _regex_extract_fallback(text: str) -> dict:
    """Extract structured data from chart text using regex."""
    member_id = re.search(r"Member ID:\s*(\S+)", text)
    visit_date = re.search(r"Visit Date:\s*([\d-]+)", text)
    npi = re.search(r"Provider NPI:\s*(\d+)", text)
    icd_line = re.search(r"Diagnosis Codes:\s*(.+)", text)

    raw_codes = [c.strip() for c in icd_line.group(1).split(",")] if icd_line else []
    valid_codes = [c for c in raw_codes if c in KNOWN_ICD]

    hba1c = re.search(r"HbA1c:\s*([\d.]+)", text)
    lab_date = re.search(r"HbA1c:.*?on\s*([\d-]+)", text)

    return {
        "member_id": member_id.group(1) if member_id else None,
        "visit_date": visit_date.group(1) if visit_date else None,
        "npi": npi.group(1) if npi else None,
        "icd_codes": valid_codes,
        "all_codes": raw_codes,
        "hba1c": float(hba1c.group(1)) if hba1c else None,
        "lab_date": lab_date.group(1) if lab_date else None,
        "raw_text": text
    }

def run_gap_match_agent(extracted: dict, gap_row: dict) -> dict:
    """Calculate gap closure score based on chart data."""
    scores = {}
    
    # R1: ICD code match (weight 0.5)
    # FIXED: Changed from split("|") to split(",")
    required = [c.strip() for c in gap_row["required_icd_codes"].split(",")]
    found = set(extracted["icd_codes"])
    icd_score = 1.0 if any(r in found for r in required) else 0.0
    scores["icd_match"] = icd_score
    
    # R2: Visit date in window (weight 0.4)
    try:
        vd = date.fromisoformat(extracted["visit_date"])
        ws = date.fromisoformat(gap_row["window_start"])
        we = date.fromisoformat(gap_row["window_end"])
        date_score = 1.0 if ws <= vd <= we else 0.0
    except:
        date_score = 0.0
    scores["date_in_window"] = date_score
    
    # R3: Provider NPI present (weight 0.1)
    scores["provider_npi"] = 1.0 if extracted.get("npi") else 0.0
    
    # Calculate composite score
    composite = scores["icd_match"] * 0.5 + scores["date_in_window"] * 0.4 + scores["provider_npi"] * 0.1
    
    return {
        "composite": round(composite, 2),
        "per_rule": scores
    }

def run_discrepancy_agent(extracted: dict) -> list:
    """Detect discrepancies and anomalies in chart data."""
    flags = []
    
    # D1: HbA1c physiologically impossible
    if extracted.get("hba1c") and (extracted["hba1c"] > 15 or extracted["hba1c"] < 2):
        flags.append({
            "severity": "high",
            "msg": f"HbA1c={extracted['hba1c']} is outside physiological range"
        })
    
    # D2: Lab date vs visit date gap
    lab_dates = re.findall(r"HbA1c:.*?on\s*([\d-]+)", extracted.get("raw_text", ""))
    if lab_dates and extracted.get("visit_date"):
        try:
            vd = date.fromisoformat(extracted["visit_date"])
            ld = date.fromisoformat(lab_dates[0])
            gap_days = abs((vd - ld).days)
            if gap_days > 365:
                flags.append({
                    "severity": "high",
                    "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"
                })
            elif gap_days > 180:
                flags.append({
                    "severity": "medium",
                    "msg": f"Lab date {lab_dates[0]} is {gap_days} days from visit"
                })
        except:
            pass
    
    # D3: Unknown ICD codes (potential typos)
    unknown = [c for c in extracted.get("all_codes", []) if c not in extracted.get("icd_codes", [])]
    if unknown:
        flags.append({
            "severity": "low",
            "msg": f"Unrecognized codes: {', '.join(unknown)}"
        })
    
    # D4: Missing member ID
    if not extracted.get("member_id"):
        flags.append({
            "severity": "high",
            "msg": "Member ID not found in chart"
        })
    
    return flags

def run_decision_agent(gap_result: dict, flags: list, extracted: dict) -> dict:
    """Make final routing decision based on score and flags."""
    base = gap_result["composite"]
    
    # Calculate penalties
    high = sum(1 for f in flags if f["severity"] == "high")
    medium = sum(1 for f in flags if f["severity"] == "medium")
    low = sum(1 for f in flags if f["severity"] == "low")
    penalty = (high * 0.20) + (medium * 0.10) + (low * 0.03)
    
    score = round(max(0.0, min(1.0, base - penalty)), 2)
    
    # Hard override rules (checked in order)
    if not extracted.get("member_id"):
        return {
            "decision": "rejected",
            "score": score,
            "reason": "Missing member ID (hard reject)"
        }
    
    if high > 0:
        return {
            "decision": "manual_review",
            "score": score,
            "reason": f"{high} high-severity flag(s) found"
        }
    
    if gap_result["per_rule"]["icd_match"] == 0.0:
        return {
            "decision": "rejected",
            "score": score,
            "reason": "Required diagnosis code not in chart"
        }
    
    # Threshold-based routing
    if score >= 0.85:
        decision = "approved"
    elif score <= 0.40:
        decision = "rejected"
    else:
        decision = "manual_review"
    
    return {
        "decision": decision,
        "score": score,
        "reason": f"Score {score} (base {base} - penalty {round(penalty, 2)})"
    }

# Made with Bob
