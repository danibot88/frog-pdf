import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalRAG:
    """
    Class responsible for local document splitting, indexing, 
    and fast multi-project search using scikit-learn without PyTorch dependencies.
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

        vectorizer = TfidfVectorizer(stop_words=None)
        corpus = [item["content"] for item in all_chunks]
        tfidf_matrix = vectorizer.fit_transform(corpus)

        safe_project_name = "".join([c if c.isalnum() else "_" for c in project_name])
        index_path = os.path.join(self.persist_directory, f"{safe_project_name}_index.pkl")
        
        data_to_store = {
            "vectorizer": vectorizer,
            "tfidf_matrix": tfidf_matrix,
            "chunks": all_chunks
        }
        
        with open(index_path, "wb") as f:
            pickle.dump(data_to_store, f)

    def query_multiple_projects(self, project_names: list, query: str, n_results: int = 2) -> str:
        """
        Performs similarity search across one or multiple projects simultaneously 
        to enable cross-client comparison.
        """
        all_retrieved_texts = []

        for project_name in project_names:
            safe_project_name = "".join([c if c.isalnum() else "_" for c in project_name])
            index_path = os.path.join(self.persist_directory, f"{safe_project_name}_index.pkl")

            if not os.path.exists(index_path):
                continue

            try:
                with open(index_path, "rb") as f:
                    saved_data = pickle.load(f)

                vectorizer = saved_data["vectorizer"]
                tfidf_matrix = saved_data["tfidf_matrix"]
                chunks = saved_data["chunks"]

                query_vector = vectorizer.transform([query])
                cosine_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
                
                top_indices = cosine_scores.argsort()[-n_results:][::-1]
                
                for idx in top_indices:
                    if cosine_scores[idx] > 0.0:
                        item = chunks[idx]
                        all_retrieved_texts.append(f"[Projeto: {project_name} | Fonte: {item['filename']}]\n{item['content']}")
            except Exception:
                continue

        if not all_retrieved_texts:
            return "Nenhum trecho relevante encontrado nos projetos selecionados."

        return "\n\n---\n\n".join(all_retrieved_texts)