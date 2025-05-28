import json
from pathlib import Path
from datetime import datetime

class QueryLogger:
    def __init__(self):
        self.log_file = Path("logs/query_log.jsonl")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_query(self, query: str, tools_used: list, execution_time: float, 
                  answer_length: int = 0, tokens_used: int = 0, domain: str = "General"):
        """Log query execution details with domain"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "domain": domain,
            "tools_used": tools_used,
            "execution_time": execution_time,
            "answer_length": answer_length,
            "tokens_used": tokens_used,
            "query_length": len(query)
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')