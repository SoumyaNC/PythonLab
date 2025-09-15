import re

# -----------------------
# Phrase dictionaries
# -----------------------
company_side_phrases = {
    "Serial No. mismatch": {
        "positive": [
            r"\bserial mismatch\b", r"\bwrong serial\b", r"\bserial not matching\b",
            r"\binvalid serial number\b", r"\bsn mismatch\b"
        ],
        "negative": [
            r"\bserial matches\b", r"\bserial is correct\b", r"\bserial is same\b",
            r"\bserial number okay\b", r"\bserial looks fine\b"
        ]
    },
    "DOB mismatch": {
        "positive": [
            r"\bdob mismatch\b", r"\bdate of birth mismatch\b", r"\bdob not matching\b",
            r"\bdob incorrect\b", r"\bdob format issue\b", r"\bbirthdate not matching\b"
        ],
        "negative": [
            r"\bdob matches\b", r"\bdob is correct\b", r"\bdob is same\b",
            r"\bdob looks fine\b", r"\bdob verified\b"
        ]
    },
    "Backend issue": {
        "positive": [
            r"\bsystem error\b", r"\bbackend error\b", r"\bactivation server issue\b",
            r"\bprovisioning failed\b", r"\bcas error\b", r"\bcard not paired\b",
            r"\bsystem failed to push activation\b", r"\bprovisioning error\b"
        ],
        "negative": []
    }
}

customer_side_phrases = {
    "WiFi problem": {
        "positive": [
            r"\bwifi issue\b", r"\bwifi not working\b", r"\binternet problem\b",
            r"\bnetwork issue\b", r"\brouter not connected\b", r"\bno internet\b"
        ],
        "negative": [
            r"\bwifi working\b", r"\bwifi fine\b", r"\binternet working\b",
            r"\bnetwork is okay\b", r"\bwifi connected\b"
        ]
    },
    "HDMI/TV issue": {
        "positive": [
            r"\bhdmi not working\b", r"\btv not displaying\b", r"\binput not set\b",
            r"\bcable unplugged\b", r"\btv issue\b"
        ],
        "negative": [
            r"\bhdmi working\b", r"\btv is fine\b", r"\bdisplay is okay\b"
        ]
    },
    "Customer mistake": {
        "positive": [r"\bwrong pin\b", r"\bentered wrong info\b", r"\buser error\b"],
        "negative": []
    }
}

# -----------------------
# Helper function to split chat into sentences
# -----------------------
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# -----------------------
# Root cause detection function
# -----------------------
def detect_causes(chat_history):
    company_causes = set()
    customer_causes = set()
    
    sentences = split_sentences(chat_history.lower())
    
    # Function to check for positive phrases without negation in a sentence
    def has_positive_without_negation(sentence, phrase_dict):
        for pos in phrase_dict["positive"]:
            if re.search(pos, sentence):
                # Check if any negative phrase matches
                if not any(re.search(neg, sentence) for neg in phrase_dict["negative"]):
                    return True
        return False
    
    # Company-side detection
    for cause, phrase_dict in company_side_phrases.items():
        for sentence in sentences:
            if has_positive_without_negation(sentence, phrase_dict):
                company_causes.add(cause)
    
    # Customer-side detection
    for cause, phrase_dict in customer_side_phrases.items():
        for sentence in sentences:
            if has_positive_without_negation(sentence, phrase_dict):
                customer_causes.add(cause)
    
    if not company_causes and not customer_causes:
        return {"company_side_causes": ["Unknown Root Cause"], "customer_side_causes": []}
    
    return {"company_side_causes": list(company_causes), "customer_side_causes": list(customer_causes)}

# -----------------------
# Main execution
# -----------------------
if __name__ == "__main__":
    # Read chat history from file
    with open(r'data\sammplechat.txt', 'r', encoding='utf-8') as f:
        chat_history = f.read()

    # Detect root causes
    outcome = detect_causes(chat_history)
    print(outcome)
