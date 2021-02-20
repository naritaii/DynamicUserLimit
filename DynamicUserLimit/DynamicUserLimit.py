# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv() # Load .env
TOKEN = os.getenv('DISCORD_TOKEN') # Grab token stored as environmental variable

client = discord.Client() # The bot

class CustomClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!') # Success!
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="naritai")) # Credit

client = CustomClient()

@client.event
async def on_voice_state_update(member, before, after): # On member leave, move, or join on voice channels
    new_channel = after.channel
    old_channel = before.channel

    if member.bot: # If member is a bot
        if new_channel: # If a bot has connected to a voice channel
            user_limit = new_channel.user_limit

            if user_limit>0 and user_limit<99: # 0 is no limit, 99 is max
                await new_channel.edit(user_limit=user_limit+1) # Increment user limit

        if old_channel: # If a bot has disconnected from a voice channel
            user_limit = old_channel.user_limit

            if user_limit>1: # Don't set to no limit if limit is 1 for whatever reason
                await old_channel.edit(user_limit=user_limit-1) # Decrement user limit



client.run(TOKEN) # Connect to Discord using token