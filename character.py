from database import get_database

# database containing all stored character information
char_db = get_database()["character_data"]

class Character:
    def __init__(self, name, author):
        # Character functionality
        self.monster = None
        self.name = name
        self.in_combat = False

        author_str = str(author)

        # Character stats
        # self.stats = {'Level': 0, 'HP': 0, 'MP': 0, 'Attack': 0, 'Defense': 0, 'Speed': 0, 'Luck': 0}
        if char_db.find_one({"_id" : name}) is None:
            self.character = {
                '_id': name,
                'discord_name': author_str,
                'stats': {
                          'level': 1,
                          'exp': 0,
                          'hp': 15,
                          'mp': 10,
                          'strength': 1,
                          'vitality': 1,
                          'dexterity': 1,
                          'intelligence': 1,
                          'agility': 1,
                          'luck': 1
                },
                'inventory': {
                    'gold': 0,
                    'equipment': [],
                    'food': []
                },
                'equipment': {
                    'main_hand': "None",
                    'off_hand': "None",
                    'helmet': "None",
                    'chestplate': "None",
                    'legs': "None",
                    'boots': "None"
                },
                'food_recipes': [],
                'in_combat' : False,
                'hp': 15,
                'mp': 10,
                'exp': 0,
                'max_exp': 1000,
                'sp': 0,
                'location': "forest_1"
            }
            char_db.insert_one(self.character)

        print(str(self.name) + ' created a new character')

    def set_opponent(self, monster):
        self.monster = monster

    def get_opponent(self):
        return self.monster

    def get_stats(self):
        return self.stats