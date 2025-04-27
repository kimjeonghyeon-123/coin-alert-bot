# 베이스 이미지 설정 (Python 3.10 환경)
FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 컨테이너 안으로 복사
COPY . .

# 필요 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 시작 파일 지정 (main.py)
CMD ["python", "main.py"]

