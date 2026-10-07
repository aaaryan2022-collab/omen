# Memory — 6 forms: conversation, session, long-term, project, document, task
class MemoryStore:
    def conversation_memory(self, user, msg): pass
    def session_memory(self): pass
    def long_term_memory(self, category, key, value): pass
    def project_memory(self, project_id, data): pass
    def document_memory(self, doc_id, chunks): pass
    def task_memory(self, task_id, state): pass
    def search(self, query): return []
    def edit(self, id, new_val): return True
    def delete(self, id): return True
    def inspect(self, id): return {}
