import discord
from discord.ext import commands
import os

# 봇의 토큰을 환경 변수에서 가져옵니다.
TOKEN = os.getenv('DISCORD_TOKEN')

# 디스코드 봇 인텐트를 설정합니다.
intents = discord.Intents.default()
intents.message_content = True

# 봇의 프리픽스를 설정하고 인텐트를 전달합니다.
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# 채팅 관리 기능 로드
import chat_management
bot.add_command(chat_management.clean)
bot.add_command(chat_management.bigclean)
bot.add_command(chat_management.follow)  # 따라하기 기능 추가

# 로스트아크 관련 기능 로드
import lostark_features
bot.load_extension("lostark_features")

# 봇을 실행합니다.
bot.run(TOKEN)