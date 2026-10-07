# Browser Agent — Search, navigate, extract, screenshot, click, type, scroll, research, summarize
class BrowserAgent:
    def search(self, query): return "Results: ..."
    def navigate(self, url): return True
    def extract(self): return "Page text"
    def screenshot(self): return True
    def click(self, selector): return True
    def type(self, text): return True
    def scroll(self): return True

class ResearchMode:
    def multi_source_search(self, query): return []
    def synthesize(self, sources): return "Report with citations."
    def detect_uncertainty(self): return True
