from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os, hashlib, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.path.expanduser("~/review-agent")
DATA_FILE = os.path.join(BASE, "data", "requests.json")
REPORTS_DIR = os.path.join(BASE, "reports")

class ReviewInput(BaseModel):
    business: str
    link: str
    reviewer: str = ""
    rating: str = ""
    review_text: str
    violation: str
    evidence: str = ""

def load_requests():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_requests(requests):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)

def make_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

@app.get("/")
def home():
    return {"status": "Review Agent API chal raha hai"}

@app.get("/requests")
def get_requests():
    return load_requests()

@app.post("/analyze")
def analyze(data: ReviewInput):
    if data.violation == "Koi violation nahi":
        return {"status": "rejected", "message": "Ye jaiz negative review hai. Report nahi banegi."}

    review_hash = make_hash(data.link + data.review_text)
    requests = load_requests()
    for r in requests:
        if r.get("review_hash") == review_hash:
            return {"status": "duplicate", "message": "Ye review pehle report ho chuka hai."}

    report = f"""Google Review Report
====================
Business: {data.business}
Review Link: {data.link}
Reviewer: {data.reviewer}
Rating: {data.rating}
Review Text:
{data.review_text}

Violation Type: {data.violation}
Evidence: {data.evidence}

Report Draft:
This review appears to violate Google's review policies.
Violation: {data.violation}
Evidence: {data.evidence}
Request: Please review this content and take action as per Google policy.
"""

    entry = {
        "id": review_hash,
        "review_hash": review_hash,
        "business_name": data.business,
        "review_url": data.link,
        "reviewer": data.reviewer,
        "rating": data.rating,
        "review_text": data.review_text,
        "violation_type": data.violation,
        "evidence": data.evidence,
        "report_draft": report,
        "status": "ready_to_submit",
        "created_at": datetime.datetime.now().isoformat()
    }
    requests.append(entry)
    save_requests(requests)

    report_file = os.path.join(REPORTS_DIR, f"{review_hash}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    return {"status": "success", "id": review_hash, "report": report}
