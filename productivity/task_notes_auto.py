# Tasks + Notes + Automations
class TaskManager:
    def add(self, title, priority, due, tags): pass
    def subtask(self, parent, title): pass
    def complete(self, id): pass
    def search(self, query): pass

class NoteSystem:
    def create(self, title, content, folder, tags): pass
    def ai_summary(self, note_id): pass
    def extract_tasks(self, note_id): pass
    def search(self, query): pass

class Automation:
    def save_workflow(self, name, steps): pass
    def run(self, name): pass
    def persist(self): pass
