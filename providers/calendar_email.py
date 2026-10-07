# Calendar + Email providers (architecture)
class CalendarProvider:
    def today(self): pass
    def upcoming(self): pass
    def create(self): pass
    def edit(self): pass
    def delete(self): pass
    def conflict_check(self): pass

class EmailProvider:
    def search(self): pass
    def read(self): pass
    def summarize(self): pass
    def draft(self): pass
    def categorize(self): pass
    def send_confirmed(self): pass  # requires confirmation unless trusted
