import discord
from discord.ext import commands
import logging
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

config = dotenv_values(".env")

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='!@')
@bot.event
async def on_ready():
    logging.info('Logged in as {0.user}'.format(bot))

@bot.command()
async def etym(ctx, word: str):
    url = "http://www.etymonline.com/word/" + word
    page = requests.get(url)
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    i = 1
    msg = "\u200B"
    definition = paragraphs[0]
    msg += definition.get_text()
    while True:
        if not paragraphs[i].has_attr('title'):
            break
        msg += "\n\n" + paragraphs[i].get_text() + paragraphs[i+1].get_text()
        i += 2
    msg += f"\n<{url}>"

    await ctx.send(msg)

bot.run(config["DISCORD_TOKEN"])
