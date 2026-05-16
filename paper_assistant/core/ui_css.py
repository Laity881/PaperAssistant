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
    bg="#f6f8f5",
    bg_2="#edf3ef",
    surface="#ffffff",
    surface_soft="#f7faf8",
    surface_tint="#eef7f3",
    ink="#111827",
    ink_2="#24302f",
    muted="#66736f",
    faint="#98a2b3",
    border="#d9e2dc",
    border_soft="#e8eee9",
    accent="#0f766e",
    accent_2="#b42318",
    warm="#b54708",
    sidebar="#181716",
    sidebar_soft="#262321",
    sidebar_line="#37332f",
    shadow="0 18px 45px rgba(16, 24, 40, 0.08)",
    shadow_soft="0 10px 26px rgba(16, 24, 40, 0.05)",
    primary_button_bg="#0f766e",
    primary_button_hover="#115e59",
    gradient_app="linear-gradient(180deg, #f8faf7 0%, #f2f6f3 48%, #edf3ef 100%)",
    chat_bg="#ffffff",
    chat_border="#e8eee9",
    stat_bg="rgba(255, 255, 255, 0.78)",
)

DARK_THEME = ThemeColors(
    bg="#111111",
    bg_2="#181716",
    surface="#1e1d1b",
    surface_soft="#25231f",
    surface_tint="#202720",
    ink="#e5e7eb",
    ink_2="#d1d5db",
    muted="#9ca3af",
    faint="#6b7280",
    border="#34312d",
    border_soft="#2b2926",
    accent="#2dd4bf",
    accent_2="#fb7185",
    warm="#f59e0b",
    sidebar="#090909",
    sidebar_soft="#171514",
    sidebar_line="#2a2623",
    shadow="0 18px 45px rgba(0, 0, 0, 0.35)",
    shadow_soft="0 10px 26px rgba(0, 0, 0, 0.25)",
    primary_button_bg="#0f766e",
    primary_button_hover="#0d9488",
    gradient_app="linear-gradient(180deg, #151515 0%, #101010 50%, #0d0d0d 100%)",
    chat_bg="#1e1d1b",
    chat_border="#34312d",
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
        --pa-chat-bg: {theme.chat_bg};
        --pa-chat-border: {theme.chat_border};
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
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.16) !important;
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
        background: linear-gradient(180deg, rgba(15, 118, 110, 0.06) 0%, rgba(15, 118, 110, 0.01) 100%);
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
        background: linear-gradient(90deg, rgba(15, 118, 110, 0.06) 0%, transparent 10%) !important;
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
        background: rgba(15, 118, 110, 0.08);
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

    /* ── Dashboard workspace ── */
    .pa-section-eyebrow {{
        color: var(--pa-accent);
        font-size: 0.72rem;
        font-weight: 820;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }}

    .pa-focus-title {{
        color: var(--pa-ink);
        font-size: 1.28rem;
        line-height: 1.28;
        font-weight: 820;
        margin-bottom: 0.28rem;
    }}

    .pa-focus-meta {{
        color: var(--pa-muted);
        font-size: 0.86rem;
        line-height: 1.5;
    }}

    .pa-progress-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.9rem 0 1rem;
    }}

    .pa-progress-chip {{
        border: 1px solid var(--pa-border);
        background: var(--pa-surface-soft);
        color: var(--pa-muted);
        border-radius: 999px;
        padding: 0.24rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 720;
    }}

    .pa-progress-chip.is-done {{
        background: rgba(15, 118, 110, 0.1);
        border-color: rgba(15, 118, 110, 0.24);
        color: var(--pa-accent);
    }}

    .pa-action-copy {{
        min-height: 5rem;
        border: 1px solid var(--pa-border-soft);
        border-radius: var(--pa-radius);
        background: var(--pa-surface-soft);
        padding: 0.72rem 0.75rem;
        margin-bottom: 0.45rem;
    }}

    .pa-action-title {{
        color: var(--pa-ink);
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }}

    .pa-action-desc {{
        color: var(--pa-muted);
        font-size: 0.78rem;
        line-height: 1.45;
    }}

    .pa-check-row {{
        display: grid;
        grid-template-columns: 0.9rem minmax(6rem, 1fr) auto;
        gap: 0.55rem;
        align-items: center;
        min-height: 2.35rem;
        border-bottom: 1px solid var(--pa-border-soft);
    }}

    .pa-check-row:last-child {{
        border-bottom: 0;
    }}

    .pa-status-dot {{
        width: 0.58rem;
        height: 0.58rem;
        border-radius: 50%;
        display: inline-block;
        background: var(--pa-warm);
        box-shadow: 0 0 0 3px rgba(181, 71, 8, 0.12);
    }}

    .pa-status-dot.ok {{
        background: var(--pa-accent);
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }}

    .pa-check-name {{
        color: var(--pa-ink);
        font-weight: 740;
        font-size: 0.88rem;
    }}

    .pa-check-status {{
        color: var(--pa-muted);
        font-size: 0.82rem;
        font-weight: 680;
    }}

    .pa-timeline-item {{
        display: grid;
        grid-template-columns: 2.45rem 1fr;
        gap: 0.75rem;
        padding: 0.68rem 0;
        border-bottom: 1px solid var(--pa-border-soft);
    }}

    .pa-timeline-item:last-child {{
        border-bottom: 0;
    }}

    .pa-timeline-num {{
        width: 2.1rem;
        height: 2.1rem;
        border-radius: var(--pa-radius);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--pa-border);
        color: var(--pa-muted);
        font-size: 0.78rem;
        font-weight: 820;
        background: var(--pa-surface-soft);
    }}

    .pa-timeline-item.is-done .pa-timeline-num {{
        color: #ffffff;
        background: var(--pa-accent);
        border-color: var(--pa-accent);
    }}

    .pa-timeline-title {{
        color: var(--pa-ink);
        font-weight: 780;
        line-height: 1.35;
    }}

    .pa-timeline-desc {{
        color: var(--pa-muted);
        font-size: 0.84rem;
        line-height: 1.55;
        margin-top: 0.12rem;
    }}

    .pa-data-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
    }}

    .pa-data-grid > div {{
        border: 1px solid var(--pa-border-soft);
        background: var(--pa-surface-soft);
        border-radius: var(--pa-radius);
        padding: 0.75rem;
        min-height: 5.1rem;
    }}

    .pa-data-grid strong {{
        display: block;
        color: var(--pa-ink);
        margin-bottom: 0.25rem;
        font-size: 0.92rem;
    }}

    .pa-data-grid span {{
        color: var(--pa-muted);
        line-height: 1.48;
        font-size: 0.8rem;
    }}

    .pa-learning-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 0.35rem 0 0.9rem;
    }}

    .pa-learning-card {{
        border: 1px solid var(--pa-border-soft);
        background: var(--pa-surface-soft);
        border-radius: var(--pa-radius);
        padding: 0.78rem;
        min-height: 5.4rem;
    }}

    .pa-learning-card strong {{
        display: block;
        color: var(--pa-ink);
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }}

    .pa-learning-card span {{
        color: var(--pa-muted);
        font-size: 0.79rem;
        line-height: 1.45;
    }}

    .pa-score-band {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.65rem;
        margin: 0.35rem 0 0.75rem;
    }}

    .pa-score-item {{
        border: 1px solid var(--pa-border-soft);
        border-radius: var(--pa-radius);
        padding: 0.65rem;
        background: var(--pa-surface-soft);
    }}

    .pa-score-label {{
        color: var(--pa-muted);
        font-size: 0.76rem;
        font-weight: 700;
    }}

    .pa-score-value {{
        color: var(--pa-ink);
        font-size: 1.18rem;
        font-weight: 820;
        margin-top: 0.12rem;
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
        .pa-learning-grid,
        .pa-score-band,
        .pa-data-grid {
            grid-template-columns: 1fr 1fr;
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
        .pa-learning-grid,
        .pa-score-band,
        .pa-data-grid {
            grid-template-columns: 1fr;
        }
        .pa-check-row {
            grid-template-columns: 0.9rem 1fr;
        }
        .pa-check-status {
            grid-column: 2;
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
