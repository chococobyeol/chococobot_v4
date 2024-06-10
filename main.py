import discord
from discord.ext import commands

# 봇 토큰 환경 변수로 가져오기
import os
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # 메시지 콘텐츠 접근을 활성화합니다.

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def echo(ctx, *, message: str):
    await ctx.send(message)

bot.run(TOKEN)