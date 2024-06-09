# Python 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# ffmpeg 설치 (TTS 기능을 위해 필요할 수 있음)
RUN apt-get update && apt-get install -y ffmpeg

# 현재 디렉토리 내용을 /app에 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 디스코드 봇 스크립트 실행
CMD ["python", "main.py"]