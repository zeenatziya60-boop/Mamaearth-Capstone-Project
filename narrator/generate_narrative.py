
from pathlib import Path
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent
NARRATOR_DIR = BASE_DIR / "narrator"
FINDINGS_FILE = NARRATOR_DIR / "findings.json"
OUTPUT_FILE = NARRATOR_DIR / "genai_narrative.txt"
SAMPLE_FILE = NARRATOR_DIR / "sample_output.txt"

with open(FINDINGS_FILE, "r", encoding="utf-8") as f:
    findings = json.load(f)


def generate_scr_narrative_offline(findings: dict) -> str:
    """Deterministic fallback; works without internet or an API key."""
    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    inflated = findings["outlier_inflated_month"]

    return f"""S — SITUATION
Mamaearth's e-commerce dataset contains {findings['cleaned_order_count']} orders after data cleaning.
Cleaned revenue is INR {findings['cleaned_total_revenue_inr']:.2f}, compared with raw revenue of INR {findings['raw_total_revenue_inr']:.2f}.

C — COMPLICATION
Five duplicate natural-key orders were removed, reducing revenue by INR {findings['duplicate_reconciliation_delta_inr']:.2f}.
COD has the highest payment-method return rate at {rates['COD']:.1f}%, compared with CARD at {rates['CARD']:.1f}% and UPI at {rates['UPI']:.1f}%.
The highest-risk segment is COD in city tier {risk['city_tier']}, with a return rate of {risk['return_rate_pct']:.1f}%.
January's apparent revenue was INR {inflated['apparent_revenue_inr']:.2f}; after excluding flagged quantity outliers, it was INR {inflated['corrected_revenue_inr']:.2f}.

R — RECOMMENDATION
Investigate COD returns, especially in tier-{risk['city_tier']} cities.
Review the duplicate-order handling process and monitor monthly revenue after flagging quantity outliers.
The highest-revenue month after excluding flagged outliers was {peak['month']}, at INR {peak['revenue_inr']:.2f}.
These findings show associations in the available dataset; they do not prove the causes of returns.
"""


def generate_scr_narrative(findings: dict) -> str:
    """Try Gemini first; use the deterministic report if unavailable."""
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=30000),
            )

            prompt = (
                "Write a concise business report with exactly these sections: "
                "S — SITUATION, C — COMPLICATION, R — RECOMMENDATION. "
                "Use only the numbers in this JSON. Do not invent numbers. "
                "Explain duplicate revenue reconciliation, payment return rates, "
                "the highest-risk segment, and the outlier-corrected peak month. "
                "State that correlation does not prove causation.\n\n"
                + json.dumps(findings, indent=2)
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a careful senior e-commerce business analyst. "
                        "Use exact supplied facts and avoid unsupported claims."
                    ),
                    temperature=0.0,
                    max_output_tokens=500,
                ),
            )

            if response.text and response.text.strip():
                return response.text.strip()

        except Exception as error:
            print(f"Gemini unavailable; using offline fallback. Reason: {error}")

    return generate_scr_narrative_offline(findings)


def check_numeric_accuracy(report: str, findings: dict) -> bool:
    """Check the five key facts required by the project rubric."""
    required_values = [
        f"{findings['cleaned_total_revenue_inr']:.2f}",
        f"{findings['return_rate_by_payment']['COD']:.1f}",
        f"{findings['highest_risk_segment']['return_rate_pct']:.1f}",
        f"{findings['duplicate_reconciliation_delta_inr']:.2f}",
        findings["true_peak_month"]["month"],
        f"{findings['true_peak_month']['revenue_inr']:.2f}",
    ]

    missing = [value for value in required_values if value not in report]

    if missing:
        print("Numeric accuracy check FAILED. Missing values:", missing)
        return False

    print("Numeric accuracy check PASSED.")
    return True


narrative = generate_scr_narrative(findings)

OUTPUT_FILE.write_text(narrative + "\n", encoding="utf-8")
SAMPLE_FILE.write_text(narrative + "\n", encoding="utf-8")

print("Narrative report saved to narrator/genai_narrative.txt")
print("Sample output saved to narrator/sample_output.txt")
check_numeric_accuracy(narrative, findings)
