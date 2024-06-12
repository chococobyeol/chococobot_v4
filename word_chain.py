import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import random
import re

class WordChainModal(Modal):
    def __init__(self, game, ctx):
        super().__init__(title="끝말잇기 단어 입력")
        self.game = game
        self.ctx = ctx

        self.word_input = TextInput(
            label="단어를 입력하세요",
            placeholder="여기에 단어를 입력하세요...",
            max_length=10  # 최대 길이 설정
        )
        self.add_item(self.word_input)

    async def on_submit(self, interaction: discord.Interaction):
        word = self.word_input.value.strip()
        user = interaction.user.name

        if len(word) < 2:
            await interaction.response.send_message(f"'{word}'은(는) 너무 짧아요. 두 글자 이상의 단어를 입력하세요.", ephemeral=True)
            return

        if not re.match(r'^[가-힣]{2,10}$', word):
            await interaction.response.send_message(f"'{word}'은(는) 유효한 한글 단어가 아닙니다. 다시 시도하세요.", ephemeral=True)
            return

        if not self.game.valid_word(word):
            await interaction.response.send_message(f"'{word}'은(는) 유효하지 않은 단어이거나 이미 사용된 단어입니다. 다른 단어를 입력하세요.", ephemeral=True)
            return

        if not self.game.matches_dueum(self.game.current_word, word[0]):
            await interaction.response.send_message(f"단어는 '{self.game.current_word[-1]}'로 시작해야 해요. 다시 시도하세요.", ephemeral=True)
            return

        self.game.used_words.append((user, word))
        self.game.current_word = word

        bot_word = self.game.next_word(word[-1])
        if bot_word:
            self.game.used_words.append(('봇', bot_word))
            self.game.current_word = bot_word
            await self.game.update_game_status(self.ctx, f"봇의 단어는 '{bot_word}'에요. 다음 단어는 '{bot_word[-1]}'로 시작해야 해요.")
        else:
            await self.ctx.send(embed=self.game.create_embed("게임 종료", "봇이 더 이상 단어를 찾을 수 없어요... 사용자가 승리했어요!"))
            await self.game.end_game(self.ctx, disable_buttons=True)

        # 모달 창 닫기
        await interaction.response.defer()
        # interaction.delete_original_response() 호출 제거

class WordChain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_list = self.load_words('words.txt')
        self.used_words = []
        self.current_word = None
        self.active_channel = None  # 끝말잇기 게임이 활성화된 채널
        self.game_message = None  # 현재 게임 상태 메시지

    def load_words(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]

    def valid_word(self, word):
        # 한 글자 단어를 제외
        if len(word) < 2:
            return False
        
        # 원래 단어와 두음 법칙을 적용한 단어를 모두 검사
        original_word = self.apply_dueum_law(word)
        return (original_word in self.word_list or word in self.word_list) and word not in [w for _, w in self.used_words]

    def apply_dueum_law(self, word):
        """두음 법칙을 적용하여 가능한 단어를 반환"""
        dueum_law_dict = {
            '녀': '여', '뇨': '요', '뉴': '유', '니': '이',
            '랴': '야', '려': '여', '례': '예', '료': '요', '류': '유', '리': '이',
            '라': '나', '래': '내', '로': '노', '뢰': '뇌', '루': '누', '르': '느'
        }
        first_char = word[0]
        if len(word) > 1 and self.is_consonant(word[1]):
            # 두음 법칙을 적용할 수 없는 경우: 두 번째 글자가 받침이 있는 경우
            return word
        return dueum_law_dict.get(first_char, first_char) + word[1:]

    def is_consonant(self, char):
        """받침이 있는지 확인"""
        return ord(char) in range(0x3131, 0x318F)

    def matches_dueum(self, last_word, first_char):
        """두음 법칙에 맞는지 확인"""
        possible_start = self.apply_dueum_law(last_word[-1])
        return first_char == possible_start or first_char == last_word[-1]

    def next_word(self, last_letter):
        candidates = [word for word in self.word_list if word.startswith(last_letter) and word not in [w for _, w in self.used_words]]
        if not candidates:
            # 두음 법칙을 적용한 다음 단어 후보군
            modified_last_letter = self.apply_dueum_law(last_letter)
            candidates = [word for word in self.word_list if word.startswith(modified_last_letter) and word not in [w for _, w in self.used_words]]
        return random.choice(candidates) if candidates else None

    async def update_game_status(self, ctx, additional_message=""):
        """게임 상태를 업데이트하고 이전 메시지를 삭제"""
        previous_words = " > ".join([f"{user}: {word}" for user, word in self.used_words])
        status_message = f"현재 단어: '{self.current_word}'\n" \
                         f"다음 단어는 '{self.current_word[-1]}'로 시작해야 해요.\n" \
                         f"{additional_message}\n\n" \
                         f"사용된 단어들:\n{previous_words}"

        # 이전 메시지 삭제
        if self.game_message:
            try:
                await self.game_message.delete()
            except discord.errors.NotFound:
                pass

        # 새 상태 메시지 전송
        self.game_message = await ctx.send(status_message, view=WordChainView(self))

    async def end_game(self, ctx_or_interaction, disable_buttons=False):
        """게임 종료와 함께 단어 기록을 보여줌"""
        self.current_word = None
        self.active_channel = None
        if self.game_message:
            try:
                await self.game_message.delete()
            except discord.errors.NotFound:
                pass

        word_list = " > ".join([f"{user}: {word}" for user, word in self.used_words])
        self.used_words = []
        embed = self.create_embed("게임 종료", f"끝말잇기 게임이 종료되었어요...\n사용된 단어들:\n{word_list}")
        
        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed)
        elif isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.followup.send(embed=embed)

        # 종료 시 버튼 비활성화
        if disable_buttons:
            view = WordChainStartView(self)
            view.disable_all_buttons()
            if isinstance(ctx_or_interaction, commands.Context):
                await ctx_or_interaction.message.edit(view=view)
            elif isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.edit_original_response(view=view)

    def create_embed(self, title, description):
        """임베드 메시지를 생성합니다."""
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        return embed

    @commands.command(name='끝말잇기')
    async def start_game(self, ctx):
        self.used_words = []
        self.current_word = None  # 첫 단어를 표시하지 않음
        self.active_channel = ctx.channel
        view = WordChainStartView(self)
        await ctx.send("끝말잇기 게임을 시작합니다. 아래 버튼을 사용하세요.", view=view)

    @commands.command(name='끝말잇기종료')
    async def manual_end_game(self, ctx):
        await self.end_game(ctx, disable_buttons=True)

class WordChainStartView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="시작", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel != self.game.active_channel:
            await interaction.response.send_message("끝말잇기 게임이 이 채널에서 활성화되지 않았습니다.", ephemeral=True)
            return

        # 첫 단어 설정 및 게임 상태 업데이트
        self.game.current_word = random.choice(self.game.word_list)
        self.game.used_words.append(('봇', self.game.current_word))
        await self.game.update_game_status(interaction.channel, "게임이 시작되었어요! 단어를 입력하려면 아래 버튼을 클릭하세요.")
        await interaction.response.defer()

    @discord.ui.button(label="종료", style=discord.ButtonStyle.danger)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel != self.game.active_channel:
            await interaction.response.send_message("끝말잇기 게임이 이 채널에서 활성화되지 않았습니다.", ephemeral=True)
            return

        # 상호작용을 지연시켜 상호작용 실패를 방지
        await interaction.response.defer()

        # 게임 종료 처리
        await self.game.end_game(interaction, disable_buttons=True)

        # 버튼 비활성화
        button.disabled = True
        self.children[0].disabled = True  # 시작 버튼도 비활성화
        await interaction.message.edit(view=self)

    def disable_all_buttons(self):
        """모든 버튼을 비활성화합니다."""
        for item in self.children:
            item.disabled = True

class WordChainView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="단어 입력", style=discord.ButtonStyle.primary)
    async def enter_word(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel != self.game.active_channel:
            await interaction.response.send_message("끝말잇기 게임이 이 채널에서 활성화되지 않았습니다.", ephemeral=True)
            return

        modal = WordChainModal(self.game, interaction.channel)
        await interaction.response.send_modal(modal)

# 봇 설정 함수
async def setup(bot):
    await bot.add_cog(WordChain(bot))