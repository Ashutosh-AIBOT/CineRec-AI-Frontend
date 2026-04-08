"""
CineRec v2.0 — Premium AI Movie Recommender
Features:
  • Mood-based landing page (Romantic, Motivational, Action, Horror, Comedy, Sci-Fi)
  • Groq-powered corner chatbot (llama-3.1-8b-instant — free, fast, generous limits)
  • Welcome DOM agent with interactive website tour
  • Auto movie jokes/comments when viewing any movie
  • Chatbot typewriter intro per genre mood
  • Full search + details + recommendations
  • Cursor-inspired dark cinema design system
  
Setup:
  1. pip install streamlit requests groq python-dotenv
  2. Add GROQ_API_KEY to .streamlit/secrets.toml or .env:
       GROQ_API_KEY = "gsk_..."
  3. Get free key at: https://console.groq.com/keys
  4. streamlit run app.py
"""

import random
import os
import requests
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG (MUST BE FIRST)
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CineRec — Your AI Movie Companion",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load local .env if present
load_dotenv()

# ══════════════════════════════════════════════════════════════════
# CONFIG (Robust Env & Secret Loading)
# ══════════════════════════════════════════════════════════════════
def get_secret(key, default=""):
    """Robust secret loader: 1. Env Var, 2. st.secrets (safely), 3. Default."""
    val = os.getenv(key)
    if val: return val
    try:
        # Check hasattr first to avoid Streamlit warning about missing secrets file
        if hasattr(st, "secrets") and key in st.secrets: 
            return st.secrets[key]
    except Exception: pass
    return default

API_BASE     = get_secret("API_BASE", "https://cinerec-ai-backend.onrender.com")
TMDB_IMG     = "https://image.tmdb.org/t/p/w500"
GROQ_MODEL   = "llama-3.1-8b-instant"

# Groq API key priority
GROQ_API_KEY = get_secret("GROQ_API_KEY", "")

# ══════════════════════════════════════════════════════════════════
# CONTENT CONFIG
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
# MOOD & CONTENT CONFIG
# ══════════════════════════════════════════════════════════════════
MOODS = {
    "romantic":     {"emoji": "💕", "label": "Romantic",     "query": "romance love story",    "color": "#e85d7a", "desc": "Love is in the air"},
    "motivational": {"emoji": "🔥", "label": "Motivational", "query": "inspirational triumph",  "color": "#f54e00", "desc": "Rise & conquer"},
    "action":       {"emoji": "💥", "label": "Action",       "query": "action adventure",       "color": "#c08532", "desc": "Buckle up"},
    "horror":       {"emoji": "👻", "label": "Horror",       "query": "horror thriller",        "color": "#7b3fe4", "desc": "If you dare"},
    "comedy":       {"emoji": "😂", "label": "Comedy",       "query": "comedy funny",           "color": "#1f8a65", "desc": "Laugh out loud"},
    "scifi":        {"emoji": "🚀", "label": "Sci-Fi",       "query": "science fiction space",  "color": "#3b82f6", "desc": "Beyond the stars"},
}

MOOD_INTROS = {
    "romantic": [
        "Ahhh love! 💕 Let me find films that'll make your heart flutter — and maybe steal a few tissues too...",
        "Romance time! 🌹 These movies will make you believe in love... or cry about it. Same thing honestly.",
        "Setting the mood! 💌 Here are films proving love makes people do wonderfully stupid things.",
    ],
    "motivational": [
        "Time to get PUMPED! 🔥 These films will make you want to quit your job and climb Everest barefoot.",
        "Warning: watching these may cause a sudden urge to do a training montage through your neighborhood. 💪",
        "Get your tissues AND dumbbells ready. These will wreck you emotionally AND inspire you. 🏆",
    ],
    "action": [
        "Buckle UP! 💥 These films have more explosions than my cooking on a bad day. Enjoy!",
        "Action incoming! 🎬 Warning: may cause sudden urge to roll over car hoods and wear sunglasses indoors.",
        "Hold on tight! 🚨 These movies have enough adrenaline to fuel a small rocket to Mars.",
    ],
    "horror": [
        "Oh you like being scared? 👻 Interesting choice. I deeply respect the chaos. Sleep is overrated anyway.",
        "Brave soul! 🦇 These films will have you sleeping with lights on and blaming the dog for every sound.",
        "Horror fan detected! 😱 I admire your courage. These films will make you regret it... beautifully.",
    ],
    "comedy": [
        "Let's laugh! 😂 These films are so funny, your neighbors will wonder why you're cackling at midnight.",
        "Comedy loading! 🎭 Life's too short for sad movies. At least on a Friday night. Let's fix that.",
        "Laughter incoming! 😄 Scientifically proven to make everything 47% better. No, really.",
    ],
    "scifi": [
        "To infinity and beyond! 🚀 These films will make you question reality, physics, and your life choices.",
        "Big brain time! 🌌 These picks will expand your mind AND give you an existential crisis. Win-win.",
        "Space, time, and your sanity... 🛸 will all be beautifully bent by these extraordinary films.",
    ],
}

MOVIE_JOKES = {
    "romantic": [
        "Bold choice! 🌹 Either you're in love, nursing a breakup, or just torturing yourself. All valid choices.",
        "A romance film? 💕 Someone's diving into their feelings tonight. I see you. I support you. Carry on.",
        "Love story time! 🥲 Your heart is either about to feel full... or get absolutely destroyed. Good luck!",
    ],
    "motivational": [
        "An inspirational film? 🔥 In 2 hours you'll have a whole life plan written on napkins. I've seen it happen.",
        "Motivational movie! 💪 Tomorrow you WILL wake up at 5am. (You won't. But you'll think about it a lot.)",
        "Watching this to feel productive without doing anything? That's called genius-level efficiency. 🧠",
    ],
    "action": [
        "Action time! 💥 You're legally required to eat popcorn and say 'he's right behind you' at least once.",
        "Ooh action! 🚨 Reminder: do NOT try any of this at home. Your coffee table is not a stunt double.",
        "Great pick! 💫 2 hours of someone solving every problem with their fists. Honestly very inspirational.",
    ],
    "horror": [
        "Horror film? 👻 Brave. Very brave. I'll be here when you need to talk at 3am. No judgment.",
        "Horror mode! 🦇 Pro tip: the monster IS behind you right now. Made you look. You're welcome.",
        "Watching horror alone? 😱 Cool cool cool. That noise in your kitchen is probably nothing. Probably.",
    ],
    "comedy": [
        "Comedy night! 😂 Laughing burns calories. That means you can have extra snacks. This is science.",
        "Great pick! 🎭 If you don't accidentally wake someone with your laugh, did you even watch it correctly?",
        "A comedy! 😄 The only genre where everything goes wrong and it's somehow the absolute best outcome.",
    ],
    "scifi": [
        "Sci-fi! 🚀 You're about to have opinions about space travel that nobody asked for but everyone will hear.",
        "Great choice! 🌌 After this you'll spend 20 minutes googling if wormholes are real. (Spoiler: kinda?)",
        "Sci-fi fan! 🛸 You either love science OR hate understanding things immediately. Both are perfectly valid.",
    ],
    "default": [
        "Interesting choice! 🎬 Why did the movie go to therapy? Too many unresolved plot issues. 😄",
        "Great pick! 🍿 The best way to watch ANY movie is with snacks you definitely don't need. Enjoy!",
        "I see your taste! 🎭 I'd judge you... but honestly I'd watch anything with decent cinematography.",
    ],
}

WELCOME_MESSAGES = [
    "🎬 Welcome to **CineRec**! I'm Reel, your AI movie buddy. I find films, make jokes, and never spoil endings. What are you in the mood for tonight?",
    "👋 Hey there, film lover! I'm **Reel** — I know movies better than I know myself (which is saying something). Pick a vibe and let's go!",
    "🍿 Welcome! I'm **Reel**, your personal movie companion. Which type of film are you in the mood for tonight?",
]

# ══════════════════════════════════════════════════════════════════
# FULL CSS — DARK CINEMA + CURSOR DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-base:#0f0e0b; --bg-surf:#181714; --bg-card:#201f1b;
    --bg-card2:#272521; --bg-in:#1a1916;
    --tx:#f2f1ed; --tx2:rgba(242,241,237,.60); --tx3:rgba(242,241,237,.35);
    --acc:#f54e00; --acc2:#ff6520; --acc-glow:rgba(245,78,0,.18);
    --gold:#c08532; --err:#cf2d56; --ok:#1f8a65;
    --b1:rgba(242,241,237,.08); --b2:rgba(242,241,237,.14); --b3:rgba(242,241,237,.28);
    --sh-card:0 4px 24px rgba(0,0,0,.55),0 1px 4px rgba(0,0,0,.35);
    --sh-post:0 8px 32px rgba(0,0,0,.7),0 2px 8px rgba(0,0,0,.5);
    --sh-hov:0 20px 60px rgba(0,0,0,.85),0 4px 16px rgba(0,0,0,.6);
    --sh-chat:0 24px 64px rgba(0,0,0,.8),0 4px 16px rgba(0,0,0,.5);
    --r4:4px;--r8:8px;--r12:12px;--r16:16px;--r24:24px;--rpill:9999px;
    --fd:'Playfair Display',Georgia,serif;
    --fu:'Inter',system-ui,sans-serif;
    --fm:'JetBrains Mono','Courier New',monospace;
    --tr:150ms ease;
}

html,body,[class*="css"]{font-family:var(--fu)!important;background:var(--bg-base)!important;color:var(--tx)!important;}
.stApp{background:var(--bg-base)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 2rem 7rem 2rem!important;max-width:1440px!important;}

/* Sidebar Premium Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0c0a 0%, #050504 100%) !important;
    border-right: 1px solid var(--b2) !important;
}
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] div,
[data-testid="stSidebar"] label {
    color: #e8e8e8 !important; /* Premium off-white */
    font-size: 0.94rem !important;
    font-weight: 500 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
[data-testid="stSidebar"] .sb-logo {
    font-family: var(--fd);
    font-size: 2.2rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 2rem;
    text-align: center;
    letter-spacing: -0.02em;
}
[data-testid="stSidebar"] .sb-lbl {
    color: var(--gold) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    margin: 1.8rem 0 0.6rem !important;
    border-bottom: 1px solid var(--b1);
    padding-bottom: 4px;
}
/* Enhanced Sidebar Selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1a1916 !important;
    border: 1px solid var(--gold) !important;
    border-radius: var(--r8) !important;
    color: white !important;
}

/* Inputs */
[data-baseweb="input"] input,.stTextInput input{
  background:var(--bg-in)!important;border:1px solid var(--b2)!important;border-radius:var(--r8)!important;
  color:var(--tx)!important;font-size:.95rem!important;padding:.65rem 1rem!important;
  transition:border-color var(--tr),box-shadow var(--tr)!important;}
[data-baseweb="input"] input:focus{border-color:var(--acc)!important;box-shadow:0 0 0 3px var(--acc-glow)!important;outline:none!important;}
[data-baseweb="input"] input::placeholder{color:var(--tx3)!important;}
.stTextInput label{color:var(--tx3)!important;font-size:.72rem!important;text-transform:uppercase!important;letter-spacing:.1em!important;font-weight:600!important;}

/* Textarea */
.stTextArea textarea{background:var(--bg-in)!important;border:1px solid var(--b2)!important;border-radius:var(--r8)!important;color:var(--tx)!important;font-size:.88rem!important;resize:none!important;}
.stTextArea textarea:focus{border-color:var(--acc)!important;box-shadow:0 0 0 3px var(--acc-glow)!important;}
.stTextArea label{display:none!important;}

/* Selectbox */
[data-baseweb="select"]>div{background:var(--bg-in)!important;border:1px solid var(--b2)!important;border-radius:var(--r8)!important;color:var(--tx)!important;}
[data-baseweb="popover"] [role="listbox"]{background:var(--bg-card)!important;border:1px solid var(--b2)!important;border-radius:var(--r8)!important;}
[data-baseweb="popover"] [role="option"]{color:var(--tx)!important;}
[data-baseweb="popover"] [role="option"]:hover{background:var(--bg-card2)!important;}

/* Buttons */
.stButton>button{
  background:var(--bg-card)!important;color:var(--tx)!important;border:1px solid var(--b2)!important;
  border-radius:var(--r8)!important;font-family:var(--fu)!important;font-size:.82rem!important;
  font-weight:500!important;letter-spacing:.03em!important;padding:.45rem 1rem!important;
  transition:all var(--tr)!important;cursor:pointer!important;width:100%!important;}
.stButton>button:hover{background:var(--acc)!important;border-color:var(--acc)!important;color:#fff!important;
  box-shadow:0 4px 16px rgba(245,78,0,.35)!important;transform:translateY(-1px)!important;}
.stButton>button:active{transform:translateY(0)!important;}

hr{border:none!important;border-top:1px solid var(--b1)!important;margin:1.5rem 0!important;}
h1{font-family:var(--fd)!important;font-size:2.4rem!important;font-weight:600!important;letter-spacing:-.02em!important;}
h2{font-family:var(--fd)!important;font-size:1.6rem!important;font-weight:500!important;}
h3{font-family:var(--fu)!important;font-size:1.05rem!important;font-weight:600!important;}
.stAlert{background:var(--bg-card)!important;border:1px solid var(--b1)!important;border-radius:var(--r12)!important;color:var(--tx2)!important;}
[data-testid="stImage"] img{border-radius:var(--r12)!important;box-shadow:var(--sh-post)!important;
  transition:transform 220ms ease,box-shadow 220ms ease!important;display:block!important;width:100%!important;}
[data-testid="stImage"] img:hover{transform:scale(1.04) translateY(-4px)!important;box-shadow:var(--sh-hov)!important;}
.stSpinner>div>div{border-top-color:var(--acc)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg-base);}
::-webkit-scrollbar-thumb{background:var(--b2);border-radius:3px;}

/* ─── PAGE HEADER ─── */
.page-header{background:linear-gradient(135deg,var(--bg-surf) 0%,var(--bg-base) 100%);
  border-bottom:1px solid var(--b1);padding:1.75rem 0 1.25rem;margin-bottom:1.75rem;}
.brand-title{font-family:var(--fd);font-size:2.5rem;font-weight:600;letter-spacing:-.03em;line-height:1.1;}
.brand-acc{color:var(--acc);}
.brand-tag{color:var(--tx3);font-size:.78rem;font-weight:500;margin-top:.3rem;letter-spacing:.08em;text-transform:uppercase;}

/* ─── MOOD LANDING ─── */
.mood-hero{text-align:center;padding:1.5rem 0 1rem;}
.mood-hero-t{font-family:var(--fd);font-size:2rem;font-weight:500;color:var(--tx);margin-bottom:.4rem;}
.mood-hero-s{font-size:.82rem;color:var(--tx3);letter-spacing:.06em;text-transform:uppercase;}

.mood-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:1.25rem 0 1.75rem;}
.mood-card{background:var(--bg-card);border:1px solid var(--b1);border-radius:var(--r16);
  padding:1.2rem .7rem;text-align:center;cursor:pointer;transition:all 200ms ease;
  position:relative;overflow:hidden;}
.mood-card::before{content:'';position:absolute;inset:0;background:var(--mc,var(--acc));opacity:0;transition:opacity 200ms;}
.mood-card:hover::before{opacity:.09;}
.mood-card:hover{border-color:var(--mc,var(--acc));transform:translateY(-5px);box-shadow:0 12px 32px rgba(0,0,0,.5);}
.mood-em{font-size:2.1rem;display:block;margin-bottom:.45rem;}
.mood-lb{font-size:.74rem;font-weight:600;color:var(--tx2);letter-spacing:.06em;text-transform:uppercase;}
.mood-ds{font-size:.66rem;color:var(--tx3);margin-top:.2rem;}

/* ─── SECTION HEADER ─── */
.sec-hdr{display:flex;align-items:center;gap:.6rem;margin:1.8rem 0 1rem;border-bottom:1px solid var(--b1);padding-bottom:.6rem;}
.sec-bar{width:3px;height:14px;background:var(--acc);border-radius:2px;flex-shrink:0;}
.sec-txt{font-size:.72rem;font-weight:600;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;}

/* ─── MOVIE CARDS ─── */
.mv-title{font-size:.76rem;font-weight:500;color:var(--tx3);line-height:1.25;margin-top:.35rem;
  overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;min-height:1.9rem;}
.no-post{background:var(--bg-card);border:1px solid var(--b1);border-radius:var(--r12);
  aspect-ratio:2/3;display:flex;align-items:center;justify-content:center;color:var(--tx3);font-size:2rem;}

/* ─── PILLS ─── */
.pill{display:inline-block;background:var(--bg-card);color:var(--tx3);border:1px solid var(--b1);
  border-radius:var(--rpill);padding:3px 10px;font-size:.7rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;margin:2px 4px 2px 0;}
.pill.on{background:rgba(245,78,0,.12);border-color:rgba(245,78,0,.3);color:var(--acc);}
.chip{background:rgba(245,78,0,.1);border:1px solid rgba(245,78,0,.25);border-radius:var(--rpill);
  color:var(--acc);font-size:.7rem;font-weight:600;padding:2px 10px;display:inline-block;letter-spacing:.04em;}

/* ─── DETAIL PAGE ─── */
.det-card{background:var(--bg-card);border:1px solid var(--b1);border-radius:var(--r16);padding:1.75rem;box-shadow:var(--sh-card);}
.det-title{font-family:var(--fd);font-size:1.9rem;font-weight:600;letter-spacing:-.02em;color:var(--tx);line-height:1.15;margin-bottom:.75rem;}
.det-overview{font-size:.92rem;color:var(--tx2);line-height:1.75;margin-top:1rem;}
.back-wrap{border-radius:var(--r16);overflow:hidden;margin-top:1.5rem;box-shadow:var(--sh-card);}

/* ─── SIDEBAR ─── */
.sb-logo{font-family:var(--fd);font-size:1.45rem;font-weight:600;letter-spacing:-.02em;
  padding:.5rem 0 1rem;border-bottom:1px solid var(--b1);margin-bottom:1.25rem;}
.sb-lbl{font-size:.68rem;font-weight:600;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin:1.25rem 0 .5rem;}

/* ─── MOOD BANNER ─── */
.mood-banner{background:var(--bg-card);border:1px solid var(--b1);border-left:3px solid var(--acc);
  border-radius:var(--r12);padding:.7rem 1rem;margin-bottom:1.25rem;display:flex;align-items:center;gap:.75rem;}
.mood-banner-txt{font-size:.83rem;color:var(--tx2);}

/* ════════════════════════════════
   WELCOME OVERLAY
   ════════════════════════════════ */
.wlc-overlay{position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:10000;
  display:flex;align-items:center;justify-content:center;padding:1rem;backdrop-filter:blur(5px);}
.wlc-card{background:var(--bg-surf);border:1px solid var(--b2);border-radius:var(--r24);
  padding:2.5rem;max-width:500px;width:100%;box-shadow:var(--sh-chat);text-align:center;position:relative;}
.wlc-icon{width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,var(--acc),#ff8040);
  display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 1.25rem;
  animation:wlc-pulse 2s ease-in-out infinite;
  box-shadow:0 0 0 8px rgba(245,78,0,.1),0 0 0 16px rgba(245,78,0,.05);}
@keyframes wlc-pulse{0%,100%{box-shadow:0 0 0 8px rgba(245,78,0,.1),0 0 0 16px rgba(245,78,0,.05);}
  50%{box-shadow:0 0 0 14px rgba(245,78,0,.07),0 0 0 26px rgba(245,78,0,.02);}}
.wlc-title{font-family:var(--fd);font-size:1.65rem;font-weight:600;color:var(--tx);margin-bottom:.7rem;}
.wlc-msg{font-size:.9rem;color:var(--tx2);line-height:1.7;margin-bottom:1.4rem;}
.wlc-tour{background:var(--bg-card);border:1px solid var(--b1);border-radius:var(--r12);
  padding:1rem;text-align:left;margin-bottom:1.5rem;}
.tour-row{display:flex;gap:.75rem;align-items:flex-start;margin-bottom:.6rem;
  font-size:.82rem;color:var(--tx2);line-height:1.55;}
.tour-row:last-child{margin-bottom:0;}
.tour-ico{font-size:1rem;flex-shrink:0;margin-top:1px;}
.wlc-btn{background:var(--acc);color:#fff;border:none;border-radius:var(--r8);
  padding:.75rem 2rem;font-size:.9rem;font-weight:600;cursor:pointer;width:100%;
  transition:all 200ms ease;letter-spacing:.02em;}
.wlc-btn:hover{background:var(--acc2);transform:translateY(-1px);box-shadow:0 8px 24px rgba(245,78,0,.4);}

/* ─── MINI BUDDY SIDEBAR ─── */
.buddy-mini {
  position: fixed; top: 100px; right: 30px; width: 280px;
  background: rgba(20, 19, 16, 0.9); backdrop-filter: blur(20px);
  border: 1px solid var(--gold); border-radius: var(--r16);
  padding: 1.5rem; z-index: 1000; box-shadow: var(--sh-chat);
  transition: all 450ms cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: right center; display: flex; flex-direction: column;
}
.buddy-mini.buddy-hide {
  opacity: 0; transform: scale(0.9) translateX(40px); pointer-events: none;
}
.buddy-tab {
  position: fixed; top: 150px; right: -10px; z-index: 1001;
  background: var(--acc); color: white; padding: 12px 16px 12px 10px;
  border-radius: 12px 0 0 12px; cursor: pointer; box-shadow: var(--sh-chat);
  writing-mode: vertical-rl; text-orientation: mixed;
  font-size: .68rem; font-weight: 700; letter-spacing: .15em;
  transition: all 300ms ease; transform: translateX(5px);
}
.buddy-tab:hover { transform: translateX(0); background: var(--acc2); }
.buddy-close {
  position: absolute; top: 12px; right: 12px; font-size: 1.1rem;
  color: var(--tx3); cursor: pointer; transition: color 200ms;
}
.buddy-close:hover { color: var(--acc); }
.buddy-mini-hdr { font-size: .65rem; color: var(--gold); font-weight: 700; text-transform: uppercase; letter-spacing: .12em; margin-bottom: .6rem; }
.buddy-mini-chat { max-height: 150px; overflow-y: auto; font-size: .85rem; color: var(--tx2); margin-bottom: 1rem; padding-right: 5px; }
.buddy-mini-chat::-webkit-scrollbar { width: 3px; }
.buddy-mini-chat::-webkit-scrollbar-thumb { background: var(--b2); }

/* ════════════════════════════════
   CHATBOT WIDGET
   ════════════════════════════════ */
/* The FAB — we'll override Streamlit's last button */
.chat-fab-wrap .stButton>button{
  position:fixed!important;bottom:28px!important;right:28px!important;
  width:56px!important;height:56px!important;border-radius:50%!important;
  background:var(--acc)!important;border:none!important;
  font-size:1.5rem!important;padding:0!important;
  box-shadow:0 4px 20px rgba(245,78,0,.55)!important;
  z-index:9999!important;animation:fab-pulse 2.5s ease-in-out infinite!important;}
@keyframes fab-pulse{0%{box-shadow:0 4px 20px rgba(245,78,0,.5),0 0 0 0 rgba(245,78,0,.35);}
  50%{box-shadow:0 4px 20px rgba(245,78,0,.5),0 0 0 14px rgba(245,78,0,0);}
  100%{box-shadow:0 4px 20px rgba(245,78,0,.5),0 0 0 0 rgba(245,78,0,0);}}
.chat-fab-wrap .stButton>button:hover{transform:scale(1.1)!important;}

/* Chat panel */
.chat-panel{position:fixed;bottom:96px;right:24px;width:370px;
  background:var(--bg-surf);border:1px solid var(--b2);border-radius:var(--r24);
  box-shadow:var(--sh-chat);z-index:9998;overflow:hidden;
  display:flex;flex-direction:column;max-height:600px;}
.chat-head{background:linear-gradient(135deg,#1a1714,#201f1b);border-bottom:1px solid var(--b1);
  padding:.9rem 1.1rem;display:flex;align-items:center;gap:.7rem;flex-shrink:0;}
.chat-av{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,var(--acc),#ff6520);
  display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}
.chat-hname{font-size:.88rem;font-weight:600;color:var(--tx);}
.chat-hstat{font-size:.68rem;color:var(--ok);display:flex;align-items:center;gap:.3rem;}
.chat-hstat::before{content:'';width:6px;height:6px;background:var(--ok);border-radius:50%;display:inline-block;}
.chat-msgs{flex:1;overflow-y:auto;padding:.9rem;display:flex;flex-direction:column;gap:.6rem;min-height:160px;max-height:290px;}
.cmsg{display:flex;gap:.45rem;align-items:flex-start;}
.cmsg.u{flex-direction:row-reverse;}
.cbub{max-width:80%;padding:.55rem .85rem;border-radius:18px;font-size:.83rem;line-height:1.55;word-wrap:break-word;}
.cbub.b{background:var(--bg-card);border:1px solid var(--b1);color:var(--tx2);border-bottom-left-radius:4px;}
.cbub.u{background:linear-gradient(135deg,var(--acc),#e04500);color:#fff;border-bottom-right-radius:4px;}
.cbub.j{background:rgba(245,78,0,.08);border:1px solid rgba(245,78,0,.2);color:var(--tx2);border-bottom-left-radius:4px;}
.cav-b{width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,var(--acc),#ff6520);
  display:flex;align-items:center;justify-content:center;font-size:.7rem;flex-shrink:0;}
.cav-u{width:24px;height:24px;border-radius:50%;background:var(--bg-card);border:1px solid var(--b2);
  display:flex;align-items:center;justify-content:center;font-size:.7rem;flex-shrink:0;}
.chat-qrow{padding:.5rem .9rem;display:flex;gap:5px;flex-wrap:wrap;border-top:1px solid var(--b1);}
.qbtn{background:var(--bg-card);border:1px solid var(--b1);border-radius:var(--rpill);
  color:var(--tx3);font-size:.7rem;padding:3px 9px;cursor:pointer;white-space:nowrap;
  transition:all var(--tr);}
.qbtn:hover{border-color:var(--acc);color:var(--acc);background:rgba(245,78,0,.08);}
.chat-inp-row{padding:.65rem .9rem;border-top:1px solid var(--b1);display:flex;gap:.45rem;align-items:flex-end;flex-shrink:0;}

/* Typing dots */
.tdots{display:flex;gap:4px;align-items:center;padding:.5rem .85rem;}
.td{width:7px;height:7px;border-radius:50%;background:var(--tx3);animation:tdot 1.2s infinite;}
.td:nth-child(2){animation-delay:.2s;}.td:nth-child(3){animation-delay:.4s;}
@keyframes tdot{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-7px);opacity:1}}
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
def _si(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_si("view",            "home")
_si("selected_id",     None)
_si("active_mood",     None)
_si("cur_movie",     "The Dark Knight")
_si("chat_history",  [])
_si("chat_open",     False)
_si("welcome_shown", True) # Intro welcome overlay disabled as requested
_si("mini_buddy_open", True)
_si("mini_buddy_chat", [])
_si("mood_shown",      set())
_si("joke_shown",      set())
_si("cur_movie",       "")
_si("cur_genre",       "default")

# Query param routing
qpv = st.query_params.get("view")
qpi = st.query_params.get("id")
if qpv in ("home", "details"):
    st.session_state.view = qpv
if qpi:
    try:
        st.session_state.selected_id = int(qpi)
        st.session_state.view = "details"
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════
# NAVIGATION
# ══════════════════════════════════════════════════════════════════
def goto_home():
    st.session_state.view = "home"
    st.session_state.active_mood = None
    st.session_state.cur_movie = ""
    st.query_params["view"] = "home"
    try:
        del st.query_params["id"]
    except Exception:
        pass
    st.rerun()

def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()

# ══════════════════════════════════════════════════════════════════
# GROQ AI
# ══════════════════════════════════════════════════════════════════
BOT_SYSTEM = (
    "You are Reel, a witty, friendly AI movie companion for CineRec. "
    "Personality: enthusiastic, funny, uses movie references, gives short punchy responses. "
    "Rules: keep replies under 3 sentences; use 1-2 emojis per message; be genuinely helpful; "
    "make clever jokes related to what the user is watching; never be rude."
)

def groq_chat(user_msg: str, history: list = None, system: str = None, max_tokens: int = 150) -> str:
    if not GROQ_API_KEY:
        return "🔑 Add GROQ_API_KEY to `.streamlit/secrets.toml` to enable AI chat!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        msgs = [{"role": "system", "content": system or BOT_SYSTEM}]
        for h in (history or [])[-6:]:
            msgs.append(h)
        msgs.append({"role": "user", "content": user_msg})
        resp = client.chat.completions.create(
            model=GROQ_MODEL, messages=msgs, max_tokens=max_tokens, temperature=0.88
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops, brain glitch! 🤖 ({str(e)[:60]})"

def get_movie_joke(title: str, genre: str) -> str | None:
    key = f"j_{title}"
    if key in st.session_state.joke_shown:
        return None
    st.session_state.joke_shown.add(key)
    if GROQ_API_KEY:
        return groq_chat(
            f"The user just opened '{title}'. Give ONE funny, warm one-liner joke or witty comment about this specific movie or its genre. Max 2 sentences, casual tone.",
            max_tokens=70
        )
    return random.choice(MOVIE_JOKES.get(genre, MOVIE_JOKES["default"]))

# ══════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}"
        return r.json(), None
    except Exception as e:
        return None, str(e)

def parse_search(data, keyword: str, limit: int = 24):
    kl = keyword.strip().lower()
    raw = []
    if isinstance(data, dict) and "results" in data:
        for m in data.get("results") or []:
            t = (m.get("title") or "").strip()
            tid = m.get("id")
            pp = m.get("poster_path")
            if t and tid:
                raw.append({"tmdb_id": int(tid), "title": t,
                    "poster_url": f"{TMDB_IMG}{pp}" if pp else None,
                    "release_date": m.get("release_date", "")})
    elif isinstance(data, list):
        for m in data:
            tid = m.get("tmdb_id") or m.get("id")
            t = (m.get("title") or "").strip()
            if t and tid:
                raw.append({"tmdb_id": int(tid), "title": t,
                    "poster_url": m.get("poster_url"), "release_date": m.get("release_date","")})
    matched = [x for x in raw if kl in x["title"].lower()]
    fl = matched if matched else raw
    sugs = []
    for x in fl[:10]:
        yr = (x.get("release_date") or "")[:4]
        sugs.append((f"{x['title']} ({yr})" if yr else x["title"], x["tmdb_id"]))
    cards = [{"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]} for x in fl[:limit]]
    return sugs, cards

def tfidf_to_cards(items):
    out = []
    for x in items or []:
        t = x.get("tmdb") or {}
        if t.get("tmdb_id"):
            out.append({"tmdb_id": t["tmdb_id"],
                "title": t.get("title") or x.get("title") or "Untitled",
                "poster_url": t.get("poster_url")})
    return out

# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════
def sec_hdr(icon: str, label: str):
    st.markdown(f"""<div class='sec-hdr'>
        <span class='sec-bar'></span>
        <span style='font-size:.95rem;'>{icon}</span>
        <span class='sec-txt'>{label}</span>
    </div>""", unsafe_allow_html=True)

def poster_grid(cards, cols=5, pfx="g"):
    if not cards:
        st.markdown("<div style='color:var(--tx3);font-size:.85rem;padding:.75rem 0;'>No movies to display.</div>", unsafe_allow_html=True)
        return
    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        cs = st.columns(cols, gap="small")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]; idx += 1
            tid = m.get("tmdb_id"); tit = m.get("title", "Untitled"); pos = m.get("poster_url")
            with cs[c]:
                if pos:
                    st.image(pos, use_column_width=True)
                else:
                    st.markdown("<div class='no-post'>🎬</div>", unsafe_allow_html=True)
                if st.button("▶ Open", key=f"{pfx}_{r}_{c}_{idx}_{tid}"):
                    if tid:
                        goto_details(tid)
                st.markdown(f"<div class='mv-title'>{tit}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════
# COMPONENT: BROWSER SCRIPTS
# ══════════════════════════════════════════════════════════════════
def render_scripts():
    """Injects JS for scroll detection and other UI behaviors."""
    st.markdown("""
        <script>
        // Scroll detection for Buddy
        const handleScroll = () => {
            const buddy = window.parent.document.querySelector('.buddy-mini');
            if(!buddy) return;
            if(window.parent.scrollY > 80) {
                buddy.classList.add('buddy-hide');
            } else {
                buddy.classList.remove('buddy-hide');
            }
        };
        
        // Auto-initialize scroll listener
        if (!window.scrollAttached) {
            window.parent.addEventListener('scroll', handleScroll);
            window.scrollAttached = true;
        }
        </script>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CHATBOT WIDGET
# ══════════════════════════════════════════════════════════════════
def render_chatbot():
    # ── FAB ─────────────────────────────────────────────────────
    st.markdown("<div class='chat-fab-wrap'>", unsafe_allow_html=True)
    fab_icon = "✕" if st.session_state.chat_open else "💬"
    if st.button(fab_icon, key="chat_fab"):
        st.session_state.chat_open = not st.session_state.chat_open
        if st.session_state.chat_open and not st.session_state.chat_history:
            if GROQ_API_KEY:
                greet = groq_chat(
                    "Introduce yourself as Reel, a fun movie AI on CineRec. Ask what movie mood they're in. Max 2 sentences.",
                    max_tokens=55
                )
            else:
                greet = "Hey! 🎬 I'm **Reel**, your movie companion. Ask me anything — recommend films, hear a joke, or just chat about movies!"
            st.session_state.chat_history.append({"role": "assistant", "content": greet})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.chat_open:
        return

    # ── Build message HTML ──────────────────────────────────────
    msgs_html = ""
    for msg in st.session_state.chat_history[-12:]:
        role = msg["role"]
        text = msg["content"].replace("\n", "<br>")
        if role == "assistant":
            msgs_html += f"<div class='cmsg'><div class='cav-b'>🎬</div><div class='cbub b'>{text}</div></div>"
        else:
            msgs_html += f"<div class='cmsg u'><div class='cav-u'>👤</div><div class='cbub u'>{text}</div></div>"

    # ── Chat panel HTML ─────────────────────────────────────────
    st.markdown(f"""
    <div class='chat-panel'>
      <div class='chat-head'>
        <div class='chat-av'>🎬</div>
        <div>
          <div class='chat-hname'>Reel &nbsp;<span style='font-size:.68rem;color:var(--tx3);font-weight:400;'>AI Movie Companion</span></div>
          <div class='chat-hstat'>Online · llama-3.1-8b-instant</div>
        </div>
      </div>
      <div class='chat-msgs' id='chat-msgs-end'>{msgs_html}</div>
      <div class='chat-qrow'>
        <span class='qbtn' onclick="void(0)">🎬 Recommend</span>
        <span class='qbtn' onclick="void(0)">😂 Joke</span>
        <span class='qbtn' onclick="void(0)">🔥 Trending</span>
        <span class='qbtn' onclick="void(0)">💕 Romance?</span>
      </div>
    </div>
    <script>
      var el = document.getElementById('chat-msgs-end');
      if(el) el.scrollTop = el.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

    # ── Input row (Streamlit widgets for actual interaction) ─────
    with st.container():
        st.markdown("<div style='position:fixed;bottom:96px;right:24px;width:370px;z-index:9999;background:var(--bg-surf);border:1px solid var(--b2);border-top:none;border-radius:0 0 var(--r24) var(--r24);padding:.65rem;'>", unsafe_allow_html=True)

        user_in = st.text_input("chat_in", placeholder="Ask about movies, get jokes, explore genres...", key="chat_user_input", label_visibility="collapsed")

        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            if st.button("Send ➤", key="chat_send_btn"):
                if (user_in or "").strip():
                    umsg = user_in.strip()
                    st.session_state.chat_history.append({"role": "user", "content": umsg})
                    ctx = f"\n\nContext: User is viewing '{st.session_state.cur_movie}'." if st.session_state.cur_movie else ""
                    reply = groq_chat(umsg, st.session_state.chat_history[:-1], BOT_SYSTEM + ctx, max_tokens=130)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()
        with c2:
            if st.button("Clear", key="chat_clr"):
                st.session_state.chat_history = []
                st.rerun()
        with c3:
            if st.button("Close ✕", key="chat_close2"):
                st.session_state.chat_open = False
                st.rerun()

        # Quick reply buttons
        q_labels = ["🎬 Recommend a movie", "😂 Tell me a joke", "🔥 What's trending?", "💕 Best romance?"]
        qc = st.columns(2)
        for i, ql in enumerate(q_labels):
            with qc[i % 2]:
                if st.button(ql, key=f"qb_{i}"):
                    ctx = f"\n\nContext: User is viewing '{st.session_state.cur_movie}'." if st.session_state.cur_movie else ""
                    st.session_state.chat_history.append({"role": "user", "content": ql})
                    reply = groq_chat(ql, max_tokens=110, system=BOT_SYSTEM + ctx)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='sb-logo'>Cine<span style='color:#f54e00;'>Rec</span></div>", unsafe_allow_html=True)

    if st.button("🏠 Home", key="sb_home"):
        goto_home()

    if st.session_state.active_mood:
        mi = MOODS.get(st.session_state.active_mood, {})
        st.markdown(f"<div class='pill on'>{mi.get('emoji','')} {mi.get('label','')} Mode</div>", unsafe_allow_html=True)
        if st.button("✕ Clear Mood", key="sb_clear_mood"):
            st.session_state.active_mood = None
            st.rerun()

    st.markdown("<div class='sb-lbl'>Browse</div>", unsafe_allow_html=True)
    home_cat = st.selectbox("Category",
        ["trending","popular","top_rated","now_playing","upcoming"],
        index=0, label_visibility="collapsed")

    cat_icons = {"trending":"🔥 Trending","popular":"⭐ Popular","top_rated":"🏆 Top Rated",
                 "now_playing":"🎞️ Now Playing","upcoming":"🗓️ Upcoming"}
    st.markdown(f"<div class='pill on'>{cat_icons.get(home_cat,'')}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-lbl'>Grid</div>", unsafe_allow_html=True)
    grid_cols = st.slider("Columns", 3, 8, 5, label_visibility="collapsed")

    st.markdown("<div class='sb-lbl'>AI Status</div>", unsafe_allow_html=True)
    astat = "🟢 Connected" if GROQ_API_KEY else "🔴 No API Key"
    st.markdown(f"<div style='font-size:.75rem;color:var(--tx3);'>{astat}<br><span style='font-size:.65rem;'>Model: {GROQ_MODEL}</span></div>", unsafe_allow_html=True)
    if not GROQ_API_KEY:
        st.markdown("<div style='font-size:.68rem;color:var(--tx3);margin-top:.4rem;'>Add key to<br><code>.streamlit/secrets.toml</code></div>", unsafe_allow_html=True)

    st.markdown("""<div style='margin-top:2rem;padding-top:1rem;border-top:1px solid var(--b1);'>
        <div style='font-size:.68rem;color:var(--tx3);line-height:1.75;'>
            Powered by TMDB + Groq API<br>
            <span style='color:var(--acc);font-weight:600;'>CineRec</span> v2.0
        </div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class='page-header'>
  <div class='brand-title'>Cine<span class='brand-acc'>Rec</span></div>
  <div class='brand-tag'>Discover · Explore · Your AI Movie Companion</div>
</div>""", unsafe_allow_html=True)

# Browser scripts (Scroll detection, etc.)
render_scripts()

# ══════════════════════════════════════════════════════════════════
# VIEW: HOME
# ══════════════════════════════════════════════════════════════════
if st.session_state.view == "home":

    # ── Mood landing (no active mood yet) ───────────────────────
    if not st.session_state.active_mood:
        st.markdown("""<div class='mood-hero'>
            <div class='mood-hero-t'>What's your vibe tonight?</div>
            <div class='mood-hero-s'>Pick a mood — I'll find the perfect films</div>
        </div>""", unsafe_allow_html=True)

        mcols = st.columns(6, gap="small")
        for i, (mk, mi) in enumerate(MOODS.items()):
            with mcols[i]:
                st.markdown(f"""<div class='mood-card' style='--mc:{mi["color"]};'>
                    <span class='mood-em'>{mi["emoji"]}</span>
                    <div class='mood-lb'>{mi["label"]}</div>
                    <div class='mood-ds'>{mi["desc"]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(mi["label"], key=f"mood_{mk}", use_container_width=True):
                    st.session_state.active_mood = mk
                    # Bot intro message
                    intro = random.choice(MOOD_INTROS[mk])
                    if mk not in st.session_state.mood_shown:
                        if GROQ_API_KEY:
                            intro = groq_chat(
                                f"User picked '{mi['label']}' movies. Give ONE short funny intro sentence for this genre. Under 25 words, end with a fun emoji.",
                                max_tokens=45
                            )
                        st.session_state.chat_history.append({"role": "assistant", "content": intro})
                        st.session_state.mood_shown.add(mk)
                    st.session_state.chat_open = True
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Search bar ───────────────────────────────────────────────
    sph = "Search movies..."
    if st.session_state.active_mood:
        mi = MOODS[st.session_state.active_mood]
        st.markdown(f"""<div class='mood-banner'>
            <span style='font-size:1.35rem;'>{mi["emoji"]}</span>
            <div>
                <span class='chip'>{mi["label"]} Mode</span>
                <span class='mood-banner-txt' style='margin-left:8px;'>Showing top {mi["label"].lower()} picks · Search to explore more</span>
            </div>
        </div>""", unsafe_allow_html=True)
        sph = f"Search {mi['label'].lower()} movies or any title..."

    typed = st.text_input("SEARCH", placeholder=sph, label_visibility="visible")

    # ── Search results ───────────────────────────────────────────
    if typed.strip():
        if len(typed.strip()) < 2:
            st.markdown("<div style='color:var(--tx3);font-size:.85rem;'>Type at least 2 characters…</div>", unsafe_allow_html=True)
        else:
            with st.spinner("Searching…"):
                data, err = api_get("/tmdb/search", {"query": typed.strip()})
            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                sugs, cards = parse_search(data, typed.strip(), limit=24)
                if sugs:
                    lbls = ["— Select a title —"] + [s[0] for s in sugs]
                    sel = st.selectbox("Quick select", lbls, index=0, label_visibility="collapsed")
                    if sel != "— Select a title —":
                        l2i = {s[0]: s[1] for s in sugs}
                        goto_details(l2i[sel])
                else:
                    st.info("No suggestions found.")
                sec_hdr("🔎", f'Results for "{typed.strip()}" — {len(cards)} found')
                poster_grid(cards, cols=grid_cols, pfx="sr")
        st.stop()

    # ── Mood feed ────────────────────────────────────────────────
    if st.session_state.active_mood:
        mi = MOODS[st.session_state.active_mood]
        sec_hdr(mi["emoji"], f"{mi['label']} Movies")
        with st.spinner(f"Loading {mi['label'].lower()} picks…"):
            mdata, merr = api_get("/tmdb/search", {"query": mi["query"]})
        if not merr and mdata:
            _, mcards = parse_search(mdata, mi["query"], limit=24)
            if mcards:
                poster_grid(mcards, cols=grid_cols, pfx="mf")
            else:
                st.info("Couldn't load mood picks — try searching manually!")
        else:
            # fallback to popular
            fbdata, _ = api_get("/home", {"category": "popular", "limit": 24})
            if fbdata:
                poster_grid(fbdata, cols=grid_cols, pfx="mf_fb")
        st.stop()

    # ── Default home feed ────────────────────────────────────────
    icon_map = {"trending":"🔥","popular":"⭐","top_rated":"🏆","now_playing":"🎞️","upcoming":"🗓️"}
    sec_hdr(icon_map.get(home_cat,"🎬"), f"{home_cat.replace('_',' ').title()} Movies")
    with st.spinner("Loading…"):
        hcards, herr = api_get("/home", {"category": home_cat, "limit": 30})
    if herr or not hcards:
        st.error(f"Could not load: {herr or 'Unknown error'}")
        st.stop()
    poster_grid(hcards, cols=grid_cols, pfx="hf")

# ══════════════════════════════════════════════════════════════════
# VIEW: DETAILS
# ══════════════════════════════════════════════════════════════════
elif st.session_state.view == "details":
    tid = st.session_state.selected_id
    if not tid:
        st.warning("No movie selected.")
        if st.button("← Back"):
            goto_home()
        st.stop()

    if st.button("← Back to Home", key="back_btn"):
        goto_home()

    with st.spinner("Loading…"):
        data, err = api_get(f"/movie/id/{tid}")
    if err or not data:
        st.error(f"Could not load movie: {err or 'Unknown error'}")
        st.stop()

    # Track for chatbot context
    mv_title = data.get("title", "")
    st.session_state.cur_movie = mv_title

    # Detect genre
    gl = data.get("genres", [])
    gnames = [g["name"].lower() for g in gl]
    det_genre = "default"
    for gn in gnames:
        if any(x in gn for x in ["romance","romantic"]): det_genre = "romantic";      break
        if "action"  in gn:                               det_genre = "action";        break
        if "horror"  in gn:                               det_genre = "horror";        break
        if "comedy"  in gn:                               det_genre = "comedy";        break
        if any(x in gn for x in ["science","sci-fi"]):    det_genre = "scifi";         break
        if "drama"   in gn:                               det_genre = "motivational";  break
    st.session_state.cur_genre = det_genre

    # Bot joke — auto-opens chat with a comment about this movie
    joke = get_movie_joke(mv_title, det_genre)
    if joke:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"🎬 *{mv_title}* — {joke}"
        })
        st.session_state.chat_open = True

    # ── Hero layout ──────────────────────────────────────────────
    lcol, rcol = st.columns([1, 2.5], gap="large")
    with lcol:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown("<div class='no-post' style='height:420px;'>🎬</div>", unsafe_allow_html=True)

    with rcol:
        st.markdown("<div class='det-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='det-title'>{mv_title}</div>", unsafe_allow_html=True)

        rel  = (data.get("release_date") or "")[:4] or "—"
        rt   = data.get("runtime")
        va   = data.get("vote_average")
        imdb = round(va, 1) if va else "N/A"

        # Interactive Mini-Buddy Sidebar
        if st.session_state.get("mini_buddy_open", True):
            st.markdown(f"""
                <div class='buddy-mini' id='small-buddy-wrap'>
                    <div class='buddy-mini-hdr'>Movie Insight</div>
                    <div class='buddy-mini-stat' style='font-size:0.8rem; color:#fff; margin-bottom:10px;'>⭐️ IMDb {imdb}/10</div>
                    <div class='buddy-mini-chat'>
                        {st.session_state.mini_buddy_chat[-1]['content'] if st.session_state.mini_buddy_chat else joke}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_in, col_cl = st.columns([5, 1])
            with col_in:
                mini_in = st.text_input("Message...", key=f"mi_in_{tid}", placeholder="Ask about this movie...", label_visibility="collapsed")
            with col_cl:
                if st.button("✕", key=f"mi_cl_{tid}", help="Minimize Buddy"):
                    st.session_state.mini_buddy_open = False
                    st.rerun()
            
            if mini_in:
                if GROQ_API_KEY:
                    resp = groq_chat(f"Context: '{mv_title}'. Short answer to: {mini_in}", max_tokens=100)
                    st.session_state.mini_buddy_chat = [{"content": resp}]
                else:
                    st.session_state.mini_buddy_chat = [{"content": "I'm ready to chat, but I need an API key! 🍿"}]
                st.rerun()
        else:
            # Minimized State (Tab)
            st.markdown("<div class='buddy-tab'>💬 BUDDY</div>", unsafe_allow_html=True)
            if st.button("➕ Open Buddy", key=f"mi_op_{tid}"):
                st.session_state.mini_buddy_open = True
                st.rerun()

        meta = f"""<div style='display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:.7rem;'>
            <span class='pill'>{rel}</span>
            {"<span class='pill'>"+str(rt)+" min</span>" if rt else ""}
            {"<span class='chip'>★ "+str(round(va,1))+"</span>" if va else ""}
        </div>
        <div style='margin-bottom:.7rem;'>
            {"".join(f"<span class='pill'>{g['name']}</span>" for g in gl)}
        </div>"""
        st.markdown(meta, unsafe_allow_html=True)
        st.markdown(f"<div class='det-overview'>{data.get('overview') or 'No overview available.'}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.markdown("<div class='back-wrap'>", unsafe_allow_html=True)
        st.image(data["backdrop_url"], use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Recommendations ──────────────────────────────────────────
    title_str = (data.get("title") or "").strip()
    if title_str:
        with st.spinner("Finding recommendations…"):
            bndl, err2 = api_get("/movie/search", {"query": title_str, "tfidf_top_n": 12, "genre_limit": 12})
        if not err2 and bndl:
            tc = tfidf_to_cards(bndl.get("tfidf_recommendations"))
            gc = bndl.get("genre_recommendations", [])
            if tc:
                sec_hdr("🔗", "Similar Movies — Content Match")
                poster_grid(tc, cols=grid_cols, pfx="rt")
            if gc:
                sec_hdr("🎭", "More Like This — Genre Match")
                poster_grid(gc, cols=grid_cols, pfx="rg")
        else:
            sec_hdr("🎭", "You Might Also Like")
            with st.spinner("Loading…"):
                go, ge = api_get("/recommend/genre", {"tmdb_id": tid, "limit": 18})
            if not ge and go:
                poster_grid(go, cols=grid_cols, pfx="rfb")
            else:
                st.info("No recommendations available right now.")
    else:
        st.info("Cannot compute recommendations — no title available.")

# ══════════════════════════════════════════════════════════════════
# CHATBOT (always last — fixed bottom-right)
# ══════════════════════════════════════════════════════════════════
render_chatbot()