import pathlib
import os
from sqlalchemy import create_engine, text
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentType

class SQLRetriever:
    def __init__(self, db_path="compass.duckdb"):
        # Ensure DB file exists
        self.db_path = pathlib.Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.touch(exist_ok=True)
        
        # Create engine and database
        self.engine = create_engine(f"duckdb:///{self.db_path}")
        
        # Create SQL Database wrapper
        self.sql_db = SQLDatabase(self.engine)
        
        # Create LLM and agent
        try:
            # Get API key from environment or session
            api_key = os.getenv("OPENAI_API_KEY")

            self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    openai_api_key=api_key
            )
                
                # Create SQL agent
            self.agent = create_sql_agent(
                    llm=self.llm,
                    db=self.sql_db,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                )
            print(" SQL agent initialized with LangChain")

                
        except Exception as e:
            print(f" Agent initialization failed: {e}")
            self.llm = None
            self.agent = None
    
    def search(self, query: str) -> str:
        """Search using LangChain SQL agent"""

        result = self.agent.invoke({"input": query})
            
            # Extract the output
        if isinstance(result, dict):
            output = result.get("output", str(result))
        else:
            output = str(result)
            
        return output