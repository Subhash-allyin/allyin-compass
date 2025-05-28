from security.pii_filter import PIIFilter
from security.compliance_tagger import ComplianceTagger

class SecureQueryWrapper:
    def __init__(self, agent):
        self.agent = agent
        self.pii_filter = PIIFilter()
        self.compliance_tagger = ComplianceTagger()
    
    def execute(self, query: str):
        """Secure wrapper for agent.execute()"""
        # Pre-process: Check and mask PII in query
        if self.pii_filter.contains_pii(query):
            query, _ = self.pii_filter.mask_pii(query)
        
        # Check compliance risk
        risk_score = self.compliance_tagger.get_risk_score(query)
        
        # Execute original query
        result = self.agent.execute(query)
        
        # Post-process: Mask PII in answer and context
        if 'answer' in result:
            result['answer'], pii_counts = self.pii_filter.mask_pii(result['answer'])
            result['pii_masked'] = pii_counts
            
        if 'context' in result:
            result['context'], _ = self.pii_filter.mask_pii(result['context'])
        
        # Add security metadata
        result['security_metadata'] = {
            'compliance_risk': risk_score,
            'high_risk': self.compliance_tagger.flag_high_risk(query)
        }
        
        return result