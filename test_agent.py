"""
端到端测试脚本：健康检查 → 上传文档 → Agent问答 → 多轮对话记忆 → 文档总结

启动服务（PowerShell）：
    .venv/Scripts/python -m uvicorn main:app --host 0.0.0.0 --port 8000

运行测试（另开一个 PowerShell）：
    .venv/Scripts/python test_agent.py
"""

import urllib.request
import json
import sys
import time

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0


# ── 工具函数 ──────────────────────────────────────────────

def get(path: str, timeout: int = 10) -> dict:
    resp = urllib.request.urlopen(f"{BASE}{path}", timeout=timeout)
    return json.loads(resp.read())


def post_json(path: str, data: dict, timeout: int = 120) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())


def upload_file(filepath: str, timeout: int = 120) -> dict:
    boundary = "----TestBoundary7890"
    filename = filepath.replace("\\", "/").split("/")[-1]
    with open(filepath, "rb") as f:
        content = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{BASE}/api/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 测试用例 ──────────────────────────────────────────────

def test_health():
    section("1. 健康检查")
    r = get("/health")
    check("GET /health 返回 200", "status" in r, str(r))
    check("status == ok", r.get("status") == "ok", r.get("status", ""))
    check("version 存在", "version" in r, str(r))
    print(f"  响应: {r}")


def test_upload():
    section("2. 上传文档")
    r = upload_file("uploads/test_doc.md")
    check("POST /api/upload 返回成功", "filename" in r, str(r))
    check("filename 正确", r.get("filename") == "test_doc.md", r.get("filename", ""))
    check("chunks > 0", r.get("chunks", 0) > 0, f"chunks={r.get('chunks')}")
    print(f"  响应: {json.dumps(r, ensure_ascii=False)}")


def test_agent_qa():
    section("3. Agent 文档问答")
    r = post_json("/api/agent/chat", {
        "query": "LangChain的核心概念有哪些？请简要列出。",
        "session_id": "test_session",
    })
    check("POST /api/agent/chat 返回成功", "answer" in r, str(r))
    answer = r.get("answer", "")
    check("回答非空", len(answer) > 0, "answer 为空")
    # 检查回答中是否包含文档中的关键概念
    keywords = ["Models", "Prompts", "Chains", "Memory", "Agents",
                "模型", "提示", "链", "记忆", "代理"]
    hit = any(kw in answer for kw in keywords)
    check("回答包含文档关键概念", hit, f"answer 前100字: {answer[:100]}")
    check("session_id 正确", r.get("session_id") == "test_session", "")
    print(f"  回答前200字: {answer[:200]}...")


def test_memory():
    section("4. 多轮对话记忆")
    # 第一轮：建立上下文
    r1 = post_json("/api/agent/chat", {
        "query": "什么是RAG？",
        "session_id": "memory_test",
    })
    check("第1轮对话成功", len(r1.get("answer", "")) > 0, "")
    print(f"  第1轮回答前100字: {r1['answer'][:100]}...")

    # 第二轮：用代词引用上一轮话题，测试记忆
    r2 = post_json("/api/agent/chat", {
        "query": "它有什么优势？",
        "session_id": "memory_test",
    })
    answer2 = r2.get("answer", "")
    check("第2轮对话成功", len(answer2) > 0, "")
    # 如果记忆生效，回答应该与 RAG 相关
    rag_related = any(kw in answer2 for kw in ["RAG", "检索", "知识库", "文档", "retrieval"])
    check("第2轮回答与RAG相关（记忆生效）", rag_related, f"answer 前100字: {answer2[:100]}")
    print(f"  第2轮回答前100字: {answer2[:100]}...")

    # 第三轮：不同 session_id，不应有上下文
    r3 = post_json("/api/agent/chat", {
        "query": "它有什么优势？",
        "session_id": "isolated_session",
    })
    check("不同session隔离", len(r3.get("answer", "")) > 0, "")
    print(f"  隔离session回答前100字: {r3['answer'][:100]}...")


def test_summary():
    section("5. 文档总结")
    r = post_json("/api/summary", {"filename": "test_doc.md"})
    check("POST /api/summary 返回成功", "summary" in r, str(r))
    summary = r.get("summary", "")
    check("总结非空", len(summary) > 0, "summary 为空")
    check("filename 正确", r.get("filename") == "test_doc.md", "")
    # 总结应包含关键主题
    hit = any(kw in summary for kw in ["LangChain", "RAG", "FAISS"])
    check("总结包含关键主题", hit, f"summary 前100字: {summary[:100]}")
    print(f"  总结前200字: {summary[:200]}...")


# ── 主流程 ────────────────────────────────────────────────

def main():
    print("\n🚀 AI Agent 端到端测试")
    print(f"   目标: {BASE}")
    start = time.time()

    try:
        test_health()
        test_upload()
        test_agent_qa()
        test_memory()
        test_summary()
    except Exception as e:
        print(f"\n💥 测试异常中断: {e}")
        sys.exit(1)

    elapsed = time.time() - start
    section("测试结果")
    print(f"  ✅ 通过: {PASS}")
    print(f"  ❌ 失败: {FAIL}")
    print(f"  ⏱  耗时: {elapsed:.1f}s")
    print()

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
