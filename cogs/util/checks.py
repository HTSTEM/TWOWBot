from discord.ext import commands


def is_staff():
    def predicate(ctx: commands.Context) -> bool:
        # Ignore DMs
        if ctx.guild is None:
            return
        return ctx.author.permissions_in(ctx.guild.default_channel).manage_channels
    return commands.check(predicate)


def is_developer():
    # Add owner bypass
    def predicate(ctx: commands.Context) -> bool:
        ids = ctx.bot.config.get('ids', {})
        in_config = ctx.author.id in ids.get('developers', [])
        has_role = False
        if ctx.guild is not None:
            has_role = ids.get('developer_role_id', 0) in map(lambda r: r.id, ctx.author.roles)
        return in_config or has_role
    return commands.check(predicate)
