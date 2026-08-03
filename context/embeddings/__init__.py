from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_default_embedding() -> BaseEmbedding:
    return HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base")
