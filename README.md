# 디스코드 봇 (Discord Bot)

이 저장소는 `discord.py` 라이브러리를 사용하여 구현된 디스코드 봇입니다. 봇은 음성 채널 관리, 로스트아크 게임 캐릭터 닉네임 처리, 채팅 관리 명령어 등을 제공합니다. 또한, 더미 HTTP 서버를 포함하여 봇이 항상 실행되도록 지원합니다.

## 주요 기능

- **음성 관리**: 사용자가 음성 채널에 봇을 초대하고, 텍스트를 음성으로 변환(TTS)하여 음성 채널에서 재생할 수 있습니다.
- **로스트아크 기능**: 사용자의 로스트아크 게임 캐릭터 정보를 조회하고, 서버의 닉네임으로 업데이트합니다.
- **채팅 관리**: 채팅 메시지를 정리하는 명령어를 제공합니다.
- **더미 HTTP 서버**: 봇이 항상 활성 상태를 유지하도록 지원하는 서버를 실행합니다.

## 설치 및 설정

### 사전 요구사항

- Python 3.7 이상
- `discord.py` 라이브러리
- `gtts` 라이브러리 (텍스트 음성 변환용)
- `aiohttp` 및 `beautifulsoup4` (웹 스크래핑용)
- 환경 변수 `DISCORD_TOKEN`에 봇 토큰 설정

### 설치

1. 이 저장소를 클론합니다:
   ```bash
   git clone https://github.com/your-repo/discord-bot.git
   cd discord-bot
   ```

2. 가상 환경을 생성하고 활성화합니다 (권장):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows에서는 venv\Scripts\activate
   ```

3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수를 설정합니다:
   ```bash
   export DISCORD_TOKEN=your-bot-token
   export PORT=8000  # 선택 사항: 기본값은 8000
   ```

### 봇 실행

메인 스크립트를 실행하여 봇을 시작합니다:
```bash
python main.py
```

## 명령어

### 음성 관리

- `!말 <텍스트>`: 주어진 텍스트를 음성으로 변환하여 사용자의 현재 음성 채널에서 재생합니다.
- `!저리가`: 봇이 음성 채널에서 나가게 합니다.
- `!이리와`: 봇을 사용자의 현재 음성 채널로 초대합니다.

### 로스트아크 기능

- `!로아닉`: 사용자의 로스트아크 캐릭터 이름을 등록하거나 등록을 해제할 수 있습니다. 봇은 등록된 캐릭터 이름, 클래스, 레벨로 디스코드 닉네임을 업데이트합니다.

### 채팅 관리

- `!청소 <개수>`: 사용자의 최근 메시지 중 지정된 개수를 삭제합니다.
- `!대청소 <개수>`: 채팅의 최근 메시지를 지정된 개수만큼 삭제합니다(관리자 전용).
- `!따라하기 <메시지>`: 봇이 주어진 메시지를 그대로 따라합니다.

## 코드 구조

- **main.py**: 봇을 초기화하고 명령어를 설정하며, 더미 HTTP 서버를 시작하는 메인 스크립트입니다.
- **voice_management.py**: 음성 채널 관리 및 TTS 기능을 구현합니다.
- **lostark_features.py**: 로스트아크 닉네임 관리 및 갱신을 처리합니다.
- **chat_management.py**: 채팅 메시지 관리를 위한 명령어를 제공합니다.

## 기여 방법

1. 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/YourFeature`).
3. 변경 사항을 커밋합니다 (`git commit -m '새 기능 추가'`).
4. 브랜치에 푸시합니다 (`git push origin feature/YourFeature`).
5. Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 문의

문의 사항이나 문제가 있을 경우 GitHub에서 이슈를 열거나 유지 관리자에게 연락해 주세요.

---

이 `README.md` 파일은 프로젝트의 특성에 맞게 자유롭게 수정할 수 있습니다.
