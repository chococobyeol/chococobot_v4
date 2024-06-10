import discord
from discord.ext import commands
import os
import asyncio

# 더미 HTTP 서버 추가
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 더미 HTTP 서버를 실행하기 위한 함수
def run_dummy_server():
    server_address = ('', int(os.getenv('PORT', 8000)))  # 포트 8000을 기본으로 사용하고, 환경변수 'PORT' 값을 사용할 수 있음
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting dummy server on port {server_address[1]}")
    httpd.serve_forever()

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

# 채팅 관리 명령어를 설정합니다.
chat_management.setup(bot)

# 로스트아크 관련 기능을 설정합니다.
lostark_features.setup(bot)

# 비동기 작업을 별도로 실행하기 위한 함수
async def start_bot_and_tasks():
    await bot.start(TOKEN)
    # 로스트아크 기능의 비동기 작업을 시작합니다.
    lostark_features.start_tasks()

# asyncio를 사용하여 이벤트 루프를 시작합니다.
if __name__ == "__main__":
    # 더미 서버를 백그라운드에서 실행합니다.
    server_thread = threading.Thread(target=run_dummy_server)
    server_thread.daemon = True
    server_thread.start()

    asyncio.run(start_bot_and_tasks())