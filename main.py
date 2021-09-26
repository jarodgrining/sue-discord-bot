import os
import discord
import random
from dotenv import load_dotenv
from asyncio import sleep
from poll import *

load_dotenv() # testing only - does nothing when actually deployed

TOKEN = os.environ.get("DISCORD_TOKEN")

client = discord.Client()

messages = {}
polls = {}
dad_jokes = []

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    await load_messages()
    await load_dad_jokes()
    print("Loaded files")

async def load_messages():
    f = open("messages.txt", "r")
    for msg in f.read().split("\n<break>\n"):
        msg_list = msg.split("\n", 1)
        messages[msg_list[0]] = msg_list[1]
    f.close()

async def load_dad_jokes():
    f = open("dadjokes.txt", "r")
    for joke in f:
        dad_jokes.append(joke)
    f.close()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("$ue"):
        return

    output = await parse_command(message.content.split(" "), message.channel, message.author)
    await message.channel.send(output)

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    for poll_name in polls:
        if polls[poll_name].message == reaction.message:
            if reaction.emoji in polls[poll_name].options:
                await handle_poll_vote(reaction, user, poll_name)
            break

async def parse_command(command, channel, user):
    if len(command) < 2:
        return messages["empty command"]

    action = command[1]

    if action == "roll":
        if len(command) < 3:
            return messages["usage roll"]
        return await roll_dice(command[2:])
    elif action == "dadjoke":
        return await tell_dad_joke()
    elif action == "poll":
        if len(command) < 3:
            return messages["usage poll"]
        return await manage_polls(command[2:], channel, user)
    elif action == "gblogbddyptstsasgts" and channel.permissions_for(user).manage_messages:
        polls = {}
        return "Polls successfully purged."
    elif action == "help":
        return messages["help"]
    else:
        return messages["bad command"]

async def roll_dice(dice):
    rolls = []
    hide_ind = False
    total = 0

    if dice[0] == "sum":
        if len(dice) < 2:
            return messages["usage roll sum"]
        dice = dice[1:]
        hide_ind = True

    for die in dice:
        ind = die.find("d")

        if ind == -1:
            ind = die.find("D")

        if ind == -1 or len(die) < 2 or ind == len(die)-1:
            return "Invalid dice entered."

        type_string = die[ind+1:]
        if not type_string.isdigit():
            return "Invalid dice entered."

        quantity = 1
        if ind > 0:
            quantity_string = die[:ind]
            if not quantity_string.isdigit():
                return "Invalid quantity of dice entered."
            quantity = int(quantity_string)

        type = int(type_string)
        if quantity < 1:
            return "Invalid quantity of dice entered."
        elif type < 1:
            return "Invalid type of dice entered."

        for _ in range(quantity):
            roll = random.randint(1, type)
            total += roll
            rolls.append(roll)

    output = ""
    if not hide_ind:
        for roll in rolls:
            output += str(roll) + " "

    if " " in output[:-1] or hide_ind:
        if not hide_ind:
            output += "\n"
        output += "Total: " + str(total)

    if len(output) > 1990:
        output = "Too many rolls to display individual results. Total: " + str(total)

    return output

async def tell_dad_joke():
    return random.choice(dad_jokes)

async def manage_polls(commands, channel, user):
    if commands[0] == "make":
        if len(commands) < 5:
            return messages["usage poll make"]
        else:
            return await make_poll(commands[1:], channel, user)
    elif commands[0] == "purge" and channel.permissions_for(user).manage_messages:
        return messages["poll purge"]
    elif commands[0] == "list":
        return await list_polls()

    if len(commands) > 1:
        if commands[1] not in polls:
            return messages["poll name missing"]
        elif user != polls[commands[1]].owner and not channel.permissions_for(user).manage_messages:
            return messages["poll permission"]

    if commands[0] == "call":
        if len(commands) < 2:
            return messages["usage poll call"]
        else:
            return await call_poll(commands[1])
    elif commands[0] == "delete":
        if len(commands) < 2:
            return messages["usage poll delete"]
        else:
            return await delete_poll(commands[1])

    if polls[commands[1]].disabled:
        return "Cannot modify a called poll."

    if commands[0] == "add":
        if len(commands) < 4:
            return messages["usage poll add"]
        else:
            return await add_poll_option(commands[1:])
    elif commands[0] == "remove":
        if len(commands) < 3:
            return messages["usage poll remove"]
        else:
            return await remove_poll_option(commands[1:])
    elif commands[0] == "changeq":
        if len(commands) < 3:
            return messages["usage poll changeq"]
        else:
            return await change_poll_question(commands[1:])
    elif commands[0] == "changeop":
        if len(commands) < 4:
            return messages["usage poll changeop"]
        else:
            return await change_poll_option(commands[1:])

    return messages["usage poll"]

async def make_poll(commands, origin_channel, user):
    name = commands.pop(0)
    type = commands.pop(0)
    votes = 0

    if type == "exclusive":
        try:
            votes = int(commands.pop(0))
        except:
            return "Bad number of votes given."
    elif type != "binary" and type != "open":
        return "Type must be open, exclusive, or binary."

    channel_name = commands.pop(0)
    question = " ".join(commands)

    for channel in origin_channel.guild.text_channels:
        if (channel.name == channel_name):
            if not channel.permissions_for(user).send_messages:
                return "You don't have the permission to send messages in the target channel."
            temp_message = await channel.send("Poll:\n" + question)
            message_id = temp_message.id
            await sleep(1) # trust me this is important
            cached_message = discord.utils.get(client.cached_messages, id=message_id)
            polls[name] = Poll(cached_message, question, type, votes, user)
            if type == "binary":
                await polls[name].init_binary()
            return "Poll successfully created."

    return "Channel name not found."

async def add_poll_option(commands):
    name = commands.pop(0)

    if polls[name].type == "binary":
        return "Cannot add options to a binary poll."

    reaction_code = commands.pop(0)
    option = " ".join(commands)
    return await polls[name].add_option(reaction_code, option)

async def remove_poll_option(commands):
    name = commands.pop(0)

    if polls[name].type == "binary":
        return "Cannot remove options from a binary poll."

    reaction_code = commands.pop(0)
    return await polls[name].remove_option(reaction_code, client.user)

async def change_poll_question(commands):
    name = commands.pop(0)
    new_question = " ".join(commands)
    return await polls[name].set_question(new_question)

async def change_poll_option(commands):
    name = commands.pop(0)
    reaction_code = commands.pop(0)
    new_option = " ".join(commands)
    return await polls[name].change_option(reaction_code, new_option)

async def call_poll(name):
    return await polls[name].call()

async def delete_poll(name):
    del polls[name]
    return "Poll successfully deleted."

async def list_polls():
    if len(polls) == 0:
        return "No polls currently exist."

    output = ""
    for poll in polls:
        output += "\n" + poll + ": " + polls[poll].question + " @ " + polls[poll].message.channel.name + " is "
        if polls[poll].disabled:
            output += "called"
        else:
            output += "active"

    return output[1:]

async def handle_poll_vote(reaction, user, name):
    if polls[name].type != "open":
        votes_made = []
        for react in reaction.message.reactions:
            react_users = await react.users().flatten()
            if user in react_users:
                votes_made.append(react)

        if len(votes_made) > polls[name].votes:
            for react in votes_made:
                await polls[name].message.remove_reaction(reaction, user)

client.run(TOKEN)
