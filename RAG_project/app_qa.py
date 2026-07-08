import streamlit as st
from rag import RagService
from knowledge_base import KnowledgeBaseService
import uuid
import time

# ====== 页面配置 ======
st.set_page_config(
    page_title="RAG 智能问答",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====== 自定义样式 ======
st.markdown("""
<style>
/* 整体背景 */
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

/* 标题样式 */
.main-title {
    text-align: center;
    color: #e94560;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.sub-title {
    text-align: center;
    color: #a0a0a0;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* 聊天消息气泡 */
.chat-container {
    max-width: 900px;
    margin: 0 auto;
}

/* 用户消息 */
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px auto;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    word-wrap: break-word;
}

/* AI 消息 */
.ai-message {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px auto 8px 0;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    word-wrap: break-word;
}

/* 消息标签 */
.message-label {
    font-size: 0.75rem;
    color: #888;
    margin-bottom: 2px;
    font-weight: 600;
}

/* 输入框样式 */
.stChatInput > div {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* 侧边栏 */
.css-1d391kg, .css-1lcbmhc {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

/* 按钮样式 */
.stButton > button {
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 危险按钮（删除） */
.delete-btn button {
    background: linear-gradient(135deg, #e94560 0%, #c0392b 100%) !important;
}
.delete-btn button:hover {
    box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4) !important;
}

/* 滚动条 */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #1a1a2e;
}
::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 4px;
}

/* 加载动画 */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.loading-text {
    animation: pulse 1.5s ease-in-out infinite;
    color: #e94560;
}

/* 知识库文档卡片 */
.kb-doc-card {
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 10px;
    margin: 6px 0;
    border: 1px solid rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)


# ====== 初始化服务 ======
@st.cache_resource
def get_rag_service():
    return RagService()


@st.cache_resource
def get_kb_service():
    return KnowledgeBaseService()


def init_session_state():
    """初始化会话状态"""
    if "sessions" not in st.session_state:
        # 默认创建一个会话
        default_session_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state["sessions"] = {
            default_session_id: {
                "name": "会话 1",
                "messages": []
            }
        }
        st.session_state["current_session_id"] = default_session_id
    if "rag_service" not in st.session_state:
        st.session_state["rag_service"] = get_rag_service()
    if "kb_service" not in st.session_state:
        st.session_state["kb_service"] = get_kb_service()
    if "kb_upload_msg" not in st.session_state:
        st.session_state["kb_upload_msg"] = None
    if "kb_delete_msg" not in st.session_state:
        st.session_state["kb_delete_msg"] = None


init_session_state()

rag_service = st.session_state["rag_service"]
kb_service = st.session_state["kb_service"]
current_session_id = st.session_state["current_session_id"]
current_session = st.session_state["sessions"][current_session_id]

# ====== 侧边栏 ======
with st.sidebar:
    # ====== 会话管理 ======
    st.markdown("## 🎛️ 会话管理")
    st.markdown("---")

    # 新建会话按钮
    if st.button("➕ 新建会话", use_container_width=True):
        new_id = f"session_{uuid.uuid4().hex[:8]}"
        session_count = len(st.session_state["sessions"]) + 1
        st.session_state["sessions"][new_id] = {
            "name": f"会话 {session_count}",
            "messages": []
        }
        st.session_state["current_session_id"] = new_id
        st.rerun()

    st.markdown("### 📋 历史会话")

    # 会话列表
    for sid, sdata in list(st.session_state["sessions"].items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            btn_label = f"💬 {sdata['name']}"
            if sid == current_session_id:
                btn_label = f"▶ {sdata['name']}"
            if st.button(btn_label, key=f"btn_{sid}", use_container_width=True):
                st.session_state["current_session_id"] = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}"):
                del st.session_state["sessions"][sid]
                if st.session_state["sessions"]:
                    st.session_state["current_session_id"] = list(st.session_state["sessions"].keys())[0]
                else:
                    # 如果删完了，创建一个新的
                    new_id = f"session_{uuid.uuid4().hex[:8]}"
                    st.session_state["sessions"][new_id] = {
                        "name": "会话 1",
                        "messages": []
                    }
                    st.session_state["current_session_id"] = new_id
                st.rerun()

    st.markdown("---")

    # 重命名当前会话
    new_name = st.text_input("✏️ 重命名当前会话", value=current_session["name"])
    if new_name != current_session["name"]:
        current_session["name"] = new_name

    st.markdown("---")

    # 清空当前会话
    if st.button("🧹 清空当前对话", use_container_width=True):
        current_session["messages"] = []
        st.rerun()

    st.markdown("---")

    # ====== 知识库管理 ======
    st.markdown("## 📚 知识库管理")
    st.markdown("---")

    # 文件上传
    st.markdown("### ⬆️ 上传文档")
    uploaded_file = st.file_uploader(
        label="上传 TXT 文件到知识库",
        type=["txt"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_size = uploaded_file.size / 1024  # KB
        st.caption(f"📄 {file_name} ({file_size:.1f} KB)")

        if st.button("🚀 确认上传", use_container_width=True, key="upload_btn"):
            with st.spinner("正在处理文档..."):
                try:
                    text = uploaded_file.getvalue().decode("utf-8")
                    result = kb_service.upload_by_str(text, file_name)
                    st.session_state["kb_upload_msg"] = result
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.session_state["kb_upload_msg"] = f"❌ 上传失败: {str(e)}"
                    st.rerun()

    # 显示上传消息
    if st.session_state.get("kb_upload_msg"):
        msg = st.session_state["kb_upload_msg"]
        if "成功" in msg:
            st.success(msg)
        elif "跳过" in msg:
            st.warning(msg)
        else:
            st.error(msg)
        # 清除消息，避免重复显示
        st.session_state["kb_upload_msg"] = None

    st.markdown("---")

    # 知识库统计
    st.markdown("### 📊 知识库状态")
    stats = kb_service.get_stats()
    st.info(f"""
    **文档数量**: {stats['total_files']} 个
    **片段数量**: {stats['total_chunks']} 个
    """)

    st.markdown("---")

    # 文档列表
    st.markdown("### 🗂️ 文档列表")
    docs = kb_service.list_documents()

    if not docs:
        st.caption("知识库为空，请上传文档")
    else:
        for doc in docs:
            if "error" in doc:
                st.error(f"加载失败: {doc['error']}")
                continue

            with st.container():
                st.markdown(f"""
                <div class='kb-doc-card'>
                    <div style='font-weight:600;color:#e94560;'>{doc['source']}</div>
                    <div style='font-size:0.8rem;color:#aaa;'>
                        ⏰ {doc['create_time']} &nbsp;|&nbsp; 📦 {doc['count']} 个片段
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 删除按钮
                del_key = f"del_doc_{doc['source']}"
                if st.button("🗑️ 删除", key=del_key, use_container_width=True):
                    with st.spinner("正在删除..."):
                        success, msg = kb_service.delete_document(doc['source'])
                        if success:
                            st.session_state["kb_delete_msg"] = msg
                        else:
                            st.session_state["kb_delete_msg"] = msg
                        st.rerun()

    # 显示删除消息
    if st.session_state.get("kb_delete_msg"):
        msg = st.session_state["kb_delete_msg"]
        if "已删除" in msg:
            st.success(msg)
        else:
            st.error(msg)
        st.session_state["kb_delete_msg"] = None

    st.markdown("---")
    st.markdown("### 📊 项目信息")
    st.info(f"""
    **当前会话**: {current_session['name']}
    **会话数量**: {len(st.session_state['sessions'])}
    **消息数量**: {len(current_session['messages'])}
    """)

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#888;font-size:0.8rem;'>Powered by RAG Project</div>", unsafe_allow_html=True)

# ====== 主界面 ======
st.markdown("<div class='main-title'>🤖 RAG 智能问答助手</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>基于知识库的检索增强生成问答系统</div>", unsafe_allow_html=True)
st.markdown("---")

# ====== 聊天区域 ======
chat_container = st.container()

with chat_container:
    # 显示历史消息
    if not current_session["messages"]:
        st.markdown("""
        <div style='text-align:center; padding: 60px 20px; color: #888;'>
            <div style='font-size: 4rem; margin-bottom: 20px;'>💬</div>
            <div style='font-size: 1.3rem; margin-bottom: 10px;'>开始你的问答之旅</div>
            <div style='font-size: 0.9rem;'>在下方输入框中提问，AI 将基于知识库为你解答</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in current_session["messages"]:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-end; margin: 10px 0;'>
                    <div style='max-width:80%;'>
                        <div class='message-label' style='text-align:right;'>你</div>
                        <div class='user-message'>{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-start; margin: 10px 0;'>
                    <div style='max-width:80%;'>
                        <div class='message-label'>🤖 AI 助手</div>
                        <div class='ai-message'>{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ====== 输入区域 ======
st.markdown("---")

# 使用 st.chat_input
user_input = st.chat_input("💭 请输入你的问题...")

if user_input:
    # 先显示用户消息
    current_session["messages"].append({"role": "user", "content": user_input})

    # 构建会话配置
    session_config = {
        "configurable": {
            "session_id": current_session_id
        }
    }

    # 显示加载状态
    with st.spinner("🤖 AI 思考中..."):
        try:
            # 调用 RAG 服务
            response = rag_service.chain.invoke(
                {"input": user_input},
                session_config
            )
            ai_reply = response
        except Exception as e:
            ai_reply = f"❌ 出错了：{str(e)}"

    # 添加 AI 回复到历史
    current_session["messages"].append({"role": "assistant", "content": ai_reply})

    # 刷新页面显示新消息
    st.rerun()
