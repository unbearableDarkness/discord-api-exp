import requests
import datetime
import discord
import aiohttp
import random
import json
import time
import os
import csv

from discord.ext import commands

# Subscribe to the privileged members intent.
intents = discord.Intents.default()
intents.members = True
command_prefix_symbol = '$'
bot = commands.Bot(command_prefix=command_prefix_symbol, intents=intents)
my_user_id = 0
my_bot_id = 0
private_channel_id = 0

active_boards = [0, 1, 6, 29, 48, 52, 61, 70]
boards = ["a", "b", "c", "d", "e", "f", "g", "gif", "h", "hr", "k", "m", "o", "p", "r", "s", "t", "u", "v", "vg", "vm",
          "vmg", "vr", "vrpg", "vst", "w", "wg", "i", "ic", "r9k", "s4s", "vip", "qa", "cm", "hm", "lgbt", "y", "3",
          "aco", "adv", "an", "bant", "biz", "cgl", "ck", "co", "diy", "fa", "fit", "gd", "hc", "his", "int", "jp",
          "lit", "mlp", "mu", "n", "news", "out", "po", "pol", "pw", "qst", "sci", "soc", "sp", "tg", "toy", "trv",
          "tv", "vp", "vt", "wsg", "wsr", "x", "xs"]

eight_ball_responses = [
    "It is certain.",
    "It is decidedly so.",
    "Most likely.",
    "The outlook is good.",
    "Signs point to yes.",
    "Without a doubt.",
    "Yes.",
    "Yes, definitely.",
    "You may rely on it.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
    "Absolutely not."
]

greetings = [
    "Hello",
    "Good morning",
    "Good afternoon",
    "Good evening",
    "Morning",
    "G'day",
    "Howdy",
    "Hi",
    "Hey",
    "Yo",
]


def trim_string(string, delimiter, part):
    # $command 'delimiter' message
    return string.partition(delimiter)[part]


def trim_string_slice(string, delimiter, part, choice):
    # $command 'delimiter' message
    if choice == 'r':
        return string.partition(delimiter)[part:]
    elif choice == 'l':
        return string.partition(delimiter)[:part]


def read_token():
    with open("token.txt", 'r') as f:
        lines = f.readlines()
        return lines[0].strip()


def get_inspirational_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    # get the quote out of the response
    rnd_quote = "\"" + json_data[0]['q'] + "\"" + " - " + json_data[0]['a']
    return rnd_quote


def get_random_sentence_from_file(filename, mode):
    with open(filename, mode, encoding="utf-8") as f:
        quotes = [[]]
        temp = ''
        for line in f:
            if line.strip() == '':
                quotes.append(temp)
                temp = ''
            else:
                temp += line

    # remove empty elements from our list
    quotes = list(filter(None, quotes))
    r = random.choice(quotes)
    return str(r)


def get_last_4chan_id():
    idx = random.choice(active_boards)
    url = "https://a.4cdn.org/{0}/catalog.json".format(boards[idx])
    response = requests.get(url)
    # json -> dictionary
    # get the json object
    data = json.loads(response.text)

    threads_info = []
    replies_info = []

    # the data contains page data, and each data has some threads inside of it
    # each thread has a unique id and a date
    # each thread has a list of last_replies
    for page_data in data:
        for thread in page_data["threads"]:
            if "sticky" not in thread:
                threads_info.append((thread["no"], thread["now"]))
                if thread["replies"] > 0:
                    for reply in thread["last_replies"]:
                        replies_info.append((reply["no"], reply["now"]))

    # sort the posts by date by considering only numbers
    [r.sort(key=lambda x: [char for char in x[1] if char.isdigit()]) for r in [threads_info, replies_info]]

    # Get only the digits from the dates and compare them
    # - then return the id associated to that date
    last_thread_date = int(''.join(char for char in threads_info[-1][1] if char.isdigit()))
    last_post_date = int(''.join(char for char in replies_info[-1][1] if char.isdigit()))

    if (max(last_thread_date, last_post_date)) == last_thread_date:
        return threads_info[-1][0]
    else:
        return replies_info[-1][0]


# Events
@bot.event
async def on_ready():
    channel = bot.get_channel(private_channel_id)
    await channel.send("I am now online. It is currently {0}".format(datetime.datetime.now().strftime("%H:%M")))

    # crunch some information
    print('We have logged in as {0.user}. It is currently {1}'.format(bot, datetime.datetime.now().time()))
    for emoji in bot.emojis:
        print("Name:", emoji.name + ",", "ID:", emoji.id)
    for user in bot.users:
        print("Name:", user.name + ",", "ID:", user.id)


# Overriding the default provided on_message forbids any extra commands from running.
# To fix this, add a bot.process_commands(message) line at the end of your on_message.
@bot.event
async def on_message(message):
    # do not react to our messages
    if message.author == bot.user:
        return
    for greeting in greetings:
        if message.content.lower() == greeting.lower():
            await message.channel.send("{0}!".format(trim_string(message.content.title(), ' ', 0)))
    await bot.process_commands(message)


# Commands
# This command can be used to check latency
@bot.command(aliases=["Ping"], description="A simple command that checks latency. Usage: <$ping>")
async def ping(ctx):
    await ctx.send(f"Pong! - {round(bot.latency * 1000)}ms")


@bot.command(aliases=["8ball"], description="Asks 8ball a question. Usage: <$8ball> <question>")
async def _8ball(ctx):
    await ctx.send(f"{random.choice(eight_ball_responses)}")


@bot.command(aliases=["Roll"], description="Returns the id of the most recent 4chan post from the most active boards. Usage: <$roll>")
async def roll(ctx):
    await ctx.send(get_last_4chan_id())


@bot.command(aliases=["Quote"], description="Returns a random quote from the zenquotes.io website. Usage: <$quote>")
async def quote(ctx):
    msg = discord.Embed(description=get_inspirational_quote(), color=discord.Colour.purple())
    await ctx.send(embed=msg)


@bot.command(aliases=["Psycho"], description="Returns a random quote from the movie American Psycho. Usage: <$psycho>")
async def psycho(ctx):
    msg = discord.Embed(description=get_random_sentence_from_file("american_psycho.txt", "r"),
                        color=discord.Colour.purple())
    await ctx.send(embed=msg)


@bot.command(aliases=["flip"], description="A simple coin flip. Usage: <$flip> <tails | head>")
async def coin(ctx):
    msg = trim_string(ctx.message.content.lower(), ' ', 2)
    r = ["tails", "heads"]
    if msg not in r:
        await ctx.send("That's not how you guess.")
        return
    else:
        correct_answer = random.choice(r)
        if msg == correct_answer:
            await ctx.send("Correct!")
            return
        else:
            await ctx.send("Wrong!")
            return


@bot.command(aliases=["quit"])
async def disconnect(ctx):
    if ctx.message.author.id == my_user_id:
        try:
            await ctx.send("I am now offline. Bye!")
            await discord.ext.commands.Bot.logout(bot)
            return
        except RuntimeError:
            exit(-1)
    else:
        await ctx.send("This command can only be called be the bot's owner.")
        return


# noinspection PyUnreachableCode
@bot.command()
async def history(ctx):
    return
    if ctx.message.author.id == my_user_id:
        await ctx.send("Started fetching messages info...")
        t1 = time.time()
        messages_limit = 10000000
        buffer_limit = 2500
        i = 0
        msg_count = 0
        user_csv_data = "user_csv_data.csv"
        user_csv_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_histories", user_csv_data)
        with open(user_csv_data_path, "a", encoding="utf-8") as fc:
            writer = csv.writer(fc, delimiter=',')
            csv_list = []
            async for message in ctx.channel.history(limit=messages_limit):
                if message.author.bot is False:
                    msg_count += 1
                    csv_list.append([str(message.author.id), message.content])
                    i += 1
                    if i >= buffer_limit:
                        writer.writerows(csv_list)
                        csv_list = []
                        i = 0
                else:
                    pass
            t2 = time.time()
            await ctx.send("Time taken: {0} seconds. Fetched {1} message/s.".format(round(t2 - t1), msg_count))
            print(t2 - t1)
            return
    else:
        await ctx.send("This command can only be called be the bot's owner.")
        return


@bot.command()
async def test_time(ctx):
    if ctx.message.author.id == my_user_id:
        channel = bot.get_channel(private_channel_id)
        t1 = time.time()
        async for _ in ctx.channel.history(limit=1000000):
            pass
        t2 = time.time()
        await ctx.send("Time taken: {0}".format(t2-t1))
        print(t2 - t1)
        return
    else:
        return


@bot.command(aliases=["insulta"], description="Allows you to insult another user. You can specify a user or type 'someone' to insult a random user. Usage: <$insult> <@id>")
async def insult(ctx):
    # here we fetch the user id of the user to insult and the insult
    random_insult = get_random_sentence_from_file("insults.txt", "r")
    msg = trim_string(ctx.message.content, ' ', 2)
    if len(msg) == 0:
        await ctx.send("Please provide a user.")
        return
    if msg == "someone" or msg == "qualcuno":
        random_member = random.choice(ctx.channel.members)
        # check if the random selected member is the author of the message or a bot, or myself
        while random_member == ctx.message.author or random_member.bot is True or random_member.id == my_user_id:
            random_member = random.choice(ctx.channel.members)
        await ctx.send("<@{0}> {1}".format(random_member.id, random_insult))
        return
    else:
        try:
            # we don't let someone insult the bot
            if ctx.message.mentions[0].id == my_bot_id:
                await ctx.send("<@{0}> Nope, sorry, I won't insult myself.".format(ctx.message.author.id))
                return
            elif ctx.message.mentions[0].id == my_user_id:
                await ctx.send("<@{0}> Nice try.".format(ctx.message.author.id))
                return
            async for member in ctx.guild.fetch_members():
                if member.id == ctx.message.mentions[0].id:
                    await ctx.send("<@{0}> {1}".format(member.id, random_insult))
                    return
            else:
                await ctx.send("Please provide a valid user.")
        except (discord.ext.commands.CommandInvokeError, IndexError):
            await ctx.send("Please provide a valid user.")


# My discord token
TOKEN = read_token()
bot.run(TOKEN)

