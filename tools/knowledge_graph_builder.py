from neo4j import GraphDatabase
from typing import Dict, List

class KnowledgeGraphBuilder:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "password")
            )
            print(" Knowledge graph builder initialized")
        except Exception as e:
            print(f" Knowledge graph unavailable: {e}")
            self.driver = None
    
    def build_enterprise_graph(self):
        """Build enterprise knowledge graph with domain-specific data"""
        if not self.driver:
            print("Neo4j not available")
            return
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # FINANCE DOMAIN DATA
            finance_customers = [
                {"id": 1, "name": "TechCorp", "sector": "Technology", "revenue": 1500000, "risk": "Low"},
                {"id": 2, "name": "FinanceMax", "sector": "Finance", "revenue": 2000000, "risk": "High"},
                {"id": 3, "name": "InvestmentPro", "sector": "Finance", "revenue": 1800000, "risk": "Medium"}
            ]
            
            for customer in finance_customers:
                session.run("""
                    CREATE (c:Customer:Finance {
                        id: $id,
                        name: $name,
                        sector: $sector,
                        revenue: $revenue,
                        risk_level: $risk,
                        domain: 'Finance'
                    })
                """, **customer)
            
            # Create financial risks
            session.run("""
                CREATE (r:Risk:Finance {name: "Market_Volatility", severity: "High"})
                CREATE (r2:Risk:Finance {name: "Regulatory_Change", severity: "Medium"})
                CREATE (r3:Risk:Finance {name: "Credit_Default", severity: "High"})
            """)
            
            # Link high-risk customers to risks
            session.run("""
                MATCH (c:Customer:Finance {risk_level: "High"}), (r:Risk:Finance)
                CREATE (c)-[:EXPOSED_TO]->(r)
            """)
            
            # BIOTECH DOMAIN DATA
            biotech_entities = [
                {"id": 4, "name": "BioLabs", "type": "Research_Facility", "trials": 5},
                {"id": 5, "name": "GeneTech", "type": "Laboratory", "trials": 3},
                {"id": 6, "name": "PharmaCore", "type": "Manufacturing", "trials": 8}
            ]
            
            for entity in biotech_entities:
                session.run("""
                    CREATE (b:Facility:Biotech {
                        id: $id,
                        name: $name,
                        type: $type,
                        active_trials: $trials,
                        domain: 'Biotech'
                    })
                """, **entity)
            
            # Create molecules and trials
            session.run("""
                CREATE (m1:Molecule:Biotech {name: "MOL-X1", status: "Phase_3"})
                CREATE (m2:Molecule:Biotech {name: "MOL-Y2", status: "Phase_2"})
                CREATE (t1:Trial:Biotech {name: "TRIAL-001", status: "Active"})
                CREATE (t2:Trial:Biotech {name: "TRIAL-002", status: "Completed"})
            """)
            
            # Create adverse events
            session.run("""
                CREATE (ae:AdverseEvent:Biotech {
                    type: "Mild_Reaction",
                    molecule: "MOL-X1",
                    severity: "Low"
                })
            """)
            
            # Link facilities to trials
            session.run("""
                MATCH (f:Facility:Biotech), (t:Trial:Biotech)
                WHERE f.active_trials > 0
                CREATE (f)-[:CONDUCTS]->(t)
            """)
            
            # ENERGY DOMAIN DATA
            energy_facilities = [
                {"id": 7, "name": "Plant_A", "emissions": 485, "type": "Coal"},
                {"id": 8, "name": "Solar_Farm_B", "emissions": 20, "type": "Solar"},
                {"id": 9, "name": "Factory_E", "emissions": 520, "type": "Manufacturing"},
                {"id": 10, "name": "Wind_Farm_C", "emissions": 15, "type": "Wind"}
            ]
            
            for facility in energy_facilities:
                session.run("""
                    CREATE (f:Facility:Energy {
                        id: $id,
                        name: $name,
                        emissions: $emissions,
                        energy_type: $type,
                        domain: 'Energy'
                    })
                """, **facility)
            
            # Create energy regulations
            session.run("""
                CREATE (r:Regulation:Energy {
                    name: "CO2_Emission_Limit",
                    limit_value: 500,
                    authority: "EPA"
                })
                CREATE (r2:Regulation:Energy {
                    name: "Renewable_Energy_Target",
                    target_percentage: 30,
                    authority: "DOE"
                })
            """)
            
            # Create compliance relationships
            session.run("""
                MATCH (f:Facility:Energy), (r:Regulation:Energy {name: "CO2_Emission_Limit"})
                WHERE f.emissions > r.limit_value
                CREATE (f)-[:VIOLATES]->(r)
            """)
            
            session.run("""
                MATCH (f:Facility:Energy), (r:Regulation:Energy {name: "CO2_Emission_Limit"})
                WHERE f.emissions <= r.limit_value
                CREATE (f)-[:COMPLIES_WITH]->(r)
            """)
            
            # Create green energy relationships
            session.run("""
                MATCH (f:Facility:Energy)
                WHERE f.energy_type IN ['Solar', 'Wind']
                CREATE (f)-[:CONTRIBUTES_TO]->(:Goal:Energy {name: "Carbon_Neutrality"})
            """)
            
            print("✅ Domain-specific enterprise knowledge graph created")
    
    def query_by_domain(self, domain: str) -> List[Dict]:
        """Query graph by specific domain"""
        if not self.driver:
            return []
        
        with self.driver.session() as session:
            if domain == "Finance":
                result = session.run("""
                    MATCH (c:Customer:Finance)-[:EXPOSED_TO]->(r:Risk:Finance)
                    RETURN c.name as entity, r.name as risk, r.severity as severity
                    LIMIT 10
                """)
            elif domain == "Biotech":
                result = session.run("""
                    MATCH (f:Facility:Biotech)-[:CONDUCTS]->(t:Trial:Biotech)
                    OPTIONAL MATCH (ae:AdverseEvent:Biotech)
                    RETURN f.name as facility, t.name as trial, ae.type as adverse_event
                    LIMIT 10
                """)
            elif domain == "Energy":
                result = session.run("""
                    MATCH (f:Facility:Energy)-[rel]->(r:Regulation:Energy)
                    RETURN f.name as facility, type(rel) as compliance, 
                           f.emissions as emissions, r.name as regulation
                    LIMIT 10
                """)
            else:
                result = session.run("""
                    MATCH (n)-[r]->(m)
                    RETURN n, r, m
                    LIMIT 10
                """)
            
            return [record.data() for record in result]
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()