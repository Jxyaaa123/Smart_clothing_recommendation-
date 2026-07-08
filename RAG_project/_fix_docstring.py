from pathlib import Path

p = Path(r"D:\python\vscode\.vscode\ai model\RAG_project\knowledge_base.py")
text = p.read_text(encoding='utf-8')
old = '    """????????????????????????"""'
new = '    """局部敏感哈希：内容只做少量修改时，海明距离很小。"""'
if old in text:
    text = text.replace(old, new)
    print('replaced')
else:
    print('not found')
p.write_text(text, encoding='utf-8')

Path(r"D:\python\vscode\.vscode\ai model\RAG_project\_fix_chinese.py").unlink(missing_ok=True)
print('cleaned')
