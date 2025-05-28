from datetime import datetime
from typing import Dict
import re
import os
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI

class MultiToolAgent:
    def __init__(self, sql_retriever, vector_retriever, graph_retriever, rag_pipeline):
        self.sql_retriever = sql_retriever
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        self.rag_pipeline = rag_pipeline
        self.query_count = 0
        
        # Few-shot examples for response formatting
        self.few_shot_examples = {
            "high_risk_query": {
                "keywords": ["high risk", "risky customer", "risk customer"],
                "template": """### High-Risk Customers Identified

**1. High-Risk Customers:**
   - **[Customer Name 1]**
   - **[Customer Name 2]**

### Key Insights

**A. Risk Analysis:**
   - [Risk categorization details based on operational practices and violations]

**B. Risk Connection Analysis:**
   - **[Customer 1]:**
     - Associated with **[Risk Type]** due to [specific reasons]
   - **[Customer 2]:**
     - Linked to **[Risk Type]** stemming from [specific issues]

**C. Risk Propagation Effects:**
   - **[Risk Category 1]:**
     - [Impact description and long-term implications]
   - **[Risk Category 2]:**
     - [Relationship effects and consequences]

### Conclusion
[Summary of identified high-risk customers and monitoring recommendations]"""
            },
            "financial_analysis": {
                "keywords": ["revenue", "profit", "financial performance", "top customers"],
                "template": """### Financial Analysis Results

**1. Key Financial Metrics:**
   - **Total Revenue:** [Amount]
   - **Top Performers:** [List]

### Detailed Breakdown

**A. Performance Analysis:**
   - [Financial metrics and trends]

**B. Customer Segmentation:**
   - **High-Value Customers:** [Details]
   - **Growth Opportunities:** [Analysis]

### Summary
[Key financial insights and recommendations]"""
            }
        }
        
        # Domain-specific tool priorities
        self.domain_tools = {
            "Finance": ["sql", "vector", "graph"],
            "Biotech": ["vector", "graph", "sql"],
            "Energy": ["graph", "vector", "sql"]
        }
        
        # Domain focus instructions
        self.domain_focus = {
            "Finance": "Focus on financial metrics, revenue, risk analysis, and regulatory compliance.",
            "Biotech": "Emphasize research findings, clinical data, safety protocols, and lab compliance.",
            "Energy": "Highlight environmental impact, emissions data, facility operations, and sustainability."
        }
        
        self._init_agent()
    
    def _init_agent(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=api_key)
            tools = [
                Tool(name="sql_search", description="Customer/financial/risk data", func=self.sql_retriever.search),
                Tool(name="document_search", description="Reports/documents/audits", func=self.vector_retriever.search),
                Tool(name="graph_search", description="Violations/relationships/compliance", func=self.graph_retriever.search)
            ]
            self.agent = initialize_agent(
                tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False, max_iterations=5, max_execution_time=45
            )
        else:
            self.agent = None
    
    def _parse_query(self, query: str) -> tuple:
        """Extract domain and clean query"""
        domain_match = re.match(r'\[Domain: (\w+)\]', query)
        domain = domain_match.group(1) if domain_match else "General"
        clean_query = re.sub(r'\[Domain: \w+\]', '', query).strip()
        return domain, clean_query
    
    def _get_response_template(self, query: str) -> str:
        """Get appropriate response template based on query type"""
        q = query.lower()
        
        for example_key, example_data in self.few_shot_examples.items():
            if any(keyword in q for keyword in example_data["keywords"]):
                return example_data["template"]
        
        return ""
    
    def _enhance_query_with_template(self, query: str) -> str:
        """Enhance query with few-shot template for better formatting"""
        template = self._get_response_template(query)
        
        if template:
            return f"""{query}

Please format your response following this structure:

{template}

Use the actual data from the search results to fill in the specific details."""
        
        return query
    
    def _get_tools_for_query(self, domain: str, query: str) -> list:
        """Determine which tools to use based on domain and query content"""
        q = query.lower()
        
        # Use domain-specific tool order if available
        if domain in self.domain_tools:
            priority_tools = self.domain_tools[domain]
        else:
            priority_tools = ["sql", "vector", "graph"]
        
        # Keyword-based tool selection
        sql_keywords = ["customer", "revenue", "risk", "financial", "profit", "top", "metric"]
        vector_keywords = ["report", "document", "audit", "compliance", "research", "finding"]
        graph_keywords = ["violation", "emission", "facility", "relationship", "connected"]
        comprehensive_keywords = ["high risk", "analysis", "overview", "assessment", "status"]
        
        # For comprehensive queries, use all tools in domain priority order
        if any(keyword in q for keyword in comprehensive_keywords):
            return priority_tools
        
        # Select tools based on keywords
        tools_needed = []
        if any(word in q for word in sql_keywords):
            tools_needed.append("sql")
        if any(word in q for word in vector_keywords):
            tools_needed.append("vector")
        if any(word in q for word in graph_keywords):
            tools_needed.append("graph")
        
        # If no specific keywords, use top 2 domain tools
        return tools_needed if tools_needed else priority_tools[:2]
    
    def _execute_tools(self, query: str, tools_needed: list) -> tuple:
        """Execute specified tools and collect results"""
        context_parts = []
        tools_used = []
        
        for tool in tools_needed:
            try:
                if tool == "sql":
                    result = self.sql_retriever.search(query)
                    context_parts.append(f"**Database Results:**\n{result}")
                elif tool == "vector":
                    result = self.vector_retriever.search(query)
                    context_parts.append(f"**Document Search:**\n{result}")
                elif tool == "graph":
                    result = self.graph_retriever.search(query)
                    context_parts.append(f"**Knowledge Graph:**\n{result}")
                tools_used.append(tool)
            except Exception:
                continue  
        
        return context_parts, tools_used
    
    def execute(self, query: str) -> Dict:
        start_time = datetime.now()
        
        # Parse query and extract domain
        domain, clean_query = self._parse_query(query)
        
        # Determine tools to use
        tools_needed = self._get_tools_for_query(domain, clean_query)
        
        # Execute tools
        context_parts, tools_used = self._execute_tools(clean_query, tools_needed)
        
        # Generate answer using RAG pipeline
        if context_parts:
            combined_context = "\n\n".join(context_parts)
            domain_context = self.domain_focus.get(domain, "")
            
            # Enhance query with few-shot template
            template_enhanced_query = self._enhance_query_with_template(clean_query)
            enhanced_query = f"{template_enhanced_query}\n\nDomain focus: {domain_context}" if domain_context else template_enhanced_query
            
            answer = self.rag_pipeline.generate_answer(enhanced_query, combined_context)["answer"]
        else:
            answer = "No relevant data found for the query."
        
        self.query_count += 1
        
        return {
            "answer": answer,
            "tools_used": tools_used,
            "execution_time": (datetime.now() - start_time).total_seconds(),
            "context": "\n\n".join(context_parts) if context_parts else "No context available",
            "domain": domain,
            "tools_summary": f"Tools used: {', '.join([f'{tool.upper()}' for tool in tools_used])}"
        }
    
    def get_metrics(self) -> Dict:
        return {
            "total_queries": self.query_count,
            "supported_domains": list(self.domain_focus.keys()),
            "agent_available": self.agent is not None
        }