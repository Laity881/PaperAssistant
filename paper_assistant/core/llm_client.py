"""DeepSeek + LangChain wrappers for paper reading workflows."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv


DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"


def _load_langchain_messages():
    """Import LangChain message classes lazily for clearer dependency errors."""

    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    except ImportError as exc:
        raise RuntimeError("缺少 langchain 依赖，请先安装 requirements.txt。") from exc
    return AIMessage, HumanMessage, SystemMessage


def is_configured() -> bool:
    """Return whether the DeepSeek API key is available."""

    load_dotenv()
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def get_deepseek_llm(temperature: float = 0.2):
    """Create a ChatOpenAI-compatible DeepSeek client."""

    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY，请先在 .env 或环境变量中设置。")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("缺少 langchain-openai 依赖，请先安装 requirements.txt。") from exc

    return ChatOpenAI(
        model=DEEPSEEK_MODEL,
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        temperature=temperature,
    )


def _trim_text(text: str, max_chars: int) -> str:
    """Trim long text while preserving beginning and ending context."""

    text = text or ""
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.72)]
    tail = text[-int(max_chars * 0.22) :]
    return f"{head}\n\n...[中间内容因长度被省略]...\n\n{tail}"


def _history_to_messages(history: list[dict[str, str]], max_turns: int = 10):
    """Convert Streamlit-style role/content history into LangChain messages."""

    AIMessage, HumanMessage, _ = _load_langchain_messages()
    messages = []
    for item in history[-max_turns * 2 :]:
        role = item.get("role")
        content = _trim_text(item.get("content", ""), 4000)
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _invoke(messages: list[Any], *, temperature: float = 0.2) -> str:
    llm = get_deepseek_llm(temperature=temperature)
    response = llm.invoke(messages)
    return getattr(response, "content", str(response))


def generate_macro_reading(paper_text: str) -> str:
    """Generate the first-round macro reading for a paper."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
请对下面论文全文进行第一轮宏观解读。你是论文阅读辅助器，需要面向正在学习论文的中文读者。

输出必须使用 Markdown，并严格包含以下三个部分：

## 摘要
用 200 字以内的中文，用通俗语言解释论文在研究什么、解决什么问题、为什么重要。

## 论文架构
按论文真实结构列出主要章节。如果原文结构不清晰，请根据内容推断，并标明“推断”。

## 创新点
列出 3-5 个要点，每个要点都要说明它相对已有工作或常见方法的区别。

论文全文：
{_trim_text(paper_text, 60000)}
""".strip()
    messages = [
        SystemMessage(content="你是一名严谨、耐心的中文论文阅读导师。"),
        HumanMessage(content=prompt),
    ]
    return _invoke(messages, temperature=0.15)


def answer_macro_question(
    question: str,
    paper_text: str,
    history: list[dict[str, str]],
) -> str:
    """Answer follow-up questions during macro reading."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    messages = [
        SystemMessage(
            content=(
                "你是论文阅读辅助器。请结合论文全文和已有对话回答用户问题。"
                "回答要用中文，必要时指出原文依据；如果信息不足，要诚实说明。"
            )
        ),
        HumanMessage(content=f"论文全文参考：\n{_trim_text(paper_text, 52000)}"),
        *_history_to_messages(history),
        HumanMessage(content=question),
    ]
    return _invoke(messages, temperature=0.25)


def explain_paragraph(
    paragraph: str,
    paper_text: str,
    *,
    paragraph_index: int,
    total_paragraphs: int,
) -> str:
    """Explain a selected paragraph in detail."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
请精读论文第 {paragraph_index + 1}/{total_paragraphs} 段。你需要自动输出：

## 原文引用
展示本段原文。

## 中文翻译
如果原文不是中文，请给出准确自然的中文翻译；如果原文是中文，请说明无需翻译并保留原意。

## 详细解释
逐句拆解本段含义，解释专业术语，指出逻辑关系（因果、转折、举例、递进等），并说明该段在全文中的作用。

## 不懂的点
主动列出 2-4 个读者可能卡住的概念或推理点，并询问用户是否需要进一步解释。

选中段落：
{paragraph}

论文全文参考：
{_trim_text(paper_text, 36000)}
""".strip()
    messages = [
        SystemMessage(content="你是一名专业、细致的中文论文精读导师。"),
        HumanMessage(content=prompt),
    ]
    return _invoke(messages, temperature=0.15)


def answer_detail_question(
    question: str,
    paper_text: str,
    selected_paragraph: str,
    history: list[dict[str, str]],
) -> str:
    """Answer a user question in detail-reading mode."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    messages = [
        SystemMessage(
            content=(
                "你是论文逐段精读助手。请优先基于当前段落回答，必要时结合论文全文。"
                "回答使用中文，解释术语时给出直观类比，但不要编造论文没有的信息。"
            )
        ),
        HumanMessage(content=f"当前段落：\n{selected_paragraph}"),
        HumanMessage(content=f"论文全文参考：\n{_trim_text(paper_text, 42000)}"),
        *_history_to_messages(history),
        HumanMessage(content=question),
    ]
    return _invoke(messages, temperature=0.25)


def explain_confusion(
    confusion: str,
    paper_text: str,
    selected_paragraph: str,
) -> str:
    """Give an additional explanation for a user-marked confusing point."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
用户标记了一个“不懂的地方”，请给出补充解释。

用户不懂的点：
{confusion}

当前段落：
{selected_paragraph}

论文全文参考：
{_trim_text(paper_text, 36000)}

请用中文回答，先直说结论，再分解原因、背景概念和它在论文中的作用。
""".strip()
    messages = [
        SystemMessage(content="你是耐心的论文助教，擅长把抽象概念讲清楚。"),
        HumanMessage(content=prompt),
    ]
    return _invoke(messages, temperature=0.2)


def generate_study_summary(summary_source: str) -> str:
    """Generate a polished Markdown study note from collected reading data."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
请根据下面的论文阅读记录生成一份完整 Markdown 学习总结。

必须包含以下标题结构：

# 论文精读笔记
## 基本信息
## 宏观解读
## 逐段精读记录
## 我不懂的地方与补充解释
## PDF 高亮与批注
## 用户自定义笔记

要求：
- 保留关键原文引用、中文翻译、AI 解释和用户问答。
- 不要丢失 DOI、分类、标题。
- 用中文组织，表达清晰，适合作为长期复习笔记。
- 如果某部分暂无内容，写“暂无”。

阅读记录：
{_trim_text(summary_source, 70000)}
""".strip()
    messages = [
        SystemMessage(content="你是严谨的学术笔记整理助手。"),
        HumanMessage(content=prompt),
    ]
    return _invoke(messages, temperature=0.1)

