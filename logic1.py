import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

# --------------------------------------
# Affirmation Detector
# --------------------------------------
class AffirmationDetector:
    def __init__(self):
        self.affirmatives = {
            "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "alright",
            "absolutely", "of course", "affirmative", "indeed", "right", "correct",
            "same", "matches", "looks okay", "confirmed", "working fine", "streaming"
        }
        self.negatives = {
            "no", "nope", "nah", "never", "negative", "not at all", "incorrect",
            "wrong", "mismatch", "failed", "does not match", "not matching",
            "activation failed", "error", "problem", "denied", "not working",
            "system failed", "blocking", "provisioning error", "drops", "disconnect"
        }

    def detect(self, sentence: str) -> str:
        s = sentence.lower().strip()
        if any(word in s for word in self.affirmatives) and any(word in s for word in self.negatives):
            return "uncertain"
        for word in self.negatives:
            if word in s:
                return "blocked"
        for word in self.affirmatives:
            if word in s:
                return "affirmed"
        if "don't" in s or "do not" in s or "not sure" in s or "not really" in s:
            return "blocked"
        sentiment = TextBlob(s).sentiment.polarity
        if sentiment > 0.2:
            return "affirmed"
        elif sentiment < -0.2:
            return "blocked"
        return "uncertain"

# --------------------------------------
# Hybrid Root Cause Detector
# --------------------------------------
class HybridRootCauseDetector:
    def __init__(self):
        # Define cause patterns and mapping
        self.CAUSE_PATTERNS = {
            'serial': r'serial|number',
            'dob': r'dob|date[ -]?of[ -]?birth',
            'wifi': r'wifi|wi-fi|internet|router|cable',
            'backend': r'backend|provisioning|server|system failed|activation server|activation error'
        }
        self.CAUSE_SIDE = {
            'serial': 'company',
            'dob': 'company',
            'wifi': 'customer',
            'backend': 'company'
        }
        self.CAUSE_NAMES = {
            'serial': 'Serial number mismatch',
            'dob': 'DOB mismatch',
            'wifi': 'Wi-Fi connectivity or cable issue',
            'backend': 'Backend provisioning error'
        }

        # Example sentences for TF-IDF similarity
        self.EXAMPLES = {
            'serial': ["serial number is invalid", "device serial doesn't match", "serial number mismatch"],
            'dob': ["date of birth incorrect", "birthday doesn't match", "dob mismatch"],
            'wifi': ["wifi not connecting", "internet connection problems", "router keeps dropping"],
            'backend': ["backend server failed", "provisioning error", "activation server problem"]
        }

        # Prepare TF-IDF vectorizer
        all_examples = []
        self.labels = []
        for intent, examples in self.EXAMPLES.items():
            all_examples.extend(examples)
            self.labels.extend([intent]*len(examples))
        self.vectorizer = TfidfVectorizer().fit(all_examples)
        self.example_vecs = self.vectorizer.transform(all_examples)
        self.detector = AffirmationDetector()

    def detect_causes_with_context(self, chat_lines, tfidf_threshold=0.3):
        # Track last known status for each cause
        cause_status_all = {k: None for k in self.CAUSE_PATTERNS.keys()}

        for line in chat_lines:
            l = line.lower()
            # Regex check per cause
            for cause, pattern in self.CAUSE_PATTERNS.items():
                if re.search(pattern, l):
                    status = self.detector.detect(line)
                    if status in ["blocked", "affirmed"]:
                        cause_status_all[cause] = status  # Override previous status with latest context

            # TF-IDF similarity check
            text_vec = self.vectorizer.transform([line])
            sims = cosine_similarity(text_vec, self.example_vecs)[0]
            for sim, label in zip(sims, self.labels):
                if sim >= tfidf_threshold:
                    status = self.detector.detect(line)
                    if status in ["blocked", "affirmed"]:
                        cause_status_all[label] = status

        # Prepare final causes output
        causes = {'company_side_causes': [], 'customer_side_causes': [], 'ruled_out': []}
        for cause, status in cause_status_all.items():
            if status == "blocked":
                side = self.CAUSE_SIDE[cause]
                causes[f'{side}_side_causes'].append(self.CAUSE_NAMES[cause])
            else:
                causes['ruled_out'].append(self.CAUSE_NAMES[cause])

        return causes

# --------------------------------------
# Example Usage
# --------------------------------------
def read_chat_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
    return lines


if __name__ == "__main__":
    chat_example = read_chat_file('data/samplechat.txt')
    detector = HybridRootCauseDetector()
    result = detector.detect_causes_with_context(chat_example)
    print(result)
