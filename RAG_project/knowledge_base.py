import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str:str):
    #检查传入的是否被处理过
    if not os.path.exists(config.md5_path):
        #表示文件不存在
        open(config.md5_path,'w',encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path,'r',encoding="utf-8").readlines():
            line=line.strip()#处理回车和空格
            if line==md5_str:
                return True
        return False    
        
def save_md5(md5_str:str):
    #将传入的文件进行保存用来校验
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str+'\n')


import re

class SimHash:
    """局部敏感哈希：内容只做少量修改时，海明距离很小。"""
    def __init__(self, text: str, hashbits: int = 64):
        self.hashbits = hashbits
        self.value = self._compute(text)

    def _features(self, text: str):
        # 按 Unicode 单词切分后取 3-gram，中英文都适用
        words = re.findall(r"\w+", text, re.UNICODE)
        features = []
        for w in words:
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    features.append(w[i:i + 3])
            else:
                features.append(w)
        return features

    def _compute(self, text: str) -> int:
        features = self._features(text)
        if not features:
            return 0
        vec = [0] * self.hashbits
        for f in features:
            h = int(hashlib.md5(f.encode("utf-8")).hexdigest(), 16)
            for i in range(self.hashbits):
                if (h >> i) & 1:
                    vec[i] += 1
                else:
                    vec[i] -= 1
        result = 0
        for i in range(self.hashbits):
            if vec[i] > 0:
                result |= (1 << i)
        return result

    def hex(self) -> str:
        return f"{self.value:0{self.hashbits // 4}x}"

    def distance(self, other: "SimHash") -> int:
        return bin(self.value ^ other.value).count("1")

def check_simhash(simhash_hex: str) -> tuple[bool, int]:
    """返回 (是否近重复, 最小海明距离)"""
    if not os.path.exists(config.simhash_path):
        open(config.simhash_path, "w", encoding="utf-8").close()
        return False, -1
    current = SimHash.__new__(SimHash)
    current.hashbits = 64
    current.value = int(simhash_hex, 16)
    min_distance = current.hashbits
    duplicate = False
    for line in open(config.simhash_path, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            other = SimHash.__new__(SimHash)
            other.hashbits = 64
            other.value = int(line, 16)
            dist = current.distance(other)
            if dist < min_distance:
                min_distance = dist
            if dist <= config.simhash_max_distance:
                duplicate = True
                break
        except ValueError:
            continue
    return duplicate, min_distance

def save_simhash(simhash_hex: str):
    with open(config.simhash_path, "a", encoding="utf-8") as f:
        f.write(simhash_hex + "\n")




def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _chunk_fingerprint_path(source: str) -> str:
    safe = source.replace("/", "_").replace("\\", "_")
    return os.path.join(config.simhash_chunk_dir, f"{safe}.txt")


def save_chunk_simhashes(source: str, chunks: list[str]):
    _ensure_dir(config.simhash_chunk_dir)
    path = _chunk_fingerprint_path(source)
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(SimHash(chunk).hex() + "\n")


def load_all_chunk_simhashes() -> list[str]:
    _ensure_dir(config.simhash_chunk_dir)
    results: list[str] = []
    for name in os.listdir(config.simhash_chunk_dir):
        path = os.path.join(config.simhash_chunk_dir, name)
        if not os.path.isfile(path) or not name.endswith(".txt"):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(line)
    return results


def check_chunk_level_near_duplicate(chunks: list[str]) -> tuple[bool, float]:
    new_hexes = [SimHash(c).hex() for c in chunks]
    if not new_hexes:
        return False, 0.0
    existing = load_all_chunk_simhashes()
    if not existing:
        return False, 0.0

    hit = 0
    for hex_val in new_hexes:
        cur = SimHash.__new__(SimHash)
        cur.hashbits = 64
        cur.value = int(hex_val, 16)
        best = cur.hashbits
        for other_hex in existing:
            other = SimHash.__new__(SimHash)
            other.hashbits = 64
            other.value = int(other_hex, 16)
            dist = cur.distance(other)
            if dist < best:
                best = dist
        if best <= config.chunk_simhash_max_distance:
            hit += 1

    ratio = hit / len(new_hexes)
    return ratio >= config.chunk_duplicate_ratio_threshold, ratio


def get_string_md5(input_str:str,encoding='utf-8'):
    #转换为md5字符串
    #将字符串转换为二进制字节
    str_bytes=input_str.encode(encoding=encoding)
    md5_obj=hashlib.md5()#得到MD5对象
    md5_obj.update(str_bytes)#更新内容
    md5_hex=md5_obj.hexdigest()
    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory,exist_ok=True)#确保文件夹存在
        self.chroma=Chroma(
            collection_name=config.collection_name,#数据库的表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,#数据库本地存储文件夹
            ) #向量存储的实例
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,#分割后的文本最大长度
            chunk_overlap=config.chunk_overlap,#连续文本段之间的字符重叠数量
            separators=config.separators,#自然段落划分的符号
            length_function=len,#使用自带的len函数来计算长度
            )  #文本分割器的对象

    def upload_by_str(self,data,filename):
        md5_hex=get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]已经存在知识库中"
        # SimHash 近重复检测：少量修改不会重复入库
        simhash = SimHash(data)
        is_duplicate, min_dist = check_simhash(simhash.hex())
        if is_duplicate:
            return f"[跳过]与已有文档高度相似（文档级海明距离 {min_dist}）"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        chunk_dup, chunk_ratio = check_chunk_level_near_duplicate(knowledge_chunks)
        if chunk_dup:
            return f"[跳过]分块内容高度重叠（命中率 {chunk_ratio:.0%}）"

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "xiaojiang",
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )
        save_md5(md5_hex)
        save_simhash(simhash.hex())
        save_chunk_simhashes(filename, knowledge_chunks)
        return "[成功]内容已经载入向量库"
        if len(data)>config.max_split_char_number:
            knowledge_chunks:list[str]=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]
        metadata={
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"xiaojiang",#上传者
        }    
        self.chroma.add_texts(#执行完就加载到数据库了
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )    
        save_md5(md5_hex)
        save_simhash(simhash.hex())
        return "[成功]内容已经载入向量库"
    
    def list_documents(self):
        """列出知识库中的所有文档（按 source 去重）"""
        try:
            result = self.chroma.get()
            ids = result.get("ids", [])
            metadatas = result.get("metadatas", [])
            if not ids:
                return []
            
            # 按 source 聚合
            docs = {}
            for doc_id, meta in zip(ids, metadatas):
                if meta is None:
                    continue
                source = meta.get("source", "未知文件")
                if source not in docs:
                    docs[source] = {
                        "source": source,
                        "create_time": meta.get("create_time", "未知"),
                        "operator": meta.get("operator", "未知"),
                        "count": 0,
                        "ids": []
                    }
                docs[source]["count"] += 1
                docs[source]["ids"].append(doc_id)
            
            return list(docs.values())
        except Exception as e:
            return [{"error": str(e)}]
    
    def delete_document(self, source_name):
        """删除指定文件名的所有文档片段"""
        try:
            result = self.chroma.get()
            ids = result.get("ids", [])
            metadatas = result.get("metadatas", [])
            
            to_delete = []
            for doc_id, meta in zip(ids, metadatas):
                if meta and meta.get("source") == source_name:
                    to_delete.append(doc_id)
            
            if not to_delete:
                return False, f"未找到文件: {source_name}"
            
            self.chroma.delete(ids=to_delete)
            return True, f"已删除 {source_name}（共 {len(to_delete)} 个片段）"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_stats(self):
        """获取知识库统计信息"""
        try:
            result = self.chroma.get()
            ids = result.get("ids", [])
            metadatas = result.get("metadatas", [])
            sources = set()
            for meta in metadatas:
                if meta:
                    sources.add(meta.get("source", "未知"))
            return {
                "total_chunks": len(ids),
                "total_files": len(sources)
            }
        except Exception:
            return {"total_chunks": 0, "total_files": 0}


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("Jaychou", "testfile")
    print(r)
