"""
ContractLawProject Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

# Auto-Connection API Configuration (자동 연동)
AUTO_API_ENABLED = True  # API 자동 연동 활성화
DEFAULT_GEMINI_API_KEY = "AIzaSyC7X4mN8pK2vL9qR5tH1wJ6uY3sE7nF2gA"  # 기본 제공 API 키 (데모용)
DEMO_MODE_ENABLED = True  # 데모 모드 지원

# API Key Priority (우선순위)
# 1. 사용자 직접 입력 키
# 2. 환경변수 키  
# 3. 기본 제공 키 (AUTO_API_ENABLED=True일 때)

def get_api_key():
    """API 키를 우선순위에 따라 반환"""
    # 1. 환경변수에서 로드된 사용자 키
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 20:
        return GEMINI_API_KEY.strip()
    
    # 2. 자동 연동이 활성화된 경우 기본 키 제공
    if AUTO_API_ENABLED and DEFAULT_GEMINI_API_KEY:
        return DEFAULT_GEMINI_API_KEY
    
    # 3. 모두 없으면 None 반환
    return None

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
GEMINI_MODEL = "gemini-1.5-flash"

# File Paths
DATA_DIR = "data"
TEMPLATES_DIR = "templates"
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
LEGAL_DATA_DIR = "."  # Root directory with Korean legal datasets

# Supported file types for document upload
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]

# Data Directories - 법률 문서가 위치한 디렉토리들
DATA_DIRECTORIES = [
    "05.계약 법률 문서 서식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터"
]

# Contract Categories
CONTRACT_CATEGORIES = {
    "business": {
        "name": "비즈니스/기업",
        "subcategories": ["기업운영", "주식/주주", "투자"],
        "files": [
            "TS_경제_경영_기업운영.zip",
            "TS_경제_경영_주식_주주.zip", 
            "TS_경제_경영_투자.zip"
        ]
    },
    "employment": {
        "name": "인사/고용",
        "subcategories": ["고용계약", "인사관리"],
        "files": [
            "TS_인사_고용_노무_고용계약.zip",
            "TS_인사_고용_노무_인사관리.zip"
        ]
    },
    "real_estate": {
        "name": "부동산",
        "subcategories": ["매매", "임대차", "개발/공사"],
        "files": [
            "TS_부동산매매_임대차_부동산매매.zip",
            "TS_부동산매매_임대차_부동산임대.zip",
            "TS_부동산개발_공사_건설계약.zip",
            "TS_부동산개발_공사_공사계약.zip",
            "TS_부동산개발_공사_하도급계약.zip"
        ]
    },
    "financial": {
        "name": "금융/채권",
        "subcategories": ["금전거래", "채권채무"],
        "files": [
            "TS_금전소비대차_채권_채무_금전거래.zip",
            "TS_금전소비대차_채권_채무_채권_채무계약.zip"
        ]
    },
    "sales": {
        "name": "매매/공급",
        "subcategories": ["물품거래"],
        "files": [
            "TS_매매_구매_납품_공급_물품거래.zip"
        ]
    },
    "services": {
        "name": "용역/컨설팅",
        "subcategories": ["용역", "지적재산권", "컨설팅"],
        "files": [
            "TS_재산권사용_용역_컨설팅_용역.zip",
            "TS_재산권사용_용역_컨설팅_지적재산권.zip",
            "TS_재산권사용_용역_컨설팅_컨설팅.zip"
        ]
    },
    "trade": {
        "name": "무역",
        "subcategories": ["국제거래"],
        "files": [
            "TS_무역_수출_입계약_국제거래.zip"
        ]
    },
    "agency": {
        "name": "대리점/프랜차이즈",
        "subcategories": ["대리점", "프랜차이즈"],
        "files": [
            "TS_대리점_프랜차이즈_대리점.zip",
            "TS_대리점_프랜차이즈_프랜차이즈.zip"
        ]
    },
    "general": {
        "name": "기타/약관",
        "subcategories": ["표준약관", "기타계약"],
        "files": [
            "TS_약관에의한계약_기타계약_표준약관.zip",
            "TS_약관에의한계약_기타계약_기타계약.zip"
        ]
    }
}

# Contract clause templates by category
CONTRACT_CLAUSES = {
    "business": {
        "name": "비즈니스/기업운영",
        "clauses": {
            "parties": {
                "title": "제1조 (당사자)",
                "content": "갑: [회사명]\n을: [회사명 또는 개인명]\n\n위 당사자들은 아래와 같이 계약을 체결한다.",
                "description": "계약 당사자의 기본 정보를 명시하는 조항"
            },
            "purpose": {
                "title": "제2조 (목적)",
                "content": "본 계약은 [구체적인 목적]을 위하여 체결한다.",
                "description": "계약의 목적과 범위를 명확히 하는 조항"
            },
            "term": {
                "title": "제3조 (계약기간)",
                "content": "본 계약의 기간은 [시작일]부터 [종료일]까지로 한다.\n단, 계약기간 만료 1개월 전까지 서면으로 통지하지 아니하면 동일한 조건으로 1년간 자동 연장된다.",
                "description": "계약의 유효기간과 연장 조건을 규정하는 조항"
            },
            "payment": {
                "title": "제4조 (대금 및 지급방법)",
                "content": "갑은 을에게 [금액]을 지급한다.\n지급방법: [지급방법 상세]\n지급시기: [지급시기]",
                "description": "계약 대금의 금액, 지급방법, 시기를 규정하는 조항"
            },
            "obligations": {
                "title": "제5조 (의무사항)",
                "content": "갑의 의무:\n- [갑의 의무사항]\n\n을의 의무:\n- [을의 의무사항]",
                "description": "각 당사자의 의무와 책임을 명시하는 조항"
            },
            "termination": {
                "title": "제6조 (해지조건)",
                "content": "다음의 경우 본 계약을 해지할 수 있다:\n1. 상대방이 본 계약을 중대하게 위반한 경우\n2. 상대방이 파산, 화의, 회사정리절차를 신청한 경우\n3. 기타 계약 목적 달성이 불가능한 경우",
                "description": "계약 해지 조건과 절차를 규정하는 조항"
            },
            "damages": {
                "title": "제7조 (손해배상)",
                "content": "계약 위반으로 인한 손해배상은 민법의 규정에 따른다.\n단, 위약금은 [금액]으로 한다.",
                "description": "계약 위반 시 손해배상과 위약금을 규정하는 조항"
            },
            "dispute": {
                "title": "제8조 (분쟁해결)",
                "content": "본 계약과 관련하여 분쟁이 발생한 경우, 갑의 주소지 관할법원을 제1심 관할법원으로 한다.",
                "description": "분쟁 발생 시 해결 방법과 관할법원을 규정하는 조항"
            }
        }
    },
    "services": {
        "name": "용역/컨설팅",
        "clauses": {
            "parties": {
                "title": "제1조 (당사자)",
                "content": "갑: [의뢰인]\n을: [컨설팅업체]\n\n위 당사자들은 아래와 같이 용역계약을 체결한다.",
                "description": "용역계약 당사자의 기본 정보를 명시하는 조항"
            },
            "service_scope": {
                "title": "제2조 (용역의 범위)",
                "content": "을이 갑에게 제공할 용역의 범위는 다음과 같다:\n1. [용역 내용 1]\n2. [용역 내용 2]\n3. [용역 내용 3]",
                "description": "컨설팅 용역의 구체적인 범위와 내용을 규정하는 조항"
            },
            "deliverables": {
                "title": "제3조 (산출물)",
                "content": "을은 용역 완료 후 다음의 산출물을 갑에게 제출한다:\n- [산출물 1]\n- [산출물 2]\n- [산출물 3]",
                "description": "용역 완료 시 제출할 산출물을 명시하는 조항"
            },
            "schedule": {
                "title": "제4조 (일정)",
                "content": "용역의 수행 일정은 다음과 같다:\n- 착수일: [날짜]\n- 중간보고: [날짜]\n- 완료일: [날짜]",
                "description": "용역 수행 일정과 마일스톤을 규정하는 조항"
            },
            "fee": {
                "title": "제5조 (용역비)",
                "content": "용역비는 총 [금액]으로 하며, 지급방법은 다음과 같다:\n- 계약금: [금액] (계약 체결 시)\n- 중도금: [금액] (중간보고 완료 시)\n- 잔금: [금액] (최종 산출물 제출 시)",
                "description": "용역비의 총액과 분할 지급 조건을 규정하는 조항"
            },
            "confidentiality": {
                "title": "제6조 (비밀유지)",
                "content": "을은 본 용역 수행 과정에서 알게 된 갑의 영업비밀, 기술정보 등 모든 정보를 엄격히 비밀유지하여야 한다.\n본 조항은 계약 종료 후에도 3년간 유효하다.",
                "description": "용역 수행 중 알게 된 정보의 비밀유지 의무를 규정하는 조항"
            },
            "intellectual_property": {
                "title": "제7조 (지적재산권)",
                "content": "본 용역을 통해 창출된 모든 지적재산권은 갑에게 귀속된다.\n을은 갑의 사전 서면 동의 없이 이를 제3자에게 제공하거나 활용할 수 없다.",
                "description": "용역 결과물의 지적재산권 귀속을 규정하는 조항"
            },
            "quality_assurance": {
                "title": "제8조 (품질보증)",
                "content": "을은 용역의 품질을 보증하며, 갑의 요청에 따라 수정 및 보완을 무상으로 수행한다.\n보증기간은 용역 완료일로부터 1년간으로 한다.",
                "description": "용역 품질 보증과 수정 의무를 규정하는 조항"
            }
        }
    },
    "employment": {
        "name": "인사/고용/노무",
        "clauses": {
            "parties": {
                "title": "제1조 (당사자)",
                "content": "갑: [회사명]\n을: [근로자명]\n\n위 당사자들은 아래와 같이 근로계약을 체결한다.",
                "description": "근로계약 당사자의 기본 정보를 명시하는 조항"
            },
            "position": {
                "title": "제2조 (근로조건)",
                "content": "을의 근로조건은 다음과 같다:\n- 직종: [직종]\n- 근무시간: [근무시간]\n- 근무장소: [근무장소]",
                "description": "근로자의 직종, 근무시간, 근무장소를 규정하는 조항"
            },
            "salary": {
                "title": "제3조 (임금)",
                "content": "을의 임금은 다음과 같다:\n- 기본급: [금액]\n- 수당: [수당 내역]\n- 지급일: 매월 [일자]",
                "description": "근로자의 임금 체계와 지급 조건을 규정하는 조항"
            },
            "working_hours": {
                "title": "제4조 (근무시간)",
                "content": "을의 근무시간은 다음과 같다:\n- 정규근무: [시간]\n- 휴식시간: [시간]\n- 초과근무: 필요시 사전 승인 후",
                "description": "근무시간과 휴식시간을 규정하는 조항"
            },
            "vacation": {
                "title": "제5조 (휴가)",
                "content": "을의 휴가는 근로기준법에 따른다:\n- 연차휴가: [일수]\n- 공가: [조건]\n- 병가: [조건]",
                "description": "휴가 종류와 조건을 규정하는 조항"
            },
            "confidentiality": {
                "title": "제6조 (비밀유지)",
                "content": "을은 재직 중 및 퇴직 후에도 회사의 영업비밀, 고객정보 등 모든 정보를 비밀유지하여야 한다.",
                "description": "회사 정보의 비밀유지 의무를 규정하는 조항"
            },
            "non_compete": {
                "title": "제7조 (경업금지)",
                "content": "을은 재직 중 및 퇴직 후 [기간]간 동종업계에 종사할 수 없다.\n위반 시 [금액]의 위약금을 지급한다.",
                "description": "경업금지 기간과 위약금을 규정하는 조항"
            },
            "termination": {
                "title": "제8조 (계약해지)",
                "content": "계약해지는 다음과 같이 한다:\n- 갑의 해고: 사전 30일 통지\n- 을의 사직: 사전 30일 통지\n- 즉시해고: 중대한 위반 시",
                "description": "계약 해지 조건과 절차를 규정하는 조항"
            }
        }
    },
    "real_estate": {
        "name": "부동산매매/임대차",
        "clauses": {
            "parties": {
                "title": "제1조 (당사자)",
                "content": "갑: [임대인]\n을: [임차인]\n\n위 당사자들은 아래와 같이 임대차계약을 체결한다.",
                "description": "임대차계약 당사자의 기본 정보를 명시하는 조항"
            },
            "property": {
                "title": "제2조 (임대물건)",
                "content": "임대물건의 표시:\n- 소재지: [주소]\n- 면적: [면적]\n- 용도: [용도]\n- 구조: [구조]",
                "description": "임대할 부동산의 기본 정보를 명시하는 조항"
            },
            "term": {
                "title": "제3조 (임대기간)",
                "content": "임대기간은 [시작일]부터 [종료일]까지로 한다.\n갑은 임대기간 만료 6개월 전까지 갱신 여부를 통지한다.",
                "description": "임대기간과 갱신 조건을 규정하는 조항"
            },
            "rent": {
                "title": "제4조 (임대료)",
                "content": "임대료는 월 [금액]으로 하며, 매월 [일자]까지 을이 갑에게 지급한다.\n지급방법: [지급방법]",
                "description": "임대료 금액과 지급 조건을 규정하는 조항"
            },
            "deposit": {
                "title": "제5조 (보증금)",
                "content": "보증금은 [금액]으로 하며, 계약 체결 시 을이 갑에게 지급한다.\n계약 종료 시 원상복구 확인 후 반환한다.",
                "description": "보증금 금액과 반환 조건을 규정하는 조항"
            },
            "maintenance": {
                "title": "제6조 (관리 및 수선)",
                "content": "갑의 의무: 구조상 수선\n을의 의무: 일상적 관리 및 경미한 수선\n수선비용: [비용 분담 원칙]",
                "description": "부동산 관리와 수선 의무를 규정하는 조항"
            },
            "use": {
                "title": "제7조 (사용 및 제한)",
                "content": "을은 임대물건을 [용도]로만 사용하여야 한다.\n갑의 사전 서면 동의 없이 용도 변경, 전대, 양도할 수 없다.",
                "description": "임대물건의 사용 용도와 제한사항을 규정하는 조항"
            },
            "return": {
                "title": "제8조 (반환)",
                "content": "계약 종료 시 을은 임대물건을 원상복구하여 갑에게 반환한다.\n반환 시점: [반환 시점]\n원상복구 범위: [복구 범위]",
                "description": "계약 종료 시 임대물건 반환 조건을 규정하는 조항"
            }
        }
    }
}

# Risk Assessment Configuration
RISK_FACTORS = [
    "payment_terms",
    "termination_clauses", 
    "liability_limitations",
    "intellectual_property",
    "confidentiality",
    "dispute_resolution",
    "force_majeure",
    "compliance_requirements"
]

# UI Configuration
STREAMLIT_CONFIG = {
    "page_title": "ContractLawProject",
    "page_icon": "C",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 2000,
    "chunk_overlap": 400,
    "top_k_results": 5,
    "similarity_threshold": 0.7
} 