#!/usr/bin/env python3

import os
import configparser
import asyncio
import traceback
import signal
from subprocess import Popen
from os import execv
from sys import argv
from subprocess import call

import discord
from discord.ext import commands

# Change to script's directory
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

bot_prefix = ["."]
bot = commands.Bot(command_prefix=bot_prefix, description="Hera, a bot to be used as a puppet.")

# Eead config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Handle errors
# Taken from 
# https://github.com/916253/Kurisu/blob/31b1b747e0d839181162114a6e5731a3c58ee34f/run.py#L88
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    if isinstance(error, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel, "{} You don't have permission to use this command.".format(ctx.message.author.mention))
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "{} You are missing required arguments.\n{}".format(ctx.message.author.mention, formatter.format_help_for(ctx, ctx.command)[0]))
    elif isinstance(error, commands.errors.CommandOnCooldown):
        try:
            await bot.delete_message(ctx.message)
        except discord.errors.NotFound:
            pass
        message = await bot.send_message(ctx.message.channel, "{} This command was used {:.2f}s ago and is on cooldown. Try again in {:.2f}s.".format(ctx.message.author.mention, error.cooldown.per - error.retry_after, error.retry_after))
        await asyncio.sleep(10)
        await bot.delete_message(message)
    else:
        await bot.send_message(ctx.message.channel, "An error occured while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        mods_msg = "Exception occured in `{0.command}` in {0.message.channel.mention}".format(ctx)
        # traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        print(''.join(tb))
        await bot.send_message(bot.botdev_channel, mods_msg + '\n```' + ''.join(tb) + '\n```')


@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args[0], commands.errors.CommandNotFound):
        return
    print('Ignoring exception in {}'.format(event_method))
    mods_msg = "Exception occured in {}".format(event_method)
    tb = traceback.format_exc()
    print(''.join(tb))
    mods_msg += '\n```' + ''.join(tb) + '\n```'
    mods_msg += '\nargs: `{}`\n\nkwargs: `{}`'.format(args, kwargs)
    await bot.send_message(bot.botdev_channel, mods_msg)
    print(args)
    print(kwargs)


@bot.event
async def on_ready():

    for server in bot.servers:
        bot.server = server

    # Roles
    bot.owner_role = discord.utils.get(server.roles, name="Owner")
    bot.botdev_role = discord.utils.get(server.roles, name="#botdev")
    bot.nsfw_role = discord.utils.get(server.roles, name="nsfw")

    # Channels
    bot.announcements_channel = discord.utils.get(server.channels, name="announcements")
    bot.botdev_channel = discord.utils.get(server.channels, name="hera-error")
    bot.nsfw_channel = discord.utils.get(server.channels, name="nsfw")
    bot.brickdms_channel = discord.utils.get(server.channels, name="brick-dms")
    bot.logs_channel = discord.utils.get(server.channels, name="admin-logs")

    # Load addons
    addons = [
         'addons.speak',
     ]

    for addon in addons:
        try:
            bot.load_extension(addon)
        except Exception as e:
            print("Failed to load {} :\n{} : {}".format(addon, type(e).__name__, e))


    print("Client logged in as {}, in the following server : {}".format(bot.user.name, server.name))
    
# Core commands

@commands.has_permissions(administrator=True)
@bot.command()
async def restart():
    """Restart the bot (Staff Only)"""
    await bot.say("`Restarting, please wait...`")
    execv("./Brick.py", argv)
        
# Run the bot
bot.run(config['Main']['token'], max_messages=10000)
