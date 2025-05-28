import re
from typing import Dict, List, Tuple

class PIIFilter:
    def __init__(self):
        self.patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        }
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text and return matches by type"""
        results = {}
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                results[pii_type] = matches
        return results
    
    def mask_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Mask PII in text and return masked text with counts"""
        masked_text = text
        pii_counts = {}
        
        # Replace SSNs
        ssn_matches = re.findall(self.patterns['ssn'], text)
        for ssn in ssn_matches:
            masked_text = masked_text.replace(ssn, f"XXX-XX-{ssn[-4:]}")
        pii_counts['ssn'] = len(ssn_matches)
        
        # Replace emails
        email_matches = re.findall(self.patterns['email'], text)
        for email in email_matches:
            user = email.split('@')[0]
            masked_text = masked_text.replace(email, f"{user[:2]}***@***.***")
        pii_counts['email'] = len(email_matches)
        
        # Replace phones
        phone_matches = re.findall(self.patterns['phone'], text)
        for phone in phone_matches:
            masked_text = masked_text.replace(phone, "(XXX) XXX-XXXX")
        pii_counts['phone'] = len(phone_matches)
        
        return masked_text, pii_counts
    
    def contains_pii(self, text: str) -> bool:
        """Quick check if text contains any PII"""
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False