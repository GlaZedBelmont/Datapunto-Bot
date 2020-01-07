
import logging
import asyncio
import yaml
import aiohttp
import discord
from discord.ext import commands
import os
import traceback
import sys
from traceback import format_exception, format_exc
from datetime import datetime
from discord import ChannelType
from discord.utils import get
'''Bot framework that can dynamically load and unload cogs.'''

config = yaml.safe_load(open('config.yml'))
secure = yaml.safe_load(open('secure.yml'))
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    config['prefix']),
    description='')

bot.loaded_cogs = []
bot.unloaded_cogs = []
script_name = os.path.basename(__file__).split('.')[0]
bot.script_name = script_name
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def initLogging():
    logformat = "%(asctime)s %(name)s:%(levelname)s:%(message)s"
    logging.basicConfig(level=logging.INFO, format=logformat,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger("discord").setLevel(logging.WARNING)
    return logging.getLogger("Datapunto Bot")

def check_if_dirs_exist():
    '''Function that creates the "cogs" directory if it doesn't exist already'''
    os.makedirs('cogs', exist_ok=True)

def load_autoload_cogs():
    '''
    Loads all .py files in the cogs subdirectory that are in the config file as "autoload_cogs" as cogs into the bot. 
    If your cogs need to reside in subfolders (ie. for config files) create a wrapper file in the cogs 
    directory to load the cog.
    '''
    for entry in os.listdir('cogs'):
        if entry.endswith('.py') and os.path.isfile('cogs/{}'.format(entry)) and entry[:-3] in config['autoload_cogs']:
            try:
                bot.load_extension("cogs.{}".format(entry[:-3]))
                bot.loaded_cogs.append(entry[:-3])
            except Exception as e:
                print(e)
            else:
                print('Succesfully loaded cog {}'.format(entry))

def get_names_of_unloaded_cogs():
    '''
    Creates an easy loadable list of cogs.
    If your cogs need to reside in subfolders (ie. for config files) create a wrapper file in the auto_cogs
    directory to load the cog.
    '''
    for entry in os.listdir('cogs'):
        if entry.endswith('.py') and os.path.isfile('cogs/{}'.format(entry)) and entry[:-3] not in bot.loaded_cogs:
            bot.unloaded_cogs.append(entry[:-3])

check_if_dirs_exist()
load_autoload_cogs()
get_names_of_unloaded_cogs()

@bot.command(aliases=['listcogs'])
async def list_cogs(ctx):
    '''Lists all cogs and their status of loading.'''
    cog_list = commands.Paginator(prefix='', suffix='')
    cog_list.add_line('**✅ Succesfully loaded:**')
    for cog in bot.loaded_cogs:
        cog_list.add_line('- ' + cog)
    cog_list.add_line('**❌ Not loaded:**')
    for cog in bot.unloaded_cogs:
        cog_list.add_line('- ' + cog)
    
    for page in cog_list.pages:
        await ctx.send(page)

@bot.command(pass_context=True)
async def textchannels(ctx):
    channels = (c.name for c in ctx.message.guild.channels if c.type==ChannelType.text)
    await ctx.send("\n".join(channels))

@bot.command(pass_context=True)
async def about(ctx):
    embed = discord.Embed(title="Datapunto Bot")
    embed.set_author(name="GlaZedBelmont", url="https://github.com/GlaZedBelmont")
    embed.description = "The only bot DGC needs!"
    embed.url = "https://github.com/GlaZedBelmont/Datapunto-Bot"
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/612447948533399571/e2c1461895d5510057d5ad9fc75d423d.png?size=512")
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def roles(ctx):
    allroles = (c.name for c in ctx.author.roles if c==ctx.author.roles)
    await ctx.send("\n".join(allroles))



class Datapunto(commands.Bot):
    def __init__(self, command_prefix, description):
        super().__init__(command_prefix=command_prefix, description=description)
        
        self.startup = datetime.now()
        
        self.channels = {
            'wiiu-assistance-roleplay': None,
            '3ds-assistance-roleplay': None,
            'bot-err': None,
            'bot-test': None,
        }

        self.admin_roles = {
            'Bot-Admin': None,
            'Admin': None,
        }
        self.roles = {
            'Bot-Admin': None,
            'Admin': None,
            'crc': None,
            'DJ': None,
            'Staff': None,
            '🛶🤠': None,
            'Epic Gamer': None,
            'Movie Night': None,
        }

        self.assistance_channels = {
         self.channels['3ds-assistance-roleplay'],
         self.channels['wiiu-assistance-roleplay'],
        }

    bot.load_extension("jishaku")

pic_ext = ['.jpg','.png','.jpeg']


@bot.event
async def on_command_error(ctx, error):

# ignored because well, 'or' works instead
#    if ctx.guild == 554178232531025940:
#        errorchannel = ctx.guild.get_channel(612386288968138754)
#    elif ctx.guild == 632566001980145675:
#        errorchannel = ctx.guild.get_channel(663858377880764417)
#    else:
#        errorchannel = ctx.guild.get_channel(663858377880764417)
#    if hasattr(ctx.command, 'on_error'):
#        return
        
    ignored = (commands.CommandNotFound)
    error = getattr(error, 'original', error)
    
    errorchannel = ctx.guild.get_channel(612386288968138754) or ctx.guild.get_channel(663858377880764417)
    
    if isinstance(error, ignored):
        return

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.MissingRole):
        try:
            return await ctx.send(f'{ctx.author.mention}, you are missing the role {missing_role} .')
        except:
            pass

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} can not be used in DMs.')
        except:
            pass

    elif isinstance(error, commands.MissingRequiredArgument):
        try:
            return await ctx.send(f'{ctx.author.mention} **Missing Argument:** {error.param.name}.\n') and await ctx.send_help(ctx.command)
        except:
            pass

    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':
            return await ctx.send('I could not find that member. Please try again.')

    msg = "".join(format_exception(type(error), error, error.__traceback__))
    await errorchannel.send(f"```{msg}```")
    
@bot.command(name='repeat', aliases=['mimic', 'copy'])
async def do_repeat(self, ctx, *, inp: str):
    await ctx.send(inp)

@do_repeat.error
async def do_repeat_handler(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'inp':
            await ctx.send("You forgot to give me input to repeat!")
            

@bot.event
async def on_ready():
    aioh = {"The Boi": f"{script_name}/1.0'"}
    bot.aiosession = aiohttp.ClientSession(headers=aioh)
    print('----------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('----------')

bot.run(secure["token"])
