import os
import faiss
import numpy as np

DIMENSION = 384 # Dimensão dos vetores de embedding, deve ser a mesma usada para criar os embeddings
INDEX_PATH = "faiss_index/index.bin"
index = faiss.IndexFlatL2(DIMENSION)

def add_vector(vector: list[float]) -> int:
    vector_np = np.array(vector, dtype=np.float32).reshape(1, -1)
    index.add(vector_np)
    
    return index.ntotal - 1

def search_vectors(vector:list[float], k:int) -> list[tuple[int, float]]:  
    vector_np = np.array(vector, dtype=np.float32).reshape(1, -1)
    distances, indices = index.search(vector_np, k)
    
    return list(zip(indices[0], distances[0]))

def save_index(file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    faiss.write_index(index, file_path)

def load_index(file_path: str):
    
    global index
    
    if os.path.exists(file_path):
        index = faiss.read_index(file_path)