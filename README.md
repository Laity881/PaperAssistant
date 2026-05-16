# PaperAssistant

一个基于 Streamlit 的本地论文阅读学习工作台，支持 PDF 入库、宏观解读、逐段精读、批注、学习包生成和 Markdown 笔记导出。

## 主要功能

- 文献库：上传 PDF、按分类管理、通过 DOI 查询 arXiv PDF。
- 宏观解读：生成摘要、论文结构、创新点，并支持上下文追问。
- 逐章节精读：按论文章节生成翻译、解释、疑问点和问答记录。
- 学习中心：生成学习路线、术语表、方法拆解、自测题和复习计划。
- 文件管理：整理 `论文/` 与 `笔记/`，预览 Markdown 笔记。

## 启动

```bash
cd paper_assistant
pip install -r requirements.txt
streamlit run app.py
```

## 模型配置

界面可在 `chat` 与 `v4-pro` 之间切换；调用 API 时会自动映射到支持的真实模型名。默认使用 `v4-pro`。在 `paper_assistant/.env` 中配置：

```env
CHAT_MODEL=v4-pro
CHAT_BASE_URL=https://api.deepseek.com/v1
CHAT_API_KEY=你的 API Key
```

`v4-pro` 会映射为 `deepseek-v4-pro`，`chat` 会映射为 `deepseek-v4-flash`。项目也兼容旧配置 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。
