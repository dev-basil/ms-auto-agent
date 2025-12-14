
import json
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

class RAGManager:
    def __init__(self, dataset_path="dataset/ds.json", model_name="all-MiniLM-L6-v2"):
        self.dataset_path = dataset_path
        self.model_name = model_name
        self.vector_store = None
        self.embeddings = None
        self._initialize_rag()

    def _initialize_rag(self):
        # Load dataset
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        
        with open(self.dataset_path, "r") as f:
            data = json.load(f)

        # Prepare documents for indexing
        # We index the 'input' (error log) and store 'output' (action) in metadata
        documents = []
        for entry in data:
            doc = Document(
                page_content=entry["input"],
                metadata={"action": entry["output"], "instruction": entry["instruction"]}
            )
            documents.append(doc)

        print(f"Loaded {len(documents)} entries from dataset.")

        # Initialize Embeddings
        # Using HuggingFace embeddings via sentence-transformers
        print(f"Loading embeddings model: {self.model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

        # Create Vector Store
        print("Creating FAISS index...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        print("RAG system initialized.")

    def get_action(self, log_entry, k=1, score_threshold=1.0):
        """
        Retrieve the action for a given log entry.
        
        Args:
            log_entry (str): The error log to query.
            k (int): Number of results to retrieve.
            score_threshold (float): Distance threshold. Lower is better for L2 distance (FAISS default).
                                   However, FAISS wrapper usually returns a score. 
                                   If using cosine similarity, higher is better.
                                   LangChain FAISS usually uses L2 distance by default. 
                                   Let's check the score. 
                                   
        Returns:
            str: The suggested action or None if no close match is found.
        """
        if not self.vector_store:
            raise RuntimeError("RAG system not initialized.")

        # Search
        results_with_score = self.vector_store.similarity_search_with_score(log_entry, k=k)
        
        if not results_with_score:
            return None
        
        best_doc, score = results_with_score[0]
        
        # Note: FAISS L2 distance: lower is better. 0 is exact match.
        # Arbitrary threshold: depends on the embedding space. 
        # For normalized embeddings, L2 distance ranges from 0 to 2.
        # Let's log the score to debug.
        print(f"Best match score (L2 distance): {score}")
        print(f"Best match content: {best_doc.page_content}")
        
        # If score is too high (meaning different), we might return None.
        # For now, let's just return the best match if it's somewhat reasonable.
        # Let's say < 1.0 for now.
        if score < score_threshold:
            return best_doc.metadata.get("action")
        
        return None

if __name__ == "__main__":
    # Test
    # Assuming run from src/ or root. Let's adjust path logic if needed.
    # Current CWD is usually project root.
    dataset_loc = "dataset/ds.json"
    if not os.path.exists(dataset_loc):
        # try parent directory if running from src
        dataset_loc = "../dataset/ds.json"
    
    rag = RAGManager(dataset_path=dataset_loc)
    
    test_log = "cache refreshed successfully."
    action = rag.get_action(test_log)
    print(f"Query: {test_log}")
    print(f"Action: {action}")
