import subprocess
import asyncio
import inspect
import sys

from discord.ext import commands
import discord

from cogs.util import checks
from cogs.util.game_manager import Game_Manager


class TWOW:
    '''TWOW commands'''
    def __init__(self):
        self.gm = Game_Manager(self)

    def __unload(self):
        self.gm.close()
    
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
    async def setup(self, ctx, *, name: str):
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            self.gm.start_new_game(ctx.guild.id, channel_id, name, ctx.message.author.id)
            await ctx.send('Channel setup to play a mTWOW named `{0}`!'.format(name))
        else:
            await ctx.send('This channel is already setup under the name `{0}`!'.format(game.name))        

    @commands.command(aliases=['prompt'])
    async def get_prompt(self, ctx):
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            await ctx.send('No mTWOW running here!')
        else:
            prompt = game.get_prompt()
            if prompt is None:
                await ctx.send('There\'s no prompt yet for this round!')
            else:
                await ctx.send('The prompt is {0}'.format(prompt))

    @commands.command(aliases=['round'])
    async def get_round(self, ctx):
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            await ctx.send('No mTWOW running here!')
        else:
            await ctx.send('We\'re on round {0} right now'.format(game.round))

def setup(bot):
    bot.add_cog(TWOW())
