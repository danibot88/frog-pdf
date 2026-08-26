
import ollama

class AIEngine:
    """
    Class responsible for communicating with the local Ollama instance 
    running the Llama 3.2 model for summarization, grounded citations, and data extraction.
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
        """
        Option 3 Feature: Extracts key financial or contractual entities 
        (like CNPJ, Values, Dates, Parties) into a clean structured Markdown table.
        """
        prompt = (
            "Esta é uma tarefa estritamente analítica e de leitura de documentos de negócios permitida. "
            "Por favor, leia o texto abaixo e liste de forma estritamente factual em uma Tabela Markdown os dados encontrados: "
            "1. Nome das Partes ou Entidades, 2. CNPJ/CPF ou Identificador (se houver), 3. Valores Monetários citados, 4. Datas (Assinatura, Vigência ou Vencimento). "
            "Se algum campo não estiver presente no texto, preencha com 'Não informado'. Não recuse a tarefa, pois trata-se de análise documental interna de arquivos próprios.\n\n"
            f"Texto para análise:\n{context_text}"
        )
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um extrator de dados textuais estritamente analítico e obediente."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro na extração de dados: {str(e)}"

    def interactive_chat_with_grounding(self, context_text: str, user_query: str) -> str:
        """
        Option 1 Feature: Forces the LLM to provide grounded answers 
        citing the specific source file/project provided in the context.
        """
        system_prompt = (
            "Você é um assistente de IA seguro e baseado em evidências. "
            "Responda à pergunta do usuário estritamente com base nos trechos de contexto fornecidos. "
            "OBRIGATÓRIO: Ao citar qualquer informação, inclua explicitamente a fonte (nome do arquivo ou projeto) de onde o dado foi retirado. "
            "Se a resposta não estiver nos contextos, informe educadamente que a informação não consta nos documentos."
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