from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict

class VectorRetriever:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        
        # Initialize embedder
        from tools.embeddings import embedding_engine
        self.embedder = embedding_engine if getattr(embedding_engine, 'available', False) else None
        
        # Initialize client
        try:
            self.client = QdrantClient("localhost", port=6333)
            collections = [c.name for c in self.client.get_collections().collections]
            
            if collection_name not in collections:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
                )
                print(f" Created vector collection '{collection_name}'")
            else:
                print(f" Connected to vector collection '{collection_name}'")
                
        except Exception as e:
            print(f" Vector retriever unavailable: {e}")
            self.client = None
    
    def search(self, query: str, top_k: int = 3) -> str:
        """Search for similar documents"""
        try:
            query_vector = self.embedder.encode_single(query)
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=top_k
            )
            
            if not results:
                return "No relevant documents found."
            
            # Format results compactly
            formatted = [f"**Found {len(results)} relevant documents:**\n"]
            
            for i, hit in enumerate(results, 1):
                source = hit.payload.get('source', 'Unknown')
                doc_type = hit.payload.get('type', 'doc')
                text = hit.payload.get('text', '')[:400]
                score = hit.score
                
                formatted.extend([
                    f" **{i}. {source}** [{doc_type}] (Score: {score:.3f})",
                    f"   {text}{'...' if len(hit.payload.get('text', '')) > 400 else ''}\n"
                ])
            
            return "\n".join(formatted)
            
        except Exception as e:
            return f"Vector search error: {e}"
    
    def add_documents(self, documents: List[Dict[str, str]]) -> bool:
        """Add documents to vector store"""
        if not (self.client and self.embedder):
            return False
        
        try:
            points = []
            for idx, doc in enumerate(documents):
                if text := doc.get('text'):
                    embedding = self.embedder.encode_single(text)
                    points.append(models.PointStruct(
                        id=idx,
                        vector=embedding.tolist(),
                        payload={
                            'text': text,
                            'source': doc.get('source', 'unknown'),
                            'type': doc.get('type', 'document'),
                            'metadata': doc.get('metadata', {})
                        }
                    ))
            
            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)
                print(f" Added {len(points)} documents to vector store")
                return True
            
        except Exception as e:
            print(f" Vector storage error: {e}")
        
        return False