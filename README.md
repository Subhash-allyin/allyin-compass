# AllyIn Compass

An AI assistant that searches across structured databases, unstructured documents, and knowledge graphs to deliver comprehensive, source-attributed answers.

---

## 🚀 Overview

**AllyIn Compass** is a multi-tool AI agent designed to solve enterprise data fragmentation. It combines:

- **SQL Retrieval**: Query structured data from DuckDB
- **Vector Search**: Semantic search through documents using Qdrant
- **Graph Traversal**: Explore relationships in Neo4j
- **RAG Pipeline**: Context-aware answer generation (e.g., GPT-4)
- **Security Layer**: PII detection and compliance filtering

**Key Features**
- ✅ **Multi-Source Intelligence:** Databases, PDFs, emails, knowledge graphs
- ✅ **Domain-Aware:** Specializations for Finance, Biotech, and Energy
- ✅ **Enterprise Security:** PII masking, compliance risk detection
- ✅ **Source Attribution:** Answers cite original sources
- ✅ **Feedback Loop:** Built-in thumbs up/down rating system

## Architecture

```
Query → Agent → [SQL|Vector|Graph] Retrievers → RAG → Answer
           ↓
      Logging & Metrics
```

## Sample Data

The system auto-generates sample data on first run:
- Customer database (CSV → DuckDB)
- Document embeddings (PDF → Qdrant)
- Graph relationships (Neo4j)
---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.10+
- Docker Desktop
- Git
- OpenAI API key

### 1. Setup Environment
```bash
git clone <your-repo>
cd allyin-compass
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Services
```bash
# Start vector DB and graph DB
docker-compose up -d

# Or manually:
# docker run -p 6333:6333 qdrant/qdrant
# docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
```

### 3. Configure API Keys
Create a .env file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Edit .env with your OpenAI API key
```

### 4. Run Application
```bash
streamlit run app.py
```

## 💡 How to Run a Query

**Using the Web Interface**: Open the Application: Go to http://localhost:8501

**Select Domain:** Choose Finance, Biotech, or Energy

**Enter Your Query:** Use natural language

**Review Results:** Answers with citations; see tools used in sidebar; rate the answer

**Example Queries:**

**Finance:**

- "Show me top customers by revenue with high risk scores"

- "Which clients have compliance violations in Q4?"

**Biotech:**

- "Find all adverse events for molecule X in clinical trials"

- "Which labs failed safety inspections this year?"

**Energy:**

- "List CO2 emissions violations near San Jose since Q1"

- "Which facilities exceed environmental limits?"
