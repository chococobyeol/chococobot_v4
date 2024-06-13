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
            label="단어를 입력하세요...",
            placeholder="여기에 단어를 입력하세요...",
            max_length=10  
        )
        self.add_item(self.word_input)

    async def on_submit(self, interaction: discord.Interaction):
        word = self.word_input.value.strip()
        user = interaction.user.display_name  

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
            await self.game.update_game_status(self.ctx, f"봇의 단어는 '{bot_word}'에요...")
        else:
            await self.game.end_game(interaction, "봇이 더 이상 단어를 찾을 수 없어요... 사용자가 승리했어요...", delete_buttons=True)

        await interaction.response.defer()

class WordChainGame:
    def __init__(self, word_list):
        self.word_list = word_list
        self.used_words = []
        self.current_word = None
        self.active_channel = None
        self.game_message = None
        self.start_message = None

    def valid_word(self, word):
        if len(word) < 2:
            return False
        
        original_word = self.apply_dueum_law(word)
        return (original_word in self.word_list or word in self.word_list) and word not in [w for _, w in self.used_words]

    def apply_dueum_law(self, word):
        dueum_law_dict = {
            '녀': '여', '뇨': '요', '뉴': '유', '니': '이',
            '랴': '야', '려': '여', '례': '예', '료': '요', '류': '유', '리': '이',
            '라': '나', '래': '내', '로': '노', '뢰': '뇌', '루': '누', '르': '느'
        }
        first_char = word[0]
        if len(word) > 1 and self.is_consonant(word[1]):
            return word
        return dueum_law_dict.get(first_char, first_char) + word[1:]

    def is_consonant(self, char):
        return ord(char) in range(0x3131, 0x318F)

    def matches_dueum(self, last_word, first_char):
        possible_start = self.apply_dueum_law(last_word[-1])
        return first_char == possible_start or first_char == last_word[-1]

    def next_word(self, last_letter):
        candidates = [word for word in self.word_list if word.startswith(last_letter) and word not in [w for _, w in self.used_words]]
        if not candidates:
            modified_last_letter = self.apply_dueum_law(last_letter)
            candidates = [word for word in self.word_list if word.startswith(modified_last_letter) and word not in [w for _, w in self.used_words]]
        return random.choice(candidates) if candidates else None

    async def update_game_status(self, ctx, additional_message=""):
        previous_words = self.get_used_words()
        status_message = f"현재 단어: '{self.current_word}'\n" \
                         f"다음 단어는 '{self.current_word[-1]}'로 시작해야 해요...\n" \
                         f"{additional_message}\n\n" \
                         f"사용된 단어들:\n{previous_words}"

        if self.game_message:
            try:
                await self.game_message.delete()
            except discord.errors.NotFound:
                self.game_message = None

        self.game_message = await ctx.send(status_message, view=WordChainView(self))

    def get_used_words(self):
        return " > ".join([f"{user}: {word}" for user, word in self.used_words])

    async def end_game(self, ctx_or_interaction, additional_message="", delete_buttons=False):
        self.current_word = None
        self.active_channel = None

        word_list = self.get_used_words()
        self.used_words = []

        embed = self.create_embed("게임 종료", f"{additional_message}\n\n사용된 단어들:\n{word_list}")

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed)
            if self.start_message:
                try:
                    await self.start_message.delete()
                except discord.errors.NotFound:
                    pass
            if self.game_message:
                try:
                    await self.game_message.delete()
                except discord.errors.NotFound:
                    pass
        elif isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.channel.send(embed=embed)
            if ctx_or_interaction.message:
                try:
                    await ctx_or_interaction.message.delete()
                except discord.errors.NotFound:
                    pass

        if delete_buttons:
            if self.start_message:
                try:
                    await self.start_message.delete()
                except discord.errors.NotFound:
                    pass
            if self.game_message:
                try:
                    await self.game_message.delete()
                except discord.errors.NotFound:
                    pass

    def create_embed(self, title, description):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        return embed

class WordChain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_list = self.load_words('words.txt')
        self.server_games = {}  # 서버별로 게임 상태를 저장할 딕셔너리

    def load_words(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]

    def get_game(self, guild_id):
        if guild_id not in self.server_games:
            self.server_games[guild_id] = WordChainGame(self.word_list)
        return self.server_games[guild_id]

    @commands.command(name='끝말잇기')
    async def start_game(self, ctx):
        game = self.get_game(ctx.guild.id)
        if game.active_channel:
            await ctx.send("끝말잇기 게임이 이미 진행 중입니다.")
            return

        game.used_words = []
        game.current_word = None
        game.active_channel = ctx.channel
        view = WordChainStartView(game)
        game.start_message = await ctx.send("끝말잇기 게임을 시작합니다. 아래 버튼을 사용하세요.", view=view)

    @commands.command(name='끝말잇기종료')
    async def manual_end_game(self, ctx):
        game = self.get_game(ctx.guild.id)
        await game.end_game(ctx, "게임이 수동으로 종료되었습니다.", delete_buttons=True)

class WordChainStartView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="시작", style=discord.ButtonStyle.success)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel != self.game.active_channel:
            await interaction.response.send_message("끝말잇기 게임이 이 채널에서 활성화되지 않았습니다.", ephemeral=True)
            return

        self.game.current_word = random.choice(self.game.word_list)
        self.game.used_words.append(('봇', self.game.current_word))
        await self.game.update_game_status(interaction.channel, "게임이 시작되었어요... 단어를 입력하려면 아래 버튼을 클릭하세요...")
        await interaction.response.defer()

    @discord.ui.button(label="종료", style=discord.ButtonStyle.danger)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel != self.game.active_channel:
            await interaction.response.send_message("끝말잇기 게임이 이 채널에서 활성화되지 않았습니다.", ephemeral=True)
            return

        await self.game.end_game(interaction, "게임이 종료되었습니다.", delete_buttons=True)
        await interaction.response.defer()

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

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True
        for button in self.children:
            self.remove_item(button)

async def setup(bot):
    await bot.add_cog(WordChain(bot))