
import sys
import os
import base64

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import streamlit as st
from modules.document_loader import DocumentLoader
from modules.ai_engine import AIEngine
from modules.merger import DocumentMerger
from modules.database import LocalDatabase
from modules.rag_engine import LocalRAG

# Configuração da Página com identidade visual FrogPDF
st.set_page_config(
    page_title="FrogPDF - Assistente de IA Local",
    page_icon="frog.ico" if os.path.exists("frog.ico") else "🐸",
    layout="wide"
)

# Trava de idioma para o navegador e CSS personalizado
st.markdown(
    """
    <html lang="pt-BR">
    <style>
    .stApp { background-color: #EAF4EC; }
    [data-testid="stSidebar"] { background-color: #DDEFE0; }
    div.stTextInput > div > div > input,
    div.stSelectbox > div > div > div,
    div.stTextArea > div > div > textarea,
    [data-testid="stExpander"],
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }
    iframe { border-radius: 8px; border: 1px solid #C8E6C9 !important; background-color: #FFFFFF; }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicialização dos Módulos
loader = DocumentLoader()
ai = AIEngine(model_name="llama3.2")
merger = DocumentMerger()
db = LocalDatabase()
rag = LocalRAG()

# Inicialização de estados na sessão para abertura automática do visualizador
if "auto_open_viewer" not in st.session_state:
    st.session_state["auto_open_viewer"] = False

# ==========================================
# ESTRUTURA DE 3 COLUNAS (Esquerda, Centro, Direita)
# ==========================================
col_left, col_center, col_right = st.columns([1.2, 2.8, 1.5])

# ------------------------------------------
# COLUNA ESQUERDA: Controles e Upload
# ------------------------------------------
with col_left:
    st.header("⚙️ FrogPDF")
    
    active_projects = db.get_projects(status='active')
    project_names = [p[1] for p in active_projects] if active_projects else ["Geral / Sem Projeto"]
    
    selected_project = st.selectbox("📂 Projeto Ativo:", project_names)
    
    st.markdown("---")
    
    st.subheader("📤 Enviar Documentos")
    uploaded_files = st.file_uploader(
        "Selecione arquivos para este projeto",
        type=["pdf", "docx", "doc", "xlsx", "csv"],
        accept_multiple_files=True
    )
    
    st.markdown("---")
    
    st.subheader("Estratégia de Merge")
    merge_choice = st.selectbox(
        "Modo de mesclagem:",
        [
            "Option 1: Sequential Concatenation", 
            "Option 2: Grouped by Document Type",
            "Nenhum (Apenas Análise Direta)"
        ]
    )
    
    st.subheader("Tipo de Análise IA")
    analysis_choice = st.selectbox(
        "Formato do sumário:",
        [
            "Option 1: Executive & Direct (Fast)", 
            "Option 2: Deep Analytical & Cross-Reference",
            "Nenhum (Apenas Merge / Sem Resumo)"
        ]
    )
    
    st.markdown("---")
    process_btn = st.button("🚀 Processar e Indexar", use_container_width=True)

# ------------------------------------------
# COLUNA CENTRAL: Área Principal & Chat Inteligente
# ------------------------------------------
with col_center:
    st.title("🐸 FrogPDF")
    st.markdown("Assistente inteligente e privado para documentos confidenciais.")
    
    current_project_id = None
    all_projects_flat = db.get_projects()
    for p in all_projects_flat:
        if p[1] == selected_project:
            current_project_id = p[0]
            break

    if process_btn:
        if not uploaded_files:
            st.warning("⚠️ Envie pelo menos um arquivo.")
        else:
            with st.spinner("Lendo arquivos, aplicando OCR e processando..."):
                project_folder = os.path.join("data", "uploads", selected_project.replace(" ", "_"))
                os.makedirs(project_folder, exist_ok=True)
                
                documents_data = {}
                for file in uploaded_files:
                    file_path = os.path.join(project_folder, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    extracted_text = loader.load_document(file_path)
                    documents_data[file.name] = extracted_text
                
                combined_text = merger.merge_documents(documents_data, merge_choice)
                st.session_state["processed_context"] = combined_text
                rag.add_documents_to_collection(selected_project, documents_data)
                
                if analysis_choice == "Nenhum (Apenas Merge / Sem Resumo)":
                    st.session_state["analysis_result"] = (
                        "### 📋 Merge Concluído sem Análise de IA\n\n"
                        "Os documentos foram mesclados com sucesso. Utilize os comandos no chat para exportar."
                    )
                else:
                    ai_response = ai.generate_summary_and_tables(combined_text, analysis_choice)
                    if ai_response["status"] == "success":
                        st.session_state["analysis_result"] = ai_response["result"]
                    else:
                        st.error(ai_response["result"])
                
                st.success("✅ Processamento concluído com sucesso!")

    # ==========================================
    # VISUALIZADOR DE DOCUMENTOS (Oculto em Expansor por padrão)
    # Abre automaticamente apenas quando novos arquivos são processados ou gerados
    # ==========================================
    st.markdown("---")
    with st.expander("👁️ Visualizador de Documentos do Projeto", expanded=st.session_state["auto_open_viewer"]):
        project_folder = os.path.join("data", "uploads", selected_project.replace(" ", "_"))
        if os.path.exists(project_folder):
            project_files = [f for f in os.listdir(project_folder) if os.path.isfile(os.path.join(project_folder, f))]
            if project_files:
                selected_file_to_view = st.selectbox("Selecione o arquivo para visualizar:", project_files)
                file_path_to_view = os.path.join(project_folder, selected_file_to_view)
                
                if selected_file_to_view.lower().endswith('.pdf'):
                    with open(file_path_to_view, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    st.markdown(
                        f'''
                        <div style="background-color: #FFFFFF; padding: 10px; border-radius: 10px; border: 1px solid #C8E6C9;">
                            <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf" style="border: none;"></iframe>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                else:
                    file_text_preview = loader.load_document(file_path_to_view)
                    st.text_area("Conteúdo:", file_text_preview, height=250)
            else:
                st.info("Nenhum arquivo enviado para este projeto.")
        else:
            st.info("Nenhuma pasta de projeto criada.")

    # Exibir Relatórios e Central de Exportação
    if "analysis_result" in st.session_state and st.session_state["analysis_result"]:
        st.markdown("---")
        st.header("📊 Resultado do Processamento")
        st.markdown(st.session_state["analysis_result"])
        
        st.markdown("---")
        st.subheader("📥 Central de Exportação")
        
        export_format = st.selectbox(
            "Escolha o formato de saída:",
            ["Relatório / Texto em Word (.docx)", "Relatório / Texto em PDF (.pdf)", "Tabelas em Excel (.xlsx)"]
        )
        
        content_to_export = st.session_state["processed_context"] if analysis_choice == "Nenhum (Apenas Merge / Sem Resumo)" else st.session_state["analysis_result"]

        if export_format == "Relatório / Texto em Word (.docx)":
            file_data = merger.export_to_docx(content_to_export)
            file_name = f"{selected_project}_Export.docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif export_format == "Relatório / Texto em PDF (.pdf)":
            file_data = merger.export_to_pdf(content_to_export)
            file_name = f"{selected_project}_Export.pdf"
            mime_type = "application/pdf"
        else:
            file_data = merger.export_markdown_tables_to_excel(content_to_export)
            file_name = f"{selected_project}_Tables.xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        # Ao gerar arquivo na central, ativa a bandeira para abrir o visualizador automaticamente
        if st.download_button(
            label=f"Baixar {export_format}",
            data=file_data,
            file_name=file_name,
            mime=mime_type,
            use_container_width=True
        ):
            st.session_state["auto_open_viewer"] = True
            st.rerun()

    # ==========================================
    # CHAT INTELIGENTE COM COMANDOS RÁPIDOS E BOTÕES INLINE
    # ==========================================
    st.markdown("---")
    st.header("💬 Chat Inteligente & Comandos Rápidos")
    
    all_active_names = [p[1] for p in db.get_projects(status='active')]
    comparison_targets = st.multiselect(
        "🔍 Selecione os projetos para incluir na busca do Chat:",
        options=all_active_names if all_active_names else [selected_project],
        default=[selected_project]
    )

    if current_project_id:
        chat_history = db.get_chat_history(current_project_id)
        for idx, msg in enumerate(chat_history):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                # Se a mensagem do assistente contiver comandos de exportação, renderiza botões inline
                if msg["role"] == "assistant" and "arquivo pronto" in msg["content"].lower():
                    pass # Botões dinâmicos tratados no fluxo
                
    user_query = st.chat_input("Digite sua dúvida ou comando (ex: 'exportar word', 'prazos', 'resumo')...")
    if user_query:
        if not comparison_targets:
            st.warning("Selecione pelo menos um projeto para realizar a busca.")
        else:
            with st.chat_message("user"):
                st.markdown(user_query)
            if current_project_id:
                db.save_message(current_project_id, "user", user_query)
            
            query_lower = user_query.lower()
            answer = ""
            
            # Tratamento inteligente direto no chat para comandos de exportação
            if any(k in query_lower for k in ["exportar word", "word"]):
                export_content = st.session_state.get("analysis_result", "Nenhum conteúdo processado.")
                docx_io = merger.export_to_docx(export_content)
                answer = "📄 **Arquivo Word (.docx)** gerado com sucesso! Clique no botão abaixo para baixar:"
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.download_button("📥 Baixar Arquivo Word", data=docx_io, file_name=f"{selected_project}_ChatExport.docx", key=f"chat_word_{os.urandom(4).hex()}")
                st.session_state["auto_open_viewer"] = True
                
            elif any(k in query_lower for k in ["gerar pdf", "pdf"]):
                export_content = st.session_state.get("analysis_result", "Nenhum conteúdo processado.")
                pdf_io = merger.export_to_pdf(export_content)
                answer = "📑 **Relatório em PDF** gerado com sucesso! Clique no botão abaixo para baixar:"
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.download_button("📥 Baixar Relatório PDF", data=pdf_io, file_name=f"{selected_project}_ChatExport.pdf", key=f"chat_pdf_{os.urandom(4).hex()}")
                st.session_state["auto_open_viewer"] = True
                
            elif any(k in query_lower for k in ["planilha excel", "excel"]):
                export_content = st.session_state.get("analysis_result", "Nenhum conteúdo processado.")
                excel_io = merger.export_markdown_tables_to_excel(export_content)
                answer = "📊 **Planilha Excel (.xlsx)** gerada com sucesso! Clique no botão abaixo para baixar:"
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.download_button("📥 Baixar Planilha Excel", data=excel_io, file_name=f"{selected_project}_ChatTables.xlsx", key=f"chat_excel_{os.urandom(4).hex()}")
                st.session_state["auto_open_viewer"] = True
                
            else:
                with st.spinner("Processando comando localmente com Llama 3.2..."):
                    relevant_context = rag.query_multiple_projects(comparison_targets, user_query)
                    answer = ai.execute_chat_command(relevant_context, user_query)
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    
            if current_project_id:
                db.save_message(current_project_id, "assistant", answer)

# ------------------------------------------
# COLUNA DIREITA: Gestão de Projetos
# ------------------------------------------
with col_right:
    st.header("🏢 Clientes & Projetos")
    
    new_project_name = st.text_input("Novo Projeto/Cliente:")
    if st.button("➕ Criar Projeto", use_container_width=True):
        if new_project_name.strip():
            db.add_project(new_project_name.strip())
            st.success(f"Projeto '{new_project_name}' criado!")
            st.rerun()
        else:
            st.warning("Digite um nome válido.")
            
    st.markdown("---")
    tab_active, tab_inactive = st.tabs(["🟢 Ativos", "⚪ Inativos"])
    
    with tab_active:
        active_list = db.get_projects(status='active')
        if active_list:
            for p in active_list:
                with st.expander(f"📁 {p[1]}"):
                    if st.button("📥 Arquivar / Inativar", key=f"inact_{p[0]}"):
                        db.toggle_project_status(p[0], 'inactive')
                        st.rerun()
        else:
            st.info("Nenhum projeto ativo.")
            
    with tab_inactive:
        inactive_list = db.get_projects(status='inactive')
        if inactive_list:
            for p in inactive_list:
                with st.expander(f"📁 {p[1]} (Inativo)"):
                    if st.button("📤 Reativar Projeto", key=f"act_{p[0]}"):
                        db.toggle_project_status(p[0], 'active')
                        st.rerun()
        else:
            st.info("Nenhum projeto inativo.")