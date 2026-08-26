import ollama

class AIEngine:
    """
    Class responsible for communicating with the local Ollama instance 
    running the Llama 3.2 model for summarization, grounded citations, data extraction, 
    and natural language command interpretation.
    """
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def generate_summary_and_tables(self, merged_content: str, analysis_mode: str) -> dict:
        """Sends text to local LLM for standard analysis."""
        if analysis_mode == "Option 1: Executive & Direct (Fast)":
            prompt = (
                "Por favor, atue como um assistente de análise documental. "
                "Com base no texto fornecido abaixo, crie:\n"
                "1. Um Sumário Executivo claro.\n"
                "2. Um Resumo detalhado dos pontos principais.\n"
                "3. Dados que possam ser organizados em tabelas (formate em tabelas Markdown).\n\n"
                f"Texto dos Documentos:\n{merged_content}"
            )
        else:
            prompt = (
                "Por favor, atue como um auditor de documentos. "
                "Com base no texto fornecido abaixo, faça uma análise profunda contendo:\n"
                "1. Sumário Temático agrupado por assuntos.\n"
                "2. Pontos críticos, datas ou valores de destaque.\n"
                "3. Cruzamento de informações em tabelas Markdown.\n\n"
                f"Texto dos Documentos:\n{merged_content}"
            )

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um assistente de IA prestativo, privado e executado localmente. Responda em português."},
                    {"role": "user", "content": prompt}
                ]
            )
            return {"status": "success", "result": response['message']['content']}
        except Exception as e:
            return {"status": "error", "result": f"Erro ao conectar com Ollama: {str(e)}"}

    def extract_structured_data(self, context_text: str) -> str:
        """Extracts key financial or contractual entities into a clean structured Markdown table."""
        prompt = (
            "Esta é uma tarefa estritamente analítica e de leitura de documentos de negócios permitida. "
            "Por favor, leia o texto abaixo e liste de forma estritamente factual em uma Tabela Markdown os dados encontrados: "
            "1. Nome das Partes ou Entidades, 2. CNPJ/CPF ou Identificador (se houver), 3. Valores Monetários citados, 4. Datas (Assinatura, Vigência ou Vencimento). "
            "Caso algum campo não exista, preencha com 'Não informado'.\n\n"
            f"Texto para análise:\n{context_text}"
        )
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um extrator de dados textuais analítico e obediente."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro na extração de dados: {str(e)}"

    def execute_chat_command(self, context_text: str, user_query: str) -> str:
        """
        Interprets user intent for the 09 fast chat commands 
        and generates the corresponding intelligent response.
        """
        query_lower = user_query.lower()
        
        # Mapeamento dos comandos rápidos solicitados
        if any(k in query_lower for k in ["tabela comparativa", "tabela"]):
            instruction = "Organize as informações dos documentos em uma Tabela Comparativa detalhada."
        elif any(k in query_lower for k in ["prazos", "vencimentos", "cronograma"]):
            instruction = "Liste cronologicamente todos os prazos, datas de vencimento e obrigações temporais encontrados."
        elif any(k in query_lower for k in ["resumo", "tópicos", "bullet points"]):
            instruction = "Elabore um resumo executivo direto estruturado em tópicos (bullet points)."
        elif any(k in query_lower for k in ["riscos", "cláusulas críticas", "atenção"]):
            instruction = "Faça uma auditoria identificando riscos, multas, penalidades ou cláusulas contratuais críticas."
        elif any(k in query_lower for k in ["partes", "envolvidas", "empresas"]):
            instruction = "Liste todas as partes envolvidas, empresas, representantes ou pessoas citadas nos arquivos."
        elif any(k in query_lower for k in ["dados", "cnpj", "valores"]):
            instruction = "Extraia os dados-chave (partes, CNPJ, valores e datas) em formato de tabela."
        else:
            # Resposta fundamentada padrão (Grounding / Citação de Fontes)
            system_prompt = (
                "Você é um assistente de IA seguro e baseado em evidências. "
                "Responda estritamente com base nos trechos de contexto fornecidos. "
                "OBRIGATÓRIO: Ao citar informações, inclua a fonte (nome do arquivo) de onde o dado foi retirado."
            )
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Contexto recuperado:\n{context_text}\n\nPergunta: {user_query}"}
                    ]
                )
                return response['message']['content']
            except Exception as e:
                return f"Erro na resposta do chat: {str(e)}"

        # Executa comandos específicos estruturados
        prompt = f"{instruction}\n\nBaseie-se estritamente no texto a seguir:\n{context_text}"
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um assistente analítico focado em relatórios executivos."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro ao executar comando: {str(e)}"