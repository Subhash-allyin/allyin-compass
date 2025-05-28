import re
from typing import Dict, List, Set

class ComplianceTagger:
    def __init__(self):
        # High risk compliance terms by category
        self.risk_terms = {
            'financial_risk': [
                'restatement', 'earnings risk', 'material weakness', 
                'accounting irregularity', 'audit failure', 'misstatement',
                'revenue recognition', 'financial fraud', 'sec investigation'
            ],
            'regulatory_risk': [
                'violation', 'non-compliant', 'regulatory action', 'penalty',
                'sanction', 'enforcement', 'investigation', 'subpoena',
                'warning letter', 'consent decree'
            ],
            'legal_risk': [
                'litigation', 'lawsuit', 'legal action', 'settlement',
                'class action', 'breach of contract', 'liability',
                'indemnification', 'arbitration'
            ],
            'operational_risk': [
                'data breach', 'security incident', 'system failure',
                'service disruption', 'recall', 'contamination',
                'workplace accident', 'fatality'
            ]
        }
        
        # Compile patterns for case-insensitive matching
        self.patterns = {}
        for category, terms in self.risk_terms.items():
            self.patterns[category] = re.compile(
                r'\b(' + '|'.join(re.escape(term) for term in terms) + r')\b',
                re.IGNORECASE
            )
    
    def tag_risks(self, text: str) -> Dict[str, List[str]]:
        """Find all risk terms in text by category"""
        results = {}
        
        for category, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Unique matches, preserve original case
                results[category] = list(set(matches))
        
        return results
    
    def get_risk_score(self, text: str) -> Dict[str, float]:
        """Calculate risk score based on term frequency"""
        scores = {}
        text_length = len(text.split())
        
        for category, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Score based on frequency and text length
                scores[category] = min(len(matches) / max(text_length / 100, 1), 1.0)
        
        # Overall risk score
        if scores:
            scores['overall'] = min(sum(scores.values()) / len(scores), 1.0)
        else:
            scores['overall'] = 0.0
        
        return scores
    
    def flag_high_risk(self, text: str, threshold: float = 0.1) -> bool:
        """Quick check if text is high risk"""
        scores = self.get_risk_score(text)
        return scores.get('overall', 0) >= threshold
    
    def summarize_risks(self, text: str) -> str:
        """Generate a brief risk summary"""
        risks = self.tag_risks(text)
        if not risks:
            return "No compliance risks detected"
        
        summary_parts = []
        for category, terms in risks.items():
            summary_parts.append(f"{category.replace('_', ' ').title()}: {', '.join(terms[:3])}")
        
        return " | ".join(summary_parts)