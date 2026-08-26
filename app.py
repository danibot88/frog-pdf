
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import streamlit as st
from modules.document_loader import DocumentLoader
from modules.ai_engine import AIEngine
from modules.merger import DocumentMerger
from modules.database import LocalDatabase
from modules.rag_engine import LocalRAG

# Configuração da Página com layout largo
st.set_page_config(
    page_title="FrogPDF - AI Local Assistant",
    page_icon="frog.ico" if os.path.exists("frog.ico") else "🐸",
    layout="wide"
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
    st.header("⚙️ Painel de Controle")
    
    projects = db.get_projects()
    project_names = [p[1] for p in projects] if projects else ["Geral / Sem Projeto"]
    
    selected_project = st.selectbox("📂 Projeto / Cliente Ativo:", project_names)
    
    st.markdown("---")
    
    # 1. UPLOAD DE ARQUIVOS
    st.subheader("📤 Enviar Documentos")
    uploaded_files = st.file_uploader(
        "Selecione arquivos para este projeto",
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
# COLUNA CENTRAL: Área Principal (Chat e Resultados)
# ------------------------------------------
with col_center:
    st.title("🐸 FrogPDF")
    st.markdown("Assistente inteligente e privado para documentos confidenciais.")
    
    current_project_id = None
    for p in projects:
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
                        st.success("✅ Documentos processados e analisados com sucesso!")
                    else:
                        st.error(ai_response["result"])

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

    # Chat Inteligente com Suporte a Comparação Multi-Projeto
    st.markdown("---")
    st.header("💬 Chat Inteligente & Comparativo")
    
    # Seletor para escolher quais projetos comparar no chat
    comparison_targets = st.multiselect(
        "🔍 Selecione os projetos para incluir na busca do Chat (Cruzamento de Dados):",
        options=project_names,
        default=[selected_project]
    )

    if current_project_id:
        chat_history = db.get_chat_history(current_project_id)
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    user_query = st.chat_input("Faça uma pergunta ou compare os projetos selecionados...")
    if user_query:
        if not comparison_targets:
            st.warning("Selecione pelo menos um projeto para realizar a busca.")
        else:
            with st.chat_message("user"):
                st.markdown(user_query)
            if current_project_id:
                db.save_message(current_project_id, "user", user_query)
            
            with st.spinner(f"Cruzando dados entre: {', '.join(comparison_targets)}..."):
                # Busca semântica cruzada em múltiplos projetos
                relevant_context = rag.query_multiple_projects(comparison_targets, user_query)
                answer = ai.interactive_chat(relevant_context, user_query)
                
            with st.chat_message("assistant"):
                st.markdown(answer)
            if current_project_id:
                db.save_message(current_project_id, "assistant", answer)

# ------------------------------------------
# COLUNA DIREITA: Gerenciamento de Projetos e Clientes
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
    st.subheader("📋 Projetos Salvos")
    
    if projects:
        for p in projects:
            with st.expander(f"📁 {p[1]}"):
                st.write(f"ID do Projeto: {p[0]}")
                project_path = os.path.join("data", "uploads", p[1].replace(" ", "_"))
                if os.path.exists(project_path):
                    files = os.listdir(project_path)
                    st.write(f"**Arquivos ({len(files)}):**")
                    for f in files:
                        st.text(f"- {f}")
                else:
                    st.text("Nenhum arquivo enviado.")
    else:
        st.info("Nenhum projeto cadastrado ainda.")