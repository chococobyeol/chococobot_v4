# main.py
import os
import discord
from discord.ext import commands
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 다른 모듈에서 기능을 가져옵니다.
import chat_management
import lostark_features
import voice_management
import command_help
import word_chain  # 끝말잇기 모듈 추가

# 봇의 토큰을 환경 변수에서 가져옵니다.
TOKEN = os.getenv('DISCORD_TOKEN')

# 디스코드 봇 인텐트를 설정합니다.
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # 음성 채널 사용을 위해 추가

# 디스코드 봇 인스턴스를 생성하고 기본 help 명령어를 비활성화합니다.
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 더미 HTTP 서버를 실행하기 위한 함수
def run_dummy_server():
    server_address = ('', int(os.getenv('PORT', 8000)))  # 포트 8000을 기본으로 사용하고, 환경변수 'PORT' 값을 사용할 수 있음
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting dummy server on port {server_address[1]}")
    httpd.serve_forever()

# 봇의 이벤트 핸들러: 봇이 준비되었을 때 호출됩니다.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    # 필요한 경우 Lost Ark 닉네임 업데이트 작업 시작
    if not lostark_features.update_nicknames.is_running():
        print("Starting the Lost Ark nickname update task")
        lostark_features.update_nicknames.start()

# 비동기 작업을 별도로 실행하기 위한 함수
async def main():
    # 더미 서버를 백그라운드에서 실행합니다.
    server_thread = threading.Thread(target=run_dummy_server)
    server_thread.daemon = True
    server_thread.start()

    # 모듈별로 기능을 설정합니다.
    chat_management.setup(bot)
    lostark_features.setup(bot)
    await voice_management.setup(bot)
    command_help.setup(bot)
    await word_chain.setup(bot)  # 끝말잇기 모듈 설정

    # 봇을 시작합니다.
    async with bot:
        await bot.start(TOKEN)

# asyncio를 사용하여 이벤트 루프를 시작합니다.
if __name__ == "__main__":
    asyncio.run(main())