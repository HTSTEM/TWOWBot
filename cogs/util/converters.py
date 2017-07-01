import re

from discord.ext.commands import IDConverter
from fuzzywuzzy import process


class FuzzyMember(IDConverter):
    async def convert(self, ctx, argument):
        message = ctx.message
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = message.guild
        if match is None:
            result = guild.get_member_named(argument)
        else:
            result = guild.get_member(int(match.group(1)))
        if result is None:
            name = process.extractOne(argument, [m.name for m in guild.members])
            result = guild.get_member_named(name[0])

        return result
