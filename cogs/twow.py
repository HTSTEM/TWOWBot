import subprocess
import asyncio
import inspect
import sys

from discord.ext import commands
import discord

from cogs.util import checks


class TWOW:
    '''TWOW commands'''
    
    @commands.command()
    async def status(self, ctx):
        '''Get's current TWOW status'''
        
        embed = discord.Embed(colour=0xFFFF00)
        embed.add_field(name='Servers', value="0")
        embed.add_field(name='Channels', value="0")
        embed.add_field(name='Games All Time', value="0")
        embed.add_field(name='Games In Progress', value="0")
        embed.set_footer(text='Footer')
        await ctx.send(embed=embed)
        
    @commands.command()
    async def setup(self, ctx):
        channel_id = ctx.channel.id
        if False:
            #TODO: check if channel in database
            await ctx.send('This channel is already setup!')
        else:
            #TODO: create database
            await ctx.send('This channel is ready to play a minitwow!')        

def setup(bot):
    bot.add_cog(TWOW())
