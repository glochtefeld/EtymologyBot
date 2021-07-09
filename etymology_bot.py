import discord
from discord.ext import commands
import logging
import requests
import re
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from random import choice

config = dotenv_values(".env")
CHANNEL_FOR_SERVER = dict()
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='!@')

def get_random_greeting():
    with open(config["GREETINGS_PATH"],'r') as infile:
        greetings = infile.readlines()
        return choice(greetings)

@bot.event
async def on_ready():
    logging.info('Logged in as {0.user}'.format(bot))

@bot.command()
async def DEBUG(ctx):
    if str(ctx.author.id) != config["DEVELOPER_ID"]:
        print('nope.')
        print(ctx.author.id)
        return
    await ctx.send(repr(CHANNEL_FOR_SERVER))
    

@bot.command()
async def etym(ctx, word: str):
    url = "http://www.etymonline.com/word/" + word
    logging.info(f"Looking up {word}")
    page = requests.get(url)
    if page.status_code != 200:
        logging.error(f"Unknown word: {word}")
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    i = 1
    msg = "\u200B"
    msg += get_random_greeting()
    definition = paragraphs[0]
    msg += definition.get_text()
    while True:
        if not paragraphs[i].has_attr('title'):
            break
        msg += "\n\n" + paragraphs[i].get_text() + paragraphs[i+1].get_text()
        i += 2
    msg += f"\n<{url}>"

    if CHANNEL_FOR_SERVER.get(ctx.guild.id) == None:
        await ctx.send(msg)
    else:
        await CHANNEL_FOR_SERVER[ctx.guild.id].send(msg)

@bot.command(name='etym_bot_channel')
async def set_channel(ctx, msg_body: str):
    global CHANNEL_FOR_SERVER
    logging.info(f'Message body: {msg_body}')
    desired_channel = re.search("<#\d+>",msg_body)
    if desired_channel:
        # slicing prevents characters like <,#,> from being parsed
        channel = int(desired_channel.group()[2:-1])
        print(f"CHANNEL: {channel}")
        CHANNEL_FOR_SERVER[ctx.guild.id] = bot.get_channel(channel)
        await CHANNEL_FOR_SERVER[ctx.guild.id].send("All messages from this bot will arrive here now.")
    else:
        await ctx.reply("Please specify a channel to send messages to.")




bot.run(config["DISCORD_TOKEN"])
