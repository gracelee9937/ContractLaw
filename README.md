# ContractLawProject

한국 법률 데이터셋을 활용한 AI 기반 계약서 분석 및 관리 시스템

## 주요 기능

### 1. AI 계약서 분석 챗봇
- **RAG 기반 AI 어시스턴트**로 계약서 Q&A 제공
- **조항 추출** 및 법적 해석
- **리스크 평가** 및 준수성 검사
- **한국어/영어 다국어 지원**

### 2. 계약서 분석 웹 애플리케이션
- **PDF 계약서 업로드** 및 처리
- **시각적 대시보드**를 통한 리스크 점수화
- **누락된 조항 감지**
- **조항 요약** 및 분석
- **법적 준수성 검사**

### 3. 계약서 템플릿 시스템
- **12개 계약서 템플릿** 지원:
  - 부동산 (매매계약서, 임대차계약서, 건설공사계약서)
  - 고용 (고용계약서, 시간제 근로계약서, 컨설팅 계약서)
  - 기업 (투자계약서, 파트너십 계약서, 기밀유지계약서)
  - 금전거래 (대출계약서, 보증계약서)
  - 기타 (프랜차이즈계약서, 지급계약서)
- **템플릿 미리보기** 및 맞춤화
- **DOCX 다운로드** 기능

### 4. Responsible AI 시스템
- **안전성 검증**: 파일 및 내용 안전성 검사
- **프라이버시 보호**: 개인정보 비식별화, 데이터 암호화
- **지속가능성 지표**: 캐시 히트율, 메모리 사용량, 처리시간 모니터링
- **설명 가능성**: AI 분석 결과에 대한 상세 설명 제공
- **감사 로그**: 시스템 사용 내역 추적

## 빠른 시작

### 설치

```bash
# 1. 프로젝트 디렉토리로 이동
cd ContractLawProject

# 2. 가상환경 생성 (권장)
python -m venv .venv

# 3. 가상환경 활성화
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. 필요한 패키지 설치
pip install -r requirements.txt
```

### 애플리케이션 실행

```bash
# Flask 웹 애플리케이션 실행 (자동으로 브라우저 열림)
python flask_app.py

# 또는 개별 컴포넌트 실행:
python src/chatbot/gradio_app.py  # Gradio 챗봇 인터페이스
```

### 접속 주소
- **메인 페이지**: http://localhost:5000
- **AI 챗봇**: http://localhost:5000/chatbot
- **계약서 분석**: http://localhost:5000/analyzer
- **템플릿**: http://localhost:5000/templates
- **Responsible AI**: http://localhost:5000/responsible-ai

## 프로젝트 구조

```
ContractLawProject/
├── flask_app.py                 # 메인 Flask 애플리케이션
├── src/
│   ├── chatbot/                # RAG 기반 계약서 챗봇
│   │   └── gradio_app.py       # Gradio 챗봇 인터페이스
│   └── utils/                  # 공유 유틸리티
│       ├── rag_system.py       # RAG 시스템
│       ├── api_manager.py      # API 키 관리
│       ├── document_processor.py # 문서 처리
│       ├── immediate_features.py # 즉시 사용 기능
│       └── responsible_ai.py   # Responsible AI 시스템
├── data/                       # 법률 데이터셋 및 임베딩
├── templates/                  # 계약서 템플릿 파일들
├── config/                     # 설정 파일들
└── 05.계약 법률 문서 서식 데이터/  # 한국 법률 데이터셋
```

## 🛠 기술 스택

- **백엔드**: Python, Flask, LangChain, Faiss
- **AI 모델**: Google Gemini API, Sentence Transformers
- **프론트엔드**: HTML/CSS/JavaScript, Gradio
- **문서 처리**: PyMuPDF, python-docx
- **데이터 분석**: Pandas, Matplotlib

## 법률 데이터 소스

- **민법 훈련 데이터**: 판결문, 법령, 심결례, 유권해석
- **계약서 템플릿**: 12개 카테고리, 다양한 계약서 템플릿
- **사례 연구**: 법적 선례 분석 데이터
- **문서 분석**: 금융 및 법률 문서 데이터셋

## 설정

`.env` 파일 생성:
```
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

## 배포

다음 플랫폼에서 배포 가능:
- **Docker 컨테이너**
- **Railway/Render**
- **Heroku**
- **로컬 개발 환경**

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.

## 라이선스

이 프로젝트는 한국 법률 데이터셋을 사용하며 적절한 데이터 사용 가이드라인을 따릅니다.



## 📞 지원

법률 데이터셋이나 구현에 대한 질문이 있으시면 이 저장소에 이슈를 생성해 주세요. 