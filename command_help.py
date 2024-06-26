# command_help.py
import discord
from discord.ext import commands

# 명령어 설명을 저장하는 딕셔너리
command_descriptions = {
    "!청소": (
        "사용자가 작성한 최근 메시지를 지정된 개수만큼 삭제해요...\n"
        "사용법: `!청소 [개수]`\n"
        "예: `!청소 10`\n"
        "알림: 한 번에 최대 100개의 메시지만 삭제할 수 있어요..."
    ),
    "!대청소": (
        "관리자가 채널의 최근 메시지를 지정된 개수만큼 대량으로 삭제해요...\n"
        "사용법: `!대청소 [개수]`\n"
        "예: `!대청소 200`\n"
        "알림: 한 번에 최대 1000개의 메시지를 삭제할 수 있고, 서버 관리자 권한이 필요해요..."
    ),
    "!따라하기": (
        "봇이 사용자가 입력한 메시지를 그대로 따라해요...\n"
        "사용법: `!따라하기 [메시지]`\n"
        "예: `!따라하기 안녕하세요`"
    ),
    "!로아닉": (
        "로스트아크 캐릭터 닉네임을 등록하거나 변경해요...\n"
        "사용법: `!로아닉`\n"
        "봇이 사용자에게 캐릭터 이름을 물어보고, 해당 이름으로 디스코드 닉네임을 업데이트해요...\n"
        "알림: 닉네임을 변경하려면 봇의 역할이 사용자의 역할보다 높아야 하고, 서버 관리 권한이 필요할 수 있어요..."
    ),
    "!말": (
        "봇이 음성 채널에서 입력된 텍스트를 음성으로 읽어요...\n"
        "사용법: `!말 [텍스트]`\n"
        "예: `!말 안녕하세요`\n"
        "알림: 봇이 음성 채널에 접속한 상태여야 하며, 채널에 들어가기 위해 권한이 필요할 수 있어요..."
    ),
    "!이리와": (
        "봇이 사용자가 있는 음성 채널로 들어와요...\n"
        "사용법: `!이리와`\n"
        "알림: 봇이 음성 채널에 들어갈 수 있는 권한이 필요하며, 사용자가 음성 채널에 있어야 해요..."
    ),
    "!저리가": (
        "봇이 현재 연결된 음성 채널에서 나가요...\n"
        "사용법: `!저리가`\n"
        "봇이 현재 연결된 음성 채널에서 나가게 돼요..."
    ),
    "!명령어": (
        "사용 가능한 명령어와 그 설명을 표시해요...\n"
        "사용법: `!명령어`\n"
        "이 명령어를 통해 봇의 지원하는 기능을 확인할 수 있어요..."
    )
}

# 명령어 설명 명령어 정의
@commands.command(name="명령어", aliases=["help_list", "도움목록"])
async def show_commands(ctx):
    help_message = "사용 가능한 명령어 목록:\n"
    for command, description in command_descriptions.items():
        help_message += f"{command}: {description}\n\n"
    await ctx.send(help_message)

# 봇 설정 함수
def setup(bot):
    bot.add_command(show_commands)