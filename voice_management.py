import discord
from discord.ext import commands, tasks
from gtts import gTTS
import os
import asyncio
import uuid
import logging
from collections import deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)

class VoiceManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.idle_time = 300  # 5분 (300초) 동안 아무도 없을 때 봇이 나가기 전 대기 시간
        self.queues = {}  # 서버별 큐를 관리하는 딕셔너리

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_idle.is_running():
            self.check_idle.start()
            logging.info("Started idle check task")

    @commands.command(name="말")
    async def say(self, ctx, *, text: str):
        logging.info(f"say command called with text: {text}")

        if ctx.author.voice and ctx.author.voice.channel:
            user_channel = ctx.author.voice.channel
            logging.info(f"User is in channel: {user_channel.name}")

            voice_client = ctx.voice_client

            # 봇이 연결된 채널이 사용자가 있는 채널과 다른 경우, 이동
            if voice_client and voice_client.is_connected():
                if voice_client.channel != user_channel:
                    await voice_client.move_to(user_channel)
                    logging.info(f"Moved to user's channel: {user_channel.name}")
            else:
                # 봇이 아직 연결되지 않은 경우, 사용자의 채널에 연결
                try:
                    voice_client = await user_channel.connect()
                    logging.info(f"Connected to channel: {user_channel.name}")
                except discord.errors.ClientException as e:
                    logging.error(f"Failed to connect to channel: {e}")
                    return
                except Exception as e:
                    logging.error(f"Unexpected error occurred while connecting to channel: {e}")
                    return

            guild_id = ctx.guild.id

            if guild_id not in self.queues:
                self.queues[guild_id] = deque()

            # 고유한 파일 이름 생성
            unique_filename = f"tts_{uuid.uuid4()}.mp3"

            # 텍스트를 음성으로 변환하여 고유한 mp3 파일로 저장
            tts = gTTS(text, lang='ko')
            tts.save(unique_filename)
            logging.info(f"TTS generated for text: {text} with file name: {unique_filename}")

            # 요청을 큐에 추가
            self.queues[guild_id].append((voice_client, unique_filename))

            # 큐가 비어 있다면 바로 재생 시작
            if len(self.queues[guild_id]) == 1:
                await self.play_next_in_queue(guild_id)
            
            # 봇이 마지막으로 사용된 시간을 갱신
            self.voice_clients[user_channel] = {
                'client': voice_client,
                'last_active': asyncio.get_event_loop().time()
            }
        else:
            logging.info("User is not in a voice channel")
            await ctx.send("음성 채널에 접속한 상태여야 해요...")

    async def play_next_in_queue(self, guild_id):
        if self.queues[guild_id]:
            voice_client, filename = self.queues[guild_id][0]  # 큐의 첫 번째 항목 가져오기

            def after_playing(error):
                if error:
                    logging.error(f"Error playing file: {error}")

                # 큐에서 첫 번째 항목 제거
                self.queues[guild_id].popleft()

                # 파일 삭제
                if os.path.exists(filename):
                    os.remove(filename)
                    logging.info(f"TTS file {filename} removed")

                # 다음 항목 재생
                if self.queues[guild_id]:
                    asyncio.run_coroutine_threadsafe(self.play_next_in_queue(guild_id), self.bot.loop)

            # 음성 파일을 재생
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegPCMAudio(filename), after=after_playing)
                logging.info(f"Playing TTS for file: {filename}")
        else:
            logging.info(f"Queue for guild {guild_id} is empty")

    @commands.command(name="저리가")
    async def leave(self, ctx):
        logging.info("leave command called")
        
        if ctx.voice_client:  # 봇이 음성 채널에 연결되어 있는 경우
            guild_id = ctx.guild.id
            channel = ctx.voice_client.channel

            # 현재 음성 재생을 중단하고 큐를 초기화
            if guild_id in self.queues:
                self.queues[guild_id].clear()
                logging.info(f"Cleared queue for guild {guild_id}")

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                logging.info("Stopped playing audio")

            await ctx.voice_client.disconnect()
            logging.info("Disconnected from voice channel")
            
            # 연결이 끊어진 채널 정보를 voice_clients에서 제거
            if channel in self.voice_clients:
                del self.voice_clients[channel]
                logging.info(f"Removed channel {channel.name} from voice_clients")

            await ctx.send("음성 채널에서 나왔어요...")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않아요...")

    @commands.command(name="이리와")
    async def join(self, ctx):
        logging.info("join command called")
        
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            logging.info(f"User is in channel: {channel.name}")

            if ctx.voice_client and ctx.voice_client.is_connected():
                if ctx.voice_client.channel == channel:
                    await ctx.send(f"{channel.name} 채널에 이미 연결되어 있어요...")
                    return
                else:
                    await ctx.voice_client.move_to(channel)
                    logging.info(f"Moved to channel: {channel.name}")
            else:
                try:
                    voice_client = await channel.connect()
                    logging.info(f"Connected to channel: {channel.name}")
                    self.voice_clients[channel] = {
                        'client': voice_client,
                        'last_active': asyncio.get_event_loop().time()
                    }
                except discord.errors.ClientException as e:
                    logging.error(f"Failed to connect to channel: {e}")
                    await ctx.send(f"채널에 연결할 수 없어요: {e}")
                    return
                except Exception as e:
                    logging.error(f"Unexpected error occurred while connecting to channel: {e}")
                    await ctx.send(f"예기치 않은 오류가 발생했어요: {e}")
                    return

            await ctx.send(f"{channel.name} 채널로 갔어요...")
        else:
            logging.info("User is not in a voice channel")
            await ctx.send("음성 채널에 접속한 상태여야 해요...")

    @tasks.loop(seconds=10)
    async def check_idle(self):
        current_time = asyncio.get_event_loop().time()
        for channel, data in list(self.voice_clients.items()):
            if current_time - data['last_active'] > self.idle_time:
                await data['client'].disconnect()
                logging.info(f"Disconnected from {channel.name} due to inactivity")
                del self.voice_clients[channel]

    @check_idle.before_loop
    async def before_check_idle(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(VoiceManagement(bot))