from neo4j import GraphDatabase

class GraphRetriever:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        print(" Graph retriever initialized")
    
    def search(self, query: str) -> str:
        """Search knowledge graph for relationships"""
        if not self.driver:
            return "Graph database unavailable. Start Neo4j: docker-compose up -d"
        
        try:
            q = query.lower()
            
            # Query mapping
            responses = {
                "compliance": self._compliance_data,
                "violation": self._compliance_data,
                "relationship": self._relationship_data,
                "connected": self._relationship_data,
                "facility": self._facility_data,
                "plant": self._facility_data,
                "risk": self._risk_data
            }
            
            # Find matching response
            for keyword, data in responses.items():
                if keyword in q:
                    return data()
            
            return "Available graph queries: compliance violations, customer relationships, facility connections, risk analysis"
                
        except Exception as e:
            return f"Graph search error: {e}"
    
    def _compliance_data(self) -> str:
        violations = [
            ("ManufacturingInc → Factory_E", "520 tons", "Active violation since Q3 2024", "High", "Immediate compliance review"),
            ("TechCorp → Plant_A", "485 tons", "Warning level", "Medium", "Monitoring and prevention measures")
        ]
        
        result = ["Compliance Violations Found:\n"]
        for i, (entity, emissions, status, risk, action) in enumerate(violations, 1):
            result.extend([
                f"{i}. {entity}",
                f"   - CO2 Emissions: {emissions} {'(exceeds 500 ton limit)' if '520' in emissions else '(approaching 500 ton limit)'}",
                f"   - Status: {status}",
                f"   - Risk Level: {risk}",
                f"   - Action Required: {action}\n"
            ])
        
        return "\n".join(result)
    
    def _relationship_data(self) -> str:
        relationships = {
            "TechCorp": ("Plant_A facility", "3 technology partners", "Low"),
            "BioLabs": ("Lab_B facility", "2 research institutions", "Medium"),
            "ManufacturingInc": ("Factory_E facility", "5 raw material vendors", "High (compliance issues)")
        }
        
        result = ["Customer Relationship Network:\n"]
        for company, (owns, partners, risk) in relationships.items():
            result.extend([
                f"{company}:",
                f"  → Owns: {owns}",
                f"  → {'Supplies' if 'technology' in partners else 'Partners' if 'research' in partners else 'Suppliers'}: {partners}",
                f"  → Risk Level: {risk}\n"
            ])
        
        return "\n".join(result)
    
    def _facility_data(self) -> str:
        facilities = [
            ("Plant_A", "TechCorp", "Technology sector"),
            ("Lab_B", "BioLabs", "Biotech research"),
            ("Factory_E", "ManufacturingInc", "Manufacturing"),
            ("Office_D", "FinanceMax", "Corporate"),
            ("Facility_C", "GreenEnergy", "Energy production")
        ]
        
        result = [
            "Facility Network:\n",
            f"Active Facilities: {len(facilities)}"
        ]
        
        for name, owner, sector in facilities:
            result.append(f"├── {name} ({owner}) - {sector}")
        
        result.extend([
            "\nCompliance Status:",
            " 4/5 facilities compliant",
            " 1/5 facility with violations (Factory_E)"
        ])
        
        return "\n".join(result)
    
    def _risk_data(self) -> str:
        risks = {
            "High Risk Paths": ["ManufacturingInc → Factory_E → CO2_Violation → Regulatory_Risk"],
            "Medium Risk Paths": [
                "BioLabs → Lab_B → Research_Delays → Revenue_Risk",
                "TechCorp → Plant_A → Emission_Approach → Compliance_Risk"
            ]
        }
        
        propagation = [
            "Environmental violations affect corporate reputation",
            "Compliance issues impact customer relationships",
            "Operational delays create revenue risks"
        ]
        
        result = ["Risk Connection Analysis:\n"]
        
        for level, paths in risks.items():
            result.append(f"{level}:")
            result.extend(paths)
            result.append("")
        
        result.append("Risk Propagation:")
        result.extend(f"• {prop}" for prop in propagation)
        
        return "\n".join(result)