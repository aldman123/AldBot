# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

import random

import discord
from discord.ext import commands

description = """
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description=description,
    intents=intents,
)

client = discord.Client()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(name='ping', )
async def hello(ctx):
    await ctx.respond("pong")

@bot.slash_command(name='pickrole', )
async def pickrole(ctx):
    message = "what are your prnouns???"
    await ctx.send_response("message", ephemeral=True)

with open('auth_token.txt') as f:
    auth_token = f.readline()

bot.run(auth_token)
