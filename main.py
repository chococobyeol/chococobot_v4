import os
from discord.ext import commands
import discord

# 봇 토큰과 포트 번호를 환경 변수에서 가져오기
TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.environ.get('PORT', 5000))  # 기본값으로 5000번 포트를 사용

# Discord Intents 설정
intents = discord.Intents.default()
intents.message_content = True

# 봇 초기화
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command(name="따라하기")
async def follow(ctx, *, text):
    await ctx.send(text)
    print(f'{ctx.author.nick}({ctx.author.name})님이 따라하기 명령어를 사용했어요...')
    print(text + '\n')

@bot.command(name="청소")
async def clean(ctx, *, text):
    amount = int(text)
    print(amount)
    if amount > 100:
        await ctx.channel.send("한 번에 하기 힘들어서 100개 까지만 가능해요...")
    else:
        def is_me(m):
            return m.author == ctx.author

        await ctx.channel.purge(limit=1, check=is_me)
        deleted = await ctx.channel.purge(limit=amount, check=is_me)
        print(f'최근 디스코드 채팅 {amount}개 중 {ctx.author.nick}({ctx.author.name})님의 메세지를\n삭제했어요...')

@bot.command(name="대청소")
async def bigclean(ctx, *, text):
    if ctx.author.guild_permissions.administrator:
        amount = int(text)
        if amount > 1000:
            await ctx.channel.send("한 번에 하기 힘들어서 1000개 까지만 가능해요...")
        else:
            await ctx.channel.purge(limit=1)
            await ctx.channel.purge(limit=amount)

            embed = discord.Embed(
                title="메시지 삭제 알림",
                description=f"최근 디스코드 채팅 {amount}개를\n관리자 {ctx.author.nick}님의 요청으로 삭제했어요...",
                color=0x000000)
            await ctx.channel.send(embed=embed)
            print(f'{ctx.author.nick}({ctx.author.name})님이 대청소 명령어를 사용했어요...')
    else:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(f"{ctx.author.mention}, 이 명령어는 서버 관리자 권한이 필요해요...")

# 웹 서버 설정 (Render에 필요)
if __name__ == "__main__":
    from aiohttp import web
    app = web.Application()
    web.run_app(app, port=PORT)

# 봇 실행
bot.run(TOKEN)