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

# 다른 모듈에서 기능을 가져옵니다.
import chat_management
import lostark_features

# 채팅 관리 명령어를 추가합니다.
bot.add_command(chat_management.clean)
bot.add_command(chat_management.bigclean)

# 로스트아크 관련 명령어를 추가합니다.
bot.add_command(lostark_features.loanickchange)

# 봇을 실행합니다.
bot.run(TOKEN)