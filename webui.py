"""
Mega-ASR Console — Streamlit 前端

依赖（硬性）:
    pip install streamlit numpy soundfile streamlit-mic-recorder
    可选: psutil（系统监控）、pynvml（NVIDIA GPU 监控）

特性:
- 三栏布局: 系统监控 / 控制台 / 转写记录
- 界面语言切换（en / zh / ja，默认 en）
- 浏览器麦克风录音（streamlit-mic-recorder，紫色按钮 → 红色停止按钮）
- 音频文件上传（蓝色按钮）
- 录音/上传 → "待识别"状态 → 点击"开始识别"才生成转写
- 真实 STFT 频谱图（黑底金黄）
"""

import base64
import io
import math
import os
import platform
import random
import time
import wave
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# ──────────────────────────────────────────────
# 可选依赖
# ──────────────────────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except Exception:
    HAS_NVML = False

OS_NAME = platform.system()

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Mega-ASR Console",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# i18n
# ──────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "brand_sub": "Speech Recognition · Realtime",
        "sec_system": "System Monitor",
        "sec_console": "Console",
        "sec_log": "Transcripts",
        "m_cpu": "CPU Usage",
        "m_mem": "Memory",
        "m_gpu": "GPU Usage",
        "m_vram": "VRAM",
        "m_disk": "Disk",
        "m_net": "Network I/O",
        "status_rec": "Recording",
        "status_proc": "Processing",
        "status_pending": "Awaiting recognition",
        "status_idle": "Idle",
        "label_model": "Model",
        "label_lang": "Interface Language",
        "toggle_compare": "Enable Qwen3-ASR comparison",
        "btn_start": "Start Recording",
        "btn_stop": "Stop",
        "btn_upload": "Upload File",
        "btn_recognize": "Start Recognition",
        "btn_recognizing": "Recognizing…",
        "btn_clear": "Clear records",
        "count_suffix": "items",
        "empty": "No records · click Start Recording or Upload File",
        "pending_note": "Pending: audio ready, click \"Start Recognition\" to transcribe",
        "pending_recorded": "Recorded · {dur}s",
        "pending_uploaded": "Uploaded · {name}",
        "spec_truncated": "spectrum shows first 10s only",
        "download": "Download",
        "lang_label": "Recognition language",  # 仍保留：用于条目展示的语言标签
    },
    "zh": {
        "brand_sub": "语音识别 · 实时",
        "sec_system": "系统监控",
        "sec_console": "控制台",
        "sec_log": "转写记录",
        "m_cpu": "CPU 使用率",
        "m_mem": "内存",
        "m_gpu": "GPU 使用率",
        "m_vram": "显存",
        "m_disk": "磁盘",
        "m_net": "网络 I/O",
        "status_rec": "录音中",
        "status_proc": "识别中",
        "status_pending": "待识别",
        "status_idle": "待机",
        "label_model": "模型",
        "label_lang": "界面语言",
        "toggle_compare": "启用 Qwen3-ASR 对比",
        "btn_start": "开始录音",
        "btn_stop": "停止",
        "btn_upload": "上传文件",
        "btn_recognize": "开始识别",
        "btn_recognizing": "识别中…",
        "btn_clear": "清空记录",
        "count_suffix": "条",
        "empty": "暂无记录 · 点击\"开始录音\"或\"上传文件\"",
        "pending_note": "已就绪：音频已加载，点击\"开始识别\"以生成转写",
        "pending_recorded": "录音 · {dur}s",
        "pending_uploaded": "已上传 · {name}",
        "spec_truncated": "频谱仅显示前 10s",
        "download": "下载",
        "lang_label": "识别语言",
    },
    "ja": {
        "brand_sub": "音声認識 · リアルタイム",
        "sec_system": "システム監視",
        "sec_console": "コンソール",
        "sec_log": "文字起こし",
        "m_cpu": "CPU 使用率",
        "m_mem": "メモリ",
        "m_gpu": "GPU 使用率",
        "m_vram": "VRAM",
        "m_disk": "ディスク",
        "m_net": "ネットワーク I/O",
        "status_rec": "録音中",
        "status_proc": "認識中",
        "status_pending": "認識待ち",
        "status_idle": "待機",
        "label_model": "モデル",
        "label_lang": "表示言語",
        "toggle_compare": "Qwen3-ASR 比較を有効化",
        "btn_start": "録音開始",
        "btn_stop": "停止",
        "btn_upload": "ファイルをアップロード",
        "btn_recognize": "認識開始",
        "btn_recognizing": "認識中…",
        "btn_clear": "記録をクリア",
        "count_suffix": "件",
        "empty": "記録なし ·「録音開始」または「ファイルをアップロード」",
        "pending_note": "準備完了：音声がロード済み、「認識開始」で文字起こし",
        "pending_recorded": "録音 · {dur}s",
        "pending_uploaded": "アップロード済み · {name}",
        "spec_truncated": "スペクトルは最初の10秒のみ",
        "download": "ダウンロード",
        "lang_label": "認識言語",
    },
}

UI_LANG_LABELS = {
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
}

# 初始化界面语言（默认英语）
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "en"


def t(key: str) -> str:
    return TRANSLATIONS[st.session_state.ui_lang].get(key, key)


# ──────────────────────────────────────────────
# 配色
# ──────────────────────────────────────────────
GOLD = "#d4af37"
GOLD_SOFT = "#b8941f"
INK = "#1a1a1a"
LINE = "#ececec"
MUTE = "#8a8a8a"

# 三个动作按钮的主题色
PURPLE = "#7c4dff"
PURPLE_DARK = "#5e35d6"
RED = "#e53935"
RED_DARK = "#c62828"
BLUE = "#1e88e5"
BLUE_DARK = "#1565c0"
GRAY_DISABLED = "#d0d0d0"

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
    }}
    #MainMenu, header, footer {{ visibility: hidden; }}
    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }}

    .brand {{ display:flex; align-items:center; gap:0.9rem; margin-bottom:1.5rem; }}
    .brand img {{ width:38px; height:38px; border-radius:6px; }}
    .brand-title {{ font-size:1.35rem; font-weight:600; color:{INK}; letter-spacing:0.01em; line-height:1.1; }}
    .brand-sub {{ font-size:0.7rem; color:{MUTE}; letter-spacing:0.18em; text-transform:uppercase; margin-top:2px; }}

    .section-label {{
        font-size:0.68rem; font-weight:600; letter-spacing:0.16em;
        text-transform:uppercase; color:#9a9a9a; margin:0 0 0.8rem 0;
    }}

    .panel {{ background:#ffffff; border:1px solid {LINE}; border-radius:8px; padding:1.25rem; }}

    .metric {{ padding:0.9rem 0; border-bottom:1px solid #f3f3f3; }}
    .metric:last-child {{ border-bottom:none; }}
    .metric-label {{ font-size:0.68rem; color:{MUTE}; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.35rem; }}
    .metric-row {{ display:flex; align-items:baseline; justify-content:space-between; gap:0.5rem; }}
    .metric-val {{ font-size:1.5rem; font-weight:600; color:{INK}; font-variant-numeric:tabular-nums; line-height:1; }}
    .metric-unit {{ font-size:0.75rem; color:{MUTE}; font-weight:500; }}
    .metric-bar {{ position:relative; height:3px; background:#f0f0f0; border-radius:2px; margin-top:0.55rem; overflow:hidden; }}
    .metric-bar > span {{ position:absolute; left:0; top:0; bottom:0; background:{INK}; border-radius:2px; transition:width 0.4s ease; }}
    .metric-bar.gold > span {{ background:{GOLD}; }}
    .metric-na {{ color:#c0c0c0; font-size:1.2rem; font-weight:500; }}

    .status-pill {{
        display:inline-flex; align-items:center; gap:0.5rem;
        font-size:0.75rem; color:#555;
        padding:0.3rem 0.7rem; background:#f7f7f7;
        border-radius:999px; border:1px solid {LINE};
        margin-bottom:1rem;
    }}
    .dot {{ width:6px; height:6px; border-radius:50%; background:#c0c0c0; }}
    .dot.live {{ background:{RED}; animation:pulse 1.4s infinite; }}
    .dot.pending {{ background:{BLUE}; }}
    .dot.proc {{ background:{GOLD}; animation:pulse 1.4s infinite; }}
    @keyframes pulse {{
        0%   {{ box-shadow:0 0 0 0   rgba(229,57,53,.5); }}
        70%  {{ box-shadow:0 0 0 8px rgba(229,57,53,0); }}
        100% {{ box-shadow:0 0 0 0   rgba(229,57,53,0); }}
    }}

    /* ── 默认按钮（深色 / 清空） ───────────────── */
    .stButton > button {{
        width:100%;
        border-radius:6px;
        border:1px solid {INK};
        background:{INK};
        color:#fafafa;
        font-weight:500; letter-spacing:0.04em;
        padding:0.55rem 1rem;
        transition:all 0.15s ease;
    }}
    .stButton > button:hover {{ background:#333; border-color:#333; color:#fff; transform:translateY(-1px); }}

    /* ── 录音按钮：mic_recorder 按钮的容器（按钮本体在同源 iframe 内，
           样式由 JS 注入到 iframe 内部，见页面顶部 <script>） ───── */
    div[data-purpose="mic-wrap"] {{
        /* 这层基本透明：iframe 内按钮会自己撑成紫色/红色按钮 */
        min-height:42px;
    }}
    /* 去掉 Streamlit 组件容器的默认 padding/margin，让 iframe 紧贴 */
    div[data-purpose="mic-wrap"] [data-testid="stIFrame"],
    div[data-purpose="mic-wrap"] [data-testid="stCustomComponentV1"] {{
        margin:0 !important;
        padding:0 !important;
    }}
    div[data-purpose="mic-wrap"] iframe {{
        width:100% !important;
        min-height:42px !important;
        border:none !important;
    }}
    @keyframes recpulse {{
        0%, 100% {{ box-shadow:0 0 0 0   rgba(229,57,53,0.35); }}
        50%      {{ box-shadow:0 0 0 6px rgba(229,57,53,0.10); }}
    }}

    /* ── 蓝色：上传文件（包裹 file_uploader 的按钮） ── */
    div[data-purpose="btn-upload"] [data-testid="stFileUploader"] section {{
        padding:0; border:none; background:transparent;
    }}
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzone"] {{
        background:{BLUE} !important;
        border:1px solid {BLUE} !important;
        border-radius:6px;
        min-height:auto !important;
        padding:0 !important;
        transition:all 0.15s ease;
        box-shadow:0 1px 0 rgba(30,136,229,0.25);
    }}
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzone"]:hover {{
        background:{BLUE_DARK} !important; border-color:{BLUE_DARK} !important;
        transform:translateY(-1px);
    }}
    /* 隐藏默认的 dropzone 提示文字 */
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzoneInstructions"] {{
        display:none !important;
    }}
    /* 把整个 dropzone 内的按钮拉伸成整个区域，与录音按钮等高 */
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzone"] button {{
        background:transparent !important;
        border:none !important;
        color:#ffffff !important;
        font-weight:500 !important;
        font-size:1rem !important;
        letter-spacing:0.04em;
        width:100% !important;
        min-height:42px !important;
        padding:0.55rem 1rem !important;
        box-shadow:none !important;
        display:inline-flex !important;
        align-items:center !important;
        justify-content:center !important;
        gap:0.55rem !important;
        line-height:1 !important;
    }}
    /* 中间 ✚ 十字图标（SVG，纯白） */
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzone"] button::before {{
        content:"";
        display:inline-block;
        width:14px; height:14px;
        flex-shrink:0;
        background-color:#ffffff;
        -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11 3h2v8h8v2h-8v8h-2v-8H3v-2h8z"/></svg>') no-repeat center / contain;
                mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11 3h2v8h8v2h-8v8h-2v-8H3v-2h8z"/></svg>') no-repeat center / contain;
    }}
    /* 文件信息条 */
    div[data-purpose="btn-upload"] [data-testid="stFileUploaderFile"] {{
        font-size:0.72rem;
    }}

    /* ── 灰色：开始识别（待识别时变深色） ───────── */
    div[data-purpose="btn-recognize-disabled"] .stButton > button {{
        background:#f2f2f2 !important;
        border:1px solid {GRAY_DISABLED} !important;
        color:#a0a0a0 !important;
        cursor:not-allowed;
    }}
    div[data-purpose="btn-recognize-disabled"] .stButton > button:hover {{
        background:#f2f2f2 !important; transform:none;
        border-color:{GRAY_DISABLED} !important; color:#a0a0a0 !important;
    }}
    div[data-purpose="btn-recognize-active"] .stButton > button {{
        background:{INK}; border-color:{INK}; color:#ffffff;
    }}
    div[data-purpose="btn-recognize-active"] .stButton > button:hover {{
        background:#000; border-color:#000;
    }}

    /* ── 清空按钮：浅色边框 ────────────────────── */
    div[data-purpose="btn-clear"] .stButton > button {{
        background:#ffffff; color:{INK}; border:1px solid #d8d8d8;
    }}
    div[data-purpose="btn-clear"] .stButton > button:hover {{
        background:#f5f5f5; border-color:{INK};
    }}

    .stSelectbox label, .stToggle label, .stRadio label {{
        font-size:0.78rem !important; color:#555 !important; font-weight:500 !important;
    }}

    /* 待识别提示卡 */
    .pending-card {{
        margin-top:0.9rem; padding:0.8rem 0.9rem;
        background:#eef5fd; border:1px solid #cfe3f7;
        border-radius:6px;
        font-size:0.78rem; color:#1d4f7c; line-height:1.5;
    }}
    .pending-title {{
        font-weight:600; font-size:0.72rem;
        letter-spacing:0.1em; text-transform:uppercase;
        color:{BLUE_DARK}; margin-bottom:0.3rem;
    }}

    .entry {{ padding:1.1rem 0 1.25rem 0; border-bottom:1px solid #f0f0f0; }}
    .entry:last-child {{ border-bottom:none; }}
    .entry-meta {{
        font-size:0.72rem; color:#a8a8a8;
        letter-spacing:0.04em; font-variant-numeric:tabular-nums;
        margin-bottom:0.6rem; display:flex; gap:0.6rem; align-items:center;
    }}
    .entry-meta .sep {{ color:#d0d0d0; }}
    .entry-text {{ font-size:0.98rem; color:#1f1f1f; line-height:1.65; }}

    .cmp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0.9rem; margin-top:0.5rem; }}
    .cmp-card {{ padding:0.7rem 0.85rem; border:1px solid {LINE}; border-radius:6px; background:#fafafa; }}
    .cmp-tag {{ font-size:0.65rem; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:{MUTE}; margin-bottom:0.4rem; }}
    .cmp-tag.primary {{ color:{GOLD_SOFT}; }}
    .cmp-card.primary {{ background:#fffaf0; border-color:#f0e3b8; }}

    .spec-wrap {{ background:#000; border-radius:6px; padding:0; margin:0.6rem 0 0.7rem 0; overflow:hidden; }}
    audio {{ width:100%; height:34px; margin-top:0.2rem; }}

    .dl-link {{
        display:inline-block; font-size:0.72rem; color:{MUTE};
        text-decoration:none; padding:0.25rem 0.65rem;
        border:1px solid {LINE}; border-radius:4px; margin-left:0.5rem;
        transition:all 0.15s ease;
    }}
    .dl-link:hover {{ color:{INK}; border-color:{INK}; }}

    .empty {{ text-align:center; padding:4rem 1rem; color:#bdbdbd; font-size:0.9rem; }}
    .empty-mark {{ font-size:2rem; color:#e0e0e0; margin-bottom:0.8rem; font-weight:200; }}

    hr {{ border:none; border-top:1px solid {LINE}; margin:1rem 0; }}
    </style>
    <script>
    // ── 上传按钮：替换 dropzone 内按钮文案（保持原行为） ─────
    const setUploadLabel = () => {{
        document.querySelectorAll('div[data-purpose="btn-upload"] [data-testid="stFileUploaderDropzone"] button')
            .forEach(b => {{
                const label = document.querySelector('div[data-purpose="btn-upload"]').getAttribute('data-label');
                if (label) {{
                    b.setAttribute('data-label', label);
                    if (!b.textContent.trim() || b.textContent !== label) b.textContent = label;
                }}
            }});
    }};

    // ── 录音按钮：进入同源 iframe 注入紫/红样式 ─────
    // mic_recorder 的 iframe 与主页同源 + sandbox allow-same-origin，
    // 因此 iframe.contentDocument 可直接访问。
    const MIC_STYLE_ID = 'mega-asr-mic-style';
    const MIC_CSS = `
      :root, body {{ margin:0 !important; padding:0 !important; background:transparent !important; }}
      .myButton {{
        all:unset;
        box-sizing:border-box;
        display:flex !important;
        align-items:center !important;
        justify-content:center !important;
        gap:0.55rem;
        width:100% !important;
        min-height:42px !important;
        padding:0.55rem 1rem !important;
        background:#7c4dff !important;
        border:1px solid #7c4dff !important;
        border-radius:6px !important;
        color:#ffffff !important;
        font-family:'Inter','PingFang SC','Microsoft YaHei',-apple-system,sans-serif !important;
        font-size:1rem !important;
        font-weight:500 !important;
        letter-spacing:0.04em !important;
        cursor:pointer !important;
        transition:all 0.15s ease !important;
        box-shadow:0 1px 0 rgba(124,77,255,0.25) !important;
      }}
      .myButton:hover {{
        background:#5e35d6 !important;
        border-color:#5e35d6 !important;
        transform:translateY(-1px);
      }}
      /* 录音中：红色 + 脉动 */
      .myButton.is-recording {{
        background:#e53935 !important;
        border-color:#e53935 !important;
        box-shadow:0 0 0 4px rgba(229,57,53,0.18) !important;
        animation: megaRec 1.6s ease-in-out infinite;
      }}
      .myButton.is-recording:hover {{
        background:#c62828 !important;
        border-color:#c62828 !important;
        transform:none;
      }}
      @keyframes megaRec {{
        0%, 100% {{ box-shadow:0 0 0 0 rgba(229,57,53,0.35) !important; }}
        50%      {{ box-shadow:0 0 0 6px rgba(229,57,53,0.10) !important; }}
      }}
      /* 内置 mic 图标（idle）/ stop 方块（recording），通过伪元素加 */
      .myButton::before {{
        content:"";
        display:inline-block;
        width:14px; height:14px;
        background:#ffffff;
        flex-shrink:0;
        -webkit-mask: var(--mega-icon) no-repeat center / contain;
                mask: var(--mega-icon) no-repeat center / contain;
        --mega-icon: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg>');
      }}
      .myButton.is-recording::before {{
        --mega-icon: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>');
      }}
    `;

    const wireMicIframe = (iframe) => {{
        try {{
            const doc = iframe.contentDocument;
            if (!doc || !doc.body) return false;

            // 注入样式表（只注入一次）
            if (!doc.getElementById(MIC_STYLE_ID)) {{
                const s = doc.createElement('style');
                s.id = MIC_STYLE_ID;
                s.textContent = MIC_CSS;
                doc.head.appendChild(s);
            }}

            const wrap = iframe.closest('div[data-purpose="mic-wrap"]');
            const stopLabel = wrap ? wrap.getAttribute('data-stop-label') : '';

            const refresh = () => {{
                const btn = doc.querySelector('.myButton');
                if (!btn) return;
                const txt = (btn.textContent || '').trim();
                if (stopLabel && txt === stopLabel) {{
                    btn.classList.add('is-recording');
                }} else {{
                    btn.classList.remove('is-recording');
                }}
            }};
            refresh();

            // 监听 iframe 内部 DOM 变化（按钮文字会在 start ↔ stop 间切换）
            if (!iframe._megaObs) {{
                iframe._megaObs = new MutationObserver(refresh);
                iframe._megaObs.observe(doc.body, {{ childList:true, subtree:true, characterData:true }});
            }}
            return true;
        }} catch (e) {{
            // contentDocument 拒绝访问，理论上不应发生（同源 + allow-same-origin）
            console.warn('[mega-asr] cannot access mic iframe:', e);
            return false;
        }}
    }};

    const wireAllMicIframes = () => {{
        document.querySelectorAll('div[data-purpose="mic-wrap"] iframe').forEach(iframe => {{
            if (iframe._megaWired) return;
            const ok = wireMicIframe(iframe);
            if (ok) {{
                iframe._megaWired = true;
            }} else {{
                // iframe 还没 load，监听 load 事件
                iframe.addEventListener('load', () => {{
                    if (wireMicIframe(iframe)) iframe._megaWired = true;
                }}, {{ once:true }});
            }}
        }});
    }};

    const tick = () => {{ setUploadLabel(); wireAllMicIframes(); }};
    new MutationObserver(tick).observe(document.body, {{ childList:true, subtree:true }});
    tick();
    </script>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 系统指标
# ──────────────────────────────────────────────
def read_cpu_percent():
    if not HAS_PSUTIL: return None
    try: return psutil.cpu_percent(interval=None)
    except Exception: return None

def read_mem_percent():
    if not HAS_PSUTIL: return None
    try: return psutil.virtual_memory().percent
    except Exception: return None

def read_gpu():
    if HAS_NVML:
        try:
            h = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
            return util, mem.used / mem.total * 100
        except Exception:
            return None, None
    return None, None

def read_disk_percent():
    if not HAS_PSUTIL: return None
    try:
        path = "C:\\" if OS_NAME == "Windows" else "/"
        return psutil.disk_usage(path).percent
    except Exception:
        return None

def read_net_kbps():
    if not HAS_PSUTIL: return None
    try:
        now = psutil.net_io_counters()
        ts = time.time()
        prev = st.session_state.get("_net_prev")
        st.session_state._net_prev = (now.bytes_sent + now.bytes_recv, ts)
        if prev is None: return 0.0
        dbytes = (now.bytes_sent + now.bytes_recv) - prev[0]
        dt = max(ts - prev[1], 1e-6)
        return max(dbytes / dt / 1024, 0)
    except Exception:
        return None


def render_metric(label, value, unit="%", bar=True, gold=False, max_bar=100):
    if value is None:
        body = '<div class="metric-row"><span class="metric-na">—</span></div>'
    else:
        v_display = f"{value:.1f}" if isinstance(value, float) else str(value)
        body = (
            f'<div class="metric-row">'
            f'<span class="metric-val">{v_display}</span>'
            f'<span class="metric-unit">{unit}</span>'
            f"</div>"
        )
        if bar:
            pct = min(max(value / max_bar * 100, 0), 100)
            cls = "metric-bar gold" if gold else "metric-bar"
            body += f'<div class="{cls}"><span style="width:{pct:.1f}%"></span></div>'
    return f'<div class="metric"><div class="metric-label">{label}</div>{body}</div>'


# ──────────────────────────────────────────────
# 真实频谱图：从 wav 解码 → STFT → 32×T 能量矩阵
# ──────────────────────────────────────────────
def decode_audio(audio_bytes: bytes, mime_hint: str = "") -> tuple:
    """返回 (samples: np.ndarray float32 mono, sample_rate: int)。解码失败抛异常。"""
    data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float32), sr


def compute_spectrogram(samples: np.ndarray, sr: int,
                         n_bins: int = 32, n_frames: int = 128,
                         f_max: int = 4000) -> np.ndarray:
    """
    返回 shape (n_bins, n_frames) 的 0~1 能量矩阵，行0=低频，行末=高频。
    使用 numpy 的滑动 FFT，频段对数压缩（更贴合人耳）。
    """
    if samples is None or len(samples) < 64:
        return np.zeros((n_bins, n_frames), dtype=np.float32)

    # 归一化幅度，防止后续 log 爆炸
    samples = samples - samples.mean()
    peak = float(np.max(np.abs(samples))) or 1.0
    samples = samples / peak

    # 切成 n_frames 帧，每帧 win_size 个样本
    win_size = max(256, min(2048, len(samples) // n_frames))
    # 等间隔取 n_frames 个起点
    starts = np.linspace(0, max(0, len(samples) - win_size), n_frames).astype(int)
    window = np.hanning(win_size).astype(np.float32)

    spec_lin = np.zeros((win_size // 2 + 1, n_frames), dtype=np.float32)
    for i, s in enumerate(starts):
        seg = samples[s:s + win_size]
        if len(seg) < win_size:
            seg = np.pad(seg, (0, win_size - len(seg)))
        fft = np.fft.rfft(seg * window)
        spec_lin[:, i] = np.abs(fft)

    # 取 0~f_max Hz
    freqs = np.fft.rfftfreq(win_size, 1 / sr)
    cap = np.searchsorted(freqs, f_max)
    spec_lin = spec_lin[:cap, :] if cap > n_bins else spec_lin

    # 用 mel-like 对数分桶到 n_bins
    n_freq = spec_lin.shape[0]
    # 对数刻度的边界索引
    log_edges = np.logspace(np.log10(1), np.log10(n_freq), n_bins + 1).astype(int)
    log_edges = np.clip(log_edges, 0, n_freq)
    binned = np.zeros((n_bins, n_frames), dtype=np.float32)
    for b in range(n_bins):
        lo, hi = log_edges[b], max(log_edges[b + 1], log_edges[b] + 1)
        binned[b] = spec_lin[lo:hi, :].mean(axis=0) if hi > lo else spec_lin[lo, :]

    # dB 压缩 + 归一化到 0~1
    eps = 1e-6
    db = 20.0 * np.log10(binned + eps)
    db -= db.max()                  # 顶为 0 dB
    db = np.clip(db, -60.0, 0.0)    # 60 dB 动态范围
    norm = (db + 60.0) / 60.0       # → 0~1

    # 让低能量更暗一些（伽马）
    norm = np.power(norm, 1.4)
    return norm.astype(np.float32)


def spectrogram_svg(spec: np.ndarray, height: int = 96) -> str:
    """黑底黄渐变的频谱热力图。低能量黑，高能量金黄。"""
    n_bins, n_frames = spec.shape
    cell_w = 5
    width = n_frames * cell_w
    # 行高度（频率维度反向：高频在上、低频在下）
    cell_h = height / n_bins

    rects = []
    for b in range(n_bins):
        row = n_bins - 1 - b   # 翻转：低频画在底部
        y = row * cell_h
        for f in range(n_frames):
            v = float(spec[b, f])
            if v < 0.04:
                continue  # 接近黑色就不画（默认背景黑）
            # 颜色：黑(#000) → 暗金(#5a3d00) → 金(#d4af37) → 亮黄(#ffd864)
            # 用线性段拼一个有点纹理的色阶
            if v < 0.35:
                # 黑 → 暗金
                k = v / 0.35
                r = int(0 + (90 - 0) * k)
                g = int(0 + (61 - 0) * k)
                bl = 0
            elif v < 0.75:
                # 暗金 → 金
                k = (v - 0.35) / 0.4
                r = int(90 + (212 - 90) * k)
                g = int(61 + (175 - 61) * k)
                bl = int(0 + (55 - 0) * k)
            else:
                # 金 → 亮黄
                k = (v - 0.75) / 0.25
                r = int(212 + (255 - 212) * k)
                g = int(175 + (216 - 175) * k)
                bl = int(55 + (100 - 55) * k)
            color = f"rgb({r},{g},{bl})"
            x = f * cell_w
            rects.append(
                f'<rect x="{x}" y="{y:.2f}" width="{cell_w}" '
                f'height="{cell_h:.2f}" fill="{color}"/>'
            )

    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" '
        f'style="display:block;background:#000;">'
        + "".join(rects) +
        "</svg>"
    )


def audio_data_uri(wav_bytes: bytes, mime: str = "audio/wav") -> str:
    b64 = base64.b64encode(wav_bytes).decode()
    return f"data:{mime};base64,{b64}"


def estimate_wav_duration(wav_bytes: bytes) -> float:
    """尝试解析 wav 时长；失败返回粗略估计值"""
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        # 非 wav 文件就用文件大小估算（16kHz 16-bit mono ≈ 32 KB/s）
        return min(max(len(wav_bytes) / 32000, 1.0), 30.0)


# ──────────────────────────────────────────────
# 状态
# ──────────────────────────────────────────────
if "records" not in st.session_state:
    st.session_state.records = []
if "seed_counter" not in st.session_state:
    st.session_state.seed_counter = 1
if "pending" not in st.session_state:
    # pending 结构: {source:'record'|'upload', audio:bytes, mime, duration, name?, seed}
    st.session_state.pending = None
if "_upload_token" not in st.session_state:
    st.session_state._upload_token = 0
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

MOCK_TEXTS = {
    "en": [
        "The meeting focused on the Q4 product roadmap.",
        "We need to finish the prototype design by month-end.",
        "Customer feedback shows the UI response time still has room to improve.",
        "Next step is to kick off user testing within two weeks.",
        "Server stability under high concurrency has been validated.",
        "Overall progress is roughly three days ahead of schedule.",
    ],
    "zh": [
        "今天的会议主要讨论了第四季度的产品路线图。",
        "我们需要在本月底之前完成原型设计。",
        "客户反馈表明界面的响应速度仍有提升空间。",
        "下一步计划是在两周内启动用户测试。",
        "服务器在高并发场景下的稳定性已通过验证。",
        "整体进度比预期提前了大约三天。",
    ],
    "ja": [
        "今日の会議では第4四半期の製品ロードマップを議論しました。",
        "今月末までにプロトタイプ設計を完了する必要があります。",
        "顧客からのフィードバックでは、UI の応答速度に改善の余地があります。",
        "次のステップは2週間以内にユーザーテストを開始することです。",
        "高負荷下でのサーバーの安定性は確認済みです。",
        "全体の進捗は予定より約3日早く進んでいます。",
    ],
}


def qwen_variant(text: str, seed: int) -> str:
    rng = random.Random(seed)
    swaps_by_lang = {
        "zh": [("第四季度", "Q4"), ("产品路线图", "产品规划"), ("原型设计", "原型"),
               ("界面", "UI"), ("响应速度", "响应延迟"), ("服务器", "后端服务")],
        "en": [("Q4", "the fourth quarter"), ("UI response time", "interface latency"),
               ("prototype design", "the prototype"), ("user testing", "user trials"),
               ("Server", "Backend"), ("Overall progress", "Progress")],
        "ja": [("第4四半期", "Q4"), ("プロトタイプ設計", "プロトタイプ"),
               ("応答速度", "レイテンシ"), ("ユーザーテスト", "ユーザー検証")],
    }
    swaps = swaps_by_lang.get(st.session_state.ui_lang, [])
    out = text
    for a, b in swaps:
        if a in out and rng.random() < 0.55:
            out = out.replace(a, b)
    return out


def commit_pending_as_record(compare: bool):
    """把 pending 转成正式 record（即"识别完成"）"""
    p = st.session_state.pending
    if not p:
        return
    seed = p["seed"]
    bucket = MOCK_TEXTS.get(st.session_state.ui_lang, MOCK_TEXTS["en"])
    rng = random.Random(seed)
    text = rng.choice(bucket)

    # 真实频谱：解码 → STFT
    samples, sr = decode_audio(p["audio"], p.get("mime", "audio/wav"))
    spec = compute_spectrogram(samples, sr or 16000)

    record = {
        "id": seed,
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "language": UI_LANG_LABELS[st.session_state.ui_lang],
        "duration": p["duration"],
        "text": text,
        "compare": compare,
        "qwen_text": qwen_variant(text, seed) if compare else None,
        "audio": p["audio"],
        "audio_mime": p.get("mime", "audio/wav"),
        "spectrogram": spec,           # ← 真实频谱矩阵 (n_bins, n_frames)
        "source": p["source"],
        "file_name": p.get("name"),
    }
    st.session_state.records.insert(0, record)
    st.session_state.pending = None


# ──────────────────────────────────────────────
# Logo + 标题
# ──────────────────────────────────────────────
try:
    logo_path = Path(__file__).parent / "logo.png"
except NameError:
    logo_path = Path("logo.png")

if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="logo"/>'
else:
    logo_html = '<div style="width:38px;height:38px;background:#1a1a1a;border-radius:6px;"></div>'

st.markdown(
    f"""
    <div class="brand">
        {logo_html}
        <div>
            <div class="brand-title">Mega-ASR Console</div>
            <div class="brand-sub">{t("brand_sub")}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 三栏布局
# ──────────────────────────────────────────────
col_sys, col_ctrl, col_log = st.columns([1, 1, 3], gap="large")

# ============== 左栏：系统监控 ==============
with col_sys:
    st.markdown(f'<div class="section-label">{t("sec_system")}</div>', unsafe_allow_html=True)

    cpu = read_cpu_percent()
    mem = read_mem_percent()
    gpu_util, gpu_mem = read_gpu()
    disk = read_disk_percent()
    net = read_net_kbps()

    html = '<div class="panel">'
    html += render_metric(t("m_cpu"), cpu, "%", gold=True)
    html += render_metric(t("m_mem"), mem, "%")
    html += render_metric(t("m_gpu"), gpu_util, "%", gold=True)
    html += render_metric(t("m_vram"), gpu_mem, "%")
    html += render_metric(t("m_disk"), disk, "%")
    html += render_metric(t("m_net"), net, "KB/s", max_bar=512)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:0.68rem;color:#b0b0b0;margin-top:0.8rem;'
        f'letter-spacing:0.1em;text-align:center;">'
        f'{OS_NAME.upper()} · {platform.machine()}</div>',
        unsafe_allow_html=True,
    )

# ============== 中栏：控制台 ==============
with col_ctrl:
    st.markdown(f'<div class="section-label">{t("sec_console")}</div>', unsafe_allow_html=True)

    # 状态徽章
    if st.session_state.is_processing:
        dot_cls, status_label = "proc", t("status_proc")
    elif st.session_state.pending is not None:
        dot_cls, status_label = "pending", t("status_pending")
    else:
        dot_cls, status_label = "", t("status_idle")
    st.markdown(
        f'<div class="status-pill"><span class="dot {dot_cls}"></span>{status_label}</div>',
        unsafe_allow_html=True,
    )

    # 模型
    st.markdown(
        f'<div style="font-size:0.7rem;color:{MUTE};letter-spacing:0.12em;'
        f'text-transform:uppercase;margin-bottom:0.3rem;">{t("label_model")}</div>'
        f'<div style="font-size:1rem;color:{INK};font-weight:600;'
        f'margin-bottom:1rem;">Mega-ASR</div>',
        unsafe_allow_html=True,
    )

    # 界面语言
    lang_codes = list(UI_LANG_LABELS.keys())
    cur_idx = lang_codes.index(st.session_state.ui_lang)
    chosen_label = st.selectbox(
        t("label_lang"),
        [UI_LANG_LABELS[c] for c in lang_codes],
        index=cur_idx,
        key="ui_lang_select",
    )
    chosen_code = lang_codes[[UI_LANG_LABELS[c] for c in lang_codes].index(chosen_label)]
    if chosen_code != st.session_state.ui_lang:
        st.session_state.ui_lang = chosen_code
        st.rerun()

    compare = st.toggle(t("toggle_compare"), value=False, key="compare_toggle")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 录音（上）：真实麦克风（单按钮，紫→红） ───────────
    # mic_recorder 的按钮在同源 iframe 内，JS 注入样式（见页面顶部 <script>）
    # start_prompt / stop_prompt 文案在 JS 端会被读取并改写按钮颜色
    st.markdown(
        f'<div data-purpose="mic-wrap" '
        f'data-start-label="{t("btn_start")}" '
        f'data-stop-label="{t("btn_stop")}">',
        unsafe_allow_html=True,
    )
    mic_value = mic_recorder(
        start_prompt=t("btn_start"),
        stop_prompt=t("btn_stop"),
        just_once=True,
        use_container_width=True,
        format="wav",
        key="mic_rec",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 收到一次完整录音 → 进入 pending
    if mic_value is not None and mic_value.get("id") != st.session_state.get("_last_mic_id"):
        st.session_state._last_mic_id = mic_value.get("id")
        audio_bytes = mic_value["bytes"]
        sr_in = mic_value.get("sample_rate", 16000)
        sw_in = mic_value.get("sample_width", 2)
        try:
            duration = round(len(audio_bytes) / (sr_in * sw_in), 1)
        except Exception:
            duration = round(estimate_wav_duration(audio_bytes), 1)
        duration = max(duration, 0.5)
        seed = st.session_state.seed_counter
        st.session_state.seed_counter += 1
        st.session_state.pending = {
            "source": "record",
            "audio": audio_bytes,
            "mime": "audio/wav",
            "duration": duration,
            "seed": seed,
        }
        st.rerun()

    # 上传按钮（下方）
    st.markdown(
        f'<div data-purpose="btn-upload" data-label="{t("btn_upload")}" '
        f'style="margin-top:0.55rem;">',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        t("btn_upload"),
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        key=f"uploader_{st.session_state._upload_token}",
        label_visibility="collapsed",
        accept_multiple_files=False,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded is not None:
        audio_bytes = uploaded.getvalue()
        mime = uploaded.type or "audio/wav"
        duration = estimate_wav_duration(audio_bytes) if mime.endswith("wav") else \
                   min(max(len(audio_bytes) / 32000, 1.0), 30.0)
        seed = st.session_state.seed_counter
        st.session_state.seed_counter += 1
        st.session_state.pending = {
            "source": "upload",
            "audio": audio_bytes,
            "mime": mime,
            "duration": round(duration, 1),
            "name": uploaded.name,
            "seed": seed,
        }
        # 重置 uploader（下次上传同一文件也能触发）
        st.session_state._upload_token += 1
        st.rerun()

    # ── 开始识别 按钮（灰/深） ─────────────────
    has_pending = st.session_state.pending is not None
    rec_purpose = "btn-recognize-active" if has_pending else "btn-recognize-disabled"
    rec_label = t("btn_recognizing") if st.session_state.is_processing else t("btn_recognize")
    st.markdown(f'<div data-purpose="{rec_purpose}" style="margin-top:0.6rem;">',
                unsafe_allow_html=True)
    recognize_clicked = st.button(
        rec_label,
        key="recognize_btn",
        use_container_width=True,
        disabled=not has_pending or st.session_state.is_processing,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if recognize_clicked and has_pending:
        st.session_state.is_processing = True
        st.rerun()

    # ── 待识别提示卡 ──────────────────────────
    if has_pending and not st.session_state.is_processing:
        p = st.session_state.pending
        if p["source"] == "record":
            desc = t("pending_recorded").format(dur=f'{p["duration"]:.1f}')
        else:
            desc = t("pending_uploaded").format(name=p.get("name", ""))
        st.markdown(
            f'<div class="pending-card">'
            f'<div class="pending-title">{t("status_pending")}</div>'
            f'{desc}<br>{t("pending_note")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── 清空 ───────────────────────────────────
    st.markdown('<div data-purpose="btn-clear" style="margin-top:0.6rem;">',
                unsafe_allow_html=True)
    if st.button(t("btn_clear"), key="clr_btn", use_container_width=True):
        st.session_state.records = []
        st.session_state.pending = None
        st.session_state.is_processing = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ============== 右栏：转写记录 ==============
with col_log:
    head_l, head_r = st.columns([3, 1])
    with head_l:
        st.markdown(f'<div class="section-label">{t("sec_log")}</div>', unsafe_allow_html=True)
    with head_r:
        st.markdown(
            f'<div style="text-align:right;font-size:0.72rem;color:{MUTE};'
            f'margin-top:2px;">{len(st.session_state.records)} {t("count_suffix")}</div>',
            unsafe_allow_html=True,
        )

    if not st.session_state.records:
        st.markdown(
            f'<div class="panel"><div class="empty">'
            f'<div class="empty-mark">◌</div>'
            f'{t("empty")}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        for r in st.session_state.records:
            duration_disp = f"{r['duration']:.1f}s"

            src_tag = ""
            if r.get("source") == "upload" and r.get("file_name"):
                src_tag = (f'<span class="sep">·</span>'
                           f'<span>↑ {r["file_name"]}</span>')

            meta = (
                f'<div class="entry-meta">'
                f'<span>{r["date"]} {r["time"]}</span>'
                f'<span class="sep">·</span>'
                f'<span>{r["language"]}</span>'
                f'<span class="sep">·</span>'
                f'<span>{duration_disp}</span>'
                f'{src_tag}'
                f"</div>"
            )

            svg = spectrogram_svg(r["spectrogram"])
            spec = f'<div class="spec-wrap">{svg}</div>'

            uri = audio_data_uri(r["audio"], r.get("audio_mime", "audio/wav"))
            ext = "wav"
            if r.get("audio_mime", "").endswith("mpeg"): ext = "mp3"
            elif r.get("audio_mime", "").endswith("mp4"): ext = "m4a"
            elif r.get("audio_mime", "").endswith("flac"): ext = "flac"
            elif r.get("audio_mime", "").endswith("ogg"): ext = "ogg"
            player = (
                f'<div style="display:flex;align-items:center;gap:0.5rem;'
                f'margin-bottom:0.3rem;">'
                f'<audio controls preload="none" src="{uri}"></audio>'
                f'<a class="dl-link" href="{uri}" '
                f'download="mega-asr-{r["id"]}.{ext}">{t("download")}</a>'
                f"</div>"
            )

            if r["compare"] and r["qwen_text"]:
                body = (
                    '<div class="cmp-grid">'
                    f'<div class="cmp-card primary">'
                    f'<div class="cmp-tag primary">Mega-ASR</div>'
                    f'<div class="entry-text">{r["text"]}</div>'
                    f"</div>"
                    f'<div class="cmp-card">'
                    f'<div class="cmp-tag">Qwen3-ASR</div>'
                    f'<div class="entry-text">{r["qwen_text"]}</div>'
                    f"</div>"
                    "</div>"
                )
            else:
                body = f'<div class="entry-text">{r["text"]}</div>'

            st.markdown(
                f'<div class="entry">{meta}{spec}{player}{body}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 后台逻辑：识别（模拟耗时）+ 监控刷新
# ──────────────────────────────────────────────
if st.session_state.is_processing:
    # 模拟识别耗时
    time.sleep(1.2)
    commit_pending_as_record(st.session_state.get("compare_toggle", False))
    st.session_state.is_processing = False
    st.rerun()
else:
    # 监控刷新：放慢节奏，避免在录音过程中频繁 rerun 干扰 mic_recorder
    time.sleep(2.0)
    st.rerun()