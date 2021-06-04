# bot.py
import os

import discord
from discord.client import Client
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv() # Load .env
TOKEN = os.getenv("DISCORD_TOKEN") # Grab token stored as environmental variable
ADMINS = os.getenv("ADMINS").split(",")

class CustomClient(commands.Bot): # Custom bot object
    def __init__(self):
        super().__init__(command_prefix="$",case_insensitive=True,help_command=None)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!") # Success!
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
            name="naritai | $help")) # Credit

client = CustomClient()

@client.event
async def on_voice_state_update(member, before, after): # On member leave, move, or join on voice channels
    if member.user.id is client.user.id: return # Ignore this bot
        
    new_channel = after.channel
    old_channel = before.channel

    if member.bot: # If member is a bot
        if new_channel: # If a bot has connected to a voice channel
            user_limit = new_channel.user_limit

            if user_limit>0 and user_limit<99: # 0 is no limit, 99 is max
                await new_channel.edit(user_limit=user_limit+1) # Increment user limit

        if old_channel: # If a bot has disconnected from a voice channel
            user_limit = old_channel.user_limit

            if user_limit>1: # Don"t set to no limit if limit is 1 for whatever reason
                await old_channel.edit(user_limit=user_limit-1) # Decrement user limit

@client.command(name="safelogout",aliases=["sl","slogout","safel"])
async def safelogout(ctx):
    if ctx.message.author.id in ADMINS:
        return
    else:
        return

@client.command(name="join",aliases=["j"])
async def join(ctx):
    author = ctx.message.author
    channel = author.voice.channel
    await channel.connect()

@client.command(name="help",aliases=["h","info","i","in"])
async def help(ctx):
    icon = client.user.avatar_url
    emoji = client.get_emoji(766352487984660480)
    emoji_placeholder = "" if emoji is None else f"{emoji} "

    embed=discord.Embed(title=f"{emoji_placeholder}Information", description=" ", color=0xffc0cb)
    embed.set_author(name="Dynamic Voice Channel User Limit",
        url="https://github.com/naritaii/DynamicUserLimit", icon_url=icon)
    embed.set_thumbnail(url=icon)
    embed.add_field(name="$help", value="Brings up this menu", inline=False)
    embed.add_field(name="$join", value="Has the bot join your voice channel to take up a slot", inline=False)
    embed.add_field(name="$safeshutdown", value="Safely logout the bot (user's ID must be listed in the ADMINS environmental variables (.env)", inline=False)
    embed.set_footer(text="v1.0.0 by naritai")
    await ctx.send(embed=embed)

try:
    client.run(TOKEN,bot=True) # Attempt to connect to bot
except discord.client.LoginFailure as e:
    print("Login unsuccessful. Improper token.")
    raise e
except AttributeError as e:
    print("Login unsuccessful. Token is NoneType, is the .env set up properly?")
    raise e
