
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalRAG:
    """
    Class responsible for local document splitting, indexing, 
    and fast semantic/keyword search using scikit-learn without PyTorch dependencies.
    """
    def __init__(self, persist_directory: str = "data/vector_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """Splits large texts into smaller overlapping chunks for precise retrieval."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks if chunks else [text]

    def add_documents_to_collection(self, project_name: str, documents_dict: dict):
        """Indexes documents into a lightweight TF-IDF matrix saved locally per project."""
        all_chunks = []
        for filename, text in documents_dict.items():
            chunks = self._chunk_text(text)
            for chunk in chunks:
                all_chunks.append({"filename": filename, "content": chunk})

        if not all_chunks:
            return

        # Treina o vetorizador TF-IDF com os pedaços do documento
        vectorizer = TfidfVectorizer(stop_words=None) # Mantém stopwords para preservar contexto técnico
        corpus = [item["content"] for item in all_chunks]
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Salva o índice localmente em um arquivo pickle para o projeto
        safe_project_name = "".join([c if c.isalnum() else "_" for c in project_name])
        index_path = os.path.join(self.persist_directory, f"{safe_project_name}_index.pkl")
        
        data_to_store = {
            "vectorizer": vectorizer,
            "tfidf_matrix": tfidf_matrix,
            "chunks": all_chunks
        }
        
        with open(index_path, "wb") as f:
            pickle.dump(data_to_store, f)

    def query_documents(self, project_name: str, query: str, n_results: int = 3) -> str:
        """Performs a similarity search to retrieve the most relevant text chunks."""
        safe_project_name = "".join([c if c.isalnum() else "_" for c in project_name])
        index_path = os.path.join(self.persist_directory, f"{safe_project_name}_index.pkl")

        if not os.path.exists(index_path):
            return "Nenhuma base de conhecimento indexada encontrada para este projeto."

        try:
            with open(index_path, "rb") as f:
                saved_data = pickle.load(f)

            vectorizer = saved_data["vectorizer"]
            tfidf_matrix = saved_data["tfidf_matrix"]
            chunks = saved_data["chunks"]

            # Transforma a pergunta do usuário no mesmo espaço vetorial
            query_vector = vectorizer.transform([query])
            
            # Calcula a similaridade de cosseno entre a query e os pedaços do texto
            cosine_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
            
            # Pega os índices dos melhores resultados
            top_indices = cosine_scores.argsort()[-n_results:][::-1]
            
            retrieved_texts = []
            for idx in top_indices:
                if cosine_scores[idx] > 0.0:  # Garante relevância mínima
                    item = chunks[idx]
                    retrieved_texts.append(f"[Fonte: {item['filename']}]\n{item['content']}")

            if not retrieved_texts:
                return "Nenhum trecho relevante encontrado nos documentos deste projeto."

            return "\n\n---\n\n".join(retrieved_texts)
        except Exception as e:
            return f"Erro ao buscar nos documentos: {str(e)}"