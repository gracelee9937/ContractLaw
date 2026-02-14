"""
Responsible AI Implementation for ContractLawProject
Ensures fairness, transparency, accountability, privacy, safety, and sustainability
"""
import re
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import os
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiasType(Enum):
    GENDER = "gender"
    AGE = "age"
    ETHNICITY = "ethnicity"
    RELIGION = "religion"
    DISABILITY = "disability"
    ECONOMIC = "economic"

@dataclass
class BiasDetectionResult:
    bias_type: BiasType
    confidence: float
    location: str
    suggestion: str

class ResponsibleAISystem:
    """Responsible AI implementation for contract analysis"""
    
    def __init__(self):
        self.bias_patterns = self._load_bias_patterns()
        self.safety_patterns = self._load_safety_patterns()
        self.privacy_patterns = self._load_privacy_patterns()
        self.audit_log = []
        
    def _load_bias_patterns(self) -> Dict[BiasType, List[str]]:
        """Load bias detection patterns"""
        return {
            BiasType.GENDER: [
                r'남성만|여성만|남자만|여자만',
                r'남성우선|여성우선',
                r'남성임원|여성임원',
                r'남성직원|여성직원'
            ],
            BiasType.AGE: [
                r'나이\s*\d{2,3}세\s*이하',
                r'나이\s*\d{2,3}세\s*이상',
                r'청년|중년|노년\s*제한',
                r'연령\s*차별'
            ],
            BiasType.ECONOMIC: [
                r'소득\s*기준',
                r'재산\s*기준',
                r'신용등급\s*제한',
                r'보증금\s*높은\s*금액'
            ]
        }
    
    def _load_safety_patterns(self) -> List[str]:
        """Load safety detection patterns"""
        return [
            r'해킹|바이러스|악성코드',
            r'SQL\s*injection|XSS|CSRF',
            r'<script>|javascript:|vbscript:',
            r'exec\(|eval\(|system\(',
            r'파일\s*업로드\s*제한',
            r'실행\s*권한'
        ]
    
    def _load_privacy_patterns(self) -> List[str]:
        """Load privacy detection patterns"""
        return [
            r'\d{6}-\d{7}',  # 주민등록번호
            r'\d{3}-\d{4}-\d{4}',  # 전화번호
            r'\d{3}-\d{2}-\d{6}',  # 사업자등록번호
            r'[가-힣]{2,4}\s*시\s*[가-힣]{2,4}\s*구\s*[가-힣]{2,4}',  # 주소
            r'이메일\s*주소',
            r'개인정보|개인\s*정보'
        ]
    
    def detect_bias(self, text: str) -> List[BiasDetectionResult]:
        """Detect bias in contract text"""
        results = []
        
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    results.append(BiasDetectionResult(
                        bias_type=bias_type,
                        confidence=0.8,
                        location=f"위치: {match.start()}-{match.end()}",
                        suggestion=self._get_bias_suggestion(bias_type)
                    ))
        
        return results
    
    def _get_bias_suggestion(self, bias_type: BiasType) -> str:
        """Get suggestion for bias correction"""
        suggestions = {
            BiasType.GENDER: "성별 중립적 표현으로 수정하세요. (예: '직원', '근로자')",
            BiasType.AGE: "연령 제한은 합리적 근거가 있어야 하며, 차별 금지법을 준수해야 합니다.",
            BiasType.ECONOMIC: "경제적 조건은 계약의 본질과 관련된 합리적 범위 내에서 설정하세요."
        }
        return suggestions.get(bias_type, "차별적 표현을 중립적 표현으로 수정하세요.")
    
    def validate_safety(self, text: str, file_content: bytes = None) -> Dict[str, Any]:
        """Validate safety of input"""
        safety_issues = []
        
        # Text-based safety check
        for pattern in self.safety_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                safety_issues.append(f"위험한 패턴 발견: {pattern}")
        
        # File-based safety check
        if file_content:
            file_issues = self._check_file_safety(file_content)
            safety_issues.extend(file_issues)
        
        return {
            'safe': len(safety_issues) == 0,
            'issues': safety_issues,
            'risk_level': 'high' if len(safety_issues) > 3 else 'medium' if len(safety_issues) > 0 else 'low'
        }
    
    def _check_file_safety(self, file_content: bytes) -> List[str]:
        """Check file safety"""
        issues = []
        
        # Check file size (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            issues.append("파일 크기가 너무 큽니다 (최대 10MB)")
        
        # Check for executable content
        executable_signatures = [b'MZ', b'ELF', b'\x7fELF']
        for sig in executable_signatures:
            if file_content.startswith(sig):
                issues.append("실행 가능한 파일 형식이 감지되었습니다")
                break
        
        return issues
    
    def anonymize_personal_info(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Anonymize personal information"""
        anonymized_text = text
        replacements = {}
        
        # 주민등록번호 마스킹
        ssn_pattern = r'(\d{6})-(\d{7})'
        for match in re.finditer(ssn_pattern, text):
            original = match.group(0)
            masked = f"{match.group(1)}-*******"
            anonymized_text = anonymized_text.replace(original, masked)
            replacements[original] = masked
        
        # 전화번호 마스킹
        phone_pattern = r'(\d{3})-(\d{4})-(\d{4})'
        for match in re.finditer(phone_pattern, text):
            original = match.group(0)
            masked = f"{match.group(1)}-****-{match.group(3)}"
            anonymized_text = anonymized_text.replace(original, masked)
            replacements[original] = masked
        
        return anonymized_text, replacements
    
    def generate_explanation(self, analysis_result: Dict[str, Any]) -> str:
        """Generate explanation for AI decision"""
        explanation = "## 분석 결과 설명\n\n"
        
        if 'risk_score' in analysis_result:
            explanation += f"**리스크 점수**: {analysis_result['risk_score']}/100\n"
            explanation += f"**평가 근거**: {analysis_result.get('risk_reason', 'N/A')}\n\n"
        
        if 'missing_clauses' in analysis_result:
            explanation += f"**누락된 조항**: {len(analysis_result['missing_clauses'])}개\n"
            for clause in analysis_result['missing_clauses']:
                explanation += f"- {clause}\n"
            explanation += "\n"
        
        if 'bias_detected' in analysis_result:
            explanation += f"**편향성 검출**: {len(analysis_result['bias_detected'])}개 항목\n"
            for bias in analysis_result['bias_detected']:
                explanation += f"- {bias.suggestion}\n"
            explanation += "\n"
        
        explanation += "**분석 방법**: 한국 법률 데이터셋과 AI 모델을 활용하여 계약서를 분석했습니다."
        
        return explanation
    
    def log_audit(self, action: str, user_input: str, result: Dict[str, Any], user_id: str = "anonymous"):
        """Log audit trail for accountability"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': self._hash_user_id(user_id),
            'input_hash': hashlib.sha256(user_input.encode()).hexdigest(),
            'result_summary': {
                'risk_score': result.get('risk_score', 0),
                'bias_detected': len(result.get('bias_detected', [])),
                'safety_issues': len(result.get('safety_issues', []))
            }
        }
        
        self.audit_log.append(audit_entry)
        
        # Save to file (in production, use proper database)
        audit_file = "data/audit_log.json"
        os.makedirs(os.path.dirname(audit_file), exist_ok=True)
        
        try:
            if os.path.exists(audit_file):
                with open(audit_file, 'r', encoding='utf-8') as f:
                    existing_log = json.load(f)
            else:
                existing_log = []
            
            existing_log.append(audit_entry)
            
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(existing_log, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Audit log 저장 실패: {e}")
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def get_sustainability_metrics(self) -> Dict[str, Any]:
        """Get sustainability metrics"""
        return {
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'memory_usage': self._get_memory_usage(),
            'processing_time_avg': self._get_avg_processing_time(),
            'energy_efficiency': self._calculate_energy_efficiency()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # Implementation would track cache hits/misses
        return 0.85  # Placeholder
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage metrics"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    def _get_avg_processing_time(self) -> float:
        """Get average processing time"""
        # Implementation would track processing times
        return 2.5  # Placeholder
    
    def _calculate_energy_efficiency(self) -> float:
        """Calculate energy efficiency score"""
        # Implementation would track energy usage
        return 0.78  # Placeholder 