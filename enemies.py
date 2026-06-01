class Enemies:
    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage

    def take_damage(self, amount):
        self.health -= amount
        
        if self.health <= 0:
            print("💀")

    def attack(self):
        return self.damage

    def __str__(self):
        return f"{self.name} (HP: {self.health}, DMG: {self.damage})"