import discord
import os
from discord.ext import commands
from discord.ui import Button, View
# from discord_ui import Button, UI, Interaction, LinkButton, Components
# from discord_components import DiscordComponents, ComponentsBot, Button
import random
import asyncio
from monster import *
from character import *
from pymongo import MongoClient
import pymongo
import math
import secrets

bot_token = secrets.bot_token

connection_str = secrets.db_connection

os.system("python monster.py")

# client = discord.Client()
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

# client = ComponentsBot(command_prefix = ".")
# database containing all stored character information
char_db = get_database()["character_data"]

# dictionary containing all currently spawned enemies
enemies = {}

if __name__ == '__main__':
    char_db.update_many({},
                        {'$set': {'in_combat': False}})


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='.start'))


# @client.event
# async def on_message(message):
#     # checks if message is from the bot
#     if message.author == client.user:
#         return
#
#     # checks the bot command from the user
#     if message.content.startswith('.'):
#         await user_input(message)

# message is instance of message class.
# content is string of message content.
# async def user_input(message):
#     content = message.content
#
#     # Set the message author. This allows the program to find who the current character is.
#     author = ctx.author
#     author = message.author
#
#     # This sets the channel for returning the appropriate message.
#     global channel
#     global client
#     channel = message.channel
#
#     # Switch statement to determine what the bot should do based on user input.
#     if content == '.w' or content == '.walk':
#         await walk()
#     elif content == '.a' or content == '.attack':
#         await attack(message)
#     elif content == '.stats':
#         await stats()
#     elif content == '.create' or content == '.start':
#         await create()
#     elif content == '.help':
#         await help()
#     elif content == '.sp' or content == '.skillpoints':
#         await sp()
#     elif content == '.inv' or content == '.inventory':
#         await inventory()
#     elif content == '.flee':
#         await flee()
#     elif content == '.loc':
#         await location()
#     elif content == '.statshelp':
#         await stats_help()
#     elif content == '.botinfo':
#         await bot_info()
#     elif content == '.leaderboard':
#         await leaderboard("level")
#     elif '.set' in content:
#         await set(content)
#     elif content == '.shop':
#         await shop()
#     elif content == '.btn':
#         await test(message)
#     else:
#         await ctx.send(Unknown command. Use .help for a list of available commands.")

"""Starts the Bot for a certain user.

If the user already has a character, will load the UI. If the user does not have a character,
then it will create a new character.
"""


@client.command()
async def start(ctx):
    author = ctx.author
    if char_db.find_one({'_id': author.id}) is None:
        await create(ctx)

    await display_default_ui(ctx)


# class View(discord.ui.View):
#     @discord.ui.button(label="click me!", style=discord.ButtonStyle.green)
#     async def button_callback(self, button, interaction):
#         await interaction.response.send_message("clicked")
#
# @client.command()
# async def test(ctx):
#     await ctx.delete()

"""Overriding class for Button.

The UIButton class overrides the callback method for every instance. This allows the Button interaction
to create a proper response.
"""


class UIButton(Button):
    def __init__(self, label, custom_id, style, ctx, view):
        super().__init__(label=label, custom_id=custom_id, style=style)
        self.ctx = ctx

    async def callback(self, interaction):
        # Removes all the buttons from the previous user interaction.
        # self.view.clear_items()
        if self.custom_id == 'walk':
            await interaction.response.defer()
            await interaction.delete_original_message()
            # await interaction.response.edit_message(embed=discord.Embed(description="You walk forward...",
            #                                                             color=0x27E8D1), view=self.view)
            await walk(self.ctx)
        elif self.custom_id == 'stats':
            # await interaction.response.edit_message(embed=discord.Embed(description="Stats",
            #                                                             color=0x27E8D1), view=self.view)
            await interaction.response.defer()
            await interaction.delete_original_message()
            await stats(self.ctx)
            await display_default_ui(self.ctx)
        elif self.custom_id == 'inventory':
            # await interaction.response.edit_message(embed=discord.Embed(description="Inventory",
            #                                                             color=0x27E8D1), view=self.view)
            await interaction.response.defer()
            await interaction.delete_original_message()
            await inventory(self.ctx)
            await display_default_ui(self.ctx)
        elif self.custom_id == 'shop':
            # await interaction.response.edit_message(embed=discord.Embed(description="General Shop",
            #                                                             color=0x27E8D1), view=self.view)
            await interaction.response.defer()
            await interaction.delete_original_message()
            await shop(self.ctx)
            await display_default_ui(self.ctx)
        elif self.custom_id == 'location':
            # await interaction.response.edit_message(embed=discord.Embed(description="Location",
            #                                                             color=0x27E8D1), view=self.view)
            await interaction.response.defer()
            await interaction.delete_original_message()
            await location(self.ctx)
            await display_default_ui(self.ctx)
        elif self.custom_id == 'attack':
            # await interaction.response.edit_message(embed=discord.Embed(description="Attack",
            #                                                             color=0x27E8D1), view=self.view)
            await interaction.response.defer()
            await interaction.delete_original_message()
            await attack(self.ctx)
        elif self.custom_id == 'flee':
            await interaction.response.defer()
            await interaction.delete_original_message()
            await flee(self.ctx)


"""Displays the default UI.

Choices for walking, opening shop, checking inventory, changing locations
"""
async def display_default_ui(ctx):
    view = View()

    walk_button = UIButton(label="Walk", custom_id='walk', style=discord.ButtonStyle.green, ctx=ctx, view=view)
    stats_button = UIButton(label="Stats", custom_id='stats', style=discord.ButtonStyle.blurple, ctx=ctx, view=view)
    shop_button = UIButton(label="Inventory", custom_id='inventory', style=discord.ButtonStyle.blurple, ctx=ctx,
                           view=view)
    inventory_button = UIButton(label="Shop", custom_id='shop', style=discord.ButtonStyle.blurple, ctx=ctx, view=view)
    location_button = UIButton(label="Move Locations", custom_id='location', style=discord.ButtonStyle.blurple, ctx=ctx,
                               view=view)

    await initialize_buttons(view, [
        walk_button, stats_button, shop_button, inventory_button, location_button
    ],ctx)

    # await ctx.message.delete()


"""Displays the combat UI.

Includes choices for attack, special attack, inventory, and flee.
"""
async def display_combat_ui(ctx):
    view = View()

    attack_button = UIButton(label="Attack", custom_id='attack', style=discord.ButtonStyle.green, ctx=ctx, view=view)
    s_attack_button = UIButton(label="Special Attack", custom_id='s_attack', style=discord.ButtonStyle.blurple, ctx=ctx,
                               view=view)
    inventory_button = UIButton(label="Inventory", custom_id='inventory', style=discord.ButtonStyle.blurple, ctx=ctx,
                                view=view)
    flee_button = UIButton(label="Flee", custom_id='flee', style=discord.ButtonStyle.red, ctx=ctx, view=view)

    await initialize_buttons(view, [
        attack_button, s_attack_button, inventory_button, flee_button
    ], ctx)


"""Initializes the buttons in button_list for the user interface.

Args:
    button_list (list): a list of Button objects to add to the view.
    view (View): a reference to the user UI.
"""
async def initialize_buttons(view, button_list, ctx, content=""):
    for button in button_list:
        view.add_item(button)
    await ctx.send(content=content,view=view)

"""Displays the shop interface.

Routes to the default, general merchant shop.
"""
@client.command()
async def shop(ctx):
    await ctx.send(embed=discord.Embed(description="Your shop looks pretty empty..", color=0x27E8D1))


"""Developer tool to debug features.

Changes a specified stat to the desired value. 

Typical Usage Example:
    set dexterity 100
"""
@client.command()
async def set(ctx):
    char_arr = ctx.message.content.split(' ')
    index = 'stats.' + str(char_arr[1])
    char_db.update_one({'_id': ctx.author.id},
                       {'$set': {index: int(str(char_arr[2]))}})


"""Displays location info for a player.

There are different stages to each biome. The higher the stage number, the more difficult the monsters will be.
"""
@client.command()
async def location(ctx):
    await ctx.send(embed=discord.Embed(description="You are currently located at " + str(char_db.find_one({'_id': ctx.author.id})['location']),color=0x27E8D1))


"""Displays a stats help page that gives a rundown on how all the stats work.

Each stat affects one part of gameplay or combat. The player will gain damage based on their stat distributions.
"""
@client.command()
async def stats_help(ctx):
    await ctx.send(embed=discord.Embed(description="__**Stats Tutorial**__\n" +
                       "Welcome to the stats tutorial! Here's a quick rundown on how the stats work:\n" +
                       "**HP** determines the amount of damage you can take before losing a combat. This can be reset using potions or food. Players will additionally regain HP periodically.\n" +
                       "**MP** dictates the amount of times you can use your special ability. Each cast of your special ability will cost some MP.\n" +
                       "**Strength** affects the amount of damage you deal with melee weapons.\n" +
                       "**Vitality** adds a small amount to your HP and increases all resistances.\n" +
                       "**Dexterity** determines your critical strike chance and critical strike damage. Additionally increases weapon damage for certain weapon types.\n" +
                       "**Intelligence** increases damage dealt by special abilities.\n" +
                       "**Agility** affects the turn order for combat. Having a higher agility ensures that a player will go first. If a player's agility is high enough, they can take multiple turns before their opponent.\n" +
                       "**Luck** increases drop rates for all items and increases rates for rare encounters.\n" +
                       "Players can allocate 3 stat points (SP) every level. Special items must be used to reset allocated SP.",color=0x27E8D1))


"""Moves the player around in their current location. 

When a player moves throughout their location, they will have random encounters. These encounters include:
    Encountering a monster
    Taking random damage
    Finding gold on the floor
    NPC encounters
"""


@client.command()
async def walk(ctx):
    author = ctx.author
    # The current character is the author of the message.
    character = char_db.find_one({'_id': author.id})

    # If the user is currently in combat, then print error message and return.
    if character['in_combat']:
        await ctx.send(embed=discord.Embed(description="You are already in combat!",color=0x27E8D1))

    choice = random.randint(0, 1000)
    if choice < 30:  # Finding money, 3% chance
        # Amount of money found = random_int(character_level / 2 + (1.35 * character_luck), character_level + (1.35 * character_luck))
        char_stats = character['stats']
        char_level = char_stats['level']
        char_luck = char_stats['luck']
        amount_found = random.randrange(int(char_level / 2 + 1.35 * char_luck), int(char_level + 1.35 * char_luck), 1)
        await ctx.send(embed=discord.Embed(description="You found {} gold on the ground.".format(amount_found),color=0x27E8D1))
        await add_gold(amount_found)

    elif choice < 40:  # Tripping and taking x damage, 1% chance
        # Amount of damage taken = random_int(character_level * 2 + (0.85 * character_defense), character_level * 2 + (0.85 * character_defense))
        char_stats = character['stats']
        char_level = char_stats['level']
        char_vitality = char_stats['vitality']
        damage_taken = random.randrange(int(char_level * 1.1 - (0.85 * char_vitality)),
                                        int(char_level * 1.5 + (0.85 * char_vitality)))
        new_hp = character['hp'] - damage_taken
        await ctx.send(embed=discord.Embed(description="You slipped on a stray banana peel and took {} damage. You now have {} HP.".format(
            damage_taken, new_hp),color=0x27E8D1))
        char_db.update_one({'_id': author.id},
                           {"$set": {'hp': new_hp}})

    elif choice >= 40:  # Monster encounter, 90% chance
        # Update the in_combat status of the user.
        char_db.update_one({'_id': author.id},
                           {'$set': {'in_combat': True}})
        await spawn(ctx)
        # Send a picture of the monster
        # with open('Capture.png', 'rb') as fp:
        #   await channel.send(file=discord.File(fp, 'Capture.png'))


"""Called when the user attacks an opponent.

Checks if the user is in a valid combat. If not, sends an error message and returns from the function. Otherwise,
the user deals damage to their opponent based on current stats and equipment.
"""


@client.command()
async def attack(ctx):
    author = ctx.author
    character = char_db.find_one({'_id': author.id})

    # Check if the character is in combat. If they are not in combat, then display an error message and return.
    if character['in_combat'] is False:
        await ctx.send(embed=discord.Embed(description="You are not in combat.",color=0x27E8D1))

    # Check if there is a mapping in the dictionary. Error happens when program is restarted and in_combat is not reset.
    try:
        if enemies[author.id] is None:
            char_db.update_one({'_id': author.id},
                               {'$set': {'in_combat': False}})
            await ctx.send(embed=discord.Embed(description="You are not in combat.",color=0x27E8D1))

    except Exception:
        pass

    # is_crit = character_luck / 100
    # if is_crit: damage_dealt = (1.5 + character_luck / 100) * (random_int(character_attack * (0.8 + character_luck / 100), (character_attack))
    # if not is_crit: damage_dealt = (random_int(character_attack * (0.8 + character_luck / 100), (character_attack))
    char_dex = character['stats']['dexterity']
    char_str = character['stats']['strength']

    crit_threshold = int(character['stats']['dexterity']) + 5
    roll = random.randrange(0, 100)
    if roll < crit_threshold:
        damage_dealt = int((1.5 + char_dex / 100) * (random.randint(int(char_str), int(char_str * 1.1))))
        enemies[author.id].take_damage(damage_dealt)
        enemy_hp_left = enemies[author.id].get_hp() if enemies[author.id].get_hp() >= 0 else 0
        await ctx.send(embed=discord.Embed(description="\U0001F4A5You landed a critical strike for {} damage.\U0001F4A5\nThe {} has {} \u2764\uFE0F left.".format(
                               damage_dealt, enemies[author.id], enemy_hp_left),color=0x27E8D1))
        if enemy_hp_left <= 0:
            await despawn(ctx)
        else:
            await display_combat_ui(ctx)
    else:
        damage_dealt = random.randint(int(char_str), int(char_str * 1.1))
        enemies[author.id].take_damage(damage_dealt)
        enemy_hp_left = enemies[author.id].get_hp() if enemies[author.id].get_hp() >= 0 else 0
        await ctx.send(embed=discord.Embed(description="\N{crossed swords}You attacked the {} for {} damage.\N{crossed swords}\nThe {} has {} \u2764\uFE0F left.".format(
                               enemies[author.id], damage_dealt, enemies[author.id], enemy_hp_left),color=0x27E8D1))
        if enemy_hp_left <= 0:
            await despawn(ctx)
        else:
            await display_combat_ui(ctx)

    # TODO

"""Allows the player to flee from combat
"""
@client.command()
async def flee(ctx):
    author = ctx.author
    # Check if the player is in combat
    if char_db.find_one({'_id': author.id})['in_combat'] is False:
        await ctx.send(embed=discord.Embed(description="You are not in combat.",color=0x27E8D1))

    # Set the players in_combat status to false.
    char_db.update_one({'_id': author.id},
                       {'$set': {'in_combat': False}})

    # Remove the dictionary mapping.
    if enemies.get(author.id) is not None:
        enemies.pop(author.id)

    await ctx.send(embed=discord.Embed(description="You fled from combat!",color=0x27E8D1))
    await display_default_ui(ctx)

"""Used to despawn a Monster instance that is associated with a user.

When a Monster's hp reaches 0, this method is called. It will remove the mapping from the dictionary and set the users
in_combat status to False.
"""


async def despawn(ctx):
    author = ctx.author

    character = char_db.find_one({'_id': author.id})

    # Send message for winning battle
    enemy = enemies[author.id]
    exp_gained = random.randrange(int(enemy.get_total_stats() * 0.925), int(enemy.get_total_stats() * 1.075))
    await add_exp(ctx, exp_gained)

    # Remove the enemy from the dictionary
    enemies.pop(author.id)

    # Change the user's in_combat status
    char_db.update_one({'_id': author.id},
                       {'$set': {'in_combat': False}})


"""Adds EXP to the user.
"""


async def add_exp(ctx, amount):
    author = ctx.author

    character = char_db.find_one({'_id': author.id})

    new_exp = char_db.find_one({'_id': author.id})['exp'] + amount
    char_db.update_one({'_id': author.id},
                       {'$set': {'exp': new_exp}})

    # Manual level up in the add_exp function to expedite the text speed
    while char_db.find_one({'_id': author.id})['exp'] >= char_db.find_one({'_id': author.id})['max_exp']:
        character = char_db.find_one({'_id': author.id})
        curr_exp = character['exp']
        max_exp = character['max_exp']

        new_curr_exp = curr_exp - max_exp
        new_max_exp = int(pow(1000, character['stats']['level'] / 100 + 1))
        new_level = character['stats']['level'] + 1
        new_max_hp = character['stats']['hp'] + 1

        char_db.update_one({'_id': author.id},
                           {'$set': {'exp': new_curr_exp, 'max_exp': new_max_exp, 'stats.level': new_level,
                                     'stats.hp': new_max_hp, 'hp': new_max_hp}})
        await ctx.send(embed=discord.Embed(description="Leveled up to {}! Max HP increased to {}.".format(character['stats']['level'],
                                                                                   char_db.find_one({'_id': author.id})[
                                                                                       'stats']['hp']),color=0x27E8D1))
    await ctx.send(embed=discord.Embed(description="You have defeated {}! Earned {} EXP ({} / {})".format(enemies[author.id], amount,
                                                                                   char_db.find_one({'_id': author.id})[
                                                                                       'exp'],
                                                                                   char_db.find_one({'_id': author.id})[
                                                                                       'max_exp']), color=0x27E8D1))
    await display_default_ui(ctx)


"""Changes level and adjusts stats upon level up.

Called if the EXP bar is filled. If so, takes the excess over the EXP bar and adds it to the new one. Changes the maximum 
EXP bar. Maximum EXP is determined by 1000^1.(level - 1)
"""
# async def level_up(author):
#     character = char_db.find_one({'_id': author.id})
#     curr_exp = character['exp']
#     max_exp = character['max_exp']
#
#     new_curr_exp = curr_exp - max_exp
#     new_max_exp = int(pow(1000, character['stats']['level'] / 100 + 1))
#     new_level = character['stats']['level'] + 1
#     new_max_hp = character['stats']['hp'] + 1
#
#     char_db.update_one({'_id': author.id},
#                        {'$set': {'exp': new_curr_exp, 'max_exp': new_max_exp, 'stats.level': new_level,
#                                  'stats.hp': new_max_hp, 'hp': new_max_hp}})
#
#     await ctx.send(Leveled up to {}! Max HP increased to {}.".format(character['stats']['level'],
#                                                                           char_db.find_one({'_id': author.id})[
#                                                                               'stats']['hp']))

"""Displays a menu for the user to assign skill points.

Shows the user the number of available skill points to be allocated. 
"""


@client.command()
async def sp(ctx):
    return


"""Adds gold to a user's inventory

Args:
    amount (int): the amount of gold to add
"""


@client.command()
async def add_gold(ctx, amount):
    author = ctx.author
    new_amount = char_db.find_one({'_id': author.id})['inventory']['gold'] + amount
    char_db.update_one(
        {'_id': author.id},
        {"$set": {'inventory.gold': new_amount}}
    )


"""Displays a character's inventory.

Searches for character based on primary key id. Creates a string representation of the inventory array.
"""


@client.command()
async def inventory(ctx):
    author = ctx.author
    char_inv = char_db.find_one({'_id': author.id})['inventory']
    await ctx.send(embed=discord.Embed(description="__**{}'s inventory**__\n\nGold: {}\nEquipment: {}\nFood: {}"
                       .format(author, char_inv['gold'], char_inv['equipment'], char_inv['food']),color=0x27E8D1))


"""Spawns a Monster during a combat encounter.

Generates a random Monster to spawn based on the location of the user. Each Monster has a different variation that 
changes their stats and item drops.
"""


async def spawn(ctx):
    author = ctx.author
    character = char_db.find_one({'_id': author.id})
    location = character['location']
    """Forest 1
    
    Monsters:
        Slimes
        
    Drops:
        
    """
    if location == "forest_1":
        monster = Slime()
        await ctx.send(embed=discord.Embed(description=monster.interaction() + '\n' + monster.stats(), color=0x27E8D1))
        enemies[author.id] = monster
        await display_combat_ui(ctx)

    # elif location is "forest_2":


"""Creates a new character.

Only called when a new user is playing for the first time. Creates an instance of the Character class and initializes
all of the default values using a pre-defined template. Will send a message indicating the success of this operation.
"""


async def create(ctx):
    author = ctx.author
    if char_db.find_one({'_id': author.id}) is None:
        Character(author.id, author)
        await ctx.send(embed=discord.Embed(description="New character created!",color=0x27E8D1))

    else:
        await ctx.send(embed=discord.Embed(description="You've already created a character!",color=0x27E8D1))


"""Prints character stats.

Accesses the stats Object from the character database. Called by the .stats keyword in the text channel.
"""


@client.command()
async def stats(ctx):
    author = ctx.author
    char_info = char_db.find_one({'_id': author.id})
    char_stats = char_info['stats']
    await ctx.send(embed=discord.Embed(description="__**Displaying {}'s stats:**__ \nLevel {} ({} EXP / {} EXP) \n\u2764\uFE0F HP:  {} / {}\n\U0001F535 MP: {} / {} \n\N{flexed biceps} STR:  {} \n\N{adhesive bandage} VIT:   {}\n\U0001F3AF DEX: {} \n\N{scroll} INT:   {} \n\U0001F45F AGL: {}\n\N{sparkles} LUK:  {}"
                       .format(author, char_stats['level'], char_db.find_one({'_id': author.id})['exp'],
                               char_db.find_one({'_id': author.id})['max_exp'],
                               char_info['hp'], char_stats['hp'], char_info['mp'], char_stats['mp'],
                               char_stats['strength'],
                               char_stats['vitality'], char_stats['dexterity'], char_stats['intelligence'],
                               char_stats['agility'],
                               char_stats['luck']),color=0x27E8D1))


# """Sends a text representation of the stats with verbal descriptions rather than emoticons.
# """
# async def send_text_stats(c):
#     # author = ctx.author
#     char_info = char_db.find_one({'_id': author.id})
#     char_stats = char_info['stats']
#     await ctx.send(__**Displaying {}'s stats:**__ \nLevel {} \nHP: {} \nMP: {} \nStrength: {} \nVitality: {}\nDexterity: {} \nIntelligence: {} \nAgility: {}\nLuck: {}"
#           .format(author, char_stats['level'], char_stats['hp'], char_stats['mp'], char_stats['strength'],
#                   char_stats['vitality'],char_stats['dexterity'],char_stats['intelligence'],char_stats['agility'],
#                   char_stats['luck']))

"""Prints a help menu for the user.

Calls send_message to print a string representation of all available user commands. Called by the keyword .help in
the text channel.
"""


@client.command()
async def tutorial(ctx):
    await ctx.send(embed=discord.Embed(description="__**Getting Started**__\n" +
                       ".create: Creates a new character\n" +
                       ".stats: View your character stats\n" +
                       ".inv: View your inventory \n" +
                       ".statshelp: Character stats tutorial" +
                       "\n\n__**Gameplay**__\n" +
                       ".w: Walk forward\n" +
                       ".a: Attack opponent (only available during combat)\n",
                       color=0x27E8D1))


"""Displays bot statistics.

Includes number of total players and the number of servers the bot is in.
"""


@client.command()
async def bot_info(ctx):
    await ctx.send(embed=discord.Embed(description="There are {players} players across {servers} servers!".format(
        players=char_db.count_documents({}), servers=str(len(client.guilds))),color=0x27E8D1))


"""Displays leaderboard rankings for a specific statistic.

Args:
    statistic (str): the statistic to display the top 20 players for.
"""


@client.command()
async def leaderboard(ctx, statistic):
    await ctx.send(embed=discord.Embed(description="__**{} Leaderboard**__".format(statistic.capitalize()),color=0x27E8D1))
    total_players = char_db.count_documents({})
    max_lb = total_players if total_players < 20 else 20
    if statistic == 'level':
        top_players = char_db.find().sort('stats.level', -1)
        for x in range(0, max_lb):
            await ctx.send(embed=discord.Embed(description=str((x + 1)) + ". " + top_players[x]['discord_name'] + " (Lv. {})".format(
                top_players[x]['stats']['level']),color=0x27E8D1))


"""Edits the embedded message.

Changes the embedded message to display the updated content based on the user button click.
"""
async def update_ui(ctx, message_content):
    embedVar = discord.Embed(description=message_content, color=0x27E8D1)
    await ctx.edit_message(embed=embedVar)


"""Tells the bot to send a message.

Args:
    message_content (str): the string message to print
    
Typical usage example:
        end_message(author.id)
"""
async def send_message(ctx, message_content):
    embedVar = discord.Embed(description=message_content, color=0x27E8D1)
    await ctx.send(embed=embedVar)

    # Return type used when user presses a button. Returns an embedded variable based on the current command.
    #
    # await channel.send('>>> {}'.format(message_content))


client.run(bot_token)
