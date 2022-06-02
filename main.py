import discord
import os
from discord.ext import commands
from discord.ui import Button, View
# from discord_ui import Button, UI, Interaction, LinkButton, Components
# from discord_components import DiscordComponents
# from discord_components import DiscordComponents, ComponentsBot
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
# DiscordComponents(client)

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


"""Tells the bot to send a message.

Args:
    message_content (str): the string message to print

Typical usage example:
        end_message(author.id)
"""
async def send_message(ctx, message_content):
    # return discord.Embed(description=message_content)
    await ctx.send(embed=discord.Embed(description=message_content, color=0x27E8D1))

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
    # If the user has not created a character before, create a new character and store in the database.
    if char_db.find_one({'_id': author.id}) is None:
        new_character = await create(ctx, False)
        await display_default_ui(ctx, new_character)
        return

    # Resumes the player combat if they are left off in the middle of combat.
    if char_db.find_one({'_id': author.id})['in_combat']:
        await display_combat_ui(ctx, "Welcome back, " + str(author)[:-5] + "!" + '\n\n' + enemies[author.id].stats())
    else:
        await display_default_ui(ctx)


"""Overriding class for stat allocation Button.

The StatButton class overrides the callback method for Button. Used for Button interactions when allocating SP.
Separate class allows for better modularity between UI buttons and stat allocation buttons.
"""
class StatButton(Button):
    def __init__(self, label, custom_id, style, ctx, row=0, disabled=False):
        super().__init__(label=label, custom_id=custom_id, style=style, row=row, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction):


        id = self.ctx.author.id
        character = char_db.find_one({'_id': id})
        character_stats = character['stats']

        # Disable leveling up stats during combat. If a user attempts to do so, ignore the response.
        if character['in_combat']:
            await interaction.response.defer()
            await display_combat_ui(self.ctx, content="You can't level up skills while in combat!\n\n" +
                                    enemies[id].stats())
            return
        if character['sp'] <= 0:
            await interaction.response.defer()
            await display_default_ui(self.ctx, content= await stats(self.ctx, False) + "\n\nYou don't have any SP available!")
            return
        # Increase HP by 5
        if self.custom_id == 'hp':
            await interaction.response.defer()
            new_hp = character_stats['hp'] + 5
            char_db.update_one({'_id': id},
                               {'$set': {'stats.hp': new_hp}})
            # Update the current HP so it is maxed.
            char_db.update_one({'_id': id},
                               {'$set': {'hp': new_hp}})
        # Increase MP by 5
        elif self.custom_id == 'mp':
            await interaction.response.defer()
            new_mp = character_stats['mp'] + 5
            char_db.update_one({'_id': id},
                               {'$set': {'stats.mp': new_mp}})
            # Update the current MP so it is maxed.
            char_db.update_one({'_id': id},
                               {'$set': {'mp': new_mp}})
        # Increase all other attributes by 1
        else:
            await interaction.response.defer()
            new_stat = character_stats[self.custom_id] + 1
            char_db.update_one({'_id': id},
                               {'$set': {'stats.{}'.format(self.custom_id): new_stat}})
        # Decrease the amount of SP by 1
        char_db.update_one({'_id':id},
                           {'$set': {'sp': (char_db.find_one({'_id':id})['sp'] - 1)}})
        # Display the new stat page with a success message.
        if len(self.custom_id) <= 2:
            # Capitalize HP and MP.
            updated_stat = self.custom_id.upper()
        else:
            # Capitalize only the first letter for other stats.
            updated_stat = self.custom_id.capitalize()
        str_rep = await stats(self.ctx, False) + '\n\n' + "Successfully allocated 1 SP to " + updated_stat + "!"
        await display_default_ui(self.ctx, str_rep, self.custom_id)

"""Overriding class for Button.

The UIButton class overrides the callback method for every instance. This allows the Button interaction
to create a proper response.
"""
class UIButton(Button):
    def __init__(self, label, custom_id, style, ctx, row=0, disabled=False):
        super().__init__(label=label, custom_id=custom_id, style=style, row=row, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction):
        # print(interaction.user.id)
        # print(interaction.user)

        # Removes all the buttons from the previous user interaction.
        # self.view.clear_items()
        if self.custom_id == 'walk':
            await interaction.response.defer()
            #await interaction.delete_original_message()
            # await interaction.response.edit_message(embed=discord.Embed(description="You walk forward...",
            #                                                           ), view=self.view)
            walk_res = await walk(self.ctx, False)
            if walk_res[0] == 'gold' or walk_res[0] == 'slip':
                await display_default_ui(self.ctx, walk_res[1])
            elif walk_res[0] == 'combat':
                await display_combat_ui(self.ctx, walk_res[1])
            elif walk_res[0] == 'already_in_combat':
                await display_combat_ui(self.ctx, walk_res[1] + '\n\n' + enemies[self.ctx.author.id].stats())
        elif self.custom_id == 'stats':
            # await interaction.response.edit_message(embed=discord.Embed(description="Stats",
            #                                                           ), view=self.view)
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await stats(self.ctx, False)
            await display_default_ui(self.ctx, str_rep, self.custom_id)
        elif self.custom_id == 'inventory':
            # await interaction.response.edit_message(embed=discord.Embed(description="Inventory",
            #                                                           ), view=self.view)
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await inventory(self.ctx, False)
            await display_default_ui(self.ctx, str_rep)
        elif self.custom_id == 'shop':
            # await interaction.response.edit_message(embed=discord.Embed(description="General Shop",
            #                                                           ), view=self.view)
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await shop(self.ctx, False)
            await display_default_ui(self.ctx, str_rep)
        elif self.custom_id == 'location':
            # await interaction.response.edit_message(embed=discord.Embed(description="Location",
            #                                                           ), view=self.view)
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await location(self.ctx, False)
            await display_default_ui(self.ctx, str_rep)
        elif self.custom_id == 'attack':
            # await interaction.response.edit_message(embed=discord.Embed(description="Attack",
            #                                                           ), view=self.view)
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await attack(self.ctx, False)
            if char_db.find_one({'_id': self.ctx.author.id})['in_combat']:
                await display_combat_ui(self.ctx, str_rep)
            else:
                await display_default_ui(self.ctx, str_rep)
        elif self.custom_id == 'flee':
            await interaction.response.defer()
            #await interaction.delete_original_message()
            str_rep = await flee(self.ctx, False)
            await display_default_ui(self.ctx, str_rep)
        elif self.custom_id == 'sp':
            await interaction.response.defer()


"""Displays the default UI.

Choices for walking, opening shop, checking inventory, changing locations
"""
async def display_default_ui(ctx, content="", custom_id=""):
    view = View()

    walk_button = UIButton(label="Walk", custom_id='walk', style=discord.ButtonStyle.green, ctx=ctx)

    # Check if there is available SP. If so, change the stats button color to green.
    if char_db.find_one({'_id': ctx.author.id})['sp'] == 0:
        stats_button_style = discord.ButtonStyle.blurple
    else:
        stats_button_style = discord.ButtonStyle.green

    stats_button = UIButton(label="Stats", custom_id='stats', style=stats_button_style, ctx=ctx)

    shop_button = UIButton(label="Inventory", custom_id='inventory', style=discord.ButtonStyle.blurple, ctx=ctx,
                           )
    inventory_button = UIButton(label="Shop", custom_id='shop', style=discord.ButtonStyle.blurple, ctx=ctx)
    location_button = UIButton(label="Move Locations", custom_id='location', style=discord.ButtonStyle.blurple, ctx=ctx,
                               )

    await initialize_buttons(view, [
        walk_button, stats_button, shop_button, inventory_button, location_button
    ],ctx,content,custom_id)


"""Displays the combat UI.

Includes choices for attack, special attack, inventory, and flee.
"""
async def display_combat_ui(ctx, content="", custom_id=""):
    view = View()

    attack_button = UIButton(label="Attack", custom_id='attack', style=discord.ButtonStyle.green, ctx=ctx)
    s_attack_button = UIButton(label="Special Attack", custom_id='s_attack', style=discord.ButtonStyle.blurple, ctx=ctx,
                              )
    inventory_button = UIButton(label="Inventory", custom_id='inventory', style=discord.ButtonStyle.blurple, ctx=ctx,
                                )
    flee_button = UIButton(label="Flee", custom_id='flee', style=discord.ButtonStyle.red, ctx=ctx)

    await initialize_buttons(view, [
        attack_button, s_attack_button, inventory_button, flee_button
    ], ctx, content)


"""Initializes the buttons in button_list for the user interface.

Args:
    button_list (list): a list of Button objects to add to the view.
    view (View): a reference to the user UI.
"""
async def initialize_buttons(view, button_list, ctx, content="", custom_id=""):
    # If there is an available Stat point and the user is on the Stat interface, display buttons to allocate Stat points.
    if char_db.find_one({'_id': ctx.author.id})['sp'] != 0 and custom_id == 'stats':
        stat_list = [StatButton(label="{} SP".format(char_db.find_one({'_id':ctx.author.id})['sp']), custom_id='sp', style=discord.ButtonStyle.red, ctx=ctx, row=0),
                     StatButton(label="HP", custom_id='hp', style=discord.ButtonStyle.blurple, ctx=ctx, row=0),
                     StatButton(label="MP", custom_id='mp', style=discord.ButtonStyle.blurple, ctx=ctx, row=0),
                     StatButton(label="STR", custom_id='strength', style=discord.ButtonStyle.blurple, ctx=ctx, row=1),
                     StatButton(label="VIT", custom_id='vitality', style=discord.ButtonStyle.blurple, ctx=ctx, row=1),
                     StatButton(label="DEX", custom_id='dexterity', style=discord.ButtonStyle.blurple, ctx=ctx, row=1),
                     StatButton(label="INT", custom_id='intelligence', style=discord.ButtonStyle.blurple, ctx=ctx, row=2),
                     StatButton(label="AGL", custom_id='agility', style=discord.ButtonStyle.blurple, ctx=ctx, row=2),
                     StatButton(label="LUK", custom_id='luck', style=discord.ButtonStyle.blurple, ctx=ctx, row=2)]
        for button in stat_list:
            view.add_item(button)
        for button in button_list:
            button.row = 3
            view.add_item(button)
    else:
        for button in button_list:
            view.add_item(button)
    

    if content == "":
        await ctx.send(embed=discord.Embed(description="Welcome back, " + str(ctx.author)[:-5] + "!", color=0x27E8D1), view=view)
    else:
        await ctx.send(embed=discord.Embed(description=content, color=0x27E8D1), view=view)

"""Displays the shop interface.

Routes to the default, general merchant shop.
"""
@client.command()
async def shop(ctx, is_sender=True):
    if is_sender:
        await send_message(ctx, "Your shop looks pretty empty..")
    else:
        return "Your shop looks pretty empty.."
        # return send_message(ctx, "Your shop looks pretty empty..")

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
async def location(ctx, is_sender=True):
    if is_sender:
        await send_message(ctx, "You are currently located at " + str(char_db.find_one({'_id': ctx.author.id})['location']))
    else:
        return "You are currently located at " + str(char_db.find_one({'_id': ctx.author.id})['location'])

"""Displays a stats help page that gives a rundown on how all the stats work.

Each stat affects one part of gameplay or combat. The player will gain damage based on their stat distributions.
"""
@client.command()
async def stats_help(ctx, is_sender=True):
    stats_help_text = "__**Stats Help Tutorial**__"
    if is_sender:
        await ctx.send(discord.Embed(description=stats_help_text))
    else:
        return stats_help_text

"""Moves the player around in their current location. 

When a player moves throughout their location, they will have random encounters. These encounters include:
    Encountering a monster ("combat")
    Taking random damage ("slip")
    Finding gold on the floor ("gold")
    NPC encounters ("npc")
"""
@client.command()
async def walk(ctx, is_sender=True):
    author = ctx.author
    # The current character is the author of the message.
    character = char_db.find_one({'_id': author.id})

    # If the user is currently in combat, then print error message and return.
    if character['in_combat']:
        if is_sender:
            await send_message(ctx, "You are already in combat!")
        else:
            return ("already_in_combat", "You are already in combat!")
    choice = random.randint(0, 1000)
    if choice < 30:  # Finding money, 3% chance
        # Amount of money found = random_int(character_level / 2 + (1.35 * character_luck), character_level + (1.35 * character_luck))
        char_stats = character['stats']
        char_level = char_stats['level']
        char_luck = char_stats['luck']
        amount_found = random.randrange(int(char_level / 2 + 1.35 * char_luck), int(char_level + 1.35 * char_luck), 1)
        await add_gold(ctx, amount_found)
        if is_sender:
            await send_message(ctx, "You found {} gold on the ground.".format(amount_found))
        else:
            return ("gold", "You found {} gold on the ground.".format(amount_found))

    elif choice < 40:  # Tripping and taking x damage, 1% chance
        # Amount of damage taken = random_int(character_level * 2 + (0.85 * character_defense), character_level * 2 + (0.85 * character_defense))
        char_stats = character['stats']
        char_level = char_stats['level']
        char_vitality = char_stats['vitality']
        damage_taken = random.randrange(int(char_level * 1.1 - (0.85 * char_vitality)),
                                        int(char_level * 1.5 + (0.85 * char_vitality)))
        new_hp = character['hp'] - damage_taken
        char_db.update_one({'_id': author.id},
                           {"$set": {'hp': new_hp}})
        if is_sender:
            await send_message(ctx, "You slipped on a stray banana peel and took {} damage. You now have {} HP.".format(
            damage_taken, new_hp))
        else:
            return ("slip", "You slipped on a stray banana peel and took {} damage. You now have {} HP.".format(damage_taken, new_hp))

    elif choice >= 40:  # Monster encounter, 90% chance
        # Update the in_combat status of the user.
        char_db.update_one({'_id': author.id},
                           {'$set': {'in_combat': True}})
        return ("combat", await spawn(ctx, False))
        # Send a picture of the monster
        # with open('Capture.png', 'rb') as fp:
        #   await channel.send(file=discord.File(fp, 'Capture.png'))


"""Called when the user attacks an opponent.

Checks if the user is in a valid combat. If not, sends an error message and returns from the function. Otherwise,
the user deals damage to their opponent based on current stats and equipment.
"""
@client.command()
async def attack(ctx, is_sender=True):
    author = ctx.author
    character = char_db.find_one({'_id': author.id})

    # Check if the character is in combat. If they are not in combat, then display an error message and return.
    if character['in_combat'] is False:
        if is_sender:
            await send_message(ctx, "You are not in combat.")
        else:
            return "You are not in combat."

    # Check if there is a mapping in the dictionary. Error happens when program is restarted and in_combat is not reset.
    try:
        if enemies[author.id] is None:
            char_db.update_one({'_id': author.id},
                               {'$set': {'in_combat': False}})
            if is_sender:
                await send_message(ctx, "You are not in combat.")
            else:
                return "You are not in combat."
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
        str_rep = "\U0001F4A5You landed a critical strike for **{} damage**\U0001F4A5".format(
                               damage_dealt) + '\n\n' + enemies[author.id].stats()
        if is_sender:
            await send_message(ctx, str_rep)
            if enemy_hp_left <= 0:
                return str_rep + '\n' + await despawn(ctx)
        else:
            try:
                return str_rep
            finally:
                if enemy_hp_left <= 0:
                    return str_rep + '\n' + await despawn(ctx)
    else:
        damage_dealt = random.randint(int(char_str), int(char_str * 1.1))
        enemies[author.id].take_damage(damage_dealt)
        enemy_hp_left = enemies[author.id].get_hp() if enemies[author.id].get_hp() >= 0 else 0
        str_rep = "\N{crossed swords}You attacked for **{} damage**\N{crossed swords}".format(
                            damage_dealt) + '\n\n' + enemies[author.id].stats()
        if is_sender:
            await send_message(ctx, str_rep)
            if enemy_hp_left <= 0:
                return str_rep + '\n' + await despawn(ctx)
        else:
            try:
                return str_rep
            finally:
                if enemy_hp_left <= 0:
                    return str_rep + '\n' + await despawn(ctx)

"""Allows the player to flee from combat
"""
@client.command()
async def flee(ctx, is_sender=True):
    author = ctx.author
    # Check if the player is in combat
    if char_db.find_one({'_id': author.id})['in_combat'] is False:
        if is_sender:
            await send_message(ctx, "You are not in combat.")
        else:
            return "You are not in combat."
    # Set the players in_combat status to false.
    char_db.update_one({'_id': author.id},
                       {'$set': {'in_combat': False}})

    # Remove the dictionary mapping.
    if enemies.get(author.id) is not None:
        enemies.pop(author.id)

    if is_sender:
        await send_message(ctx, "You fled from combat!")
    else:
        return "You fled from combat!"

"""Used to despawn a Monster instance that is associated with a user.

When a Monster's hp reaches 0, this method is called. It will remove the mapping from the dictionary and set the users
in_combat status to False.
"""
async def despawn(ctx):
    author = ctx.author

    # Send message for winning battle
    enemy = enemies[author.id]
    exp_gained = random.randrange(int(enemy.get_total_stats() * 0.925), int(enemy.get_total_stats() * 1.075))

    # Remove the enemy from the dictionary
    enemy = enemies.pop(author.id)

    # Change the user's in_combat status
    char_db.update_one({'_id': author.id},
                       {'$set': {'in_combat': False}})

    return await add_exp(ctx, exp_gained, enemy)


"""Adds EXP to the user.
"""
async def add_exp(ctx, amount, enemy=None):
    author = ctx.author

    new_exp = char_db.find_one({'_id': author.id})['exp'] + amount
    char_db.update_one({'_id': author.id},
                       {'$set': {'exp': new_exp}})

    character = char_db.find_one({'_id': author.id})

    # If the maximum EXP is met, then level up.
    if character['exp'] >= character['max_exp']:
        return await level_up(ctx, amount, enemy)

        # await ctx.send(discord.Embed(description="Leveled up to {}! Max HP increased to {}.".format(character['stats']['level'],
        #                                                                            char_db.find_one({'_id': author.id})[
        #                                                                                'stats']['hp'])))

    if enemy is None:
        return "Earned {} EXP ({} / {})".format(amount,
                                                char_db.find_one({'_id': author.id})[
                                                    'exp'],
                                                char_db.find_one({'_id': author.id})[
                                                    'max_exp'])
    else:
        return "Defeated {}! Earned **{} EXP** ({} / {})".format(enemy, amount,
                                                                      char_db.find_one({'_id': author.id})[
                                                                          'exp'],
                                                                      char_db.find_one({'_id': author.id})[
                                                                          'max_exp'])

"""Changes level and adjusts stats upon level up.

Called if the EXP bar is filled. If so, takes the excess over the EXP bar and adds it to the new one. Changes the maximum 
EXP bar. Maximum EXP is determined by 1000^1.(level - 1)
"""
async def level_up(ctx, amount, enemy=None):
    author = ctx.author

    # Calculate the new amount of EXP after adding the earned EXP.
    new_exp = char_db.find_one({'_id': author.id})['exp'] + amount
    char_db.update_one({'_id': author.id},
                       {'$set': {'exp': new_exp}})

    # While the EXP exceeds the maximum EXP, add levels to the character.
    while char_db.find_one({'_id': author.id})['exp'] >= char_db.find_one({'_id': author.id})['max_exp']:
        character = char_db.find_one({'_id': author.id})
        curr_exp = character['exp']
        max_exp = character['max_exp']

        new_curr_exp = curr_exp - max_exp
        new_max_exp = int(pow(1000, character['stats']['level'] / 100 + 1))
        new_level = character['stats']['level'] + 1
        new_max_hp = character['stats']['hp'] + 1

        # Update current EXP, max EXP, level, HP, and MP.
        char_db.update_one({'_id': author.id},
                           {'$set': {'exp': new_curr_exp, 'max_exp': new_max_exp, 'stats.level': new_level,
                                     'stats.hp': new_max_hp, 'hp': new_max_hp, 'mp': char_db.find_one({'_id':author.id})['stats']['mp']}})

    # Increase the amount of SP by 1 for every level.
    updated_sp = char_db.find_one({'_id': author.id})['sp'] + 1
    char_db.update_one({'_id': author.id},
                       {'$set': {'sp': updated_sp}})

    if enemy is None:
        return "Earned {} EXP ({} / {})".format(amount,
                                                char_db.find_one({'_id': author.id})[
                                                    'exp'],
                                                char_db.find_one({'_id': author.id})[
                                                    'max_exp']) + '\n\n' + "Leveled up to {}! Max HP increased to {}. Earned **1 SP**.".format(character['stats']['level'],
                                                                                                                              char_db.find_one({'_id': author.id})[
                                                                                                                                  'stats']['hp'])
    else:
        return "Defeated {}! Earned **{} EXP** ({} / {})".format(enemy, amount,
                                                                      char_db.find_one({'_id': author.id})[
                                                                          'exp'],
                                                                      char_db.find_one({'_id': author.id})[
                                                                          'max_exp']) + '\n\n' + "Leveled up to {}! Max HP increased to {}. Earned **1 SP**.".format(character['stats']['level'],
                                                                                                                                                    char_db.find_one({'_id': author.id})[
                                                                                                                                                        'stats']['hp'])

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
async def inventory(ctx, is_sender=True):
    author = ctx.author
    char_inv = char_db.find_one({'_id': author.id})['inventory']
    if is_sender:
        await send_message(ctx, "__**{}'s inventory**__\n\nGold: {}\nEquipment: {}\nFood: {}"
                       .format(author, char_inv['gold'], char_inv['equipment'], char_inv['food']))
    else:
        return "__**{}'s inventory**__\n\nGold: {}\nEquipment: {}\nFood: {}"\
            .format(author, char_inv['gold'], char_inv['equipment'], char_inv['food'])


"""Spawns a Monster during a combat encounter.

Generates a random Monster to spawn based on the location of the user. Each Monster has a different variation that 
changes their stats and item drops.
"""
async def spawn(ctx, is_sender=True):
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
        enemies[author.id] = monster
        if is_sender:
            await ctx.send(discord.Embed(description=monster.encounter() + '\n\n' + monster.stats()))
            await display_combat_ui(ctx)
        else:
            return str(monster.encounter() + '\n\n' + monster.stats())

    # elif location is "forest_2":


"""Creates a new character.

Only called when a new user is playing for the first time. Creates an instance of the Character class and initializes
all of the default values using a pre-defined template. Will send a message indicating the success of this operation.
"""
async def create(ctx, is_sender=True):
    author = ctx.author
    if char_db.find_one({'_id': author.id}) is None:
        Character(author.id, author)
        if is_sender:
            await send_message(ctx, "New character created! Welcome, " + str(ctx.author)[:-5] + "!")
        else:
            return "New character created! Welcome, " + str(ctx.author)[:-5] + "!"

    else:
        if is_sender:
            await send_message(ctx, "You've already created a character!")
        else:
            return "You've already created a character!"


"""Prints character stats.

Accesses the stats Object from the character database. Called by the .stats keyword in the text channel.
"""
@client.command()
async def stats(ctx, is_sender=True):
    author = ctx.author
    char_info = char_db.find_one({'_id': author.id})
    char_stats = char_info['stats']
    stats = "__**Displaying {}'s stats:**__ \nLevel {} ({} EXP / {} EXP) \n\u2764\uFE0F HP:  {} / {}\n\U0001F535 MP: {} / {} \n\N{flexed biceps} STR:  {} \n\N{adhesive bandage} VIT:   {}\n\U0001F3AF DEX: {} \n\N{scroll} INT:   {} \n\U0001F45F AGL: {}\n\N{sparkles} LUK:  {}" \
        .format(author, char_stats['level'], char_db.find_one({'_id': author.id})['exp'],
                char_db.find_one({'_id': author.id})['max_exp'],
                char_info['hp'], char_stats['hp'], char_info['mp'], char_stats['mp'],
                char_stats['strength'],
                char_stats['vitality'], char_stats['dexterity'], char_stats['intelligence'],
                char_stats['agility'],
                char_stats['luck'])
    if char_info['sp'] != 0:
        stats += '\n\n' + "You have {sp} SP available to allocate!".format(sp=char_info['sp'])
    if is_sender:
        await send_message(ctx, stats)
    else:
        return stats


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
async def tutorial(ctx, is_sender=True):
    if is_sender:
        await ctx.send(discord.Embed(description="__**Getting Started**__\n" +
                       ".create: Creates a new character\n" +
                       ".stats: View your character stats\n" +
                       ".inv: View your inventory \n" +
                       ".statshelp: Character stats tutorial" +
                       "\n\n__**Gameplay**__\n" +
                       ".w: Walk forward\n" +
                       ".a: Attack opponent (only available during combat)\n",
                ))
    else:
        return ("__**Getting Started**__\n" +
        ".create: Creates a new character\n" +
        ".stats: View your character stats\n" +
        ".inv: View your inventory \n" +
        ".statshelp: Character stats tutorial" +
        "\n\n__**Gameplay**__\n" +
        ".w: Walk forward\n" +\
        ".a: Attack opponent (only available during combat)\n")


"""Displays bot statistics.

Includes number of total players and the number of servers the bot is in.
"""
@client.command()
async def bot_info(ctx, is_sender=True):
    if is_sender:
        await send_message(ctx, "There are {players} players across {servers} servers!".format(
        players=char_db.count_documents({}), servers=str(len(client.guilds))))
    else:
        return "There are {players} players across {servers} servers!".format(
        players=char_db.count_documents({}), servers=str(len(client.guilds)))


"""Displays leaderboard rankings for a specific statistic.

Args:
    statistic (str): the statistic to display the top 20 players for.
"""
@client.command()
async def leaderboard(ctx, statistic):
    await send_message("__**{} Leaderboard**__".format(statistic.capitalize()))
    total_players = char_db.count_documents({})
    max_lb = total_players if total_players < 20 else 20
    list = []
    if statistic == 'level':
        top_players = char_db.find().sort('stats.level', -1)
        for x in range(0, max_lb):
             await ctx.send(discord.Embed(description=str((x + 1)) + ". " + top_players[x]['discord_name'] + " (Lv. {})".format(
                top_players[x]['stats']['level'])))


"""Edits the embedded message.

Changes the embedded message to display the updated content based on the user button click.
"""
async def update_ui(ctx, message_content):
    embedVar = discord.Embed(description=message_content)
    await ctx.edit_message(embed=embedVar)

    # Return type used when user presses a button. Returns an embedded variable based on the current command.
    #
    # await channel.send('{}'.format(message_content))

@client.command()
async def test(ctx):
    embedVar = discord.Embed(description="this is the desc")
    await ctx.send(embed=embedVar, components=UIButton(label="Walk", custom_id='walk', style=discord.ButtonStyle.green, ctx=ctx))

client.run(bot_token)