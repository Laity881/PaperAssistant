"""CSS system for Paper Assistant — organized builders with light/dark theme support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    bg: str
    bg_2: str
    surface: str
    surface_soft: str
    surface_tint: str
    ink: str
    ink_2: str
    muted: str
    faint: str
    border: str
    border_soft: str
    accent: str
    accent_2: str
    warm: str
    sidebar: str
    sidebar_soft: str
    sidebar_line: str
    shadow: str
    shadow_soft: str
    primary_button_bg: str
    primary_button_hover: str
    gradient_app: str
    chat_bg: str
    chat_border: str
    stat_bg: str


LIGHT_THEME = ThemeColors(
    bg="#f3f5f8",
    bg_2="#eef1f5",
    surface="#ffffff",
    surface_soft="#f8fafc",
    surface_tint="#f4f7fb",
    ink="#111827",
    ink_2="#1f2937",
    muted="#667085",
    faint="#98a2b3",
    border="#d8dee8",
    border_soft="#e8edf3",
    accent="#2563eb",
    accent_2="#0f766e",
    warm="#a16207",
    sidebar="#0f172a",
    sidebar_soft="#1e293b",
    sidebar_line="#334155",
    shadow="0 18px 45px rgba(16, 24, 40, 0.08)",
    shadow_soft="0 10px 26px rgba(16, 24, 40, 0.05)",
    primary_button_bg="#1e40af",
    primary_button_hover="#1e3a8a",
    gradient_app="radial-gradient(ellipse at 20% 0%, rgba(37, 99, 235, 0.035) 0%, transparent 55%), linear-gradient(180deg, #f8f9fb 0%, #f3f5f8 42%, #edf0f4 100%)",
    chat_bg="#ffffff",
    chat_border="#e8edf3",
    stat_bg="rgba(255, 255, 255, 0.78)",
)

DARK_THEME = ThemeColors(
    bg="#0f1117",
    bg_2="#16181d",
    surface="#1c1f26",
    surface_soft="#22252e",
    surface_tint="#1a1d24",
    ink="#e5e7eb",
    ink_2="#d1d5db",
    muted="#9ca3af",
    faint="#6b7280",
    border="#2d3139",
    border_soft="#262930",
    accent="#3b82f6",
    accent_2="#14b8a6",
    warm="#f59e0b",
    sidebar="#080b10",
    sidebar_soft="#13161d",
    sidebar_line="#1f232b",
    shadow="0 18px 45px rgba(0, 0, 0, 0.35)",
    shadow_soft="0 10px 26px rgba(0, 0, 0, 0.25)",
    primary_button_bg="#2563eb",
    primary_button_hover="#1d4ed8",
    gradient_app="radial-gradient(ellipse at 20% 0%, rgba(59, 130, 246, 0.06) 0%, transparent 55%), linear-gradient(180deg, #13161d 0%, #0f1117 42%, #0c0e14 100%)",
    chat_bg="#1c1f26",
    chat_border="#2d3139",
    stat_bg="rgba(28, 31, 38, 0.85)",
)


# ── CSS builders ──────────────────────────────────────────────


def _build_variables(theme: ThemeColors) -> str:
    return f"""
    :root {{
        --pa-bg: {theme.bg};
        --pa-bg-2: {theme.bg_2};
        --pa-surface: {theme.surface};
        --pa-surface-soft: {theme.surface_soft};
        --pa-surface-tint: {theme.surface_tint};
        --pa-ink: {theme.ink};
        --pa-ink-2: {theme.ink_2};
        --pa-muted: {theme.muted};
        --pa-faint: {theme.faint};
        --pa-border: {theme.border};
        --pa-border-soft: {theme.border_soft};
        --pa-accent: {theme.accent};
        --pa-accent-2: {theme.accent_2};
        --pa-warm: {theme.warm};
        --pa-sidebar: {theme.sidebar};
        --pa-sidebar-soft: {theme.sidebar_soft};
        --pa-sidebar-line: {theme.sidebar_line};
        --pa-shadow: {theme.shadow};
        --pa-shadow-soft: {theme.shadow_soft};
        --pa-radius: 8px;
        --pa-radius-sm: 6px;
        --pa-transition: 180ms ease;
    }}
    """


def _build_base() -> str:
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent;
        height: 2.2rem;
    }

    .stApp {
        font-family:
            Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
        color: var(--pa-ink);
    }

    .block-container {
        max-width: 1680px;
        padding: 0.9rem 1.45rem 2.2rem;
    }

    h1, h2, h3 {
        color: var(--pa-ink);
        letter-spacing: 0;
    }

    h1 {
        font-size: 1.62rem;
        line-height: 1.2;
        font-weight: 760;
        margin-bottom: 0.35rem;
    }

    h2 {
        font-size: 1.18rem;
        font-weight: 720;
    }

    h3 {
        font-size: 1.02rem;
        font-weight: 700;
    }

    p, li {
        line-height: 1.66;
    }

    /* ── Sidebar structural ── */
    section[data-testid="stSidebar"] {
        background: var(--pa-sidebar);
        border-right: 1px solid var(--pa-sidebar-line);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] * {
        color: #d7dde6;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMetric label,
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--pa-sidebar-line);
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.035);
        border-radius: var(--pa-radius);
        margin: 0.18rem 0;
        min-height: 2.55rem;
        font-size: 0.88rem;
        transition: var(--pa-transition);
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
        background: rgba(255, 255, 255, 0.09);
        border-color: rgba(255, 255, 255, 0.18);
    }

    /* ── Tabs ── */
    div[data-testid="stTabs"] {
        background: transparent;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        height: 2.55rem;
        padding: 0 0.85rem;
        color: var(--pa-muted);
        font-weight: 680;
        border-radius: var(--pa-radius) var(--pa-radius) 0 0;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--pa-ink);
        background: var(--pa-surface);
        border-bottom: 2px solid var(--pa-accent);
    }

    /* ── Inputs ── */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    div[data-baseweb="select"] > div,
    div[data-baseweb="radio"] {
        border-radius: var(--pa-radius) !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        border-color: var(--pa-border);
        background: var(--pa-surface);
        color: var(--pa-ink);
    }

    .stTextArea textarea {
        line-height: 1.58;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        background: var(--pa-chat-bg, var(--pa-surface));
        border: 1px solid var(--pa-chat-border, var(--pa-border-soft));
        border-radius: var(--pa-radius);
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 1px 0 rgba(16, 24, 40, 0.03);
        border-left: 3px solid var(--pa-accent);
    }

    [data-testid="stChatInput"] {
        background: var(--pa-surface-soft);
        border-top: 2px solid var(--pa-border);
        padding: 0.65rem 0;
    }

    [data-testid="stChatInput"] textarea {
        border: 2px solid var(--pa-accent) !important;
        border-radius: var(--pa-radius) !important;
        transition: var(--pa-transition);
    }

    [data-testid="stChatInput"] textarea:focus {
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }
    """


def _build_color_dependent(theme: ThemeColors) -> str:
    return f"""
    .stApp {{
        background: {theme.gradient_app};
    }}

    /* ── Containers ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {theme.surface};
        border: 1px solid var(--pa-border-soft);
        border-radius: var(--pa-radius);
        box-shadow: var(--pa-shadow-soft);
        transition: var(--pa-transition);
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: var(--pa-border);
        transform: translateY(-1px);
        box-shadow: var(--pa-shadow);
    }}

    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--pa-radius);
        padding: 0.65rem 0.7rem;
    }}

    /* ── Buttons ── */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{
        border-radius: var(--pa-radius);
        border: 1px solid var(--pa-border);
        background: var(--pa-surface);
        color: var(--pa-ink-2);
        font-weight: 700;
        min-height: 2.45rem;
        box-shadow: 0 1px 0 rgba(16, 24, 40, 0.03);
        transition: var(--pa-transition);
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        border-color: #b8c2d0;
        background: var(--pa-surface-soft);
        color: var(--pa-ink);
    }}

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {{
        background: {theme.primary_button_bg};
        border-color: {theme.primary_button_bg};
        color: #ffffff;
    }}

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {{
        background: {theme.primary_button_hover};
        border-color: {theme.primary_button_hover};
        color: #ffffff;
    }}

    /* ── Brand block ── */
    .pa-brand {{
        border: 1px solid rgba(255, 255, 255, 0.09);
        background: linear-gradient(180deg, #1b222b 0%, #13181e 100%);
        border-radius: var(--pa-radius);
        padding: 0.9rem 0.9rem 0.85rem;
        margin-bottom: 0.9rem;
    }}

    .pa-brand-mark {{
        width: 2.15rem;
        height: 2.15rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--pa-radius);
        background: #f8fafc;
        color: #101316;
        font-weight: 820;
        margin-right: 0.58rem;
    }}

    .pa-brand-row {{
        display: flex;
        align-items: center;
    }}

    .pa-brand-title {{
        color: #ffffff;
        font-size: 1.03rem;
        font-weight: 780;
        line-height: 1.15;
    }}

    .pa-brand-subtitle {{
        color: #9aa4b2;
        font-size: 0.78rem;
        margin-top: 0.12rem;
    }}

    /* ── Active page indicator ── */
    .pa-active-page {{
        border-left: 3px solid #d6b36a;
        color: #f8fafc;
        background: rgba(214, 179, 106, 0.08);
        padding: 0.58rem 0.7rem;
        border-radius: var(--pa-radius);
        font-size: 0.84rem;
        margin: 0.75rem 0;
        animation: paPulse 2.8s ease-in-out infinite;
    }}

    /* ── Page header ── */
    .pa-page-head {{
        display: flex;
        justify-content: space-between;
        gap: 1.2rem;
        align-items: flex-end;
        border-bottom: 1px solid var(--pa-border);
        padding: 0.25rem 0 0.9rem;
        margin-bottom: 1rem;
    }}

    .pa-kicker {{
        color: var(--pa-accent);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.26rem;
    }}

    .pa-title {{
        font-size: 1.78rem;
        line-height: 1.12;
        font-weight: 820;
        color: var(--pa-ink);
    }}

    .pa-subtitle {{
        margin-top: 0.38rem;
        color: var(--pa-muted);
        line-height: 1.55;
        max-width: 820px;
    }}

    .pa-head-stats {{
        display: flex;
        gap: 0.55rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }}

    .pa-stat {{
        min-width: 6.5rem;
        border: 1px solid var(--pa-border-soft);
        background: {theme.stat_bg};
        border-radius: var(--pa-radius);
        padding: 0.55rem 0.7rem;
        box-shadow: 0 1px 0 rgba(16, 24, 40, 0.03);
    }}

    .pa-stat-label {{
        color: var(--pa-faint);
        font-size: 0.72rem;
        font-weight: 760;
    }}

    .pa-stat-value {{
        color: var(--pa-ink);
        font-size: 0.98rem;
        font-weight: 780;
        margin-top: 0.12rem;
    }}

    /* ── Panel title ── */
    .pa-panel-title {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.7rem 0 0.45rem;
    }}

    .pa-panel-title-main {{
        color: var(--pa-ink);
        font-size: 0.9rem;
        font-weight: 780;
        letter-spacing: 0.02em;
    }}

    .pa-panel-title-meta {{
        color: var(--pa-muted);
        font-size: 0.78rem;
        font-weight: 640;
    }}

    /* ── Paper strip ── */
    .pa-paper-strip {{
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
    }}

    .pa-paper-title {{
        font-weight: 780;
        font-size: 1.02rem;
        line-height: 1.35;
        color: var(--pa-ink);
    }}

    .pa-meta {{
        color: var(--pa-muted);
        font-size: 0.84rem;
        line-height: 1.55;
        margin-top: 0.18rem;
    }}

    /* ── Pills & tags ── */
    .pa-pill,
    .pa-tag {{
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--pa-border);
        border-radius: 999px;
        padding: 0.22rem 0.58rem;
        margin: 0.35rem 0.35rem 0 0;
        background: var(--pa-surface-soft);
        color: var(--pa-muted);
        font-size: 0.78rem;
        font-weight: 680;
        white-space: nowrap;
    }}

    .pa-tag-dark {{
        background: #151b23;
        border-color: #151b23;
        color: #ffffff;
    }}

    /* ── Paragraph display ── */
    .selected-para {{
        border-left: 4px solid var(--pa-accent);
        background: linear-gradient(180deg, rgba(37, 99, 235, 0.04) 0%, rgba(37, 99, 235, 0.01) 100%);
        padding: 1rem 1.05rem;
        border-radius: var(--pa-radius);
        line-height: 1.78;
        color: var(--pa-ink);
        font-size: 0.96rem;
    }}

    .plain-para {{
        color: var(--pa-ink-2);
        line-height: 1.58;
        font-size: 0.9rem;
        padding: 0.5rem 0.1rem;
    }}

    .pa-empty {{
        color: var(--pa-muted);
        background: linear-gradient(180deg, var(--pa-surface) 0%, var(--pa-surface-soft) 100%);
        border: 1px dashed #cbd5e1;
        border-radius: var(--pa-radius);
        padding: 1rem;
        line-height: 1.65;
    }}

    .pa-library-row {{
        display: grid;
        grid-template-columns: minmax(260px, 1fr) 120px 170px;
        gap: 1rem;
        align-items: center;
    }}

    .pa-muted {{
        color: var(--pa-muted);
    }}

    /* ── Library card grid ── */
    .pa-card-title {{
        font-weight: 780;
        font-size: 0.96rem;
        line-height: 1.35;
        color: var(--pa-ink);
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 0.4rem;
    }}

    .pa-card-date {{
        color: var(--pa-faint);
        font-size: 0.76rem;
        margin-left: 0.5rem;
    }}

    .pa-card-current {{
        border-left: 3px solid var(--pa-accent) !important;
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.03) 0%, transparent 10%) !important;
    }}

    /* ── Paragraph list ── */
    .pa-para-list-item {{
        display: flex;
        gap: 0.5rem;
        padding: 0.35rem 0.5rem;
        border-radius: var(--pa-radius-sm);
        font-size: 0.84rem;
        line-height: 1.45;
        transition: var(--pa-transition);
    }}

    .pa-para-list-item:hover {{
        background: var(--pa-surface-tint);
    }}

    .pa-para-current {{
        background: rgba(37, 99, 235, 0.06);
        border-left: 3px solid var(--pa-accent);
        font-weight: 600;
    }}

    .pa-para-num {{
        color: var(--pa-muted);
        font-weight: 700;
        min-width: 2rem;
        text-align: right;
        font-size: 0.76rem;
    }}

    .pa-para-excerpt {{
        color: var(--pa-ink-2);
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}

    /* ── AI explanation ── */
    .pa-ai-explanation h2 {{
        font-size: 1rem;
        color: var(--pa-accent);
        border-bottom: 1px solid var(--pa-border-soft);
        padding-bottom: 0.35rem;
        margin-top: 1rem;
    }}

    .pa-ai-explanation h3 {{
        font-size: 0.92rem;
        color: var(--pa-ink);
        margin-top: 0.8rem;
    }}

    .pa-ai-explanation blockquote {{
        border-left: 3px solid var(--pa-border);
        padding-left: 0.8rem;
        color: var(--pa-muted);
        font-style: italic;
    }}

    .pa-ai-explanation ul {{
        padding-left: 1.2rem;
    }}

    .pa-ai-explanation li {{
        margin-bottom: 0.35rem;
    }}

    /* ── File manager ── */
    .pa-file-registered {{
        border-left: 3px solid var(--pa-accent);
        padding-left: 0.5rem;
    }}

    .pa-file-unregistered {{
        border-left: 3px solid var(--pa-warm);
        padding-left: 0.5rem;
        opacity: 0.85;
    }}

    .pa-file-status {{
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ── Home page checklist ── */
    .pa-checklist-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0;
        border-bottom: 1px solid var(--pa-border-soft);
        font-size: 0.9rem;
    }}

    .pa-checklist-item:last-child {{
        border-bottom: none;
    }}

    .pa-checklist-num {{
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 50%;
        background: var(--pa-surface-tint);
        border: 1px solid var(--pa-border);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.78rem;
        color: var(--pa-muted);
    }}

    .pa-checklist-status {{
        margin-left: auto;
        font-size: 0.85rem;
    }}

    /* ── Status indicator (st.status area) ── */
    [data-testid="stStatusWidget"] {{
        border-radius: var(--pa-radius);
        border: 1px solid var(--pa-border-soft);
    }}
    """


def _build_animations() -> str:
    return """
    @keyframes paFadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .block-container {
        animation: paFadeIn 320ms ease-out;
    }

    @keyframes paPulse {
        0%, 100% { border-left-color: #d6b36a; }
        50%      { border-left-color: #f0c97d; }
    }
    """


def _build_responsive() -> str:
    return """
    @media (max-width: 1200px) {
        .block-container {
            padding: 0.7rem 1rem 1.8rem;
        }
    }

    @media (max-width: 920px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }
        .pa-page-head {
            display: block;
        }
        .pa-head-stats {
            justify-content: flex-start;
            margin-top: 0.8rem;
        }
        .pa-library-row {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 0.5rem 0.65rem 1.2rem;
        }
        h1 {
            font-size: 1.3rem;
        }
        .pa-paper-strip {
            flex-direction: column;
        }
    }
    """


def assemble_css(theme: ThemeColors) -> str:
    return (
        _build_variables(theme)
        + _build_base()
        + _build_color_dependent(theme)
        + _build_animations()
        + _build_responsive()
    )
