#!/usr/bin/env python3
import json, os, hashlib, datetime

BASE = os.path.expanduser("~/review-agent")
DATA_FILE = os.path.join(BASE, "data", "requests.json")
REPORTS_DIR = os.path.join(BASE, "reports")

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

def main():
    print("=== Google Negative Review Removal Agent ===")
    business = input("Business ka naam: ").strip()
    link = input("Review ka Google Maps link: ").strip()
    reviewer = input("Reviewer ka naam: ").strip()
    rating = input("Rating (1-5): ").strip()
    print("Review ka text paste karein. Khatam karne ke liye empty line phir Enter:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    review_text = "\n".join(lines).strip()

    if not link or not review_text:
        print("Link aur review text zaroori hain.")
        return

    review_hash = make_hash(link + review_text)
    requests = load_requests()
    for r in requests:
        if r.get("review_hash") == review_hash:
            print("Ye review pehle report ho chuka hai. Duplicate skip.")
            return

    print("\n--- Violation type select karein ---")
    print("1. Spam / advertisement")
    print("2. Fake engagement / jhoothi review")
    print("3. Off-topic / unrelated")
    print("4. Threat / harassment / hate")
    print("5. Personal information leak")
    print("6. Koi violation nahi (jaiz negative review)")
    choice = input("Choice (1-6): ").strip()

    violation_map = {
        "1": "Spam / advertisement",
        "2": "Fake engagement / jhoothi review",
        "3": "Off-topic / unrelated",
        "4": "Threat / harassment / hate",
        "5": "Personal information leak",
        "6": "Koi violation nahi"
    }
    violation = violation_map.get(choice, "Koi violation nahi")

    if violation == "Koi violation nahi":
        print("Ye jaiz negative review lag raha hai. Report nahi banayi jayegi.")
        return

    evidence = input("Evidence / tafseel: ").strip()

    report = f"""Google Review Report
====================
Business: {business}
Review Link: {link}
Reviewer: {reviewer}
Rating: {rating}
Review Text:
{review_text}

Violation Type: {violation}
Evidence: {evidence}

Report Draft:
This review appears to violate Google's review policies.
Violation: {violation}
Evidence: {evidence}
Request: Please review this content and take action as per Google policy.
"""

    print("\n--- Report Preview ---")
    print(report)
    approve = input("Submit karna chahte hain? (yes/no): ").strip().lower()
    if approve != "yes":
        print("Report cancel.")
        return

    entry = {
        "id": review_hash,
        "review_hash": review_hash,
        "business_name": business,
        "review_url": link,
        "reviewer": reviewer,
        "rating": rating,
        "review_text": review_text,
        "violation_type": violation,
        "evidence": evidence,
        "report_draft": report,
        "status": "ready_to_submit",
        "created_at": datetime.datetime.now().isoformat()
    }
    requests.append(entry)
    save_requests(requests)

    report_file = os.path.join(REPORTS_DIR, f"{review_hash}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport save ho gayi: {report_file}")
    print("Ab Google ke official form par ja kar ye report submit karein.")

if __name__ == "__main__":
    main()

