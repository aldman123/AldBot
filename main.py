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


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(853108688730587146)
    embed=discord.Embed(title="Welcome!",description=f"{member.mention} Just Joined")
    await channel.send(embed=embed)

# @bot.slash_command(name='ping', )
# async def hello(ctx):
#     await ctx.respond("pong")


with open('auth_token.txt') as f:
    auth_token = f.readline()

bot.run(auth_token)
