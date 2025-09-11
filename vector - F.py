import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Intent dictionary (example phrases)
intent_examples = {
   
}

# Regex patterns for faster rule-based detection
regex_patterns = {
    "": r"\b(wifi|wi[- ]?fi|||)\b",
    "": r"\b(|||)\b.*\b(|||)\b",
    "": r"\b(||)\b.*\b(|||)\b"
}

# Prepare TF-IDF vectorizer
all_examples = []
labels = []
for intent, phrases in intent_examples.items():
    all_examples.extend(phrases)
    labels.extend([intent] * len(phrases))

vectorizer = TfidfVectorizer().fit(all_examples)
example_vecs = vectorizer.transform(all_examples)

def detect_intents(chat_log, threshold=0.2):
    detected = set()
    text = chat_log.lower()

    # --- Step 1: Regex check ---
    for intent, pattern in regex_patterns.items():
        if re.search(pattern, text):
            detected.add(intent)

    # --- Step 2: TF-IDF semantic check ---
    text_vec = vectorizer.transform([chat_log])
    sims = cosine_similarity(text_vec, example_vecs)[0]

    for sim, label in zip(sims, labels):
        if sim >= threshold:
            detected.add(label)

    return list(detected)
