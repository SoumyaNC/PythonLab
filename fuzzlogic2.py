import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# Step 1: Train a lightweight semantic classifier with scikit-learn

def train_semantic_classifier():
    # Example labeled training data (expand with more domain-specific samples)
    texts = [
        "DOB matches correctly",
        "The serial number does not match",
        "Wi-Fi is not working",
        "DOB is confirmed as valid",
        "Activation failed due to mismatch",
        "Wi-Fi connectivity looks fine",
        "No issues with DOB",
        "Serial number confirmed correct",
        "Wi-Fi problem detected",
        "DOB mismatch found"
    ]
    labels = [
        'affirmation',  # confirmed okay
        'block',        # cause of failure
        'block',
        'affirmation',
        'block',
        'affirmation',
        'affirmation',
        'affirmation',
        'block',
        'block'
    ]

    clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=200))
    clf.fit(texts, labels)
    return clf

# Step 2: Root cause extraction combining pattern matching + semantic classification

def extract_root_causes_with_semantics(chat_lines, semantic_clf):
    CAUSE_PATTERNS = {
        'serial': r'serial|number',
        'dob': r'dob|date[ -]?of[ -]?birth',
        'wifi': r'wi[- ]?fi|internet|router|cable'
    }

    CAUSE_SIDE = {
        'serial': 'company',
        'dob': 'company',
        'wifi': 'customer'
    }

    affirmation_phrases = [
        "working fine", "looks okay", "no problem", "no issues", "is fine", "ok", "confirmed"
    ]

    cause_states = {cause: None for cause in CAUSE_PATTERNS}
    lower_lines = [line.lower() for line in chat_lines]

    for line in lower_lines:
        for cause, pattern in CAUSE_PATTERNS.items():
            if re.search(pattern, line):
                # Explicit affirmation override for Wi-Fi
                if cause == 'wifi':
                    if any(phrase in line for phrase in affirmation_phrases):
                        cause_states[cause] = 'ok'
                        continue

                pred = semantic_clf.predict([line])[0]
                print(cause)
                print(line)
                print(pred)
                if pred == 'block':
                    if cause_states[cause] != 'block':
                        cause_states[cause] = 'block'
                elif pred == 'affirmation':
                    if cause_states[cause] != 'block':
                        cause_states[cause] = 'ok'

    causes = {'company_side_causes': [], 'customer_side_causes': []}
    cause_names = {
        'serial': 'Serial number mismatch',
        'dob': 'DOB mismatch',
        'wifi': 'Wi-Fi connectivity or cable issue'
    }

    for cause, state in cause_states.items():
        if state == 'block':
            side = CAUSE_SIDE.get(cause, 'customer')
            if side == 'company':
                causes['company_side_causes'].append(cause_names[cause])
            else:
                causes['customer_side_causes'].append(cause_names[cause])

    return causes

def read_chat_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]  # Remove empty lines and strip whitespace
    return lines
# Example usage

if __name__ == "__main__":
    # Train the lightweight semantic classifier once
    semantic_clf = train_semantic_classifier()

    # Sample chat lines (replace with reading from file if needed)
    chat_example = read_chat_file('data\samplechat.txt')

    result = extract_root_causes_with_semantics(chat_example, semantic_clf)
    print(result)
