class Glass:
    def __init__(self, kapasitet):
        self.innhold = 0
    
    def fyll(self, mengde):
        self.mengde = mengde
        self.innhold += self.mengde
            
    def tøm(self, mengde):
        self.mengde = mengde
        self.innhold -= self.mengde
        
    def sjekkInnhold(self):
        return self.innhold