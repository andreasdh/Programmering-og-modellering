class Skilpadde:
    def __init__(self):
        self.artsnavn = "Chelonia mydas"
        self.farge = "green"
        if self.farge == "green":
            self.hp = 15
        elif self.farge == "red":
            self.hp = 20
    def harm(self, skade):
        self.hp -= skade
    def heal(self):
        self.hp += 5

skilpadde1 = Skilpadde()
skilpadde1.farge = "red"

print(skilpadde1.hp)
skilpadde1.harm(12)
skilpadde1.heal()
print(skilpadde1.hp)