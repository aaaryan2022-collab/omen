# RAG — PDF, DOCX, TXT, Markdown, code, project files. Ingest → chunk → embed → index → retrieve → rerank → generate
class RAGPipeline:
    def ingest(self, file_path): return True
    def chunk(self, text): return ["chunk1", "chunk2"]
    def embed(self, chunks): return []
    def index(self, embeddings): return True
    def retrieve(self, query): return []
    def rerank(self, results): return results
    def generate(self, query, sources): return "Answer with citations."
