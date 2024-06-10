import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote
import asyncio

# 사용자 게임 캐릭터 정보를 저장할 딕셔너리
user_character_data = {}

# 로스트아크 캐릭터 정보를 가져오는 함수
async def fetch_lostark_info(character_name):
    try:
        qtext = quote(character_name)
        url = f"https://lostark.game.onstove.com/Profile/Character/{qtext}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status != 200:
                    print(f"HTTP 요청 오류: 상태 코드 {res.status}")
                    return None, None
                html = await res.text()
        
        # 'html.parser'를 사용하여 HTML을 파싱합니다.
        soup = BeautifulSoup(html, 'html.parser')

        # 선택자 확인 및 예외 처리
        loaclass_element = soup.select_one('#lostark-wrapper > div > main > div > div.profile-character-info > img')
        loalevel_element = soup.select_one('#lostark-wrapper > div > main > div > div.profile-ingame > div.profile-info > div.level-info2 > div.level-info2__expedition > span:nth-child(2)')
        
        if loaclass_element is None or loalevel_element is None:
            print("HTML 구조가 예상과 다릅니다. 선택자를 확인해주세요.")
            return None, None
        
        loaclass = loaclass_element.get('alt', 'Unknown Class')
        loalevel = loalevel_element.text.replace("Lv.", "").rstrip("0").rstrip(".")
        
        return loaclass, loalevel
    
    except Exception as e:
        print(f"로스트아크 캐릭터 정보를 가져오는 중 오류 발생: {e}")
        return None, None

# 버튼 뷰 클래스
class NicknameView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)  # 타임아웃 60초 설정
        self.ctx = ctx

    @discord.ui.button(label="닉네임 등록", style=discord.ButtonStyle.primary)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("이 버튼은 당신을 위한 것이 아닙니다.", ephemeral=True)
            return

        await interaction.response.send_message("로스트아크 캐릭터 이름을 입력해주세요...", ephemeral=True)

        def check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        try:
            message = await self.ctx.bot.wait_for('message', check=check, timeout=60)
            character_name = message.content
            user_character_data[self.ctx.author.id] = character_name
            loaclass, loalevel = await fetch_lostark_info(character_name)

            if loaclass is None or loalevel is None:
                await self.ctx.send("캐릭터 정보를 가져오지 못했어요. 다시 시도해주세요...", ephemeral=True)
                return

            await self.ctx.author.edit(nick=f'{character_name}/{loaclass}/{loalevel}')
            await self.ctx.send(f"{self.ctx.author.mention}, 닉네임이 {character_name}/{loaclass}/{loalevel}로 변경됐어요...", ephemeral=True)
        except asyncio.TimeoutError:
            await self.ctx.send("시간이 초과됐어요...", ephemeral=True)
        except Exception as e:
            await self.ctx.send(f"오류가 발생했어요: {e}", ephemeral=True)

        # 버튼을 비활성화하여 제거
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="등록 해제", style=discord.ButtonStyle.danger)
    async def unregister(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("이 버튼은 당신을 위한 것이 아닙니다.", ephemeral=True)
            return

        if self.ctx.author.id in user_character_data:
            del user_character_data[self.ctx.author.id]
            try:
                await self.ctx.author.edit(nick=self.ctx.author.name)  # 기본 닉네임으로 변경
                await self.ctx.send(f"{self.ctx.author.mention}, 닉네임 등록이 해제됐어요...", ephemeral=True)
            except discord.Forbidden:
                await self.ctx.send(f"{self.ctx.author.mention}, 닉네임을 변경할 권한이 없어요...", ephemeral=True)
            except Exception as e:
                await self.ctx.send(f"{self.ctx.author.mention}, 닉네임 등록 해제 중 오류가 발생했어요: {e}", ephemeral=True)
        else:
            await self.ctx.send(f"{self.ctx.author.mention}, 닉네임이 등록되어 있지 않아요...", ephemeral=True)

        # 버튼을 비활성화하여 제거
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

# 로스트아크 닉네임 변경 명령어
@commands.command(name="로아닉", aliases=["로아닉네임", "로스트아크닉네임"])
async def loanickchange(ctx):
    view = NicknameView(ctx)
    # 명령어를 실행한 사용자에게만 메시지를 보이도록 설정
    await ctx.send("닉네임을 등록하거나 등록을 해제할 수 있습니다.", view=view, ephemeral=True)

# 봇 객체를 글로벌 변수로 사용
bot = None

# 매일 닉네임 갱신 작업
@tasks.loop(minutes=1)  # 갱신 주기를 1분으로 설정
async def update_nicknames():
    await bot.wait_until_ready()
    
    for user_id, character_name in user_character_data.items():
        member = bot.get_user(user_id)
        if member:
            loaclass, loalevel = await fetch_lostark_info(character_name)
            if loaclass and loalevel:
                try:
                    await member.edit(nick=f'{character_name}/{loaclass}/{loalevel}')
                    await member.send(f"{member.mention}, 닉네임이 {character_name}/{loaclass}/{loalevel}로 갱신됐어요...")
                except discord.Forbidden:
                    await member.send(f"{member.mention}, 닉네임을 변경할 권한이 없어요...")
                except Exception as e:
                    await member.send(f"{member.mention}, 닉네임을 갱신하는 중 오류가 발생했어요: {e}")
            else:
                await member.send(f"{member.mention}, 캐릭터 정보를 갱신하는 중 오류가 발생했어요...")

# 비동기 작업을 시작하는 함수
def start_tasks():
    update_nicknames.start()

# 메인 파일에서 이 함수를 호출하여 기능을 추가할 수 있도록 합니다.
def setup(bot_instance):
    global bot
    bot = bot_instance
    bot.add_command(loanickchange)