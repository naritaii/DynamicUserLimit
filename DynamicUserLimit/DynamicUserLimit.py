# DynamicUserLimit.py
import os
from dotenv import load_dotenv
import psycopg2
import discord
from discord.client import Client
from discord.ext import commands

load_dotenv() # Load .env
TOKEN=os.getenv("DISCORD_TOKEN") # Grab token stored as environmental variable
ADMINS=list(map(int,os.getenv("ADMINS").split(","))) # Get bot hoster IDs for admin commands

class CustomClient(commands.Bot): # Custom bot object
    def __init__(self):
        super().__init__(command_prefix="$",case_insensitive=True,help_command=None, # Super client and define
            intents=discord.Intents.all())                                      # command variables and intents
        return
    async def on_ready(self):
        print(f"{self.user} has connected to Discord!") # Success!
        await client.change_presence(status=discord.Status.online,activity=discord.Activity(
            type=discord.ActivityType.watching,name="naritai | $help")) # Credit

        try:
            conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode='require')
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS variables (
                    ID TEXT, 
                    bit BIT
                )
            """)
            cur.execute("""
                SELECT * FROM variables WHERE ID='login_type'
            """)
            if (cur.fetchall() is None or 1):
                cur.execute("INSERT INTO variables (ID,bit) VALUES ('login_type',b'0')")
                print("Initializing user limits...")
                for guilds in self.guilds: await initializelimits(guilds)
                print("Initialization complete!")
            conn.commit()
            conn.close()
        except psycopg2.OperationalError:
            pass
        return


client = CustomClient()

@client.event
async def on_guild_join(guild):
    await initializelimits(guild)

async def initializelimits(guild):
    for vc in guild.voice_channels:
        user_limit=vc.user_limit

        if user_limit>0: # Ignore if no limit
            members=vc.members
            bots=sum(m.bot for m in members if m is not client.user) # Bots in channel ignoring this bot

            if bots>0:
                if user_limit+bots<99: await vc.edit(user_limit=user_limit+bots)
                else: await vc.edit(user_limit=99)
                print(str(bots)+" bot(s) in "+str(vc)+" in "+str(guild)+".")
    return

@client.event
async def on_guild_leave(guild):
    await revertlimits(guild)

async def revertlimits(guild):
    for vc in guild.voice_channels:
        user_limit=vc.user_limit

        if user_limit>0: # Ignore if no limit
            members=vc.members
            bots=sum(m.bot for m in members if m is not client.user) # Bots in channel ignoring this bot

            if bots>0 and user_limit>bots+1: # Don't set to no limit
                await vc.edit(user_limit=user_limit-bots)
                print(str(bots)+" bot(s) in "+str(vc)+" in "+str(guild)+".")
    return

@client.event
async def on_voice_state_update(member, before, after): # On member leave, move, or join on voice channels
    if member is client.get_user: return # Ignore this bot
        
    new_channel=after.channel
    old_channel=before.channel

    if member.bot: # If member is a bot
        if new_channel: # If a bot has connected to a voice channel
            user_limit=new_channel.user_limit

            if user_limit>0 and user_limit<99: # 0 is no limit, 99 is max
                await new_channel.edit(user_limit=user_limit+1) # Increment user limit

        if old_channel: # If a bot has disconnected from a voice channel
            user_limit=old_channel.user_limit

            if user_limit>1: # Don't set to no limit if limit is 1 for whatever reason
                await old_channel.edit(user_limit=user_limit-1) # Decrement user limit

@client.command(name="safelogout",aliases=["sl","slogout","safel","safeshutdown","ss","sshutdown","safes"])
async def safelogout(ctx):
    if ctx.message.author.id in ADMINS:
        await ctx.send("Safely shutting down... Please wait.")
        for guilds in client.guilds:
            await revertlimits(guilds)
        try:
            conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode='require')
            cur = conn.cursor()
            cur.execute("INSERT INTO variables (logout_type) VALUES (b'1')")
            conn.close()
        except psycopg2.OperationalError:
            pass
        await ctx.send("Logging out...")
        await client.change_presence(status=discord.Status.offline)
        await client.close()
        print("Bot successfully logged out!")
    else:
        await ctx.send("You are not listed under ADMINS in the .env (environmental variables), this command "+
            "is intended for the bot hoster to safely shutdown the bot on all servers.")

@client.command(name="join",aliases=["j","summon","s"])
async def join(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
    return

@client.command(name="help",aliases=["h","info","i","in"])
async def help(ctx):
    icon=client.user.avatar_url
    emoji=client.get_emoji(766352487984660480)
    emoji_placeholder="" if emoji is None else f"{emoji} "
    color=ctx.guild.get_member(client.user.id).color
    if color.value==0x000000: color=0xffc0cb

    embed=discord.Embed(title=f"{emoji_placeholder}Information",description=" ",color=color)
    embed.set_author(name="Dynamic Voice Channel User Limit",
        url="https://github.com/naritaii/DynamicUserLimit",icon_url=icon)
    embed.set_thumbnail(url=icon)
    embed.add_field(name="$help",value="Brings up this menu.", inline=False)
    embed.add_field(name="$join",value="Has the bot join your voice channel to take up a slot.",inline=False)
    if ctx.message.author.id in ADMINS:
        embed.add_field(name="$safeshutdown",value="Safely logout the bot.",inline=False)
    embed.set_footer(text="v1.0.0 by naritai")

    await ctx.send(embed=embed)

try:
    client.run(TOKEN,bot=True) # Attempt to connect to bot
except discord.client.LoginFailure:
    print("Login unsuccessful. Improper token.")
    pass
except AttributeError:
    print("Login unsuccessful. Token is NoneType, is the .env (environmental variables) set up properly?")
    pass

# Code after crash
print('Bot has crashed or otherwise shutdown.')
