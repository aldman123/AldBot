# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import requests

import discord
from discord.ext import commands

import json

from reply import *

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
        await doReply(message)

async def doReply(message: Message):
    for trigger in triggers:
        if (trigger.isTriggered(message.content)):
            if (trigger is TextReplyTrigger):
                await message.reply(trigger.reply)
            elif (trigger is ImageReplyTrigger):
                await message.reply(trigger.imageUrl)
            else:
                print('''ReplyTrigger {} wasn't a supported trigger''', trigger)
            return

def parseReplyConfig(reply: dict) -> ReplyTrigger:
    if (reply['type'] == 'text'):
        return TextReplyTrigger(
            triggers=reply['triggers'],
            reply=reply['reply'],
            exceptTriggers=reply.get('exceptTriggers', [])
        )
    elif (reply['type'] == 'image'):
        return ImageReplyTrigger(
            triggers=reply['triggers'],
            imageURL=reply['imageUrl'],
            exceptTriggers=reply.get('exceptTriggers', [])
        )

with open('auth_token.txt') as f:
    auth_token = f.readline()

with open('replies.json') as f:
    replies = json.load(f)

reply: dict

triggers: list[ReplyTrigger] = map(parseReplyConfig, replies)

bot.run(auth_token)
