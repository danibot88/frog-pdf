
import ollama

class AIEngine:
    """
    Class responsible for communicating with the local Ollama instance 
    running the Llama 3.2 model for summarization and data structuring.
    """
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def generate_summary_and_tables(self, merged_content: str, analysis_mode: str) -> dict:
        """
        Sends the merged text to the local LLM with an optimized prompt 
        to ensure reliable local processing on Llama 3.2.
        """
        
        # Prompt simplificado e direto para evitar bloqueios do modelo local
        if analysis_mode == "Option 1: Executive & Direct (Fast)":
            prompt = (
                "Por favor, atue como um assistente de análise documental. "
                "Com base no texto fornecido abaixo, crie:\n"
                "1. Um Sumário Executivo claro.\n"
                "2. Um Resumo detalhado dos pontos principais.\n"
                "3. Quaisquer dados ou informações que possam ser organizadas em tabelas (formate em tabelas Markdown).\n\n"
                f"Texto dos Documentos:\n{merged_content}"
            )
        else:  # Option 2: Deep Analytical & Cross-Reference
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
                    {
                        "role": "system",
                        "content": "Você é um assistente de IA prestativo, privado e executado localmente. Responda sempre em português do Brasil e cumpra a solicitação do usuário."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return {"status": "success", "result": response['message']['content']}
        except Exception as e:
            return {
                "status": "error", 
                "result": f"Falha ao conectar com o Ollama local. Certifique-se de que ele está ativo. Erro: {str(e)}"
            }

    def interactive_chat(self, context_text: str, user_query: str) -> str:
        """Allows the user to chat locally and interactively with the loaded documents."""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"Responda à pergunta do usuário estritamente com base no seguinte contexto:\n\n{context_text}"
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro na resposta do chat: {str(e)}"