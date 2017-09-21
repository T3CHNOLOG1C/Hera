#!/usr/bin/python3

import discord
from discord.ext import commands

class Speak:
    """Give the bot a voice"""

    def __init__(self, bot):
        self.bot = bot
        print("{} addon loaded.".format(self.__class__.__name__))

    @commands.has_permissions(manage_messages=True)
    @commands.command(pass_context=True)
    async def speak(self, ctx, destination, *, message):
        """Make the bot speak (Staff Only)"""
        await self.bot.delete_message(ctx.message)
        if len(ctx.message.channel_mentions) > 0:
            channel = ctx.message.channel_mentions[0]
            await self.bot.send_message(channel, message)

def setup(bot):
    bot.add_cog(Speak(bot))
