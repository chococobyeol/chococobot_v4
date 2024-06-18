# change_botname.py
import discord
from discord.ext import commands

async def change_bot_nickname(ctx: commands.Context, new_nickname: str):
    """
    봇의 닉네임을 변경하는 함수입니다.
    
    :param ctx: 명령어를 실행한 context.
    :param new_nickname: 변경할 새로운 닉네임.
    """
    try:
        guild = ctx.guild
        bot_member = guild.get_member(ctx.bot.user.id)
        if bot_member:
            await bot_member.edit(nick=new_nickname)
            await ctx.send(f'봇의 닉네임이 "{new_nickname}"(으)로 변경되었습니다.')
        else:
            await ctx.send('봇의 정보를 가져올 수 없습니다.')
    except discord.Forbidden:
        await ctx.send('봇의 닉네임을 변경할 권한이 없습니다.')
    except discord.HTTPException as e:
        await ctx.send(f'닉네임 변경 중 오류가 발생했습니다: {e}')

def setup(bot: commands.Bot):
    """
    봇에 change_nickname 명령어를 추가합니다.
    
    :param bot: discord.ext.commands.Bot 인스턴스.
    """
    @bot.command(name='초코코봇이름변경')
    async def change_nickname_command(ctx: commands.Context, *, new_nickname: str):
        await change_bot_nickname(ctx, new_nickname)