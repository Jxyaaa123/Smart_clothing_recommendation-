md5_path="D:/python/vscode/.vscode/ai model/RAG_project/md5.text"
simhash_path="D:/python/vscode/.vscode/ai model/RAG_project/simhash.text"
simhash_chunk_dir="D:/python/vscode/.vscode/ai model/RAG_project/simhash_chunks"

# Document-level simhash threshold
simhash_max_distance=10
# Chunk-level near-duplicate controls
chunk_simhash_max_distance=6
chunk_duplicate_ratio_threshold=0.8

collection_name="rag"
persist_directory="D:/python/vscode/.vscode/ai model/RAG_project/chroma_db"

chunk_size=1000
chunk_overlap=100
separators=["\n\n","\n",".","!","?","。","！"," ",""]
max_split_char_number=1000#文本分割阈值

similarity_threshold=1 #检索返回文本数量 

embedding_model_name="text-embedding-v4"
chat_model_name="qwen3-max"
