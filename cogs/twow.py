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
    @commands.command()
    async def set_prompt(self, ctx, *, prompt):
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            await ctx.send('No mTWOW running here!')
        else:
            if not game.is_owner(ctx.message.author.id):
                await ctx.send('You don\'t have permission to set the prompt :smirk:')
            else:
                res = game.set_prompt(prompt)

                if res == game.PROMPT_ALLREADY_SET:
                    await ctx.send('The prompt has allready been set for this round.')
                else:
                    await ctx.send('The prompt has been set to {0}!'.format(prompt))
    
    @commands.command()
    async def respond(self, ctx, *, response):
        # TODO: MAKE THIS MUCH BETTER!!!! THIS RELYS ON THE USER RESPONDING IN CHAT AND IS MORE OF AN
        #       EXAMPLE OF HOW TO INTERFACE WITH A GAME OBJECT!!!!
    
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            await ctx.send('No mTWOW running here!')
            return

        # TODO: Remove these three lines if you are allowed to change your response
        if game.get_response(ctx.message.author.id) is not None:
            await ctx.send('You have already responded this round!')
            return
        
        # TODO: Allow users to force submit
        if len(response.split(" ")) > 10:
            await ctx.send('**Warning:** You response appears to be over 10 words! (I counted `{0}`)'.format(len(response.split(" "))))
            #return
            
        ret = game.add_response(ctx.message.author.id, response)
        print(ret)
        if ret:
            await ctx.send(':ok_hand: Response recorded!')
        else:
            await ctx.send('Umm.. This is awkward.. Try again? ¯\_(ツ)_/¯')
    @commands.command(aliases=['responses'])
    async def get_responses(self, ctx):
        channel_id = ctx.channel.id
        
        game = self.gm.get_game(channel_id)
        
        if game is None:
            await ctx.send('No mTWOW running here!')
            return
        if not game.is_owner(ctx.message.author.id):
            await ctx.send('You though I\'d tell *you* everyone\'s respones? :smirk:')
            return
        
        rs = "**Responses:**\n"
        resp = list(game.get_responses(anon=False))
        if len(resp) == 0:
            rs += "None yet :("
        else:
            rs += "\n".join(["{1}: `{0}`".format(r[0], ctx.bot.get_user(r[1]).name) for r in resp])
            
        await ctx.message.author.send(rs)
        await ctx.send(":grin: Check yo' DMs!")
        

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
