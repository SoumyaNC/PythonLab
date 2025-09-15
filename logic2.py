from textblob import TextBlob
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class CauseScannerVADER:
    DOMAIN_NEGATIVE_KEYWORDS = [
        'mismatch', 'blocking', 'fail', 'failed', 'error', 'denied', 'problem',
        'authentication mismatch', 'typo', 'not correct', 'not matching'
    ]

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
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

    def scan_cause_status(self, chat_lines, window=5):
        cause_status = {cause: 'unknown' for cause in self.CAUSE_KEYWORDS}
        n = len(chat_lines)

        for i, line in enumerate(chat_lines):
            line_lower = line.lower()
            
            # if not line.startswith('Agent:'):
            #     continue

            for cause, keywords in self.CAUSE_KEYWORDS.items():
                if cause_status[cause] != 'unknown':
                    continue
                
                if any(k in line_lower for k in keywords):
                    print('---------------start of new cause --------------------')
                    print(cause)
                    print(keywords)
                    print(line_lower)
                    print('---------------------------------------------')
                    start = i + 1
                    end = min(i + 1 + window, n)
                    #  # For DOB and serial, concatenate only agent lines
                    # # if cause in ['serial', 'dob']:
                    # #     concat_text = [
                    # #         chat_lines[j] for j in range(start, end) if chat_lines[j].startswith('Agent:')
                    # #     ]
                    # # else:
                    #     # For others, concatenate all lines in window
                    # concat_text = chat_lines[start:end]

                    # #concat_text_lower = concat_text.lower()
                    # # Domain keyword override for negative detection
                    # # if any(neg_kw in concat_text_lower for neg_kw in self.DOMAIN_NEGATIVE_KEYWORDS):
                    # #     cause_status[cause] = 'blocked'
                    # #     continue
                    # print(concat_text)
                    # scores = self.analyzer.polarity_scores(concat_text)
                    # compound = scores['compound']
                    # print(compound)
                    # if compound <= -0.05:
                    #     cause_status[cause] = 'blocked'
                    # elif compound >= 0.05:
                    #     cause_status[cause] = 'affirmed'
                    # else:
                    #     cause_status[cause] = 'affirmed'  # Treat neutral as affirmat

                    for j in range(start, end):
                        next_line = chat_lines[j]
                        print(next_line)
                        if cause in ['dob', 'serial']:
                            if not next_line.startswith('Agent:'):
                                continue

                        next_line_lower = next_line.lower()

                        #Domain keyword override for negative detection
                        if any(neg_kw in next_line_lower for neg_kw in self.DOMAIN_NEGATIVE_KEYWORDS):
                            cause_status[cause] = 'blocked'
                            print('blockd by domain negative words')
                            break

                        scores = self.analyzer.polarity_scores(next_line)
                        compound = scores['compound']
                        print(compound)
                        if compound <= -0.05:
                            cause_status[cause] = 'blocked'
                            print('blockd')
                            break
                        # elif compound >= 0.05:
                        else:
                            cause_status[cause] = 'affirmed'
                            print('affrmd')
                            break

                    if cause_status[cause] != 'unknown':
                        break

        # Build output
        causes = {'company_side_causes': [], 'customer_side_causes': [], 'ruled_out': []}
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

# Test with problematic scenarios
if __name__ == "__main__":
    
    
    detector = CauseScannerVADER()
    # result = detector.detect_root_causes(dob_test)
    # print("DOB Test:", result)
    chat_example = read_chat_file('data/samplechat.txt')
    result2 = detector.scan_cause_status(chat_example)
    print(result2)
