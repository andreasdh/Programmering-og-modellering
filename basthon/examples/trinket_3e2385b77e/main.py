class Vektor:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, vektor):
        x = self.x + vektor.x
        y = self.y + vektor.y
        z = self.z + vektor.z
        return [x, y, z]
    
u = Vektor(1,2,2)
v = Vektor(4,4,4)
print(u.add(v))