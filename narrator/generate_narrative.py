
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
FINDINGS_FILE = BASE_DIR / "narrator" / "findings.json"
OUTPUT_FILE = BASE_DIR / "narrator" / "genai_narrative.txt"

with open(FINDINGS_FILE, "r", encoding="utf-8") as file:
    findings = json.load(file)

# Offline fallback: works without an API key or internet access.
narrative = (
    "Mamaearth E-commerce Business Analysis\n\n"
    f"Total revenue: {findings.get('total_revenue', 'Not available')}\n"
    f"Total orders: {findings.get('total_orders', 'Not available')}\n"
    f"Overall return rate: {findings.get('overall_return_rate_pct', 'Not available')}%\n\n"
    "This report summarizes the available structured findings. "
    "Review category and monthly trends to identify areas for improvement. "
    "These patterns describe the dataset and do not prove the causes of returns."
)

OUTPUT_FILE.write_text(narrative, encoding="utf-8")
print("Narrative report generated using the offline fallback.")
