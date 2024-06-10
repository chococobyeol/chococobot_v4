import discord
from discord.ext import commands

# 최근 메시지를 청소하는 명령어
@commands.command(name="청소")
async def clean(ctx, *, text: str):
    amount = int(text)
    print(amount)
    if amount > 100:
        await ctx.channel.send("한 번에 하기 힘들어서 100개 까지만 가능해요...")
    else:
        def is_me(m):
            return m.author == ctx.author
        deleted = await ctx.channel.purge(limit=amount, check=is_me)
        print(f'최근 디스코드 채팅 {amount}개 중 {ctx.author.nick}({ctx.author.name})님의 메세지를\n삭제했어요...')

# 관리자가 최근 메시지를 대청소하는 명령어
@commands.command(name="대청소")
async def bigclean(ctx, *, text: str):
    if ctx.author.guild_permissions.administrator:
        amount = int(text)
        if amount > 1000:
            await ctx.channel.send("한 번에 하기 힘들어서 1000개 까지만 가능해요...")
        else:
            await ctx.channel.purge(limit=amount)
            embed = discord.Embed(
                title="메시지 삭제 알림",
                description=f"최근 디스코드 채팅 {amount}개를\n관리자 {ctx.author.nick}님의 요청으로 삭제했어요...",
                color=0x000000)
            await ctx.channel.send(embed=embed)
            print(f'{ctx.author.nick}({ctx.author.name})님이 대청소 명령어를 사용했어요...')
    else:
        await ctx.channel.send(f"{ctx.author.mention}, 이 명령어는 서버 관리자 권한이 필요해요...")

# 따라하기 명령어
@commands.command(name="따라하기")
async def follow(ctx, *, message: str):
    await ctx.send(message)
    print(f'{ctx.author.nick}({ctx.author.name})님이 따라하기 명령어를 사용했어요...')
    print(message + '\n')