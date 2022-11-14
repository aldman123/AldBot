# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import discord
from discord import *
from discord.ext import commands

import requests
import aiocron
from datetime import datetime, timedelta

from role_picker import PronounView
import json

from reply import *
from dotenv import load_dotenv
import os 

load_dotenv()
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
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return
    
    if (message.content.strip().lower() == 'nice'):
        await nice(message)
    
    if (message.type in (MessageType.default, MessageType.reply)):
        await doReply(message)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(os.getenv('INTRO_CHANNEL')))
    embed=discord.Embed(title="Welcome!",description=f"Hello {member.mention}! Please pick your roles by running the command `/pickrole`")
    await channel.send(embed=embed)

@aiocron.crontab('0 12 * * 1,3,5')
async def xkcd_commic():
    channel = bot.get_channel(int(os.getenv('MATH_CHANNEL')))
    raw = requests.get('https://xkcd.com/info.0.json')

    resp_json = raw.json()
    if resp_json.get('img') and resp_json.get('safe_title'):
        resp = resp_json.get('safe_title') + " \n" + resp_json.get('img')
    else:
        resp = "I was unable to catch the comic... Try again later"
    await channel.send(resp)

@aiocron.crontab('0 8 * * 3')
async def xkcd_commic():
    channel = bot.get_channel(int(os.getenv('GAMES_CHANNEL')))
    await channel.send("https://youtu.be/B_qnI1WrlnU")

@bot.slash_command(name='ping', )
async def ping(ctx):
    await ctx.respond("pong")

@bot.slash_command(name='pickrole', )
async def pickrole(ctx):
    await ctx.send_response("What are your pronouns? If you want to remove a pronoun role, click on one you already have. If you prefer not to say or are happy with your pronoun roles press 'Next'", view=PronounView(), ephemeral=True)

@bot.slash_command(name='getcat', description="Get a random cat image!", )
async def getcat(ctx):
    raw = requests.get('https://api.thecatapi.com/v1/images/search')
    cat_resp = raw.json()
    if cat_resp[0].get('url'):
        resp = cat_resp[0].get('url')
    else:
        resp = "I was unable to catch the cat for a picture... Try again later"
    await ctx.respond(resp)

@bot.slash_command(name='get-aldbucks', description="Returns a user's AldBuck balance")
async def printUsersAldbucks(ctx: ApplicationContext):
    author = ctx.author.id
    await ctx.respond(f'<@{author}> currently has {getAldBucks(author)} AldBucks')

'''
    Checks a message for any trigger words, and if triggered it replies accordingly
'''
async def doReply(message: Message):
    for trigger in triggers:
        if (trigger.isTriggered(message.content)):
            await trigger.doReply(message)

'''
    Parses json into ReplyTrigger subclasses
'''
def parseReplyConfig(reply: dict) -> ReplyTrigger:
    if (reply['type'] == 'text'):
        return TextReplyTrigger(
            triggers=tuple(reply['triggers']),
            reply=reply['reply'],
            exceptTriggers=reply.get('exceptTriggers', ())
        )
    elif (reply['type'] == 'image'):
        return ImageReplyTrigger(
            triggers=tuple(reply['triggers']),
            imageURL=reply['imageUrl'],
            exceptTriggers=reply.get('exceptTriggers', ())
        )

'''
    Gives an AldBuck to the previous message's owner
'''
async def nice(message: Message):

    channel = message.channel
    messages = await channel.history(limit=100).flatten()
    messages = sorted(messages, key=lambda m: m.created_at)

    targetMessage = await getTargetMessage(messages)

    author = targetMessage.author.id

    if message.author.id == author:
        addAldBuck(author, -1)
        await channel.send(f"<@{author}> You can't vote on yourself! You lose an AldBuck and now have {getAldBucks(author)}")
        return

    addAldBuck(author, 1)
    await channel.send(f'Thank you for voting on <@{author}>.\nThey now have {getAldBucks(author)} AldBucks')

'''
    Get the most recent message that's not 'nice' or an AldBot message
'''
async def getTargetMessage(messages: list[Message]) -> Message:
    targetMessage = messages.pop()
    print(f'Is target message {targetMessage.content}?')

    if targetMessage.author.id == bot.user.id or targetMessage.content.strip().lower() == 'nice':
        return await getTargetMessage(messages)
    else:
        return targetMessage

'''
    Add a quantity of AldBucks and then save the file
'''
def addAldBuck(userId: int, quantity: int):
    if userId not in aldbucks:
        aldbucks[userId] = 0

    aldbucks[userId] += quantity

    with open('aldbucks.json', 'w') as f:
        json.dump(aldbucks, f)

'''
    Get's a user's AldBucks (defaults to zero)
'''
def getAldBucks(userId: int):
    return aldbucks.get(userId, 0)


with open('auth_token.txt') as f:
    auth_token = f.readline()

with open('replies.json') as f:
    replies = json.load(f)

aldbucks: dict[str, int] = {}
with open('aldbucks.json') as f:
    aldbucks = json.load(f)

triggers = list(map(parseReplyConfig, replies))

bot.run(auth_token)
