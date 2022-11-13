# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import requests, discord, json

from discord import *
from discord.ext import commands
from role_picker import PronounView
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

@bot.slash_command(name='ping', description="Retrieve bot latency.", )
async def hello(ctx):
    await ctx.respond(f"pong, {bot.latency * 1000:.1f}ms latency")

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

@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return
    
    if (message.type in (MessageType.default, MessageType.reply)):
        await doReply(message)

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

auth_token = open('auth_token.txt','r').readline()
replies = json.load(open('replies.json','r'))

triggers = list(map(parseReplyConfig, replies))

bot.run(auth_token)
