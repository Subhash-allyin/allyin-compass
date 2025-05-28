import pandas as pd
import duckdb
from pathlib import Path
from qdrant_client import QdrantClient
import json
from qdrant_client.models import Distance, VectorParams, PointStruct
from tools.document_parser import DocumentParser

class DataIngester:
    def __init__(self, db_path="compass.duckdb"):
        self.db_path = str(Path(db_path).resolve())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        from tools.embeddings import embedding_engine
        self.embedder = embedding_engine if getattr(embedding_engine, 'available', False) else None

        self.vector_client = QdrantClient("localhost", port=6333)

    
    def get_db_path(self):
        return self.db_path
    
    def ingest_structured(self, data_path="data/structured"):
        """Load CSV files into DuckDB"""
        data_path = Path(data_path)
        data_path.mkdir(parents=True, exist_ok=True)
        
        with duckdb.connect(self.db_path) as db:
            existing = {row[0] for row in db.execute("SHOW TABLES").fetchall()} if self._safe_execute(db, "SHOW TABLES") else set()
            
            for csv_file in data_path.glob("*.csv"):
                table_name = csv_file.stem
                
                # Skip if already has data
                if table_name in existing and self._table_has_data(db, table_name):
                    continue
                
                try:
                    df = pd.read_csv(csv_file)
                    db.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
                    print(f" Loaded {len(df)} rows into {table_name}")
                except Exception as e:
                    print(f" Error loading {csv_file}: {e}")
    
    def _safe_execute(self, db, sql):
        try:
            return db.execute(sql).fetchall()
        except:
            return None
    
    def _table_has_data(self, db, table_name):
        try:
            count = db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            if count > 0:
                print(f" Table {table_name} already loaded ({count} rows)")
                return True
        except:
            pass
        return False
    
    def ingest_unstructured(self, data_path="data/unstructured"):

        """Parse documents and create embeddings"""
        data_path = Path(data_path)
        data_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize document parser
        parser = DocumentParser(chunk_size=1000, chunk_overlap=200)
        
        # Parse all documents and save to JSONL
        output_path = data_path / "parsed.jsonl"
        documents, chunks = parser.parse_directory(data_path, output_path)
        
        
        # Vector storage using chunks
        if self.embedder and self.vector_client:
            try:
                # Setup collection (ignore if exists)
                try:
                    self.vector_client.create_collection("documents", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
                except:
                    pass
                
                # Store chunks with embeddings
                texts = [chunk["text"] for chunk in chunks]
                embeddings = self.embedder.encode(texts)
                points = [
                    PointStruct(
                        id=i, 
                        vector=embeddings[i].tolist(), 
                        payload=chunks[i]
                    ) for i in range(len(chunks))
                ]
                
                self.vector_client.upsert("documents", points)
                print(f" Stored {len(chunks)} chunks in vector DB")
            except Exception as e:
                print(f" Vector storage error: {e}")
        else:
            print(" Vector storage unavailable")
        
        return len(chunks) 