
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

# Injeção de CSS personalizado para garantir fundo verde claro e caixas brancas
st.markdown(
    """
    <style>
    /* Cor de fundo geral da aplicação (Verde Claro) */
    .stApp {
        background-color: #EAF4EC;
    }
    
    /* Cor de fundo da barra lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #DDEFE0;
    }

    /* Força as caixas de texto, expansores e blocos internos a ficarem em Branco */
    div.stTextInput > div > div > input,
    div.stSelectbox > div > div > div,
    div.stTextArea > div > div > textarea,
    [data-testid="stExpander"],
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }

    /* Remove qualquer tom azulado indesejado em molduras ou bordas de componentes */
    iframe {
        border-radius: 8px;
        border: 1px solid #C8E6C9 !important;
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Trava de idioma para o navegador
st.markdown('<html lang="pt-BR">', unsafe_allow_html=True)

# Inicialização dos Módulos
loader = DocumentLoader()
ai = AIEngine(model_name="llama3.2")
merger = DocumentMerger()
db = LocalDatabase()
rag = LocalRAG()

# ==========================================
# ESTRUTURA DE 3 COLUNAS (Esquerda, Centro, Direita)
# ==========================================
col_left, col_center, col_right = st.columns([1.2, 2.8, 1.5])

# ------------------------------------------
# COLUNA ESQUERDA: Upload, Merge e Análise
# ------------------------------------------
with col_left:
    st.header("⚙️ Inicio")
    
    # Busca apenas projetos ativos para o fluxo de trabalho diário
    active_projects = db.get_projects(status='active')
    project_names = [p[1] for p in active_projects] if active_projects else ["Geral / Sem Projeto"]
    
    selected_project = st.selectbox("📂 Projeto:", project_names)
    
    st.markdown("---")
    
    # 1. UPLOAD DE ARQUIVOS
    st.subheader("📤 Enviar Docs")
    uploaded_files = st.file_uploader(
        "Selecione ou arraste arquivos aqui ",
        type=["pdf", "docx", "doc", "xlsx", "csv"],
        accept_multiple_files=True
    )
    
    st.markdown("---")
    
    # 2. OPÇÕES DE MERGE E ANÁLISE
    st.subheader("Estratégia de Merge")
    merge_choice = st.selectbox(
        "Modo de mesclagem:",
        [
            "Option 1: Sequential Concatenation", 
            "Option 2: Grouped by Document Type",
            "Nenhum (Apenas Análise Direta)"
        ]
    )
    
    st.subheader("Análise de IA")
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
# COLUNA CENTRAL: Área Principal
# ------------------------------------------
with col_center:
    st.title("🐸 FrogPDF")
    st.markdown("Assistente inteligente e privado para documentos confidenciais.")
    
    current_project_id = None
    all_projects_flat = db.get_projects() # Todos para mapear ID
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
                        "Os documentos foram mesclados com sucesso conforme a estratégia selecionada."
                    )
                    st.success("✅ Merge executado com sucesso.")
                else:
                    ai_response = ai.generate_summary_and_tables(combined_text, analysis_choice)
                    if ai_response["status"] == "success":
                        st.session_state["analysis_result"] = ai_response["result"]
                        st.success("✅ Documentos processados, indexados e analisados com sucesso!")
                    else:
                        st.error(ai_response["result"])

    # Botão de Extração de Dados-Chave
    if st.session_state.get("processed_context"):
        st.markdown("---")
        if st.button("🔍 Extrair Dados Estruturados (CNPJ, Valores, Datas)", use_container_width=True):
            with st.spinner("Extraindo entidades e dados-chave dos documentos..."):
                extracted_table = ai.extract_structured_data(st.session_state["processed_context"])
                st.session_state["extracted_data_result"] = extracted_table

    if "extracted_data_result" in st.session_state:
        st.markdown("### 📑 Dados-Chave Extraídos")
        st.markdown(st.session_state["extracted_data_result"])

    # Visualizador Nativo de Documentos do Projeto (Via HTML/Base64)
    st.markdown("---")
    st.header("👁️ Visualizador de Documentos")
    project_folder = os.path.join("data", "uploads", selected_project.replace(" ", "_"))
    
    if os.path.exists(project_folder):
        project_files = [f for f in os.listdir(project_folder) if os.path.isfile(os.path.join(project_folder, f))]
        if project_files:
            selected_file_to_view = st.selectbox("Selecione o arquivo para visualizar:", project_files)
            file_path_to_view = os.path.join(project_folder, selected_file_to_view)
            
            if selected_file_to_view.lower().endswith('.pdf'):
                # Renderiza PDF de forma limpa dentro de um container emoldurado em branco
                with open(file_path_to_view, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                st.markdown(
                    f'''
                    <div style="background-color: #FFFFFF; padding: 10px; border-radius: 10px; border: 1px solid #C8E6C9;">
                        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf" style="border: none;"></iframe>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            elif selected_file_to_view.lower().endswith(('.docx', '.xlsx', '.csv', '.txt')):
                with st.expander(f"Ver conteúdo extraído de: {selected_file_to_view}"):
                    file_text_preview = loader.load_document(file_path_to_view)
                    st.text_area("Conteúdo:", file_text_preview, height=300)
        else:
            st.info("Nenhum arquivo enviado para este projeto ainda.")
    else:
        st.info("Nenhuma pasta de projeto criada ainda.")

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
            
        st.download_button(
            label=f"Baixar {export_format}",
            data=file_data,
            file_name=file_name,
            mime=mime_type,
            use_container_width=True
        )

    # Chat Inteligente com Recurso de Citação de Fontes
    st.markdown("---")
    st.header("💬 Chat")
    
    all_active_names = [p[1] for p in db.get_projects(status='active')]
    comparison_targets = st.multiselect(
        "🔍 Selecione os projetos para incluir na busca do Chat:",
        options=all_active_names if all_active_names else [selected_project],
        default=[selected_project]
    )

    if current_project_id:
        chat_history = db.get_chat_history(current_project_id)
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    user_query = st.chat_input("Faça uma pergunta (o assistente citará as fontes)...")
    if user_query:
        if not comparison_targets:
            st.warning("Selecione pelo menos um projeto para realizar a busca.")
        else:
            with st.chat_message("user"):
                st.markdown(user_query)
            if current_project_id:
                db.save_message(current_project_id, "user", user_query)
            
            with st.spinner("Buscando trechos e gerando resposta fundamentada..."):
                relevant_context = rag.query_multiple_projects(comparison_targets, user_query)
                answer = ai.interactive_chat_with_grounding(relevant_context, user_query)
                
            with st.chat_message("assistant"):
                st.markdown(answer)
            if current_project_id:
                db.save_message(current_project_id, "assistant", answer)

# ------------------------------------------
# COLUNA DIREITA: Gestão de Projetos (Ativos / Inativos)
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
    
    # Abas visuais intuitivas para Ativos e Inativos
    tab_active, tab_inactive = st.tabs(["🟢 Ativos", "⚪ Inativos"])
    
    with tab_active:
        active_list = db.get_projects(status='active')
        if active_list:
            for p in active_list:
                with st.expander(f"📁 {p[1]}"):
                    st.write(f"ID: {p[0]}")
                    project_path = os.path.join("data", "uploads", p[1].replace(" ", "_"))
                    if os.path.exists(project_path):
                        files = os.listdir(project_path)
                        st.write(f"**Arquivos ({len(files)}):**")
                        for f in files:
                            st.text(f"- {f}")
                    else:
                        st.text("Nenhum arquivo.")
                    
                    # Botão intuitivo para desativar (enviar para referência)
                    if st.button("📥 Arquivar / Inativar", key=f"inactivate_{p[0]}"):
                        db.toggle_project_status(p[0], 'inactive')
                        st.rerun()
        else:
            st.info("Nenhum projeto ativo.")
            
    with tab_inactive:
        inactive_list = db.get_projects(status='inactive')
        if inactive_list:
            for p in inactive_list:
                with st.expander(f"📁 {p[1]} (Inativo)"):
                    st.write(f"ID: {p[0]}")
                    project_path = os.path.join("data", "uploads", p[1].replace(" ", "_"))
                    if os.path.exists(project_path):
                        files = os.listdir(project_path)
                        st.write(f"**Arquivos de Referência ({len(files)}):**")
                        for f in files:
                            st.text(f"- {f}")
                    else:
                        st.text("Nenhum arquivo.")
                    
                    # Botão intuitivo para reativar
                    if st.button("📤 Reativar Projeto", key=f"activate_{p[0]}"):
                        db.toggle_project_status(p[0], 'active')
                        st.rerun()
        else:
            st.info("Nenhum projeto inativo.")