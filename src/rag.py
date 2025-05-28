import openai
from typing import Dict

class RAGPipeline:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        
        # Try to load fine-tuned model
        try:
            with open("config/model.txt", "r") as f:
                self.model = f.read().strip()
            print(f" Using fine-tuned model: {self.model}")
        except:
            self.model = "gpt-4o-mini"
            
    
    def generate_answer(self, query: str, context: str) -> Dict:
        """Generate answer using context"""
        if not self.client:
            return {
                "answer": f"Based on available data:\n\n{context[:300]}...",
                "tokens_used": 0
            }
        
        prompt = f"""Use the following context to answer the question comprehensively.

Context:
{context}

Question: {query}
Rules:
- Give specific names, numbers, and facts from the data
- Don't add explanations or business advice
- If asked for "which customers", list the exact customer names
- If asked for numbers, give the exact values
- Keep answers short and factual
- Use bullet points for lists

Provide a clear, structured answer with key insights:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are AllyIn Compass, an enterprise AI assistant. Provide clear, structured answers with key insights highlighted."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.1
            )
            
            return {
                "answer": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            return {
                "answer": f"Based on available data:\n\n{context[:300]}...\n\nNote: {str(e)}",
                "tokens_used": 0
            }