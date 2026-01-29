import json
import re
import sys
from pathlib import Path

def classify_threads(input_path, output_path):
    print(f"Reading input from: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            threads = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)

    classified = {
        "discuss": [],
        "release": [],
        "spip": [],
        "others": []
    }

    # Classification Logic based on Updated Skill Rules
    for thread in threads:
        subject = thread.get("subject", "").strip()
        # Safely get body.
        root = thread.get("root", {})
        body = root.get("body", "") if root else ""
        
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        category = "others"

        # 1. SPIP Check (Highest priority for proposals)
        # Skill: Subject contains SPIP (case-insensitive)
        is_spip = False
        if "spip" in subject_lower:
             is_spip = True
             # Double check: if it is SPIP, does it override Discuss? 
             # Usually SPIP implies discussion, but SPIP is the more specific bucket.
        
        # 2. Release Check (STRICT)
        # Skill: Subject MUST contain "announce" (case-insensitive)
        is_release = False
        if "announce" in subject_lower:
            is_release = True
            
        # 3. Discuss Check
        is_discuss = False
        if "[discuss]" in subject_lower:
            is_discuss = True
        elif subject.endswith("?"):
            is_discuss = True
        elif any(x in subject_lower for x in ["question", "how to", "help"]):
             is_discuss = True
        # Heuristic from previous script: if body asks for feedback/questions and not a JIRA/FYI
        elif ("?" in body_lower or "feedback" in body_lower or "question" in body_lower):
             if not any(tag in subject_lower for tag in ["[fyi]", "[jira]", "[post-commit]"]):
                 is_discuss = True

        # Extraction Logic: Find Google Doc links
        doc_links = list(set(re.findall(r'https?://docs\.google\.com/document/d/[a-zA-Z0-9_-]+', body)))
        thread["doc_links"] = doc_links
        thread["doc_content"] = ""

        # Decision Logic (Priority: Release > SPIP > Discuss > Others)
        if is_release:
            category = "release"
        elif is_spip:
            category = "spip"
        elif is_discuss:
            category = "discuss"
        else:
            category = "others"

        classified[category].append(thread)

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(classified, f, indent=2, ensure_ascii=False)
    
    print(f"Classification Complete.")
    print(f"Output saved to: {output_path}")
    print("Summary:")
    for cat, items in classified.items():
        print(f"  {cat}: {len(items)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python src/classify_tool.py <input_json> <output_json>")
        sys.exit(1)
    else:
        classify_threads(sys.argv[1], sys.argv[2])
