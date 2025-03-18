import json
import os

import aiocron
import discord
import requests
import xkcd
from discord import Message, MessageType
from discord.ext import commands
from dotenv import load_dotenv

from reply import ImageReplyTrigger, ReplyTrigger, TextReplyTrigger

REPLIES_FILE = "replies.json"
AUTH_TOKEN_FILE = "auth_token.txt"

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    description="AldBot is aldmost aldsome",
    intents=intents,
)


@bot.event
async def on_ready():
    await post_xkcd_comic()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return

    if message.type in (MessageType.default, MessageType.reply):
        await doReply(message)


LAST_POSTED_XKCD = -1


@aiocron.crontab("0 */2 * * 1,3,5")
async def hourly_cron():
    post_xkcd_comic()


async def post_xkcd_comic():
    channel = bot.get_channel(int(os.getenv("MATH_CHANNEL")))

    last_message = await channel.history().find(lambda m: m.author.id == bot.user.id)

    comic = xkcd.getLatestComic()
    new_post = f"# [Lungfish]({comic.getImageLink()})\n||{comic.getAltText()}||"

    if new_post != last_message.content:
        await channel.send(content=new_post)


@aiocron.crontab("0 0 * * *")
async def new_day_new_meme():
    """
    Set NEW_DAY_NEW_MEME every day at midnight
    """
    global NEW_DAY_NEW_MEME
    NEW_DAY_NEW_MEME = True


@bot.slash_command(
    name="ping",
)
async def ping(ctx):
    await ctx.respond("pong")


@bot.slash_command(
    name="getcat",
    description="Get a random cat image!",
)
async def getcat(ctx):
    raw = requests.get("https://api.thecatapi.com/v1/images/search")
    cat_resp = raw.json()
    if cat_resp[0].get("url"):
        resp = cat_resp[0].get("url")
    else:
        resp = "I was unable to catch the cat for a picture... Try again later"
    await ctx.respond(resp)


async def doReply(message: Message):
    """
    Checks a message for any trigger words, and if triggered it replies accordingly
    """
    for trigger in triggers:
        if trigger.isTriggered(message.content):
            await trigger.doReply(message)


def parseReplyConfig(reply: dict) -> ReplyTrigger:
    """
    Parses json into ReplyTrigger subclasses
    """
    if reply["type"] == "text":
        return TextReplyTrigger(
            triggers=tuple(reply["triggers"]),
            reply=reply["reply"],
            exceptTriggers=reply.get("exceptTriggers", ()),
        )
    elif reply["type"] == "image":
        return ImageReplyTrigger(
            triggers=tuple(reply["triggers"]),
            imageURL=reply["imageUrl"],
            exceptTriggers=reply.get("exceptTriggers", ()),
        )


async def getTargetMessage(messages: list[Message]) -> Message:
    """
    Get the most recent message that's not in VOTE_TRIGGERS or an AldBot message
    """
    targetMessage = messages.pop()
    if targetMessage.author.id == bot.user.id:
        return await getTargetMessage(messages)
    else:
        return targetMessage


with open(AUTH_TOKEN_FILE, "r") as f:
    auth_token = f.readline()

with open(REPLIES_FILE, "r") as f:
    replies = json.load(f)

triggers = list(map(parseReplyConfig, replies))

bot.run(auth_token)
