class FactMemory:
    def __init__(self):
        self.facts = {}
    def remember(self,k,v):
        self.facts[k]=v
    def forget(self,k):
        self.facts.pop(k,None)
