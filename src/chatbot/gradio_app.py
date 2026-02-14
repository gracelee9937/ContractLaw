"""
ContractLawProject - Standalone Gradio Chatbot Interface
RAG-based contract analysis chatbot with Gradio UI
"""
import gradio as gr
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.document_processor import DocumentProcessor, clean_korean_text
from src.utils.rag_system import ContractRAGSystem
from config.settings import CONTRACT_CATEGORIES

class ContractChatbot:
    """Gradio-based contract analysis chatbot"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.rag_system = ContractRAGSystem()
        self.current_contract = ""
        self.chat_history = []
        self.is_initialized = False
    
    def initialize_system(self):
        """Initialize the RAG system"""
        if self.is_initialized:
            return " 시스템이 이미 초기화되었습니다."
        
        try:
            # Load sample data if ZIP files not accessible
            data_dirs = [
                "05.계약 법률 문서 서식 데이터/3.개방데이터/1.데이터/Training/01.원천데이터",
                "01.민사법 LLM 사전학습 및 Instruction Tuning 데이터/3.개방데이터/1.데이터/Training/01.원천데이터"
            ]
            
            # Check if actual data directories exist
            existing_dirs = [d for d in data_dirs if os.path.exists(d)]
            
            if existing_dirs:
                loaded_count = self.rag_system.load_legal_documents(existing_dirs)
            else:
                # Use sample data
                loaded_count = self.load_sample_data()
            
            if loaded_count > 0:
                if self.rag_system.build_vector_store():
                    if self.rag_system.setup_qa_chain():
                        self.is_initialized = True
                        return f" AI 시스템 초기화 완료! ({loaded_count}개 문서 로드됨)"
                    else:
                        return " QA 시스템 설정에 실패했습니다."
                else:
                    return " 벡터 데이터베이스 구축에 실패했습니다."
            else:
                return " 법률 문서 로드에 실패했습니다."
                
        except Exception as e:
            return f" 초기화 중 오류 발생: {str(e)}"
    
    def load_sample_data(self):
        """Load sample contract data for demo purposes"""
        sample_contracts = [
            {
                "category": "employment",
                "content": """
                고용계약서
                
                제1조 (목적) 이 계약은 갑과 을 간의 고용관계에 관한 조건을 정함을 목적으로 한다.
                
                제2조 (고용기간) 고용기간은 2024년 1월 1일부터 2024년 12월 31일까지로 한다.
                
                제3조 (근무장소) 을의 근무장소는 서울특별시 강남구 테헤란로 123번지로 한다.
                
                제4조 (업무내용) 을은 소프트웨어 개발 업무를 수행한다.
                
                제5조 (임금) 월 기본급은 300만원으로 하며, 매월 말일에 지급한다.
                
                제6조 (근무시간) 1일 8시간, 주 40시간을 원칙으로 한다.
                
                제7조 (해지조건) 다음 각 호의 사유 발생시 계약을 해지할 수 있다:
                1. 당사자 일방의 중대한 계약 위반
                2. 30일 전 서면 통보에 의한 해지
                
                제8조 (비밀유지) 을은 업무상 알게 된 기밀정보를 제3자에게 누설하지 않는다.
                """
            },
            {
                "category": "sales",
                "content": """
                물품매매계약서
                
                제1조 (목적) 이 계약은 갑이 을에게 물품을 공급함에 관한 사항을 정한다.
                
                제2조 (물품 및 수량) 
                - 품명: 노트북 컴퓨터
                - 수량: 100대
                - 단가: 1,500,000원
                - 총액: 150,000,000원
                
                제3조 (납품조건) 물품은 2024년 3월 31일까지 을이 지정하는 장소에 납품한다.
                
                제4조 (대금지급) 을은 물품 인수 후 30일 이내에 대금을 지급한다.
                
                제5조 (품질보증) 갑은 납품한 물품에 대해 1년간 품질을 보증한다.
                
                제6조 (손해배상) 계약 위반으로 인한 손해는 위반 당사자가 배상한다.
                
                제7조 (불가항력) 천재지변 등 불가항력으로 인한 계약 이행 지연은 면책된다.
                """
            },
            {
                "category": "real_estate",
                "content": """
                부동산임대차계약서
                
                제1조 (목적) 갑은 을에게 아래 부동산을 임대하고 을은 이를 임차한다.
                
                제2조 (임대물건) 서울시 서초구 반포동 123-45번지 아파트 101동 501호
                
                제3조 (임대차기간) 2024년 1월 1일부터 2025년 12월 31일까지 2년간
                
                제4조 (임대료) 
                - 보증금: 50,000,000원
                - 월임대료: 1,500,000원
                - 지급일: 매월 말일
                
                제5조 (임대료 증액) 임대인은 약정한 차임의 20분의 1을 초과하지 않는 범위에서 증액할 수 있다.
                
                제6조 (수선의무) 임대인은 임대물의 수선의무를 부담한다.
                
                제7조 (계약해지) 을이 차임을 2기 이상 연체한 때에는 갑은 계약을 해지할 수 있다.
                
                제8조 (원상회복) 임대차 종료시 을은 임대물을 원상회복하여 반환한다.
                """
            }
        ]
        
        # Add sample contracts to RAG system
        texts = [contract["content"] for contract in sample_contracts]
        metadata = [{"source": f"sample_{contract['category']}", "category": contract["category"]} 
                   for contract in sample_contracts]
        
        self.rag_system.documents = texts
        self.rag_system.document_metadata = metadata
        
        return len(sample_contracts)
    
    def upload_contract(self, file):
        """Process uploaded contract file"""
        if file is None:
            return "파일을 선택해주세요.", ""
        
        try:
            contract_text = self.doc_processor.extract_text_from_file(file)
            if contract_text:
                self.current_contract = clean_korean_text(contract_text)
                preview = self.current_contract[:500] + "..." if len(self.current_contract) > 500 else self.current_contract
                return f" 계약서 업로드 완료! ({len(self.current_contract):,}글자)", preview
            else:
                return " 파일 처리 중 오류가 발생했습니다.", ""
        except Exception as e:
            return f" 파일 업로드 오류: {str(e)}", ""
    
    def ask_question(self, question, chat_history):
        """Process user question and return response"""
        if not self.is_initialized:
            response = " AI 시스템이 초기화되지 않았습니다. 먼저 '시스템 초기화' 버튼을 클릭해주세요."
            chat_history.append([question, response])
            return chat_history, ""
        
        if not question.strip():
            response = "질문을 입력해주세요."
            chat_history.append([question, response])
            return chat_history, ""
        
        try:
            # Get response from RAG system
            result = self.rag_system.ask_question(question, self.current_contract)
            
            if result['error']:
                response = f" {result['answer']}"
            else:
                response = result['answer']
                
                # Add source information if available
                if result['sources']:
                    response += "\n\n **참고 자료:**\n"
                    for i, source in enumerate(result['sources'][:2], 1):
                        response += f"{i}. {source['content']}\n"
            
            chat_history.append([question, response])
            return chat_history, ""
            
        except Exception as e:
            error_response = f" 답변 생성 중 오류가 발생했습니다: {str(e)}"
            chat_history.append([question, error_response])
            return chat_history, ""
    
    def get_suggested_questions(self):
        """Get suggested questions based on current contract"""
        if self.current_contract:
            return [
                "이 계약서의 주요 조항은 무엇인가요?",
                "결제 조건이 어떻게 되나요?",
                "계약 해지 조건을 알려주세요",
                "위험한 조항이 있는지 확인해주세요",
                "누락된 중요 조항이 있나요?"
            ]
        else:
            return [
                "고용계약서 작성시 주의사항은 무엇인가요?",
                "임대차계약에서 중요한 조항은?",
                "매매계약서의 필수 조항을 알려주세요",
                "계약서 위험도를 평가하는 방법은?",
                "표준 계약서 조항에 대해 설명해주세요"
            ]
    
    def create_interface(self):
        """Create Gradio interface"""
        
        # Custom CSS
        custom_css = """
        .gradio-container {
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        .chatbot {
            height: 500px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        """
        
        with gr.Blocks(css=custom_css, title=" ContractLawProject - AI 챗봇") as interface:
            
            # Header
            gr.Markdown("""
            #  ContractLawProject - AI 계약서 챗봇
            **RAG 기반 계약서 분석 AI 어시스턴트**
            
            계약서를 업로드하고 AI에게 질문해보세요! 법률 전문 지식을 바탕으로 정확한 답변을 제공합니다.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # System initialization
                    gr.Markdown("###  시스템 설정")
                    init_btn = gr.Button("AI 시스템 초기화", variant="primary")
                    init_status = gr.Textbox(label="초기화 상태", interactive=False)
                    
                    # File upload
                    gr.Markdown("###  계약서 업로드")
                    file_input = gr.File(
                        label="계약서 파일 (PDF, DOCX, TXT)",
                        file_types=[".pdf", ".docx", ".txt"]
                    )
                    upload_status = gr.Textbox(label="업로드 상태", interactive=False)
                    contract_preview = gr.Textbox(
                        label="계약서 미리보기",
                        lines=10,
                        interactive=False
                    )
                    
                    # Contract category
                    gr.Markdown("###  계약 유형")
                    category_dropdown = gr.Dropdown(
                        choices=[(info['name'], key) for key, info in CONTRACT_CATEGORIES.items()],
                        label="계약서 유형 선택",
                        value="business"
                    )
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("###  AI와 대화하기")
                    
                    chatbot = gr.Chatbot(
                        label="대화 내역",
                        height=400,
                        show_label=True
                    )
                    
                    with gr.Row():
                        question_input = gr.Textbox(
                            label="질문 입력",
                            placeholder="계약서에 대해 궁금한 것을 물어보세요...",
                            scale=4
                        )
                        send_btn = gr.Button("질문하기", variant="primary", scale=1)
                    
                    # Suggested questions
                    gr.Markdown("### 추천 질문")
                    with gr.Row():
                        suggest_btns = []
                        for i in range(3):
                            btn = gr.Button(f"추천 질문 {i+1}", variant="secondary", scale=1)
                            suggest_btns.append(btn)
                    
                    # Additional suggested questions
                    with gr.Row():
                        for i in range(2):
                            btn = gr.Button(f"추천 질문 {i+4}", variant="secondary", scale=1)
                            suggest_btns.append(btn)
                    
                    # Clear button
                    clear_btn = gr.Button("대화 기록 삭제", variant="secondary")
            
            # Event handlers
            init_btn.click(
                fn=self.initialize_system,
                outputs=[init_status]
            )
            
            file_input.upload(
                fn=self.upload_contract,
                inputs=[file_input],
                outputs=[upload_status, contract_preview]
            )
            
            send_btn.click(
                fn=self.ask_question,
                inputs=[question_input, chatbot],
                outputs=[chatbot, question_input]
            )
            
            question_input.submit(
                fn=self.ask_question,
                inputs=[question_input, chatbot],
                outputs=[chatbot, question_input]
            )
            
            # Suggested question handlers
            suggestions = [
                "이 계약서의 주요 조항은 무엇인가요?",
                "결제 조건이 어떻게 되나요?",
                "계약 해지 조건을 알려주세요",
                "위험한 조항이 있는지 확인해주세요",
                "누락된 중요 조항이 있나요?"
            ]
            
            for i, btn in enumerate(suggest_btns):
                if i < len(suggestions):
                    btn.click(
                        fn=lambda history, q=suggestions[i]: self.ask_question(q, history),
                        inputs=[chatbot],
                        outputs=[chatbot, question_input]
                    )
            
            clear_btn.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, question_input]
            )
            
            # Footer
            gr.Markdown("""
            ---
            ### 사용 가이드
            1. **시스템 초기화**: 먼저 'AI 시스템 초기화' 버튼을 클릭하세요
            2. **파일 업로드**: PDF, DOCX, TXT 형식의 계약서를 업로드하세요
            3. **질문하기**: 자연어로 계약서에 대해 질문하세요
            4. **추천 질문**: 미리 준비된 질문들을 활용해보세요
            
            ### 주의사항
            - 이 시스템은 참고용으로만 사용하세요
            - 중요한 법적 결정은 반드시 전문가와 상담하세요
            - 개인정보가 포함된 계약서 업로드시 주의하세요
            """)
        
        return interface

def main():
    """Main function to run the Gradio app"""
    chatbot = ContractChatbot()
    interface = chatbot.create_interface()
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        debug=True
    )

if __name__ == "__main__":
    main() 