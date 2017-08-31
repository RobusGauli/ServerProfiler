import psutil

class Memory(object):
    threshold = 100
    def __init__(self):
        self.memory = psutil.virtual_memory()
        
    
    @property
    def total(self):
        return self.memory.total // (1024 * 1024)

    @property
    def available(self):
        return self.memory.available // (1024 * 1024)

    @property
    def use_percentage(self):
        return self.memory.percent

    @property
    def health(self):
        return 'Good' if self.available >= self.threshold else 'Critical'