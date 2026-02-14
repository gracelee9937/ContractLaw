"""
API Key Management Utilities
Handles secure storage and retrieval of API keys
"""
import os
import json
import base64
from typing import Optional, Dict
from pathlib import Path

class APIKeyManager:
    """API 키 안전 저장 및 관리"""
    
    def __init__(self):
        self.config_dir = Path("data/config")
        self.config_file = self.config_dir / "api_keys.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _encode_key(self, key: str) -> str:
        """API 키를 간단히 인코딩 (보안 강화)"""
        if not key:
            return ""
        return base64.b64encode(key.encode()).decode()
    
    def _decode_key(self, encoded_key: str) -> str:
        """인코딩된 API 키를 디코딩"""
        if not encoded_key:
            return ""
        try:
            return base64.b64decode(encoded_key.encode()).decode()
        except Exception:
            return ""
    
    def save_api_key(self, service: str, api_key: str) -> bool:
        """API 키를 안전하게 저장"""
        try:
            # 기존 설정 로드
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # API 키 저장 (인코딩)
            config[service] = self._encode_key(api_key)
            
            # 파일에 저장
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"API 키 저장 오류: {str(e)}")
            return False
    
    def load_api_key(self, service: str) -> Optional[str]:
        """저장된 API 키 로드"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            encoded_key = config.get(service, "")
            return self._decode_key(encoded_key) if encoded_key else None
            
        except Exception as e:
            print(f"API 키 로드 오류: {str(e)}")
            return None
    
    def delete_api_key(self, service: str) -> bool:
        """특정 서비스의 API 키 삭제"""
        try:
            if not self.config_file.exists():
                return True
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if service in config:
                del config[service]
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"API 키 삭제 오류: {str(e)}")
            return False
    
    def clear_all_keys(self) -> bool:
        """모든 API 키 삭제"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            return True
        except Exception as e:
            print(f"API 키 전체 삭제 오류: {str(e)}")
            return False
    
    def get_all_services(self) -> Dict[str, bool]:
        """저장된 모든 서비스와 키 존재 여부 반환"""
        try:
            if not self.config_file.exists():
                return {}
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return {service: bool(key) for service, key in config.items()}
            
        except Exception:
            return {}
    
    def is_key_valid(self, service: str) -> bool:
        """API 키가 유효한지 확인"""
        key = self.load_api_key(service)
        if not key:
            return False
        
        # Gemini API 키 형식 확인
        if service == "gemini":
            return key.startswith("AIza") and len(key) > 20
        
        # 기본적으로 길이만 확인
        return len(key) > 10


class UserPreferences:
    """사용자 설정 관리"""
    
    def __init__(self):
        self.config_dir = Path("data/config")
        self.prefs_file = self.config_dir / "user_preferences.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 기본 설정
        self.default_prefs = {
            "auto_initialize": True,
            "max_documents": 10000,
            "batch_size": 100,
            "time_limit": 30,
            "show_progress": True,
            "cache_enabled": True,
            "language": "ko"
        }
    
    def load_preferences(self) -> Dict:
        """사용자 설정 로드"""
        try:
            if not self.prefs_file.exists():
                return self.default_prefs.copy()
            
            with open(self.prefs_file, 'r', encoding='utf-8') as f:
                saved_prefs = json.load(f)
            
            # 기본 설정과 병합
            prefs = self.default_prefs.copy()
            prefs.update(saved_prefs)
            return prefs
            
        except Exception as e:
            print(f"설정 로드 오류: {str(e)}")
            return self.default_prefs.copy()
    
    def save_preferences(self, preferences: Dict) -> bool:
        """사용자 설정 저장"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 저장 오류: {str(e)}")
            return False
    
    def get_preference(self, key: str, default=None):
        """특정 설정값 가져오기"""
        prefs = self.load_preferences()
        return prefs.get(key, default)
    
    def set_preference(self, key: str, value) -> bool:
        """특정 설정값 저장"""
        prefs = self.load_preferences()
        prefs[key] = value
        return self.save_preferences(prefs)


# 전역 인스턴스
api_manager = APIKeyManager()
user_prefs = UserPreferences() 