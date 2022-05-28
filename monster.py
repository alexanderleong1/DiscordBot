import random


class Monster:
    def __init__(self, type, attack, defense, hp, speed, variants, mp = 10, luck = 10):
        self.type = type
        self.attack = attack
        self.defense = defense
        self.hp = hp
        self.mp = mp
        self.speed = speed
        self.luck = luck
        self.choose_variant(variants)

    def interaction(self):
        return "A {variant} {type} has appeared!".format(variant=self.variant, type=self.type)

    def stats(self):
        return  "{variant} {type} \n\u2764\uFE0F : {hp} \n\N{crossed swords}: {attack} \n\N{shield}: {defense} \n".format(variant = self.variant,
                                                                                                                          type = self.type,
                                                                                            attack = self.attack,
                                                                                            defense = self.defense,
        hp = self.hp)

    def choose_variant(self, variants):
        self.variant = variants[random.randrange(0, len(variants) - 1, 1)]

    def get_hp(self):
        return self.hp

    def take_damage(self, damage):
        self.hp = self.hp - damage

    """Used to determine the total amount of EXP gained.
    
    HP is weighed more heavily than the other stats.
    """
    def get_total_stats(self):
        return 1000
        # return (1.5 * self.hp) + self.attack + self.defense + self.speed + self.luck

    def __str__(self):
        return ("{variant} {type}").format(variant=self.variant, type=self.type)

class Slime(Monster):
    def __init__(self):
        variants = ['Red', 'Blue', 'Yellow', 'Green']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Ant(Monster):
    def __init__(self):
        variants = ['Soldier', 'Worker', 'Queen', 'King', 'Flying']

        super().__init__(type="Ant", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Boar(Monster):
    def __init__(self):
        variants = ['Sleepy', 'Depressed', 'Agitated', 'Golden']

        super().__init__(type="Boar", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Goblin(Monster):
    def __init__(self):
        variants = ['Tall', 'Mean', 'Angry', 'Sad', 'Aggressive']

        super().__init__(type="Goblin", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)


class Undead(Monster):
    def __init__(self):
        variants = ['Warrior', 'Archer', 'Mage', 'Shaman', 'King', 'Necromancer']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Skeleton(Undead):
    def __init__(self):
        variants = ['Warrior', 'Archer', 'Mage', 'Shaman', 'King', 'Necromancer']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1),
                         hp=random.randrange(3, 5, 1), speed=random.randrange(3, 5, 1), variants=variants, luck=1)

class Zombie(Undead):
    def __init__(self):
        variants = ['Warrior', 'Archer', 'Mage', 'Shaman', 'King', 'Necromancer']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1),
                         hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants=variants, luck=1)

class Spirit(Undead):
    def __init__(self):
        variants = ['Spooky', 'Angry', 'Vengeful', 'Frightened', 'Peaceful']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1),
                         hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants=variants, luck=1)


class Orc(Monster):
    def __init__(self):
        variants = ['Warrior', 'Archer', 'Mage', 'Shaman', 'King']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Bandit(Monster):
    def __init__(self):
        variants = ['Sneaky', 'Swift', 'Sly', 'Leader']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class DarkElf(Monster):
    def __init__(self):
        variants = ['Warrior', 'Archer', 'Mage', 'Shaman', 'King']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)

class Dragon(Monster):
    def __init__(self):
        # changes damage types
        variants = ['Crimson', 'Sapphire', 'Emerald', 'White']

        super().__init__(type="Slime", attack=random.randrange(1, 3, 1), defense=random.randrange(1, 3, 1), hp=random.randrange(3, 5, 1),
                         speed=random.randrange(3, 5, 1), variants = variants, luck = 1)