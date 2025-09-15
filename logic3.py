from sentence_transformers import SentenceTransformer, util

class SemanticCauseDetector:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight, fast model

        # Prototype phrases indicating affirmation or negation of cause
        self.affirm_prototypes = [
            "That is correct.",
            "No issues found.",
            "Everything matches perfectly.",
            "Confirmed no problem.",
            "No mismatch detected.",
            "This looks good.",
            "We have confirmed this is fine.",
            "No errors detected.",
            "The details are accurate."
        ]

        self.negate_prototypes = [
            "There is a mismatch.",
            "Activation is blocked due to error.",
            "Problem detected here.",
            "This is causing an error.",
            "The cause is blocking activation.",
            "An issue has been found.",
            "The details do not match.",
            "Error found in the system.",
            "This is a blocking issue."
        ]

        # Precompute embeddings for prototype phrases
        self.affirm_emb = self.model.encode(self.affirm_prototypes, convert_to_tensor=True)
        self.negate_emb = self.model.encode(self.negate_prototypes, convert_to_tensor=True)

    def classify_cause_status(self, context_text):
        """
        Classifies if context_text semantically affirms, blocks, or is unknown about a cause.
        """
        emb = self.model.encode(context_text, convert_to_tensor=True)

        sim_affirm = util.cos_sim(emb, self.affirm_emb).max().item()
        sim_negate = util.cos_sim(emb, self.negate_emb).max().item()

        threshold = 0.5  # similarity threshold
        print('Semantic Negative:' +str(sim_negate))
        print('Semantic Positive:' +str(sim_affirm))

        if sim_affirm > threshold and sim_affirm > sim_negate:
            return 'affirmed'
        elif sim_negate > threshold and sim_negate > sim_affirm:
            return 'blocked'
        else:
            return 'unknown'


class RootCauseExtractor:
    def __init__(self, window=3):
        self.cause_detector = SemanticCauseDetector()
        self.window = window

        self.CAUSE_KEYWORDS = {
            'serial': ['serial', 'number'],
            'dob': ['dob', 'date of birth', 'birthday'],
            'wifi': ['wi-fi', 'wifi', 'internet', 'router', 'connection'],
            'backend': ['backend', 'server', 'provisioning', 'activation server']
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

    def extract(self, chat_lines):
        cause_status = {cause: 'unknown' for cause in self.CAUSE_KEYWORDS}
        n = len(chat_lines)

        for cause, keywords in self.CAUSE_KEYWORDS.items():
            if cause_status[cause] != 'unknown':
                continue
            print('---------------start of new cause --------------------')
            print(cause)
            print(keywords)
            print('--------------------------------- --------------------')

            for i, line in enumerate(chat_lines):
                line_lower = line.lower()

                # Only consider agent lines mentioning cause keywords
                # if not line.startswith('Agent:'):
                #     continue

                if any(k in line_lower for k in keywords):
                    print(line_lower)
                    start = i
                    end = min(i + 1 + self.window, n)

                    # Concatenate agent lines within the window
                    context_lines = [chat_lines[start]]
                    for j in range(i+1, end):
                        if cause in ['serial', 'dob']:
                            if chat_lines[j].startswith('Agent:'):
                                context_lines.append(chat_lines[j])

                    context_text = ' '.join(context_lines)
                    print('Context')
                    print(context_text)
                    status = self.cause_detector.classify_cause_status(context_text)
                    cause_status[cause] = status
                    break  # stop scanning more lines for this cause

        # Build output dictionary with categorized causes
        causes = {
            'company_side_causes': [],
            'customer_side_causes': [],
            'ruled_out': []
        }
        for cause, status in cause_status.items():
            if status == 'blocked':
                side = self.CAUSE_SIDE[cause]
                causes[f'{side}_side_causes'].append(self.CAUSE_NAMES[cause])
            else:
                causes['ruled_out'].append(self.CAUSE_NAMES[cause])

        return causes
    
def read_chat_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]  # Remove empty lines and strip whitespace
    return lines

if __name__ == "__main__":
    chat_example = read_chat_file('data/samplechat.txt')
    while True:
        extractor = RootCauseExtractor()
        result = extractor.extract(chat_example)
        print("Root Cause Detection Output:")
        print(result)
        cont = input("\nRun another scan? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting.")
            break 
