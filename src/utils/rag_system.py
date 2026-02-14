"""
RAG System for ContractLawProject
Handles vector embeddings, document retrieval, and AI-powered responses
"""
import os
import json
import pickle
import time
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, EMBEDDING_MODEL, RAG_CONFIG, GEMINI_MODEL
from src.utils.document_processor import extract_zip_content, clean_korean_text

class ContractRAGSystem:
    """RAG system for contract analysis and Q&A"""
    
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None
        self.retriever = None
        self.llm = None
        self.qa_chain_ready = False  # QA 체인 준비 상태
        self.documents = []
        self.document_chunks = []
        self.cache_dir = "data/cache"
        self.documents_cache_path = os.path.join(self.cache_dir, "documents.pkl")
        self.embeddings_cache_path = os.path.join(self.cache_dir, "embeddings.pkl")
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        self._setup_prompts()
    
    def _initialize_models(self):
        """Initialize embedding model and LLM"""
        try:
            print("AI 모델을 초기화하고 있습니다...")
            start_time = time.time()
            
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize Gemini LLM - 동적으로 환경변수에서 API 키 로드
            current_api_key = os.getenv("GEMINI_API_KEY", "")
            if current_api_key and len(current_api_key.strip()) > 20:
                genai.configure(api_key=current_api_key)
                self.llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    temperature=0.3,
                    google_api_key=current_api_key
                )
                print(f"Gemini LLM 초기화 완료 (키: {current_api_key[:8]}...{current_api_key[-4:]})")
            else:
                print("WARNING: Gemini API 키가 설정되지 않았습니다. 챗봇 기능이 제한됩니다.")
                self.llm = None
            
            elapsed = time.time() - start_time
            print(f"모델 초기화 완료 ({elapsed:.1f}초)")
            
        except Exception as e:
            print(f"ERROR: 모델 초기화 중 오류 발생: {str(e)}")

    def reinitialize_llm(self):
        """Reinitialize LLM with current API key (for cache-based loading)"""
        try:
            print("LLM 재초기화 중...")
            current_api_key = os.getenv("GEMINI_API_KEY", "")
            
            if current_api_key and len(current_api_key.strip()) > 20:
                genai.configure(api_key=current_api_key)
                self.llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    temperature=0.3,
                    google_api_key=current_api_key
                )
                print(f"LLM 재초기화 완료 (키: {current_api_key[:8]}...{current_api_key[-4:]})")
                return True
            else:
                print("API 키가 설정되지 않아 LLM 초기화 실패")
                return False
                
        except Exception as e:
            print(f"LLM 재초기화 오류: {str(e)}")
            return False

    def _load_cached_data(self) -> bool:
        """캐시된 데이터 로드 시도"""
        try:
            if os.path.exists(self.documents_cache_path) and os.path.exists(self.embeddings_cache_path):
                print(" 캐시된 데이터를 로드하고 있습니다...")
                
                with open(self.documents_cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.documents = cached_data['documents']
                    self.document_metadata = cached_data['metadata']
                
                print(f" 캐시에서 {len(self.documents)}개 문서 로드 완료")
                return True
        except Exception as e:
            print(f" 캐시 로드 실패: {str(e)}")
        return False

    def _save_to_cache(self):
        """현재 데이터를 캐시에 저장"""
        try:
            cached_data = {
                'documents': self.documents,
                'metadata': self.document_metadata
            }
            with open(self.documents_cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            print(" 데이터를 캐시에 저장했습니다.")
        except Exception as e:
            print(f" 캐시 저장 실패: {str(e)}")
    
    def _setup_prompts(self):
        """Setup prompts for different types of queries - 직접 구현 방식"""
        self.prompts = {
            "contract_analysis": """당신은 한국의 계약법 전문가입니다. 주어진 계약 관련 문서들을 바탕으로 정확하고 유용한 답변을 제공해주세요.

관련 문서 내용:
{context}

사용자 질문:
{question}

답변 가이드라인:
1. 주어진 문서 내용을 바탕으로 답변하세요
2. 법적 위험이나 주의사항이 있다면 명확히 언급하세요
3. 구체적인 조항이나 근거를 인용하세요
4. 한국어로 답변하며, 전문적이지만 이해하기 쉽게 설명하세요
5. 확실하지 않은 내용은 추가 검토가 필요하다고 안내하세요

답변:""",
            
            "clause_extraction": """다음 계약서에서 {clause_type} 관련 조항들을 찾아서 분석해주세요.

계약서 내용:
{context}

분석해야 할 조항 유형: {clause_type}

다음 형식으로 답변해주세요:
1. 발견된 조항들
2. 각 조항의 내용 요약
3. 법적 의미와 주의사항
4. 개선 제안사항

답변:""",
            
            "risk_assessment": """다음 계약서의 법적 위험 요소들을 분석해주세요.

계약서 내용:
{context}

다음 관점에서 분석해주세요:
1. 높은 위험 요소들
2. 중간 위험 요소들
3. 낮은 위험 요소들
4. 위험 완화 방안
5. 추가 검토가 필요한 부분

답변:"""
        }
    
    def check_cache_available(self) -> Dict[str, bool]:
        """캐시 파일 존재 여부 확인"""
        try:
            documents_exist = os.path.exists(self.documents_cache_path)
            embeddings_exist = os.path.exists(self.embeddings_cache_path)
            
            return {
                'documents': documents_exist,
                'embeddings': embeddings_exist
            }
        except Exception as e:
            print(f"캐시 상태 확인 오류: {e}")
            return {'documents': False, 'embeddings': False}
    
    def load_from_cache(self) -> bool:
        """캐시에서 데이터 로드"""
        try:
            # 문서 캐시 로드
            if os.path.exists(self.documents_cache_path):
                with open(self.documents_cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.documents = cached_data.get('documents', [])
                    self.document_chunks = cached_data.get('document_chunks', [])
                    print(f" 문서 캐시 로드됨: {len(self.documents)}개 문서")
            
            return True
            
        except Exception as e:
            print(f"캐시 로드 오류: {e}")
            return False
    
    def load_vector_store(self) -> bool:
        """벡터 스토어 로드"""
        try:
            if os.path.exists(self.embeddings_cache_path):
                # 임베딩 모델이 없으면 초기화
                if not self.embedding_model:
                    self.embedding_model = HuggingFaceEmbeddings(
                        model_name=EMBEDDING_MODEL,
                        model_kwargs={'device': 'cpu'}
                    )
                
                # FAISS 벡터 스토어 로드
                embeddings_dir = os.path.dirname(self.embeddings_cache_path)
                faiss_index_path = os.path.join(embeddings_dir, "contract_vectorstore")
                
                if os.path.exists(faiss_index_path):
                    self.vector_store = FAISS.load_local(
                        faiss_index_path, 
                        self.embedding_model
                    )
                    print(" 벡터 스토어 로드 완료")
                    return True
            
            return False
            
        except Exception as e:
            print(f"벡터 스토어 로드 오류: {e}")
            return False
    
    def build_vector_store(self, force_rebuild=False, progress_callback=None, batch_size=100) -> bool:
        """벡터 스토어 구축"""
        try:
            if not self.document_chunks and not self.documents:
                print("ERROR: 문서가 로드되지 않았습니다.")
                return False
            
            # 문서 청크가 없으면 생성
            if not self.document_chunks and self.documents:
                self._create_document_chunks()
            
            if not self.embedding_model:
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'}
                )
            
            # 벡터 스토어 생성
            if self.document_chunks:
                print(f" {len(self.document_chunks)}개 문서로 벡터 스토어 생성 중...")
                
                # 진행률 콜백 호출
                if progress_callback:
                    progress_callback(50, "벡터 임베딩 생성 중...")
                
                self.vector_store = FAISS.from_texts(
                    [chunk for chunk in self.document_chunks],
                    self.embedding_model
                )
                
                # 벡터 스토어 저장
                embeddings_dir = os.path.dirname(self.embeddings_cache_path)
                faiss_index_path = os.path.join(embeddings_dir, "contract_vectorstore")
                os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
                
                self.vector_store.save_local(faiss_index_path)
                
                # 캐시 파일도 생성
                with open(self.embeddings_cache_path, 'wb') as f:
                    pickle.dump({'vector_store_path': faiss_index_path}, f)
                
                if progress_callback:
                    progress_callback(100, "벡터 스토어 구축 완료")
                
                print(" 벡터 스토어 구축 및 저장 완료")
                return True
            
            return False
            
        except Exception as e:
            print(f"벡터 스토어 구축 오류: {e}")
            return False
    
    def _create_document_chunks(self):
        """문서를 청크로 분할"""
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAG_CONFIG.get('chunk_size', 2000),
                chunk_overlap=RAG_CONFIG.get('chunk_overlap', 400),
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            self.document_chunks = []
            for doc in self.documents:
                if isinstance(doc, dict) and 'content' in doc:
                    chunks = splitter.split_text(doc['content'])
                    self.document_chunks.extend(chunks)
                elif isinstance(doc, str):
                    chunks = splitter.split_text(doc)
                    self.document_chunks.extend(chunks)
            
            print(f" {len(self.documents)}개 문서를 {len(self.document_chunks)}개 청크로 분할 완료")
            
        except Exception as e:
            print(f"문서 청킹 오류: {e}")
    
    def load_legal_documents(self, data_directories, progress_callback=None, max_docs=None, time_limit=None):
        """법률 문서 로드 (간단 버전)"""
        try:
            from .document_processor import extract_zip_content, clean_korean_text
            
            print(" 법률 문서 로드를 시작합니다...")
            
            if progress_callback:
                progress_callback(10, "문서 디렉토리 스캔 중...")
            
            all_documents = []
            processed_count = 0
            
            for data_dir in data_directories:
                if not os.path.exists(data_dir):
                    continue
                    
                zip_files = [f for f in os.listdir(data_dir) if f.endswith('.zip')]
                
                for zip_file in zip_files:
                    if max_docs and processed_count >= max_docs:
                        break
                        
                    try:
                        zip_path = os.path.join(data_dir, zip_file)
                        documents = extract_zip_content(zip_path)
                        
                        for doc in documents:
                            # extract_zip_content는 문자열 리스트를 반환함
                            if isinstance(doc, str):
                                cleaned_content = clean_korean_text(doc)
                                if len(cleaned_content) > 100:  # 최소 길이 필터
                                    all_documents.append({
                                        'content': cleaned_content,
                                        'source': zip_file,
                                        'metadata': {}
                                    })
                                    processed_count += 1
                                    
                                    if max_docs and processed_count >= max_docs:
                                        break
                            # 기존 딕셔너리 형태도 지원 (호환성 유지)
                            elif isinstance(doc, dict) and 'content' in doc:
                                cleaned_content = clean_korean_text(doc['content'])
                                if len(cleaned_content) > 100:  # 최소 길이 필터
                                    all_documents.append({
                                        'content': cleaned_content,
                                        'source': zip_file,
                                        'metadata': doc.get('metadata', {})
                                    })
                                    processed_count += 1
                                    
                                    if max_docs and processed_count >= max_docs:
                                        break
                        
                        if progress_callback:
                            progress = min(90, 10 + (processed_count / (max_docs or 1000)) * 80)
                            progress_callback(progress, f"처리됨: {zip_file}")
                            
                    except Exception as e:
                        print(f" {zip_file} 처리 중 오류: {e}")
                        continue
            
            self.documents = all_documents
            
            # 캐시에 저장
            cache_data = {
                'documents': self.documents,
                'document_chunks': []
            }
            
            with open(self.documents_cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            if progress_callback:
                progress_callback(100, f"문서 로드 완료: {len(self.documents)}개")
            
            print(f" 총 {len(self.documents)}개 문서 로드 완료")
            return True
            
        except Exception as e:
            print(f"문서 로드 오류: {e}")
            return False
    
    def _extract_category_from_filename(self, filename: str) -> str:
        """Extract category from ZIP filename"""
        category_mappings = {
            "경제_경영": "business",
            "인사_고용": "employment", 
            "부동산": "real_estate",
            "금전소비대차": "financial",
            "매매": "sales",
            "재산권사용_용역": "services",
            "무역": "trade",
            "대리점_프랜차이즈": "agency",
            "약관": "general"
        }
        
        for key, value in category_mappings.items():
            if key in filename:
                return value
        return "general"
    
    def _split_documents(self, texts: List[str], metadata: List[Dict]) -> Tuple[List[str], List[Dict]]:
        """Split documents into smaller chunks for better retrieval"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CONFIG['chunk_size'],
            chunk_overlap=RAG_CONFIG['chunk_overlap'],
            length_function=len,
            separators=['\n\n', '\n', '. ', ' ', '']
        )
        
        all_chunks = []
        all_chunk_metadata = []
        
        for text, meta in zip(texts, metadata):
            chunks = text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_meta = meta.copy()
                chunk_meta['chunk_id'] = i
                chunk_meta['chunk_text'] = chunk[:100] + "..." if len(chunk) > 100 else chunk
                all_chunk_metadata.append(chunk_meta)
        
        return all_chunks, all_chunk_metadata
    
    def setup_qa_chain(self):
        """Setup the QA chain for contract analysis - 완전 직접 구현 방식"""
        print(" QA 체인을 설정하고 있습니다...")
        
        # 필수 구성 요소 확인
        if not self.vector_store:
            print("ERROR: 벡터 스토어가 초기화되지 않았습니다.")
            return False
        
        # LLM이 없으면 재초기화 시도
        if not self.llm:
            print("LLM이 초기화되지 않았습니다. 재초기화를 시도합니다...")
            if not self.reinitialize_llm():
                print("ERROR: LLM 재초기화에 실패했습니다. Gemini API 키를 확인해주세요.")
                return False
        
        try:
            # 벡터 검색기 설정 (LangChain 의존성 최소화)
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": RAG_CONFIG.get('top_k_results', 5)}
            )
            
            # 직접 구현된 프롬프트 템플릿
            self.qa_prompt_template = """당신은 한국의 계약법 전문가입니다. 계약 관련 지식을 바탕으로 정확하고 유용한 답변을 제공해주세요.

참고 정보:
{context}

질문: {question}

답변 가이드라인:
1. 계약법 관련 지식을 바탕으로 답변하세요
2. 법적 위험이나 주의사항이 있다면 명확히 언급하세요
3. 구체적인 조항이나 근거를 설명하세요
4. 한국어로 답변하며, 전문적이지만 이해하기 쉽게 설명하세요
5. 확실하지 않은 내용은 추가 검토가 필요하다고 안내하세요

답변:"""
            
            # QA 체인을 직접 구현 방식으로 설정
            self.qa_chain_ready = True
            
            print("SUCCESS: QA 체인이 직접 구현 방식으로 설정되었습니다.")
            return True
            
        except Exception as e:
            print(f"ERROR: QA 체인 설정 중 오류 발생: {str(e)}")
            self.qa_chain_ready = False
            return False
    
    def ask_question(self, question: str, contract_context: str = "") -> Dict[str, Any]:
        """Ask a question about contracts and get AI response - 완전 직접 구현 방식"""
        print(f" 질문 처리 중: {question[:50]}...")
        
        # 시스템 준비 상태 확인
        if not hasattr(self, 'qa_chain_ready') or not self.qa_chain_ready:
            return {
                "answer": "QA 시스템이 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요.",
                "sources": [],
                "error": True
            }
        
        if not hasattr(self, 'retriever') or not self.retriever:
            return {
                "answer": "문서 검색 시스템이 준비되지 않았습니다.",
                "sources": [],
                "error": True
            }
        
        if not self.llm:
            return {
                "answer": "AI 모델이 초기화되지 않았습니다. API 키를 확인해주세요.",
                "sources": [],
                "error": True
            }
        
        try:
            # 질문 강화 (계약서 컨텍스트 포함)
            enhanced_question = question
            if contract_context and len(contract_context.strip()) > 0:
                enhanced_question = f"다음 계약서 내용을 참고하여 답변해주세요:\n\n{contract_context[:2000]}...\n\n질문: {question}"
            
            print(" 관련 문서를 검색하고 있습니다...")
            
            # 1. 벡터 검색으로 관련 문서 찾기
            try:
                # 검색어 길이 제한 (너무 길면 검색 성능 저하)
                search_query = enhanced_question[:1000] if enhanced_question else question[:1000]
                
                # 벡터 검색 실행
                docs = self.retriever.get_relevant_documents(search_query)
                print(f" {len(docs)}개의 관련 문서를 찾았습니다.")
                
                # 문서가 없는 경우 처리
                if not docs:
                    print(" 관련 문서를 찾을 수 없습니다. 일반적인 지식으로 답변합니다.")
                    
            except Exception as search_error:
                print(f" 문서 검색 중 오류: {search_error}")
                docs = []
                # 검색 실패 시에도 기본 답변 생성 시도
            
            # 2. 컨텍스트 구성
            if docs:
                context_parts = []
                for i, doc in enumerate(docs[:5]):  # 최대 5개 참고자료만 사용
                    context_parts.append(f"참고자료 {i+1}: {doc.page_content[:800]}")
                context = "\n\n".join(context_parts)
            else:
                context = "관련 정보를 찾을 수 없습니다. 일반적인 계약법 지식을 바탕으로 답변하겠습니다."
            
            # 3. 프롬프트 생성
            prompt = self.qa_prompt_template.format(
                context=context[:4000],  # 컨텍스트 길이 제한
                question=enhanced_question
            )
            
            print(" AI가 답변을 생성하고 있습니다...")
            
            # 4. AI 답변 생성
            try:
                # API 키 재확인 및 LLM 재초기화
                current_api_key = os.getenv("GEMINI_API_KEY", "")
                if not current_api_key or len(current_api_key.strip()) < 20:
                    print("API 키가 유효하지 않습니다. LLM을 재초기화합니다.")
                    if not self.reinitialize_llm():
                        return {
                            "answer": "API 키가 유효하지 않습니다. Gemini API 키를 확인해주세요.",
                            "sources": [],
                            "error": True
                        }
                
                response = self.llm.invoke(prompt)
                
                # 응답에서 텍스트 추출
                if hasattr(response, 'content'):
                    answer = response.content
                elif hasattr(response, 'text'):
                    answer = response.text
                else:
                    answer = str(response)
                
                # 답변 검증
                if not answer or len(answer.strip()) < 10:
                    answer = "죄송합니다. 적절한 답변을 생성할 수 없습니다. 질문을 다시 확인해주세요."
                
            except Exception as llm_error:
                print(f" AI 답변 생성 중 오류: {llm_error}")
                answer = f"AI 답변 생성 중 오류가 발생했습니다: {str(llm_error)}"
            
            # 5. 소스 정보 구성
            sources = []
            for i, doc in enumerate(docs[:3]):  # 최대 3개 소스만
                try:
                    source_info = {
                        "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                        "metadata": doc.metadata if hasattr(doc, 'metadata') else {"source": f"문서 {i+1}"}
                    }
                    sources.append(source_info)
                except Exception as source_error:
                    print(f"소스 정보 처리 오류: {source_error}")
            
            print(" 답변 생성이 완료되었습니다.")
            
            return {
                "answer": answer,
                "sources": sources,
                "error": False
            }
            
        except Exception as e:
            error_msg = f"질문 처리 중 예상치 못한 오류가 발생했습니다: {str(e)}"
            print(f" {error_msg}")
            
            return {
                "answer": error_msg,
                "sources": [],
                "error": True
            }
    
    def analyze_contract_clauses(self, contract_text: str, clause_type: str) -> str:
        """Analyze specific types of clauses in a contract"""
        if not self.llm:
            return "LLM이 초기화되지 않았습니다."
        
        try:
            prompt = self.prompts["clause_extraction"].format(
                context=contract_text[:3000],  # Limit context size
                clause_type=clause_type
            )
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"조항 분석 중 오류 발생: {str(e)}"
    
    def assess_contract_risk(self, contract_text: str, contract_type: str = "일반") -> str:
        """Assess overall risk level of a contract"""
        if not self.llm:
            return "LLM이 초기화되지 않았습니다."
        
        try:
            prompt = self.prompts["risk_assessment"].format(
                context=contract_text[:3000],
                contract_type=contract_type
            )
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"위험도 평가 중 오류 발생: {str(e)}"
    
    def search_similar_contracts(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar contracts based on query"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            similar_contracts = []
            for doc, score in results:
                similar_contracts.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
                    "similarity_score": float(score)
                })
            
            return similar_contracts
            
        except Exception as e:
            print(f"ERROR: 유사 계약서 검색 중 오류 발생: {str(e)}")
            return []
    
    def get_contract_recommendations(self, contract_type: str) -> List[str]:
        """Get recommendations for contract improvement"""
        recommendations = {
            "business": [
                "명확한 사업 목적 및 범위 정의",
                "구체적인 성과 지표 설정",
                "지적재산권 보호 조항 포함",
                "사업 기밀 유지 조항 강화"
            ],
            "employment": [
                "근무 조건 및 업무 범위 명시",
                "임금 지급 조건 상세화",
                "근로기준법 준수 확인",
                "퇴직 및 경업금지 조항 검토"
            ],
            "real_estate": [
                "부동산 소유권 및 등기 상태 확인",
                "대금 지급 일정 및 조건 명확화",
                "하자 담보 책임 조항 포함",
                "불가항력 사유에 대한 처리 방안"
            ],
            "financial": [
                "대출 조건 및 이자율 명시",
                "상환 계획 및 연체 시 처리 방안",
                "담보 설정 및 보증 조건",
                "조기 상환 조건 검토"
            ]
        }
        
        return recommendations.get(contract_type, [
            "계약 목적 및 범위 명확화",
            "당사자 권리와 의무 균형 조정",
            "분쟁 해결 절차 수립",
            "계약 해지 조건 명시"
        ])
    
    def export_analysis_report(self, contract_text: str, analysis_results: Dict) -> str:
        """Export contract analysis as a structured report"""
        report = {
            "contract_summary": {
                "length": len(contract_text),
                "word_count": len(contract_text.split())
            },
            "risk_assessment": analysis_results.get("risk_scores", {}),
            "missing_clauses": analysis_results.get("missing_clauses", []),
            "recommendations": analysis_results.get("recommendations", []),
            "analysis_timestamp": pd.Timestamp.now().isoformat()
        }
        
        # Save as JSON
        report_path = f"data/reports/contract_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report_path

    def test_qa_system(self) -> bool:
        """QA 시스템이 제대로 작동하는지 테스트"""
        print("🔧 QA 시스템 테스트를 시작합니다...")
        
        try:
            # 간단한 테스트 질문
            test_question = "계약서에서 가장 중요한 조항은 무엇인가요?"
            
            # QA 체인 준비 상태 확인
            if not hasattr(self, 'qa_chain_ready') or not self.qa_chain_ready:
                print(" QA 체인이 준비되지 않았습니다.")
                return False
            
            # 간단한 답변 생성 테스트
            response = self.ask_question(test_question)
            
            if response and not response['error'] and len(response['answer']) > 10:
                print(" QA 시스템 테스트 성공!")
                return True
            else:
                print(f" QA 시스템 테스트 실패: {response.get('answer', '응답 없음')}")
                return False
                
        except Exception as e:
            print(f" QA 시스템 테스트 중 오류: {e}")
            return False

# Initialize global RAG system instance
rag_system = ContractRAGSystem() 