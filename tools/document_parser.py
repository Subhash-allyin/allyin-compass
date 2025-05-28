import json
import fitz  # PyMuPDF
import email
from email import policy
from pathlib import Path
from typing import Dict, List, Any
import re
import warnings
import multiprocessing

warnings.filterwarnings('ignore', category=UserWarning, message='resource_tracker: There appear to be')

class DocumentParser:
    def __init__(self, chunk_size=1000, chunk_overlap=200, min_chunk_size=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def parse_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text from PDF"""
        text = ""
        page_count = 0
        with fitz.open(pdf_path) as doc:
            page_count = len(doc)
            text = "".join([page.get_text() for page in doc])
        
        return {
            "source": pdf_path.name,
            "type": "pdf",
            "content": text.strip(),
            "metadata": {
                "pages": page_count
            }
        }
    
    def parse_eml(self, eml_path: Path) -> Dict[str, Any]:
        """Extract subject and body from email"""
        with open(eml_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        subject = msg.get('Subject', 'No Subject')
        sender = msg.get('From', 'Unknown')
        date = msg.get('Date', 'Unknown')
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return {
            "source": eml_path.name,
            "type": "email",
            "content": f"Subject: {subject}\nFrom: {sender}\nDate: {date}\n\n{body}",
            "metadata": {
                "subject": subject,
                "sender": sender,
                "date": date
            }
        }
    
    def chunk_text(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks without duplicates"""
        # Clean text
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        last_chunk_text = None
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '! ', '? ', ';\n', ':\n']:
                    last_delim = text.rfind(delimiter, start, end)
                    if last_delim > start + self.chunk_size // 2:
                        end = last_delim + len(delimiter) - 1
                        break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            # Only add if it's not empty, not a duplicate, and meets minimum size
            if chunk_text and chunk_text != last_chunk_text and len(chunk_text) >= self.min_chunk_size:
                chunks.append({
                    "id": f"{doc_id}_chunk_{chunk_id}",
                    "text": chunk_text,
                    "chunk_index": chunk_id,
                    "doc_id": doc_id
                })
                chunk_id += 1
                last_chunk_text = chunk_text
            
            # Calculate next start position
            if end >= len(text):
                break
                
            # Apply overlap
            next_start = max(start + 1, end - self.chunk_overlap)
            
            # Ensure we make progress
            if next_start <= start:
                start = end
            else:
                start = next_start
        
        return chunks
    
    def parse_directory(self, data_path: Path, output_path: Path):
        """Parse all documents in directory and save as JSONL"""
        documents = []
        all_chunks = []
        
        # Parse PDFs
        for pdf_path in data_path.glob("*.pdf"):
            try:
                doc = self.parse_pdf(pdf_path)
                doc_id = f"pdf_{pdf_path.stem}"
                doc["id"] = doc_id
                documents.append(doc)
                
                # Create chunks
                chunks = self.chunk_text(doc["content"], doc_id)
                all_chunks.extend(chunks)
                print(f"✓ Parsed {pdf_path.name}: {len(chunks)} chunks")
            except Exception as e:
                print(f"✗ Error parsing {pdf_path}: {e}")
        
        # Parse emails
        for eml_path in data_path.glob("*.eml"):
            try:
                doc = self.parse_eml(eml_path)
                doc_id = f"eml_{eml_path.stem}"
                doc["id"] = doc_id
                documents.append(doc)
                
                # Create chunks
                chunks = self.chunk_text(doc["content"], doc_id)
                all_chunks.extend(chunks)
                print(f"✓ Parsed {eml_path.name}: {len(chunks)} chunks")
            except Exception as e:
                print(f"✗ Error parsing {eml_path}: {e}")
        
        # Save as JSONL
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk) + '\n')
        
        print(f"\n✓ Saved {len(all_chunks)} chunks to {output_path}")
        return documents, all_chunks
