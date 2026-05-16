"""Chat model wrappers for paper reading workflows."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv


DEFAULT_CHAT_BASE_URL = "https://api.deepseek.com/v1"
CHAT_MODEL_OPTIONS = {
    "chat": "deepseek-v4-flash",
    "v4-pro": "deepseek-v4-pro",
}
DEFAULT_CHAT_MODEL_LABEL = "v4-pro"
DEFAULT_CHAT_MODEL = CHAT_MODEL_OPTIONS[DEFAULT_CHAT_MODEL_LABEL]

# Backward-compatible names for existing code and user environments.
DEEPSEEK_BASE_URL = DEFAULT_CHAT_BASE_URL
DEEPSEEK_MODEL = DEFAULT_CHAT_MODEL


def normalize_chat_model(model: str | None) -> str:
    """Map UI/env model aliases to API model names."""

    raw = (model or "").strip()
    if not raw:
        return DEFAULT_CHAT_MODEL
    lowered = raw.lower()
    return CHAT_MODEL_OPTIONS.get(lowered, raw)


def get_chat_model_label(model: str | None = None) -> str:
    """Return a user-facing model label for a model id or current config."""

    api_name = normalize_chat_model(model or get_chat_model_name())
    for label, mapped in CHAT_MODEL_OPTIONS.items():
        if api_name == mapped:
            return label
    return api_name


def _get_session_model() -> str:
    """Return model choice from Streamlit session state when available."""

    try:
        import streamlit as st
    except ImportError:
        return ""
    try:
        return st.session_state.get("pa_chat_model", "")
    except Exception:
        return ""


def get_chat_model_name() -> str:
    """Return the configured API chat model name."""

    load_dotenv()
    configured = (
        _get_session_model()
        or os.getenv("CHAT_MODEL")
        or os.getenv("DEEPSEEK_MODEL")
        or DEFAULT_CHAT_MODEL
    )
    return normalize_chat_model(configured)


def get_chat_base_url() -> str:
    """Return the OpenAI-compatible chat API base URL."""

    load_dotenv()
    return (
        os.getenv("CHAT_BASE_URL")
        or os.getenv("DEEPSEEK_BASE_URL")
        or DEFAULT_CHAT_BASE_URL
    )


def _get_api_key() -> str:
    """Return the configured chat API key, keeping DeepSeek env compatibility."""

    load_dotenv()
    return os.getenv("CHAT_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or ""


def _load_langchain_messages():
    """Import LangChain message classes lazily for clearer dependency errors."""

    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    except ImportError as exc:
        raise RuntimeError("缺少 langchain 依赖，请先安装 requirements.txt。") from exc
    return AIMessage, HumanMessage, SystemMessage


def is_configured() -> bool:
    """Return whether a chat API key is available."""

    return bool(_get_api_key())


def get_chat_llm(temperature: float = 0.2):
    """Create a ChatOpenAI-compatible client for the configured model."""

    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("未配置 CHAT_API_KEY 或 DEEPSEEK_API_KEY，请先在 .env 或环境变量中设置。")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("缺少 langchain-openai 依赖，请先安装 requirements.txt。") from exc

    return ChatOpenAI(
        model=get_chat_model_name(),
        api_key=api_key,
        base_url=get_chat_base_url(),
        temperature=temperature,
        streaming=True,
    )


def get_deepseek_llm(temperature: float = 0.2):
    """Backward-compatible alias for older imports."""

    return get_chat_llm(temperature=temperature)


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
    llm = get_chat_llm(temperature=temperature)
    response = llm.invoke(messages)
    return getattr(response, "content", str(response))


def _stream(messages: list[Any], *, temperature: float = 0.2):
    """Yield streamed text chunks from the configured chat model."""

    llm = get_chat_llm(temperature=temperature)
    for chunk in llm.stream(messages):
        content = getattr(chunk, "content", "")
        if isinstance(content, list):
            content = "".join(str(item) for item in content)
        if content:
            yield str(content)


def _macro_messages(paper_text: str) -> list[Any]:
    """Build messages for the first-round macro reading."""

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
    return messages


def generate_macro_reading(paper_text: str) -> str:
    """Generate the first-round macro reading for a paper."""

    return _invoke(_macro_messages(paper_text), temperature=0.15)


def stream_macro_reading(paper_text: str):
    """Stream the first-round macro reading for a paper."""

    return _stream(_macro_messages(paper_text), temperature=0.15)


def answer_macro_question(
    question: str,
    paper_text: str,
    history: list[dict[str, str]],
) -> str:
    """Answer follow-up questions during macro reading."""

    return _invoke(
        _macro_question_messages(question, paper_text, history),
        temperature=0.25,
    )


def _macro_question_messages(
    question: str,
    paper_text: str,
    history: list[dict[str, str]],
) -> list[Any]:
    """Build messages for macro-reading follow-up questions."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    return [
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


def stream_answer_macro_question(
    question: str,
    paper_text: str,
    history: list[dict[str, str]],
):
    """Stream a follow-up answer during macro reading."""

    return _stream(
        _macro_question_messages(question, paper_text, history),
        temperature=0.25,
    )


def explain_paragraph(
    paragraph: str,
    paper_text: str,
    *,
    paragraph_index: int,
    total_paragraphs: int,
) -> str:
    """Explain a selected section in detail."""

    return _invoke(
        _paragraph_messages(
            paragraph,
            paper_text,
            paragraph_index=paragraph_index,
            total_paragraphs=total_paragraphs,
        ),
        temperature=0.15,
    )


def _paragraph_messages(
    paragraph: str,
    paper_text: str,
    *,
    paragraph_index: int,
    total_paragraphs: int,
) -> list[Any]:
    """Build messages for selected section explanation."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
请精读论文第 {paragraph_index + 1}/{total_paragraphs} 个章节片段。你需要自动输出：

## 原文引用
展示本章节片段原文。

## 中文翻译
如果原文不是中文，请给出准确自然的中文翻译；如果原文是中文，请说明无需翻译并保留原意。

## 给初学者的详细解释
请默认读者刚开始读这篇论文。先用通俗中文讲清本章节想解决什么问题，再按“背景动机 -> 关键概念 -> 方法/论证流程 -> 这一节在全文中的作用”解释。解释专业术语时要给直观类比；遇到公式、实验指标或模型模块，要说明它为什么出现、解决什么困惑、读者应该抓住什么结论。

## 不懂的点
主动列出 2-4 个初学者可能卡住的概念、公式、实验或推理点，并用一句话说明该如何继续追问。

选中章节片段：
{paragraph}

论文全文参考：
{_trim_text(paper_text, 36000)}
""".strip()
    messages = [
        SystemMessage(content="你是一名专业、细致的中文论文精读导师。"),
        HumanMessage(content=prompt),
    ]
    return messages


def stream_explain_paragraph(
    paragraph: str,
    paper_text: str,
    *,
    paragraph_index: int,
    total_paragraphs: int,
):
    """Stream a selected section explanation."""

    return _stream(
        _paragraph_messages(
            paragraph,
            paper_text,
            paragraph_index=paragraph_index,
            total_paragraphs=total_paragraphs,
        ),
        temperature=0.15,
    )


def answer_detail_question(
    question: str,
    paper_text: str,
    selected_paragraph: str,
    history: list[dict[str, str]],
) -> str:
    """Answer a user question in detail-reading mode."""

    return _invoke(
        _detail_question_messages(question, paper_text, selected_paragraph, history),
        temperature=0.25,
    )


def _detail_question_messages(
    question: str,
    paper_text: str,
    selected_paragraph: str,
    history: list[dict[str, str]],
) -> list[Any]:
    """Build messages for detail-reading questions."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    return [
        SystemMessage(
            content=(
                "你是论文逐章节精读助手。请优先基于当前章节回答，必要时结合论文全文。"
                "回答使用中文，面向初学者解释术语、公式、实验和方法动机；不要编造论文没有的信息。"
            )
        ),
        HumanMessage(content=f"当前章节片段：\n{selected_paragraph}"),
        HumanMessage(content=f"论文全文参考：\n{_trim_text(paper_text, 42000)}"),
        *_history_to_messages(history),
        HumanMessage(content=question),
    ]


def stream_answer_detail_question(
    question: str,
    paper_text: str,
    selected_paragraph: str,
    history: list[dict[str, str]],
):
    """Stream an answer in detail-reading mode."""

    return _stream(
        _detail_question_messages(question, paper_text, selected_paragraph, history),
        temperature=0.25,
    )


def explain_confusion(
    confusion: str,
    paper_text: str,
    selected_paragraph: str,
) -> str:
    """Give an additional explanation for a user-marked confusing point."""

    return _invoke(
        _confusion_messages(confusion, paper_text, selected_paragraph),
        temperature=0.2,
    )


def _confusion_messages(
    confusion: str,
    paper_text: str,
    selected_paragraph: str,
) -> list[Any]:
    """Build messages for a user-marked confusing point."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
用户标记了一个“不懂的地方”，请面向论文初学者给出补充解释。

用户不懂的点：
{confusion}

当前章节片段：
{selected_paragraph}

论文全文参考：
{_trim_text(paper_text, 36000)}

请用中文回答，先直说结论，再分解原因、背景概念、直观类比、它在论文中的作用，以及读者下一步该回到原文哪里看。
""".strip()
    messages = [
        SystemMessage(content="你是耐心的论文助教，擅长把抽象概念讲清楚。"),
        HumanMessage(content=prompt),
    ]
    return messages


def stream_explain_confusion(
    confusion: str,
    paper_text: str,
    selected_paragraph: str,
):
    """Stream an additional explanation for a confusing point."""

    return _stream(
        _confusion_messages(confusion, paper_text, selected_paragraph),
        temperature=0.2,
    )


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


def generate_learning_pack(paper: dict[str, Any], paper_text: str) -> str:
    """Generate a learning-oriented plan, glossary, quiz, and review guide."""

    return _invoke(_learning_pack_messages(paper, paper_text), temperature=0.18)


def _learning_pack_messages(paper: dict[str, Any], paper_text: str) -> list[Any]:
    """Build messages for the learning pack."""

    _, HumanMessage, SystemMessage = _load_langchain_messages()
    prompt = f"""
请基于下面的论文，为正在学习该论文的中文读者生成一份可执行的学习包。输出必须是 Markdown，并严格包含：

## 1. 学习路线
用 5-7 个步骤安排阅读顺序，每一步说明目标、要重点看的章节或内容、预计耗时。

## 2. 核心术语表
列出 8-12 个术语。每个术语包含：一句话解释、论文中的作用、常见误解。

## 3. 方法拆解
把论文方法拆成输入、关键模块、训练/推理流程、输出、与基线差异。

## 4. 自测题
给出 8 道题：4 道理解题、2 道对比题、2 道开放题。每题附参考答案。

## 5. 复习计划
给出今天、明天、3 天后、7 天后的复习任务，每项都要能勾选执行。

论文元信息：
- 标题：{paper.get("title", "Untitled Paper")}
- DOI：{paper.get("doi") or "暂无"}
- 分类：{paper.get("category") or "未分类"}

论文全文：
{_trim_text(paper_text, 56000)}
""".strip()
    messages = [
        SystemMessage(content="你是一名擅长把学术论文转化为学习计划的中文研究助教。"),
        HumanMessage(content=prompt),
    ]
    return messages


def stream_learning_pack(paper: dict[str, Any], paper_text: str):
    """Stream a learning-oriented plan, glossary, quiz, and review guide."""

    return _stream(_learning_pack_messages(paper, paper_text), temperature=0.18)
