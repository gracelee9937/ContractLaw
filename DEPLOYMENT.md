# ContractLawProject - 배포 가이드

이 가이드는 ContractLawProject를 다양한 플랫폼에 배포하는 방법을 설명합니다.

## 배포 전 준비사항

### 1. API 키 설정
```bash
# .env 파일 생성 (env_template.txt 참고)
cp env_template.txt .env

# Gemini API 키 설정 (필수)
GEMINI_API_KEY=your_actual_api_key_here

# Hugging Face 토큰 설정 (선택)
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

### 2. 의존성 설치
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 패키지 설치
pip install -r requirements.txt
```

### 3. 로컬 테스트
```bash
# Flask 앱 실행
python flask_app.py

# 또는 Gradio 챗봇 실행
python src/chatbot/gradio_app.py
```

## 플랫폼별 배포 방법

### 1. Docker 컨테이너

#### Flask 앱 배포
```bash
# 이미지 빌드
docker build -t contract-law-project .

# 컨테이너 실행 (Flask)
docker run -p 5000:5000 \
  -e GEMINI_API_KEY="your_api_key" \
  contract-law-project
```

#### Gradio 앱 배포
```bash
# Gradio용 실행
docker run -p 7860:7860 \
  -e GEMINI_API_KEY="your_api_key" \
  contract-law-project \
  python src/chatbot/gradio_app.py
```

### 2. Railway

1. [Railway](https://railway.app/) 계정 생성
2. GitHub 레포지토리 연결
3. **Environment Variables** 설정:
   - `GEMINI_API_KEY`
   - `PORT=5000` (Flask의 경우)
4. 자동 배포 완료

### 3. Render

1. [Render](https://render.com/) 계정 생성
2. **New Web Service** 선택
3. GitHub 레포지토리 연결
4. 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python flask_app.py`
5. 환경변수 설정 후 배포

### 4. Heroku

1. [Heroku](https://heroku.com/) 계정 생성
2. Heroku CLI 설치 및 로그인
3. 앱 생성:
   ```bash
   heroku create your-app-name
   ```
4. 환경변수 설정:
   ```bash
   heroku config:set GEMINI_API_KEY="your_api_key"
   ```
5. 배포:
   ```bash
   git push heroku main
   ```

### 5. 로컬 개발 환경

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd ContractLawProject

# 2. 가상환경 설정
python -m venv .venv
.venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
# .env 파일 생성 및 API 키 설정

# 5. 앱 실행
python flask_app.py
```

## 배포 최적화 팁

### 1. 메모리 사용 최적화
```python
# config/settings.py에서 조정
RAG_CONFIG = {
    "chunk_size": 500,  # 더 작은 청크 크기
    "chunk_overlap": 100,
    "top_k_results": 3,  # 더 적은 검색 결과
    "similarity_threshold": 0.8
}
```

### 2. 모델 캐싱
```python
# 임베딩 모델 캐싱으로 로딩 시간 단축
from functools import lru_cache

@lru_cache(maxsize=1)
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
```

### 3. 데이터 전처리
실제 배포 시에는 ZIP 파일을 미리 추출하고 전처리된 텍스트 파일로 저장하여 초기 로딩 시간을 단축할 수 있습니다.

## 문제 해결

### 일반적인 오류들

#### 1. API 키 오류
```
Error: Gemini API key not found
```
**해결방법**: 환경변수가 올바르게 설정되었는지 확인

#### 2. 메모리 부족
```
ResourceExhaustedError: Out of memory
```
**해결방법**: 
- 청크 크기 줄이기
- 더 작은 임베딩 모델 사용
- 처리할 문서 수 제한

#### 3. 모델 로딩 실패
```
OSError: Can't load tokenizer
```
**해결방법**: 
- 네트워크 연결 확인
- requirements.txt의 transformers 버전 확인
- Hugging Face 토큰 설정

#### 4. Flask 포트 충돌
```
OSError: [Errno 98] Address already in use
```
**해결방법**:
```bash
# 포트 사용 중인 프로세스 확인
netstat -tulpn | grep :5000

# 프로세스 종료
kill -9 <process_id>
```

### 로그 확인 방법

#### Flask
```bash
# 로컬에서 디버깅 모드 실행
python flask_app.py
# 또는
export FLASK_ENV=development
python flask_app.py
```

#### Docker
```bash
# 컨테이너 로그 확인
docker logs container_name

# 실시간 로그 보기
docker logs -f container_name
```

## 성능 모니터링

### 1. 메모리 사용량
```python
import psutil

def check_memory():
    memory = psutil.virtual_memory()
    print(f"메모리 사용량: {memory.percent:.1f}%")
```

### 2. 응답 시간 측정
```python
import time

def timed_function():
    start_time = time.time()
    # 함수 실행
    end_time = time.time()
    print(f"처리 시간: {end_time - start_time:.2f}초")
```

## 보안 고려사항

### 1. API 키 보안
- 환경변수로 API 키 관리
- 소스 코드에 API 키 직접 입력 금지
- 정기적인 API 키 로테이션

### 2. HTTPS 설정
- 프로덕션 환경에서는 HTTPS 필수
- SSL 인증서 설정

### 3. 입력 검증
- 파일 업로드 시 파일 형식 검증
- 사용자 입력 데이터 검증

## 📞 지원

배포 관련 문제가 있을 경우:
1. GitHub Issues에 문제 보고
2. 로그와 오류 메시지 포함
3. 사용한 플랫폼과 설정 정보 제공

---

**참고**: 무료 플랫폼의 경우 리소스 제한이 있으므로, 큰 데이터셋이나 복잡한 모델 사용 시 성능이 제한될 수 있습니다. 