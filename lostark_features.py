import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote
import logging
import asyncio
import json
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 사용자 게임 캐릭터 정보를 저장할 딕셔너리
user_character_data = {}

# JSON 파일 경로
USER_DATA_FILE = 'user_character_data.json'

# JSON 파일에서 데이터 로드
def load_user_data():
    global user_character_data
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            user_character_data = json.load(file)
            logging.info("User character data loaded from file.")
            print("User character data loaded from file.")
    else:
        logging.info("No user data file found. Starting with an empty data set.")
        print("No user data file found. Starting with an empty data set.")

# JSON 파일에 데이터 저장
def save_user_data():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_character_data, file)
        logging.info("User character data saved to file.")
        print("User character data saved to file.")

# 로스트아크 캐릭터 정보를 가져오는 함수
async def fetch_lostark_info(character_name):
    try:
        qtext = quote(character_name)
        url = f"https://lostark.game.onstove.com/Profile/Character/{qtext}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status != 200:
                    logging.error(f"HTTP 요청 오류: 상태 코드 {res.status}")
                    return None, None
                html = await res.text()
        
        # 'html.parser'를 사용하여 HTML을 파싱합니다.
        soup = BeautifulSoup(html, 'html.parser')

        # 선택자 확인 및 예외 처리
        loaclass_element = soup.select_one('#lostark-wrapper > div > main > div > div.profile-character-info > img')
        loalevel_element = soup.select_one('#lostark-wrapper > div > main > div > div.profile-ingame > div.profile-info > div.level-info2 > div.level-info2__expedition > span:nth-child(2)')
        
        if loaclass_element is None or loalevel_element is None:
            logging.error("HTML 구조가 예상과 다릅니다. 선택자를 확인해주세요.")
            return None, None
        
        loaclass = loaclass_element.get('alt', 'Unknown Class')
        loalevel = loalevel_element.text.replace("Lv.", "").replace(",", "").strip()  # 쉼표 제거 및 공백 제거

        logging.info(f"Fetched info for {character_name}: Class = {loaclass}, Level = {loalevel}")
        print(f"Fetched info for {character_name}: Class = {loaclass}, Level = {loalevel}")
        
        return loaclass, loalevel
    
    except Exception as e:
        logging.error(f"로스트아크 캐릭터 정보를 가져오는 중 오류 발생: {e}")
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
            save_user_data()  # 데이터를 저장합니다.
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
            save_user_data()  # 데이터를 저장합니다.
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

# 닉네임 갱신 작업
@tasks.loop(minutes=60)
async def update_nicknames():
    logging.info("Starting nickname update task.")
    await bot.wait_until_ready()

    # 디버깅을 위해 user_character_data의 내용을 출력
    logging.info(f"user_character_data: {user_character_data}")
    print(f"user_character_data: {user_character_data}")

    for user_id, character_name in user_character_data.items():
        logging.info(f"Processing user_id: {user_id}, character_name: {character_name}")
        print(f"Processing user_id: {user_id}, character_name: {character_name}")

        # 명령어를 실행한 서버 내에서만 해당 사용자를 찾습니다.
        member = None
        for guild in bot.guilds:
            member = guild.get_member(user_id)
            if member:
                break

        if member is None:
            logging.warning(f"Member with ID {user_id} not found in any guild")
            print(f"Member with ID {user_id} not found in any guild")
            continue

        logging.info(f"Found member: {member.name}")
        print(f"Found member: {member.name}")

        current_nick = member.display_name
        logging.info(f"Checking nickname for {member.name}: current nickname is '{current_nick}'")
        print(f"Current nickname for {member.name}: '{current_nick}'")

        # 최신 캐릭터 정보 가져오기
        loaclass, loalevel = await fetch_lostark_info(character_name)
        if not loaclass or not loalevel:
            logging.error(f"Failed to fetch info for character {character_name}. Skipping...")
            continue

        logging.info(f"Current character info: Class = {loaclass}, Level = {loalevel}")
        print(f"Current character info: Class = {loaclass}, Level = {loalevel}")
        
        # 현재 닉네임에서 클래스와 레벨 추출 (캐릭터이름/클래스/레벨 형식)
        parts = current_nick.split('/')
        if len(parts) == 3 and parts[0] == character_name:
            current_class, current_level = parts[1], parts[2]
            logging.info(f"Comparing current class = {current_class}, current level = {current_level} with fetched class = {loaclass}, fetched level = {loalevel}")
            print(f"Comparing current class = {current_class}, current level = {current_level} with fetched class = {loaclass}, fetched level = {loalevel}")

            # 문자열로 비교하지 않기 위해, 레벨을 숫자로 변환하여 비교
            try:
                current_level_num = float(current_level)
                fetched_level_num = float(loalevel)
            except ValueError:
                logging.error(f"Failed to convert levels to numbers for comparison: current_level = {current_level}, fetched_level = {loalevel}")
                continue  # 비교를 진행할 수 없으므로, 다음 루프를 진행합니다.

            # 클래스나 레벨이 다른 경우 닉네임 갱신
            if current_class != loaclass or current_level_num != fetched_level_num:
                new_nick = f'{character_name}/{loaclass}/{loalevel}'
                logging.info(f"Updating nickname for {member.name} to '{new_nick}'")
                print(f"Updating nickname for {member.name} to '{new_nick}'")
                try:
                    await member.edit(nick=new_nick)
                except discord.Forbidden:
                    logging.error(f"Failed to update nickname for {member.name}: insufficient permissions.")
                except Exception as e:
                    logging.error(f"Error updating nickname for {member.name}: {e}")
            else:
                logging.info(f"No change needed for {member.name}. Current class and level are up-to-date.")
                print(f"No change needed for {member.name}. Current class and level are up-to-date.")
        else:
            # 현재 닉네임이 예상 형식이 아닌 경우 닉네임 갱신
            new_nick = f'{character_name}/{loaclass}/{loalevel}'
            logging.info(f"Updating nickname for {member.name} to '{new_nick}'")
            print(f"Updating nickname for {member.name} to '{new_nick}'")
            try:
                await member.edit(nick=new_nick)
            except discord.Forbidden:
                logging.error(f"Failed to update nickname for {member.name}: insufficient permissions.")
            except Exception as e:
                logging.error(f"Error updating nickname for {member.name}: {e}")

# 비동기 작업을 시작하는 함수
def start_tasks():
    update_nicknames.start()

# setup 함수: 봇의 설정을 초기화합니다.
def setup(bot_instance):
    global bot
    bot = bot_instance
    load_user_data()  # 봇 시작 시 저장된 사용자 데이터를 로드
    bot.add_command(loanickchange)  # 로아닉 명령어 추가
    start_tasks()  # 닉네임 업데이트 태스크 시작