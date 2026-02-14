"""
Background Initialization Manager - Simple Version
기존 rag_system과 호환되는 간단한 백그라운드 초기화 매니저
"""

import threading
import time
from typing import Dict, Any, Callable
from .rag_system import rag_system  # 기존 rag_system 인스턴스 사용
from .api_manager import api_manager

class BackgroundInitManager:
    """간단한 백그라운드 초기화 매니저"""
    
    def __init__(self):
        self.rag_system = rag_system  # 기존 전역 인스턴스 사용
        self.initialization_thread = None
        self.is_initializing = False
        self.initialization_complete = False
        
        # 초기화 상태 추적
        self.status = {
            'basic_features': True,      # 즉시 사용 가능
            'api_ready': False,          # API 키 로드 완료
            'document_cache': False,     # 문서 캐시 로드 완료
            'vector_store': False,       # 벡터 스토어 준비 완료
            'ai_chatbot': False,         # AI 챗봇 활성화 완료
            'full_system': False         # 전체 시스템 완료
        }
        
        # 진행률 추적
        self.progress = {
            'current_step': 0,
            'total_steps': 5,
            'message': '시스템 준비 중...',
            'percentage': 0
        }
        
        # 상태 업데이트 콜백들
        self.status_callbacks = []
    
    def add_status_callback(self, callback: Callable[[Dict], None]):
        """상태 업데이트 콜백 추가"""
        self.status_callbacks.append(callback)
    
    def _update_status(self, step: str, message: str, is_complete: bool = False):
        """상태 업데이트 및 콜백 호출"""
        if is_complete:
            self.status[step] = True
            self.progress['current_step'] += 1
        
        self.progress['message'] = message
        # 진행률을 100%로 제한
        raw_percentage = int((self.progress['current_step'] / self.progress['total_steps']) * 100)
        self.progress['percentage'] = min(100, max(0, raw_percentage))
        
        # 콜백 호출 (백그라운드 스레드에서 안전하게)
        for callback in self.status_callbacks:
            try:
                # 백그라운드 스레드에서는 streamlit 세션 상태에 접근할 수 없음
                # 따라서 콜백 오류를 무시하고 계속 진행
                callback({
                    'status': self.status.copy(),
                    'progress': self.progress.copy(),
                    'step': step,
                    'message': message
                })
            except Exception as e:
                # 백그라운드 스레드에서의 세션 상태 접근 오류는 무시
                if "ScriptRunContext" not in str(e) and "session_state" not in str(e):
                    print(f"상태 콜백 오류: {e}")
                # 아니면 조용히 넘어감
    
    def start_background_initialization(self):
        """백그라운드 초기화 시작"""
        if self.initialization_thread is None or not self.initialization_thread.is_alive():
            self.is_initializing = True
            self.initialization_complete = False
            
            self.initialization_thread = threading.Thread(
                target=self._background_initialization,
                daemon=True,
                name="BackgroundInit"
            )
            self.initialization_thread.start()
            print(" 백그라운드 초기화가 시작되었습니다.")
    
    def _background_initialization(self):
        """백그라운드에서 단계별 초기화 실행"""
        try:
            # 1단계: API 키 준비
            self._update_status('api_ready', ' API 키 로드 중...')
            if self._setup_api():
                self._update_status('api_ready', ' API 키 준비 완료', True)
                time.sleep(0.5)
            
            # 2단계: 문서 캐시 로드
            self._update_status('document_cache', ' 문서 캐시 로드 중...')
            if self._load_document_cache():
                self._update_status('document_cache', ' 문서 캐시 로드 완료', True)
                time.sleep(0.5)
            
            # 3단계: 벡터 스토어 준비
            self._update_status('vector_store', ' 벡터 스토어 준비 중...')
            if self._prepare_vector_store():
                self._update_status('vector_store', ' 벡터 스토어 준비 완료', True)
                time.sleep(0.5)
            
            # 4단계: AI 챗봇 활성화
            self._update_status('ai_chatbot', ' AI 챗봇 활성화 중...')
            if self._activate_ai_chatbot():
                self._update_status('ai_chatbot', ' AI 챗봇 활성화 완료', True)
                time.sleep(0.5)
            
            # 5단계: 전체 시스템 완료
            self._update_status('full_system', ' 모든 기능 사용 가능!', True)
            
            self.initialization_complete = True
            self.is_initializing = False
            
            print(" 백그라운드 초기화가 완료되었습니다!")
            
        except Exception as e:
            self.is_initializing = False
            self._update_status('error', f' 초기화 오류: {str(e)}')
            print(f" 백그라운드 초기화 오류: {e}")
    
    def _setup_api(self) -> bool:
        """API 키 설정"""
        try:
            api_key = api_manager.load_api_key('gemini')
            if api_key:
                import os
                os.environ['GEMINI_API_KEY'] = api_key
                return True
            return False
        except Exception as e:
            print(f"API 설정 오류: {e}")
            return False
    
    def _load_document_cache(self) -> bool:
        """문서 캐시 로드 (간단 버전)"""
        try:
            # 캐시 상태 확인
            cache_status = self.rag_system.check_cache_available()
            
            if cache_status['documents']:
                # 캐시가 있으면 로드
                success = self.rag_system.load_from_cache()
                if success:
                    print(" 문서 캐시 로드 성공")
                    return True
            
            # 캐시가 없으면 빠른 생성
            return self._create_fast_cache()
            
        except Exception as e:
            print(f"문서 캐시 로드 오류: {e}")
            return False
    
    def _create_fast_cache(self) -> bool:
        """빠른 캐시 생성"""
        try:
            from config.settings import DATA_DIRECTORIES
            
            # 진행률 콜백
            def progress_callback(percentage, message):
                self._update_status('document_cache', f' {message}')
            
            # 빠른 문서 로드
            success = self.rag_system.load_legal_documents(
                data_directories=DATA_DIRECTORIES,
                progress_callback=progress_callback,
                max_docs=3000,  # 빠른 로드를 위해 제한
                time_limit=15
            )
            
            return success
            
        except Exception as e:
            print(f"빠른 캐시 생성 오류: {e}")
            return False
    
    def _prepare_vector_store(self) -> bool:
        """벡터 스토어 준비"""
        try:
            # 벡터 스토어가 이미 있으면 로드
            cache_status = self.rag_system.check_cache_available()
            if cache_status['embeddings']:
                success = self.rag_system.load_vector_store()
                if success:
                    return True
            
            # 없으면 생성
            def progress_callback(percentage, message):
                self._update_status('vector_store', f' {message}')
            
            success = self.rag_system.build_vector_store(
                force_rebuild=False,
                progress_callback=progress_callback,
                batch_size=200
            )
            
            return success
            
        except Exception as e:
            print(f"벡터 스토어 준비 오류: {e}")
            return False
    
    def _activate_ai_chatbot(self) -> bool:
        """AI 챗봇 활성화"""
        try:
            # 모델 초기화
            if not self.rag_system.llm:
                self.rag_system._initialize_models()
            
            # QA 체인 설정
            success = self.rag_system.setup_qa_chain()
            
            if success:
                # QA 시스템 테스트 실행
                print(" AI 챗봇 기능 테스트 중...")
                test_success = self.rag_system.test_qa_system()
                if test_success:
                    print(" AI 챗봇이 성공적으로 활성화되었습니다!")
                else:
                    print(" AI 챗봇 테스트에서 일부 문제가 발견되었지만 기본 기능은 사용 가능합니다.")
                
                return True
            else:
                print(" QA 체인 설정에 실패했습니다.")
                return False
            
        except Exception as e:
            print(f"AI 챗봇 활성화 오류: {e}")
            return False
    
    def get_rag_system(self):
        """RAG 시스템 반환"""
        return self.rag_system
    
    def is_feature_ready(self, feature: str) -> bool:
        """특정 기능이 준비되었는지 확인"""
        return self.status.get(feature, False)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """현재 상태 요약 반환"""
        return {
            'status': self.status.copy(),
            'progress': self.progress.copy(),
            'is_initializing': self.is_initializing,
            'is_complete': self.initialization_complete
        }

# 전역 백그라운드 매니저 인스턴스
_background_manager = None

def get_background_manager() -> BackgroundInitManager:
    """전역 백그라운드 매니저 인스턴스 반환"""
    global _background_manager
    if _background_manager is None:
        _background_manager = BackgroundInitManager()
    return _background_manager 