# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import requests
import discord
from discord import *
from discord.ext import commands

description = """
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
"""

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description=description,
    intents=intents,
)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(name='ping', )
async def hello(ctx):
    await ctx.respond("pong")

@bot.slash_command(name='getcat', description="Get a random cat image!", )
async def getcat(ctx):
    raw = requests.get('https://api.thecatapi.com/v1/images/search')
    cat_resp = raw.json()
    if cat_resp[0].get('url'):
        resp = cat_resp[0].get('url')
    else:
        resp = "I was unable to catch the cat for a picture... Try again later"
    await ctx.respond(resp)

@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return
    
    if (message.type in (MessageType.default, MessageType.reply)):
        await doReactions(message)


async def doReactions(message: Message):

    if ('vote' in message.content.lower()):
        await message.reply('I love democracy')
        return
    if ('linux' in message.content.lower() and 'gnu' not in message.content.lower()):
        await message.reply('Did you mean GNU Linux?')



with open('auth_token.txt') as f:
    auth_token = f.readline()

bot.run(auth_token)
