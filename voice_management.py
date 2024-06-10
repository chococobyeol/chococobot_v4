import discord
from discord.ext import commands, tasks
from gtts import gTTS
import os
import asyncio

class VoiceManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.idle_time = 300  # 5분 (300초) 동안 아무도 없을 때 봇이 나가기 전 대기 시간

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_idle.is_running():
            self.check_idle.start()
            print("Started idle check task")

    @commands.command(name="말")
    async def say(self, ctx, *, text: str):
        print(f"say command called with text: {text}")

        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            print(f"User is in channel: {channel.name}")

            if ctx.voice_client and ctx.voice_client.is_connected():
                voice_client = ctx.voice_client
            else:
                try:
                    voice_client = await channel.connect()
                    print(f"Connected to channel: {channel.name}")
                except discord.errors.ClientException as e:
                    print(f"Failed to connect to channel: {e}")
                    return
                except Exception as e:
                    print(f"Unexpected error occurred while connecting to channel: {e}")
                    return

            self.voice_clients[channel] = {
                'client': voice_client,
                'last_active': asyncio.get_event_loop().time()
            }

            # 텍스트를 음성으로 변환하여 mp3 파일로 저장
            tts = gTTS(text, lang='ko')
            tts.save("tts.mp3")
            print(f"TTS generated for text: {text}")

            # 음성 파일을 재생
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegPCMAudio("tts.mp3"))
                print(f"Playing TTS for text: {text}")
            
            # 재생된 파일 삭제
            while voice_client.is_playing():
                await asyncio.sleep(1)

            os.remove("tts.mp3")
            print(f"TTS file removed")

            # 봇이 마지막으로 사용된 시간을 갱신
            self.voice_clients[channel]['last_active'] = asyncio.get_event_loop().time()
        else:
            print("User is not in a voice channel")
            await ctx.send("음성 채널에 접속한 상태여야 해요...")

    @commands.command(name="저리가")
    async def leave(self, ctx):
        print("leave command called")
        
        if ctx.voice_client:  # 봇이 음성 채널에 연결되어 있는 경우
            await ctx.voice_client.disconnect()
            print("Disconnected from voice channel")
            
            # 연결이 끊어진 채널 정보를 voice_clients에서 제거
            if ctx.author.voice.channel in self.voice_clients:
                del self.voice_clients[ctx.author.voice.channel]
                print(f"Removed channel {ctx.author.voice.channel.name} from voice_clients")

            await ctx.send("음성 채널에서 나왔어요...")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않아요...")

    @commands.command(name="이리와")
    async def join(self, ctx):
        print("join command called")
        
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            print(f"User is in channel: {channel.name}")

            if ctx.voice_client and ctx.voice_client.is_connected():
                if ctx.voice_client.channel == channel:
                    await ctx.send(f"{channel.name} 채널에 이미 연결되어 있어요...")
                    return
                else:
                    await ctx.voice_client.move_to(channel)
                    print(f"Moved to channel: {channel.name}")
            else:
                try:
                    voice_client = await channel.connect()
                    print(f"Connected to channel: {channel.name}")
                    self.voice_clients[channel] = {
                        'client': voice_client,
                        'last_active': asyncio.get_event_loop().time()
                    }
                except discord.errors.ClientException as e:
                    print(f"Failed to connect to channel: {e}")
                    await ctx.send(f"채널에 연결할 수 없어요: {e}")
                    return
                except Exception as e:
                    print(f"Unexpected error occurred while connecting to channel: {e}")
                    await ctx.send(f"예기치 않은 오류가 발생했어요: {e}")
                    return

            await ctx.send(f"{channel.name} 채널로 갔어요...")
        else:
            print("User is not in a voice channel")
            await ctx.send("음성 채널에 접속한 상태여야 해요...")

    @tasks.loop(seconds=10)
    async def check_idle(self):
        current_time = asyncio.get_event_loop().time()
        for channel, data in list(self.voice_clients.items()):
            if current_time - data['last_active'] > self.idle_time:
                await data['client'].disconnect()
                print(f"Disconnected from {channel.name} due to inactivity")
                del self.voice_clients[channel]

    @check_idle.before_loop
    async def before_check_idle(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(VoiceManagement(bot))