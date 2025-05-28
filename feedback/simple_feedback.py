import json
from pathlib import Path
from datetime import datetime

class SimpleFeedback:
    def __init__(self):
        self.feedback_file = Path("feedback/feedback.jsonl")
        self.feedback_file.parent.mkdir(exist_ok=True)
    
    def log(self, query: str, answer: str, rating: int):
        """Log feedback: 1 = thumbs up, -1 = thumbs down"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer": answer,
            "rating": rating
        }
        
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_stats(self):
        """Get feedback statistics"""
        if not self.feedback_file.exists():
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "ready_for_training": False
            }
        
        total = positive = 0
        with open(self.feedback_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    total += 1
                    if data['rating'] > 0:
                        positive += 1
                except:
                    continue
        
        return {
            "total": total,
            "positive": positive,
            "negative": total - positive,
            "ready_for_training": positive >= 5,
            "satisfaction_rate": positive / total if total > 0 else 0
        }
