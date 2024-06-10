import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote

# 사용자 게임 캐릭터 정보를 저장할 딕셔너리
user_character_data = {}

# 로스트아크 캐릭터 정보를 가져오는 함수
async def fetch_lostark_info(character_name):
    qtext = quote(character_name)
    url = f"https://lostark.game.onstove.com/Profile/Character/{qtext}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()
    
    soup = BeautifulSoup(html, 'lxml')
    loaclass = soup.select_one('#lostark-wrapper > div > main > div > div.profile-character-info > img')['alt']
    loalevel = soup.select_one('#lostark-wrapper > div > main > div > div.profile-ingame > div.profile-info > div.level-info2 > div.level-info2__expedition > span:nth-child(2)').text

    loalevel = loalevel.replace("Lv.", "").rstrip("0").rstrip(".")
    return loaclass, loalevel

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

        await interaction.response.send_message("로스트아크 캐릭터 이름을 입력해주세요.", ephemeral=True)

        def check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        try:
            message = await self.ctx.bot.wait_for('message', check=check, timeout=60)
            character_name = message.content
            user_character_data[self.ctx.author.id] = character_name
            loaclass, loalevel = await fetch_lostark_info(character_name)
            await self.ctx.author.edit(nick=f'{character_name}/{loaclass}/{loalevel}')
            await self.ctx.send(f"{self.ctx.author.mention}, 닉네임이 {character_name}/{loaclass}/{loalevel}로 변경되었습니다.")
        except Exception as e:
            await self.ctx.send("시간 초과되었습니다. 다시 시도해주세요.")

    @discord.ui.button(label="등록 해제", style=discord.ButtonStyle.danger)
    async def unregister(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("이 버튼은 당신을 위한 것이 아닙니다.", ephemeral=True)
            return

        if self.ctx.author.id in user_character_data:
            del user_character_data[self.ctx.author.id]
            await self.ctx.send(f"{self.ctx.author.mention}, 닉네임 등록이 해제되었습니다.")
        else:
            await self.ctx.send(f"{self.ctx.author.mention}, 닉네임이 등록되어 있지 않습니다.")

# 로스트아크 닉네임 변경 명령어
@commands.command(name="로아닉", aliases=["로아닉네임", "로스트아크닉네임"])
async def loanickchange(ctx):
    view = NicknameView(ctx)
    await ctx.send("닉네임을 등록하거나 등록을 해제할 수 있습니다.", view=view)

# 매일 닉네임 갱신 작업
@tasks.loop(hours=24)
async def update_nicknames():
    await bot.wait_until_ready()
    
    for user_id, character_name in user_character_data.items():
        member = bot.get_user(user_id)
        if member:
            loaclass, loalevel = await fetch_lostark_info(character_name)
            await member.edit(nick=f'{character_name}/{loaclass}/{loalevel}')
            await member.send(f"{member.mention}, 닉네임이 {character_name}/{loaclass}/{loalevel}로 갱신되었습니다.")

# 메인 파일에서 이 함수를 호출하여 기능을 추가할 수 있도록 합니다.
def setup(bot):
    bot.add_command(loanickchange)
    update_nicknames.start()