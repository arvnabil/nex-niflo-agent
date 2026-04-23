import fitz  # PyMuPDF
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.schemas.document import DocumentChunk, DocumentMetadata

class DocumentLoader:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            is_separator_regex=False
        )
        
    def load_pdf(self, file_path, tenant="default"):
        doc = fitz.open(file_path)
        chunks = []
        source = os.path.basename(file_path)
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            split_texts = self.splitter.split_text(text)
            for st in split_texts:
                metadata = DocumentMetadata(
                    source=source,
                    type="pdf",
                    tenant=tenant,
                    page=page_num + 1
                )
                chunks.append(DocumentChunk(text=st, metadata=metadata))
        return chunks

    def load_text(self, file_path, tenant="default"):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        source = os.path.basename(file_path)
        split_texts = self.splitter.split_text(text)
        chunks = []
        for st in split_texts:
            metadata = DocumentMetadata(
                source=source,
                type="text",
                tenant=tenant
            )
            chunks.append(DocumentChunk(text=st, metadata=metadata))
        return chunks
