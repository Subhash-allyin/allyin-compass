import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
sys.path.append(str(Path(__file__).parent.parent))

from src.ingest import DataIngester
from retrievers.sql import SQLRetriever
from retrievers.vector import VectorRetriever
from retrievers.graph import GraphRetriever
from src.rag import RAGPipeline
from agents.multi_tool_agent import MultiToolAgent
from feedback.simple_feedback import SimpleFeedback
from dashboards.metrics import MetricsDashboard
from security.security_wrapper import SecureQueryWrapper


def init_system():
    """Initialize the AllyIn Compass system"""
    try:
        ingester = DataIngester()
        ingester.ingest_structured()
        ingester.ingest_unstructured()
        
        sql_retriever = SQLRetriever(ingester.get_db_path())
        vector_retriever = VectorRetriever()
        graph_retriever = GraphRetriever()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        rag_pipeline = RAGPipeline(openai_key)
        
        # Create the base agent
        agent = MultiToolAgent(sql_retriever, vector_retriever, graph_retriever, rag_pipeline)
        
        # Wrap with security layer
        secure_agent = SecureQueryWrapper(agent)
        
        return secure_agent
    
    except Exception as e:
        st.error(f"System initialization failed: {e}")
        return None

def main():
    st.set_page_config(page_title="AllyIn Compass", page_icon="🧭", layout="wide")
    
    # Initialize session state
    if 'last_query_result' not in st.session_state:
        st.session_state.last_query_result = None
    if 'selected_domain' not in st.session_state:
        st.session_state.selected_domain = "Finance"
    
    st.title("🧭 AllyIn Compass")
    st.markdown("* AI Assistant - Search across databases, documents, and knowledge graphs*")
    
    feedback = SimpleFeedback()
    dashboard = MetricsDashboard()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # API Key input
        if not os.getenv("OPENAI_API_KEY"):
            api_key = st.text_input("OpenAI API Key", type="password")
            if api_key:
                st.session_state.openai_key = api_key
        
        dashboard.display_live_dashboard()
        st.markdown("---")
        
        # Feedback Stats
        stats = feedback.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👍 Positive", stats["positive"])
        with col2:
            st.metric("👎 Negative", stats["negative"])
        
        if stats["total"] > 0:
            st.metric("Satisfaction", f"{stats['satisfaction_rate']:.1%}")
        
        if stats["ready_for_training"]:
            st.success("✅ Ready for fine-tuning!")
        else:
            needed = max(0, 10 - stats["positive"])
            if needed > 0:
                st.warning(f"⏳ Need {needed} more 👍")
    
    # Initialize system
    if 'agent' not in st.session_state:
        with st.spinner("Initializing AllyIn Compass..."):
            st.session_state.agent = init_system()
    
    if not st.session_state.agent:
        st.error("❌ System initialization failed")
        return
    
    # Domain Selection
    domain = st.selectbox("🏢 Domain", ["Finance", "Biotech", "Energy"])
    st.session_state.selected_domain = domain
    
    # Quick Actions
    quick_actions = {
        "Finance": [
            ("📊 Revenue Analytics", "Show me top customers by revenue"),
            ("🎯 Risk Analysis", "Which customers are high risk?"),
            ("💰 Profit Margins", "Show profit margins by customer")
        ],
        "Biotech": [
            ("🧪 Lab Compliance", "Which labs have safety violations?"),
            ("⚗️ Clinical Trials", "Show clinical trial compliance status"),
            ("🔬 Research Issues", "Find research protocol deviations")
        ],
        "Energy": [
            ("⚠️ Emissions Violations", "Find CO2 emissions violations"),
            ("🏭 Facility Status", "Show facility emission levels"),
            ("🌱 Green Compliance", "Environmental compliance status")
        ]
    }
    
    st.subheader(f"Quick Actions - {domain}")
    col1, col2, col3 = st.columns(3)
    
    for idx, (label, query_text) in enumerate(quick_actions[domain]):
        with [col1, col2, col3][idx]:
            if st.button(label, use_container_width=True):
                st.session_state.query = query_text
    
    # Sample Queries
    sample_queries = {
        "Finance": ["What's our total revenue by sector?", "Find financial performance trends"],
        "Biotech": ["Find adverse outcomes for molecule X", "Patient data privacy compliance"],
        "Energy": ["Renewable energy adoption rates", "Carbon footprint by facility"]
    }
    
    with st.expander(f"📝 More {domain} Queries"):
        for query in sample_queries[domain]:
            if st.button(query, key=f"sample_{query}"):
                st.session_state.query = query
    
    # Query Input
    query = st.text_input(
        "Your Question:",
        value=st.session_state.get("query", ""),
        placeholder=f"Ask about {domain.lower()} topics..."
    )
    
    col_clear, col_search = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Clear"):
            st.session_state.query = ""
            st.session_state.last_query_result = None
            st.rerun()
    
    with col_search:
        if st.button("🔍 Search", type="primary", use_container_width=True) and query:
            with st.spinner("🧠 Analyzing..."):
                enhanced_query = f"[Domain: {domain}] {query}"
                result = st.session_state.agent.execute(enhanced_query)
                
                st.session_state.last_query_result = {
                    "query": query,
                    "answer": result["answer"],
                    "result": result
                }
    
    # Display Results
    if st.session_state.last_query_result:
        result = st.session_state.last_query_result["result"]
        
        st.markdown("---")
        st.header("📋 Results")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("💡 Answer")
            st.markdown(result["answer"])
            
            with st.expander("📚 Sources & Context"):
                st.text(result["context"])
        
        with col2:
            st.subheader("🔧 Details")
            
            domain_badges = {"Finance": "💰", "Biotech": "🧬", "Energy": "⚡"}
            st.write(f"**Domain:** {domain_badges.get(domain, '🏢')} {domain}")
            
            # Tools used
            tool_badges = {
                "sql": "🗃️ SQL",
                "vector": "📄 Vector", 
                "graph": "🕸️ Graph"
            }
            tools_display = [tool_badges.get(tool, tool) for tool in result["tools_used"]]
            st.write(f"**Tools Used:** {' + '.join(tools_display)}")
            st.write(f"**Time:** {result['execution_time']:.2f}s")
            
            # Feedback
            st.subheader("👍 Rate Answer")
            feedback_col1, feedback_col2 = st.columns(2)
            
            with feedback_col1:
                if st.button("👍", key="thumbs_up", use_container_width=True):
                    feedback.log(
                        st.session_state.last_query_result["query"], 
                        st.session_state.last_query_result["answer"], 
                        1
                    )
                    st.success("Thanks!")
                    st.rerun()
            
            with feedback_col2:
                if st.button("👎", key="thumbs_down", use_container_width=True):
                    feedback.log(
                        st.session_state.last_query_result["query"], 
                        st.session_state.last_query_result["answer"], 
                        -1
                    )
                    st.info("Will improve!")
                    st.rerun()

if __name__ == "__main__":
    main()