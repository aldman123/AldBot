# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import discord
from discord import *
from discord.ext import commands

import requests
import aiocron
from datetime import datetime, timedelta, date

from role_picker import PronounView
import json

from reply import *
from dotenv import load_dotenv
import os

ALDBUCKS_FILE = 'aldbucks.json'
DAILY_RESOURCE_FILE = 'daily-resources.json'
REPLIES_FILE = 'replies.json'
AUTH_TOKEN_FILE = 'auth_token.txt'

VOTES_PER_DAY = 3
NEW_DAY_NEW_MEME = True
VOTE_TRIGGERS = ['nice', 'good bot', 'good robot']
NEGATIVE_VOTE_TRIGGERS = ['yikes', 'bad bot', 'bad robot', 'i hate you']

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
    
    if (message.content.strip().lower() in VOTE_TRIGGERS):
        await vote(message, True)
    
    if (message.content.strip().lower() in NEGATIVE_VOTE_TRIGGERS):
        await vote(message, False)
    
    if (message.type in (MessageType.default, MessageType.reply)):
        await doReply(message)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(os.getenv('INTRO_CHANNEL')))
    embed=discord.Embed(title="Welcome!",description=f"Hello {member.mention}! Please pick your roles by running the command `/pickrole`")
    await channel.send(embed=embed)

'''
Every 2 hours on monday, wednesday, and friday check if there is a new xkcd comic matching todays date, if so post it
'''
@aiocron.crontab('0 */2 * * 1,3,5')
async def xkcd_commic():
    global NEW_DAY_NEW_MEME
    channel = bot.get_channel(int(os.getenv('MATH_CHANNEL')))
    raw = requests.get('https://xkcd.com/info.0.json')
    resp_json = raw.json()
    
    if NEW_DAY_NEW_MEME and int(resp_json.get("day")) == date.today().day:
        if resp_json.get('img') and resp_json.get('safe_title'):
            resp = resp_json.get('safe_title') + " \n" + resp_json.get('img')
            NEW_DAY_NEW_MEME = False
        else:
            resp = "I was unable to catch the comic... Try again later"
        await channel.send(resp)

'''
Set NEW_DAY_NEW_MEME every day at midnight
'''
@aiocron.crontab('0 0 * * *')
async def new_day_new_meme():
    global NEW_DAY_NEW_MEME
    NEW_DAY_NEW_MEME = True

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


'''
    AldBucks Commands
'''
aldbuckCommands = SlashCommandGroup(name='aldbucks', description='The hip new crypto currency AldBucks')

@aldbuckCommands.command(name='get', description="Returns a user's AldBuck balance")
async def printUsersAldbucks(ctx: ApplicationContext, user: discord.User=None):
    if user is None:
        user = ctx.user
    author = user.id
    await ctx.respond(f'<@{author}> currently has {getAldBucks(author)} AldBucks')

@aldbuckCommands.command(name='send', description="Send AldBucks to another user")
async def sendAldbuck(ctx: ApplicationContext, user: discord.User, quantity: int):
    sender = ctx.author.id
    reciever = user.id

    if sender == reciever:
        await ctx.respond(f"<@{sender}> You can't send yourself AldBucks!")
        return
    
    senderBalance = getAldBucks(sender)
    if quantity > senderBalance:
        await ctx.respond(f"<@{sender}> You can't send {quantity} AldBucks to <@{reciever}>!\nYou only have {senderBalance} AldBucks")
        return
    
    addAldBuck(sender, -1 * quantity)
    addAldBuck(reciever, quantity)
    await ctx.respond(f"<@{reciever}> just got {quantity} more AldBucks!\n<@{sender}> has {getAldBucks(sender)} remaining.")
    
bot.add_application_command(aldbuckCommands)

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
    Either adds or removes an AldBuck from user, and consumes a daily vote
'''
async def vote(message: Message, isPositive: bool):

    channel = message.channel
    messages = await channel.history(limit=100).flatten()
    messages = sorted(messages, key=lambda m: m.created_at)

    targetMessage = await getTargetMessage(messages)

    author = targetMessage.author.id

    if message.author.id == author:
        addAldBuck(author, -1)
        await channel.send(f"<@{author}> You can't vote on yourself! You lose an AldBuck and now have {getAldBucks(author)}")
        return
    
    voter = message.author.id
    remainingVotes = getVotes(voter)
    if remainingVotes < 1:
        await channel.send(f"<@{voter}>You've already used {VOTES_PER_DAY} votes today!")
        return

    useVote(voter)
    if isPositive:
        addAldBuck(author, 1)
    else:
        addAldBuck(author, -1)
    await channel.send(f'Thank you for voting on <@{author}>.\nThey now have {getAldBucks(author)} AldBucks')

'''
    Get the most recent message that's not in VOTE_TRIGGERS or an AldBot message
'''
async def getTargetMessage(messages: list[Message]) -> Message:
    targetMessage = messages.pop()
    content = targetMessage.content.strip().lower()
    if targetMessage.author.id == bot.user.id or content in VOTE_TRIGGERS or content in NEGATIVE_VOTE_TRIGGERS:
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

    with open(ALDBUCKS_FILE, 'w') as f:
        json.dump(aldbucks, f)

'''
    Get's a user's AldBucks (defaults to zero)
'''
def getAldBucks(userId: int):
    return aldbucks.get(userId, 0)

'''
    Get's a user's daily vote balance
'''
def getVotes(userId: int) -> int:
    if dailyUses['day'] == getToday():
        votes: dict = dailyUses['votes']
        return votes.get(userId, VOTES_PER_DAY)
    else:
        resetDailyUses()
        return VOTES_PER_DAY

'''
    Reduces a user's votes by one
'''
def useVote(userId: int):
    currentVotes = getVotes(userId)
    dailyUses['votes'][userId] = currentVotes - 1
    saveDailyUses()

'''
    Saves the daily uses to the filesystem
'''
def saveDailyUses():
    with open(DAILY_RESOURCE_FILE, 'w') as f:
        json.dump(dailyUses, f)

'''
    Resets everyone's daily resources
'''
def resetDailyUses():
    dailyUses = {'day': getToday(), 'votes': {}}
    saveDailyUses()


def getToday() -> str:
    return str(datetime.today().date())



with open(AUTH_TOKEN_FILE, 'r') as f:
    auth_token = f.readline()

with open(REPLIES_FILE, 'r') as f:
    replies = json.load(f)

aldbucks: dict[str, int] = {}
try:
    with open(ALDBUCKS_FILE) as f:
        aldbucks = json.load(f)
except:
    aldbucks = {}
    with open(ALDBUCKS_FILE, 'a') as f:
        json.dump(aldbucks, f)

dailyUses: dict = {}
try:
    with open(DAILY_RESOURCE_FILE, 'r') as f:
        dailyUses = json.load(f)
except:
    dailyUses = {'day': getToday(), 'votes': {}}
    with open(DAILY_RESOURCE_FILE, 'a') as f:
        json.dump(dailyUses, f, default=str)
triggers = list(map(parseReplyConfig, replies))

bot.run(auth_token)
