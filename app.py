from flask import Flask, render_template_string, request, jsonify
from ytmusicapi import YTMusic
import yt_dlp
import random

app = Flask(__name__)
yt = YTMusic()

def get_high_res_thumb(url):
    if not url:
        return ''
    if 'w60' in url or 'w120' in url:
        url = url.split('=')[0] + '=w500-h500-l90-rj'
    return url

def get_direct_audio_url(video_id):
    ydl_opts = {
        'format': 'bestaudio/best', 
        'quiet': True, 
        'no_warnings': True,
        'socket_timeout': 10
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('url', None)
        except Exception as e:
            print("Gagal ekstrak audio:", e)
            return None

ICONS = {
    "search": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>""",
    "heart": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-6.5-4.35-9-8.5A5.5 5.5 0 0 1 12 7a5.5 5.5 0 0 1 9 5.5c-2.5 4.15-9 8.5-9 8.5z"/></svg>""",
    "play": """<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.14v14l11-7-11-7z"/></svg>""",
    "pause": """<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>""",
    "next": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 5l10 7-10 7V5z"/><rect x="19" y="5" width="2" height="14" rx="1"/></svg>""",
    "prev": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 19L9 12l10-7v14z"/><rect x="3" y="5" width="2" height="14" rx="1"/></svg>""",
    "shuffle": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M16 3h5v5"/><path d="M4 20l7-7"/><path d="M21 3l-8 8"/><path d="M16 21h5v-5"/><path d="M4 4l5 5"/></svg>""",
    "repeat": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>""",
    "close": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>""",
    "more": """<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="1.8"/><circle cx="19.5" cy="12" r="1.8"/><circle cx="4.5" cy="12" r="1.8"/></svg>""",
    "home": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-5H9v5H4a1 1 0 0 1-1-1V9.5z"/></svg>""",
    "collection": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/></svg>"""
}

APP_TEMPLATE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NADA - Premium Music Player</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box;font-family:'Plus Jakarta Sans',sans-serif;-webkit-tap-highlight-color:transparent}
body{background:#080a12;color:#eef2ff;min-height:100vh;padding-bottom:145px}
:root{--accent:#7c3aed;--accent2:#06b6d4;--nada-red:#ef4444}

/* Splash Screen */
#splash-screen {
    position: fixed; inset: 0; background: #060912; z-index: 99999;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transition: opacity 0.6s ease, visibility 0.6s ease;
}
.splash-logo-container { display: flex; font-size: 42px; font-weight: 800; letter-spacing: -1px; }
.splash-na { color: #fff; transform: translateX(-40px); opacity: 0; animation: slideInNa 0.8s forwards 0.2s; }
.splash-da { color: var(--accent); transform: translateX(40px); opacity: 0; animation: slideInDa 0.8s forwards 0.2s; }
.splash-author { font-size: 13px; font-weight: 700; color: #6b7280; letter-spacing: 3px; text-transform: uppercase; margin-top: 12px; opacity: 0; animation: fadeInAuthor 0.8s forwards 0.8s; }

@keyframes slideInNa { to { transform: translateX(0); opacity: 1; } }
@keyframes slideInDa { to { transform: translateX(0); opacity: 1; } }
@keyframes fadeInAuthor { to { opacity: 1; } }

.bg{position:fixed;inset:0;background:radial-gradient(600px 400px at 20% 0%, #1e1b4b 0%, transparent 60%), radial-gradient(500px 500px at 90% 20%, #0e2a3a 0%, transparent 60%), #080a12;z-index:-1}
.header{padding:24px 20px 14px;display:flex;justify-content:space-between;align-items:center}
.logo{font-size:24px;font-weight:800;letter-spacing:-1px}.logo i{color:var(--accent);font-style:normal}

/* Foto Profil */
.profile-avatar-wrap { position: relative; width: 36px; height: 36px; cursor: pointer; }
.profile-avatar { width: 100%; height: 100%; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.2); object-fit: cover; }

.search{margin:4px 20px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(16px);border-radius:16px;padding:13px 16px;display:flex;gap:10px;align-items:center}
.search input{background:transparent;border:0;color:#fff;width:100%;outline:none;font-size:13px}
.search svg{color:#6b7280;flex-shrink:0}

/* History Box */
.history-container { padding: 0 20px 14px 20px; display: none; }
.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.clear-history { background: none; border: none; color: var(--nada-red); cursor: pointer; font-size: 11px; font-weight: 700; }
.history-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.history-tag { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); padding: 5px 12px; border-radius: 50px; font-size: 12px; color: #fff; cursor: pointer; transition: 0.2s; }

/* Playlist Creator & Grid Rapi */
.playlist-creator-box { padding: 0 20px 14px 20px; display: none; }
.playlist-form { display: flex; gap: 8px; background: rgba(255,255,255,0.03); padding: 8px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }
.playlist-input { flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 12px; color: #fff; font-size: 13px; outline: none; }
.playlist-btn { background: var(--accent); color: #fff; border: none; border-radius: 8px; padding: 0 14px; font-weight: 700; font-size: 12px; cursor: pointer; }

.playlists-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 0 20px 16px 20px; display: none; }
.playlist-card { background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border-radius: 16px; padding: 14px; border: 1px solid rgba(255,255,255,0.08); cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; justify-content: space-between; height: 100px; }
.playlist-card:hover { border-color: var(--accent2); transform: translateY(-2px); }
.playlist-card-title { font-size: 14px; font-weight: 800; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.playlist-card-count { font-size: 11px; color: #94a3b8; font-weight: 600; }
.playlist-back-bar { padding: 0 20px 12px 20px; display: none; align-items: center; justify-content: space-between; }
.back-btn { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 5px 12px; border-radius: 50px; font-size: 11px; font-weight: 700; cursor: pointer; }

.section{padding:18px 20px 10px;font-size:16px;font-weight:800;letter-spacing:-0.3px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 20px}
.card{border-radius:16px;background:linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(12px);display:flex;align-items:center;overflow:hidden;cursor:pointer;transition:0.2s}
.card:hover{transform:translateY(-1px);border-color:rgba(255,255,255,0.15)}
.card img{width:60px;height:60px;object-fit:cover;flex-shrink:0}
.card span{padding:0 10px;font-size:12px;font-weight:700;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.list{margin:0 20px 8px;border-radius:16px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.06);padding:8px 12px;display:flex;gap:12px;align-items:center}
.list img{width:50px;height:50px;border-radius:12px;object-fit:cover;cursor:pointer;flex-shrink:0}
.track-meta{flex:1;overflow:hidden;cursor:pointer}

/* Button Love SVG */
.btn-love { background: none; border: none; cursor: pointer; padding: 4px; display: flex; align-items: center; justify-content: center; }
.btn-love svg { width: 20px; height: 20px; stroke: #94a3b8; fill: none; stroke-width: 1.8; transition: 0.2s; }
.btn-love.active svg { stroke: var(--nada-red); fill: var(--nada-red); filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6)); }

/* Mini Player Pro Ramping */
.mini{position:fixed;left:12px;right:12px;bottom:68px;background:rgba(18,22,40,0.96);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:8px 12px;display:flex;gap:10px;align-items:center;box-shadow:0 15px 40px rgba(0,0,0,0.6);z-index:990}
.mini img{width:40px;height:40px;border-radius:10px;object-fit:cover;cursor:pointer;flex-shrink:0}
.mini-ctrl-btn { background: none; border: none; color: #94a3b8; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 4px; transition: 0.2s; }
.mini-ctrl-btn:hover { color: #fff; }

/* Bottom Navigation Ramping & Premium */
.nav{position:fixed;bottom:0;left:0;right:0;background:rgba(8,10,18,0.98);backdrop-filter:blur(24px);border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-around;padding:8px 0 14px;z-index:1000}
.nav div{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:9px;color:#6b7280;font-weight:600;cursor:pointer}
.nav .on{color:#fff}.nav .on svg{stroke:#fff;fill:rgba(255,255,255,0.1)}

/* Fullscreen Player Modal */
#player-modal {
    position: fixed; inset: 0; background: #060912; z-index: 9999; display: none; flex-direction: column; overflow-y: auto; padding-bottom: 30px;
}
.blur{position:fixed;inset:0;background:center/cover;filter:blur(70px) brightness(0.35) saturate(1.2);transform:scale(1.3);z-index:-2}
.mask{position:fixed;inset:0;background:linear-gradient(180deg, rgba(6,9,18,0.2) 0%, rgba(6,9,18,0.9) 75%);z-index:-1}
.top{padding:20px 22px;display:flex;justify-content:space-between;align-items:center}
.top h1{font-size:11px;letter-spacing:3px;color:#a78bfa;font-weight:800}
.cover-wrap{padding:12px 28px;display:grid;place-items:center}
.cover{width:min(80vw,300px);aspect-ratio:1/1;border-radius:28px;overflow:hidden;box-shadow:0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.1);position:relative}
.cover img{width:100%;height:100%;object-fit:cover}
.info{padding:18px 24px 0;display:flex;justify-content:space-between;align-items:center}
.info h3{font-size:18px;font-weight:800;letter-spacing:-0.4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.info p{color:#9ca3af;font-size:12px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.progress{padding:18px 24px 0}
.track{height:4px;background:rgba(255,255,255,0.12);border-radius:20px;position:relative;cursor:pointer}
.fill{height:100%;width:0%;background:linear-gradient(90deg,#fff,#a78bfa);border-radius:20px}
.knob{position:absolute;top:50%;left:0%;width:12px;height:12px;background:#fff;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 10px #fff}
.time{display:flex;justify-content:space-between;margin-top:8px;color:#6b7280;font-size:11px;font-weight:600}

/* Kontrol 5 Tombol Sempurna */
.controls{display:grid;grid-template-columns:repeat(5, 1fr);align-items:center;justify-items:center;padding:20px 10px}
.ctrl{color:#6b7280;display:grid;place-items:center;cursor:pointer;position:relative;padding:8px;background:none;border:none;}
.ctrl.active{color:var(--accent2); filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.6));}
.repeat-badge { position: absolute; font-size: 7px; font-weight: 900; color: #060912; background: #06b6d4; border-radius: 50%; width: 10px; height: 10px; display: none; align-items: center; justify-content: center; bottom: 2px; right: 2px; }
.play{width:60px;height:60px;background:#fff;color:#000;border-radius:50%;display:grid;place-items:center;box-shadow:0 10px 25px rgba(255,255,255,0.2);cursor:pointer}

/* Up Next & Lyrics */
.upnext-card { margin: 0 20px 12px; background: rgba(255,255,255,0.04); border-radius: 14px; padding: 10px 14px; border: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; gap: 10px; cursor: pointer; }
.upnext-thumb { width: 36px; height: 36px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.lyric{margin:0 20px;background:rgba(255,255,255,0.06);backdrop-filter:blur(20px);border:1px solid rgba(255,255,258,0.08);border-radius:20px;padding:16px 18px}
.lyric h4{font-size:9px;letter-spacing:2px;color:#a78bfa;font-weight:800;margin-bottom:8px}
.lyric p{font-size:12px;line-height:1.5;color:#cbd5e1;max-height:90px;overflow-y:auto;white-space:pre-line}

/* Modal Sheet Playlist */
#playlist-modal-sheet { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 20000; display: none; align-items: flex-end; backdrop-filter: blur(5px); }
.sheet-content { background: #111827; width: 100%; border-top-left-radius: 24px; border-top-right-radius: 24px; padding: 22px; border-top: 1px solid rgba(255,255,255,0.1); max-height: 70vh; overflow-y: auto; }
.sheet-title { font-size: 15px; font-weight: 800; margin-bottom: 14px; color: #fff; display: flex; justify-content: space-between; align-items: center; }
.sheet-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.sheet-item { background: rgba(255,255,255,0.04); padding: 10px 14px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; border: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; }
.sheet-new-box { display: flex; gap: 8px; margin-top: 10px; }
</style></head><body>

<!-- Splash Screen -->
<div id="splash-screen">
    <div class="splash-logo-container">
        <span class="splash-na">NA</span><span class="splash-da">DA</span>
    </div>
    <div class="splash-author">by NANDAR</div>
</div>

<div class="bg"></div>
<div class="header">
    <div class="logo">NA<i>DA</i></div>
    <!-- Foto Profil -->
    <div class="profile-avatar-wrap" onclick="document.getElementById('profile-file-input').click()" title="Ganti Foto Profil">
        <img id="user-profile-img" src="https://i.pravatar.cc/80?img=12" class="profile-avatar">
        <input type="file" id="profile-file-input" accept="image/*" style="display:none" onchange="autoCropAndSaveProfile(event)">
    </div>
</div>

<!-- Search Bar -->
<div class="search" id="search-box-wrap">
    ICON_SEARCH <input type="text" id="query-input" placeholder="Cari lagu atau penyanyi favoritmu..." oninput="performSearchDebounced()" onfocus="showHistory()">
</div>

<!-- Riwayat Pencarian -->
<div class="history-container" id="history-container">
    <div class="history-header"><span>Riwayat Pencarian</span><button class="clear-history" onclick="clearHistory()">Hapus</button></div>
    <div class="history-tags" id="history-tags"></div>
</div>

<!-- Playlist Creator & Koleksi -->
<div class="playlist-creator-box" id="playlist-creator-box">
    <div class="playlist-form">
        <input type="text" id="new-playlist-name" class="playlist-input" placeholder="Buat nama playlist baru...">
        <button class="playlist-btn" onclick="createCustomPlaylist()">Buat</button>
    </div>
</div>

<div class="playlists-grid" id="playlists-grid"></div>
<div class="playlist-back-bar" id="playlist-back-bar">
    <span id="active-playlist-title-header" style="font-weight: 800; font-size: 15px;">Playlist</span>
    <button class="back-btn" onclick="backToPlaylistsGrid()">← Kembali</button>
</div>

<!-- Grid Viral (Beranda) -->
<div class="section" id="viral-section-title">Diputar untukmu 🔥</div>
<div class="grid" id="quick-grid">
    {% for s in results[:4] %}
    <div class="card" onclick="playSongOnly('{{ s.videoId }}', '{{ s.title | replace("'", "") }}', '{{ s.artist | replace("'", "") }}', '{{ s.thumb }}')">
        <img src="{{ s.thumb }}">
        <span>{{ s.title }}</span>
    </div>
    {% endfor %}
</div>

<div class="section" id="section-title">Rekomendasi terpopuler</div>

<!-- Track List -->
<div id="track-list-container">
    {% for s in results %}
    <div class="list" id="track-item-{{ s.videoId }}">
        <img src="{{ s.thumb }}" onclick="selectSongAndOpen('{{ s.videoId }}', '{{ s.title | replace("'", "") }}', '{{ s.artist | replace("'", "") }}', '{{ s.thumb }}')" title="Buka Pemutar">
        <div class="track-meta" onclick="playSongOnly('{{ s.videoId }}', '{{ s.title | replace("'", "") }}', '{{ s.artist | replace("'", "") }}', '{{ s.thumb }}')">
            <div style="font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ s.title }}</div>
            <div style="color:#9ca3af;font-size:11px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ s.artist }}</div>
        </div>
        <button class="btn-love" id="btn-add-{{ s.videoId }}" onclick="openPlaylistModalSheet('{{ s.videoId }}', '{{ s.title | replace("'", "") }}', '{{ s.artist | replace("'", "") }}', '{{ s.thumb }}', event)">ICON_HEART</button>
    </div>
    {% endfor %}
</div>

<!-- Mini Player Pro Ramping & Aman -->
<div class="mini" id="mini-player" style="display: none;">
    <img id="mini-thumb" src="" onclick="openFullscreenPlayer()">
    <div style="flex:1;overflow:hidden;cursor:pointer" onclick="openFullscreenPlayer()">
        <div style="font-weight:700;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" id="mini-title">Judul Lagu</div>
        <div style="color:#9ca3af;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" id="mini-artist">Artis</div>
    </div>
    <button class="btn-love" id="mini-like-btn" onclick="openPlaylistModalSheet(currentSongData.videoId, currentSongData.title, currentSongData.artist, currentSongData.thumb, event)">ICON_HEART</button>
    <button class="mini-ctrl-btn" onclick="playPrev()" title="Sebelumnya">ICON_PREV</button>
    <button class="mini-ctrl-btn" onclick="togglePlay(event)" id="mini-play-btn" title="Play/Pause">ICON_PAUSE</button>
    <button class="mini-ctrl-btn" onclick="playNext()" title="Berikutnya">ICON_NEXT</button>
</div>

<!-- Bottom Navigation Lebih Ramping & Premium -->
<div class="nav">
    <div class="on" id="nav-beranda" onclick="switchTab('all')">ICON_HOME<span>Beranda</span></div>
    <div id="nav-cari" onclick="focusSearch()">ICON_SEARCH<span>Cari</span></div>
    <div id="nav-koleksi" onclick="switchTab('playlist')">ICON_COLLECTION<span>Koleksi</span></div>
</div>

<!-- Fullscreen Player Modal -->
<div id="player-modal">
    <div class="blur" id="modal-blur"></div><div class="mask"></div>
    <div class="top"><div onclick="closeFullscreenPlayer()" style="cursor:pointer">ICON_CLOSE</div><h1>PEMUTAR NADA PREMIUM</h1><div>ICON_MORE</div></div>
    <div class="cover-wrap"><div class="cover"><img id="big-art" src=""></div></div>
    <div class="info">
        <div style="overflow:hidden">
            <h3 id="big-title">-</h3>
            <p id="big-artist">-</p>
        </div>
        <button class="btn-love" id="fullscreen-like-btn" onclick="openPlaylistModalSheet(currentSongData.videoId, currentSongData.title, currentSongData.artist, currentSongData.thumb, event)" style="transform:scale(1.2)">ICON_HEART</button>
    </div>
    <div class="progress">
        <div class="track" id="progress-container" onclick="seekAudio(event)">
            <div class="fill" id="fill"></div>
            <div class="knob" id="knob"></div>
        </div>
        <div class="time"><span id="cur">0:00</span><span id="dur">0:00</span></div>
    </div>
    <!-- Kontrol 5 Tombol Sempurna -->
    <div class="controls">
        <button class="ctrl" id="shuffle-btn" onclick="toggleShuffle()" title="Acak">ICON_SHUFFLE</button>
        <button class="ctrl active" onclick="playPrev()" title="Sebelumnya">ICON_PREV</button>
        <div class="play" id="btn" onclick="togglePlay()">ICON_PAUSE</div>
        <button class="ctrl active" onclick="playNext()" title="Berikutnya">ICON_NEXT</button>
        <button class="ctrl" id="repeat-btn" onclick="toggleRepeat()" title="Ulangi">
            ICON_REPEAT
            <div class="repeat-badge" id="repeat-one-badge">1</div>
        </button>
    </div>
    <div class="upnext-card" onclick="playNext()">
        <img id="upnext-thumb" src="" class="upnext-thumb">
        <div style="overflow:hidden;flex:1">
            <div style="font-size:8px;font-weight:800;color:#06b6d4;letter-spacing:1px;margin-bottom:2px">LAGU SELANJUTNYA</div>
            <div style="font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" id="upnext-title">-</div>
            <div style="font-size:10px;color:#9ca3af;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" id="upnext-artist">-</div>
        </div>
    </div>
    <div class="lyric">
        <h4>LIRIK PREMIUM • SINKRON</h4>
        <p id="lyrics-content">Memuat lirik otomatis...</p>
    </div>
</div>

<!-- Modal Playlist Sheet -->
<div id="playlist-modal-sheet" onclick="closePlaylistModalSheet()">
    <div class="sheet-content" onclick="event.stopPropagation()">
        <div class="sheet-title">
            <span>Simpan ke Playlist</span>
            <button onclick="closePlaylistModalSheet()" style="background:none; border:none; color:#fff; font-size:18px; cursor:pointer;">✕</button>
        </div>
        <div class="sheet-list" id="sheet-playlist-options"></div>
        <div class="sheet-new-box">
            <input type="text" id="sheet-new-name" class="playlist-input" placeholder="Nama playlist baru...">
            <button class="playlist-btn" onclick="createAndAddToPlaylistFromSheet()">Tambah</button>
        </div>
    </div>
</div>

<audio id="audio-player" preload="auto"></audio>

<script>
    let playlist = JSON.parse(localStorage.getItem('nada_playlist')) || [];
    let customPlaylists = JSON.parse(localStorage.getItem('nada_custom_playlists')) || { "Semua Favorit": [] };
    let activePlaylistTab = null;
    let searchHistory = JSON.parse(localStorage.getItem('nada_search_history')) || [];
    let baseQueue = [];
    let currentQueue = [];
    let currentIndex = 0;
    let currentSongData = {};
    let audioCache = {};
    let searchTimeout = null;
    let repeatMode = 0;
    let shuffleMode = false;
    let targetSongForModal = null;

    const audio = document.getElementById('audio-player');

    window.addEventListener('load', () => {
        setTimeout(() => {
            let splash = document.getElementById('splash-screen');
            if(splash) {
                splash.style.opacity = '0';
                setTimeout(() => splash.style.display = 'none', 600);
            }
        }, 1600);

        let savedPic = localStorage.getItem('nada_profile_pic');
        if(savedPic) {
            document.getElementById('user-profile-img').src = savedPic;
        }
    });

    // Auto-Crop Cerdas & Rapi Langsung Simpan
    function autoCropAndSaveProfile(event) {
        let file = event.target.files[0];
        if (!file) return;

        let reader = new FileReader();
        reader.onload = function(e) {
            let img = new Image();
            img.onload = function() {
                let canvas = document.createElement('canvas');
                let ctx = canvas.getContext('2d');
                let size = 200;
                canvas.width = size;
                canvas.height = size;

                let minSide = Math.min(img.width, img.height);
                let startX = (img.width - minSide) / 2;
                let startY = (img.height - minSide) / 2;

                ctx.drawImage(img, startX, startY, minSide, minSide, 0, 0, size, size);
                let compressedDataUrl = canvas.toDataURL('image/jpeg', 0.8);

                document.getElementById('user-profile-img').src = compressedDataUrl;
                try {
                    localStorage.setItem('nada_profile_pic', compressedDataUrl);
                } catch(err) {
                    alert("Ukuran gambar terlalu besar!");
                }
            }
            img.src = e.target.result;
        }
        reader.readAsDataURL(file);
    }

    // Toggle Shuffle & Repeat (Eksklusif)
    function toggleShuffle() {
        shuffleMode = !shuffleMode;
        const sBtn = document.getElementById('shuffle-btn');
        const rBtn = document.getElementById('repeat-btn');
        const badge = document.getElementById('repeat-one-badge');

        if (shuffleMode) {
            sBtn.classList.add('active');
            repeatMode = 0;
            rBtn.classList.remove('active');
            badge.style.display = 'none';
            let currentPlaying = currentQueue[currentIndex];
            currentQueue = [...baseQueue].sort(() => Math.random() - 0.5);
            if(currentPlaying) {
                currentIndex = currentQueue.findIndex(s => s.videoId === currentPlaying.videoId);
                if(currentIndex === -1) { currentIndex = 0; currentQueue.unshift(currentPlaying); }
            }
        } else {
            sBtn.classList.remove('active');
            currentQueue = [...baseQueue];
            if(currentSongData.videoId) {
                currentIndex = currentQueue.findIndex(s => s.videoId === currentSongData.videoId);
                if(currentIndex === -1) currentIndex = 0;
            }
        }
        updateUpNextCard();
    }

    function toggleRepeat() {
        const rBtn = document.getElementById('repeat-btn');
        const sBtn = document.getElementById('shuffle-btn');
        const badge = document.getElementById('repeat-one-badge');
        
        repeatMode = (repeatMode + 1) % 3;
        
        if (repeatMode > 0) {
            shuffleMode = false;
            sBtn.classList.remove('active');
            currentQueue = [...baseQueue];
            if(currentSongData.videoId) {
                currentIndex = currentQueue.findIndex(s => s.videoId === currentSongData.videoId);
                if(currentIndex === -1) currentIndex = 0;
            }
            updateUpNextCard();
        }

        if (repeatMode === 0) {
            rBtn.classList.remove('active');
            badge.style.display = 'none';
        } else if (repeatMode === 1) { 
            rBtn.classList.add('active');
            badge.style.display = 'none';
        } else if (repeatMode === 2) { 
            rBtn.classList.add('active');
            badge.style.display = 'flex';
        }
    }

    audio.addEventListener('ended', () => {
        if (repeatMode === 2) {
            audio.currentTime = 0;
            audio.play();
        } else {
            playNext();
        }
    });

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('play', () => updatePlayIcons(true));
    audio.addEventListener('pause', () => updatePlayIcons(false));

    document.addEventListener("DOMContentLoaded", () => {
        {% for s in results %}
        baseQueue.push({
            videoId: "{{ s.videoId }}",
            title: "{{ s.title | replace("'", "") }}",
            artist: "{{ s.artist | replace("'", "") }}",
            thumb: "{{ s.thumb }}"
        });
        {% endfor %}
        currentQueue = [...baseQueue];
        updateAllAddButtons();
        renderHistoryTags();
        updateUpNextCard();
    });

    function switchTab(tab) {
        document.querySelectorAll('.nav div').forEach(n => n.classList.remove('on'));
        let quickGrid = document.getElementById('quick-grid');
        let viralTitle = document.getElementById('viral-section-title');
        let creatorBox = document.getElementById('playlist-creator-box');
        let playlistsGrid = document.getElementById('playlists-grid');
        let backBar = document.getElementById('playlist-back-bar');
        let trackList = document.getElementById('track-list-container');
        
        if(tab === 'playlist') {
            document.getElementById('nav-koleksi').classList.add('on');
            document.getElementById('history-container').style.display = 'none';
            quickGrid.style.display = 'none';
            viralTitle.style.display = 'none';
            creatorBox.style.display = 'block';
            activePlaylistTab = null;
            renderPlaylistsGrid();
        } else {
            document.getElementById('nav-beranda').classList.add('on');
            quickGrid.style.display = 'grid';
            viralTitle.style.display = 'block';
            creatorBox.style.display = 'none';
            playlistsGrid.style.display = 'none';
            backBar.style.display = 'none';
            trackList.style.display = 'block';
            performSearch();
        }
    }

    function focusSearch() {
        document.querySelectorAll('.nav div').forEach(n => n.classList.remove('on'));
        document.getElementById('nav-cari').classList.add('on');
        let input = document.getElementById('query-input');
        input.focus();
        showHistory();
    }

    function showHistory() {
        if (searchHistory.length > 0) {
            document.getElementById('history-container').style.display = 'block';
        }
    }

    function addSearchHistory(query) {
        if(!query.trim()) return;
        searchHistory = searchHistory.filter(item => item.toLowerCase() !== query.toLowerCase());
        searchHistory.unshift(query);
        if (searchHistory.length > 8) searchHistory.pop();
        localStorage.setItem('nada_search_history', JSON.stringify(searchHistory));
        renderHistoryTags();
    }

    function renderHistoryTags() {
        let container = document.getElementById('history-tags');
        let html = '';
        searchHistory.forEach(item => {
            html += `<div class="history-tag" onclick="selectHistory('${item}')">${item}</div>`;
        });
        container.innerHTML = html;
    }

    function selectHistory(query) {
        document.getElementById('query-input').value = query;
        document.getElementById('history-container').style.display = 'none';
        performSearch();
    }

    function clearHistory() {
        searchHistory = [];
        localStorage.removeItem('nada_search_history');
        document.getElementById('history-container').style.display = 'none';
    }

    function createCustomPlaylist() {
        let name = document.getElementById('new-playlist-name').value.trim();
        if(!name) return;
        if(!customPlaylists[name]) {
            customPlaylists[name] = [];
            localStorage.setItem('nada_custom_playlists', JSON.stringify(customPlaylists));
            document.getElementById('new-playlist-name').value = '';
            renderPlaylistsGrid();
        }
    }

    function renderPlaylistsGrid() {
        document.getElementById('playlists-grid').style.display = 'grid';
        document.getElementById('playlist-back-bar').style.display = 'none';
        document.getElementById('track-list-container').style.display = 'none';
        document.getElementById('section-title').innerText = "Koleksi Playlist Kamu";

        let grid = document.getElementById('playlists-grid');
        let html = '';
        for(let plName in customPlaylists) {
            let count = customPlaylists[plName].length;
            html += `
            <div class="playlist-card" onclick="openPlaylistDetail('${plName}')">
                <div class="playlist-card-title">🎵 ${plName}</div>
                <div class="playlist-card-count">${count} Lagu</div>
            </div>`;
        }
        grid.innerHTML = html;
    }

    function openPlaylistDetail(plName) {
        activePlaylistTab = plName;
        document.getElementById('playlists-grid').style.display = 'none';
        document.getElementById('playlist-back-bar').style.display = 'flex';
        document.getElementById('active-playlist-title-header').innerText = `Playlist: ${plName}`;
        document.getElementById('track-list-container').style.display = 'block';
        renderPlaylistTracks();
    }

    function backToPlaylistsGrid() {
        renderPlaylistsGrid();
    }

    function openPlaylistModalSheet(videoId, title, artist, thumb, event) {
        if(event) event.stopPropagation();
        targetSongForModal = { videoId, title, artist, thumb };
        
        let listContainer = document.getElementById('sheet-playlist-options');
        let html = '';
        for(let plName in customPlaylists) {
            let isAdded = customPlaylists[plName].some(s => s.videoId === videoId);
            html += `
            <div class="sheet-item" onclick="toggleSongInPlaylist('${plName}')">
                <span>${plName}</span>
                <span style="color: ${isAdded ? 'var(--accent2)' : '#94a3b8'}; font-weight: 800;">${isAdded ? '✔ Ditambahkan' : '+ Tambah'}</span>
            </div>`;
        }
        listContainer.innerHTML = html;
        document.getElementById('playlist-modal-sheet').style.display = 'flex';
    }

    function closePlaylistModalSheet() {
        document.getElementById('playlist-modal-sheet').style.display = 'none';
    }

    function toggleSongInPlaylist(plName) {
        if(!targetSongForModal) return;
        let { videoId, title, artist, thumb } = targetSongForModal;
        let songObj = { videoId, title, artist, thumb };
        
        let exists = customPlaylists[plName].some(s => s.videoId === videoId);
        if(!exists) {
            customPlaylists[plName].push(songObj);
        } else {
            customPlaylists[plName] = customPlaylists[plName].filter(s => s.videoId !== videoId);
        }
        
        let allFavs = [];
        for(let k in customPlaylists) {
            if(k !== 'Semua Favorit') {
                customPlaylists[k].forEach(s => {
                    if(!allFavs.some(x => x.videoId === s.videoId)) allFavs.push(s);
                });
            }
        }
        customPlaylists['Semua Favorit'] = allFavs;
        playlist = allFavs;
        
        localStorage.setItem('nada_playlist', JSON.stringify(playlist));
        localStorage.setItem('nada_custom_playlists', JSON.stringify(customPlaylists));
        
        openPlaylistModalSheet(videoId, title, artist, thumb, null);
        updateAllAddButtons();
        if(activePlaylistTab) renderPlaylistTracks();
    }

    function createAndAddToPlaylistFromSheet() {
        let name = document.getElementById('sheet-new-name').value.trim();
        if(!name || !targetSongForModal) return;
        if(!customPlaylists[name]) {
            customPlaylists[name] = [];
        }
        document.getElementById('sheet-new-name').value = '';
        toggleSongInPlaylist(name);
    }

    function performSearchDebounced() {
        clearTimeout(searchTimeout);
        showHistory();
        searchTimeout = setTimeout(() => {
            performSearch();
        }, 400);
    }

    function performSearch() {
        let query = document.getElementById('query-input').value.trim();
        let quickGrid = document.getElementById('quick-grid');
        let viralTitle = document.getElementById('viral-section-title');
        
        if (query) {
            quickGrid.style.display = 'none';
            viralTitle.style.display = 'none';
            addSearchHistory(query);
        } else {
            quickGrid.style.display = 'grid';
            viralTitle.style.display = 'block';
        }

        fetch('/api/search?query=' + encodeURIComponent(query))
            .then(res => res.json())
            .then(data => {
                baseQueue = data;
                currentQueue = shuffleMode ? [...baseQueue].sort(() => Math.random() - 0.5) : [...baseQueue];
                renderTrackList(data, query ? "Hasil Pencarian: " + query : "Rekomendasi terpopuler");
                highlightActiveTrack();
                updateUpNextCard();
            });
    }

    function renderTrackList(data, titleText) {
        let html = '';
        if (data.length === 0) {
            html = '<p style="text-align: center; color: #94a3b8; margin-top: 40px; font-size: 13px;">Tidak ada lagu ditemukan.</p>';
        } else {
            data.forEach(song => {
                let isAdded = playlist.some(p => p.videoId === song.videoId);
                let isPlaying = currentSongData.videoId === song.videoId ? 'playing' : '';
                html += `
                <div class="list ${isPlaying}" id="track-item-${song.videoId}">
                    <img src="${song.thumb}" onclick="selectSongAndOpen('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}')" title="Buka Pemutar">
                    <div class="track-meta" onclick="playSongOnly('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}')">
                        <div style="font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${song.title}</div>
                        <div style="color:#9ca3af;font-size:11px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${song.artist}</div>
                    </div>
                    <button class="btn-love ${isAdded ? 'active' : ''}" id="btn-add-${song.videoId}" onclick="openPlaylistModalSheet('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}', event)">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-6.5-4.35-9-8.5A5.5 5.5 0 0 1 12 7a5.5 5.5 0 0 1 9 5.5c-2.5 4.15-9 8.5-9 8.5z"/></svg>
                    </button>
                </div>`;
            });
        }
        document.getElementById('track-list-container').innerHTML = html;
        document.getElementById('section-title').innerText = titleText;
    }

    function playSongOnly(videoId, title, artist, thumb) {
        currentSongData = { videoId, title, artist, thumb };
        let foundIdx = currentQueue.findIndex(s => s.videoId === videoId);
        if(foundIdx !== -1) currentIndex = foundIdx;

        document.getElementById('mini-player').style.display = 'flex';
        document.getElementById('mini-thumb').src = thumb;
        document.getElementById('mini-title').innerText = title;
        document.getElementById('mini-artist').innerText = artist;

        document.getElementById('big-art').src = thumb;
        document.getElementById('modal-blur').style.backgroundImage = `url('${thumb}')`;
        document.getElementById('big-title').innerText = title;
        document.getElementById('big-artist').innerText = artist;

        updateLikeButtonsState();
        highlightActiveTrack();
        updateUpNextCard();
        playAudioDirect(videoId);

        document.getElementById('lyrics-content').innerText = "Memuat lirik otomatis...";
        fetch('/api/lyrics?videoId=' + videoId + '&title=' + encodeURIComponent(title) + '&artist=' + encodeURIComponent(artist))
            .then(res => res.json())
            .then(data => {
                document.getElementById('lyrics-content').innerText = data.lyrics;
            });
    }

    function selectSongAndOpen(videoId, title, artist, thumb) {
        playSongOnly(videoId, title, artist, thumb);
        openFullscreenPlayer();
    }

    function updateUpNextCard() {
        if (currentQueue.length > 0) {
            let nextIdx = (currentIndex + 1) % currentQueue.length;
            let nextSong = currentQueue[nextIdx];
            if (nextSong) {
                document.getElementById('upnext-thumb').src = nextSong.thumb;
                document.getElementById('upnext-title').innerText = nextSong.title;
                document.getElementById('upnext-artist').innerText = nextSong.artist;
            }
        }
    }

    function highlightActiveTrack() {
        document.querySelectorAll('.list').forEach(el => el.classList.remove('playing'));
        if(currentSongData.videoId) {
            let activeEl = document.getElementById('track-item-' + currentSongData.videoId);
            if(activeEl) activeEl.classList.add('playing');
        }
    }

    function playAudioDirect(videoId) {
        // Fix mutlak agar audio sebelumnya tidak nyangkut / dobel suara
        audio.pause();
        audio.currentTime = 0;
        audio.src = "";

        if (audioCache[videoId]) {
            audio.src = audioCache[videoId];
            audio.play().catch(e => console.log("Auto-play blocked/interrupted:", e));
            preloadNextAudio();
        } else {
            fetch('/api/stream?videoId=' + videoId)
                .then(res => res.json())
                .then(data => {
                    if (data.url) {
                        audioCache[videoId] = data.url;
                        audio.src = data.url;
                        audio.play().catch(e => console.log("Auto-play blocked/interrupted:", e));
                        preloadNextAudio();
                    }
                });
        }
    }

    function preloadNextAudio() {
        if (currentQueue.length > 0) {
            let nextIdx = (currentIndex + 1) % currentQueue.length;
            let nextSong = currentQueue[nextIdx];
            if (nextSong && !audioCache[nextSong.videoId]) {
                fetch('/api/stream?videoId=' + nextSong.videoId)
                    .then(res => res.json())
                    .then(data => {
                        if (data.url) audioCache[nextSong.videoId] = data.url;
                    });
            }
        }
    }

    function togglePlay(event) {
        if(event) event.stopPropagation();
        if (!audio.src) return;
        if (audio.paused) {
            audio.play();
        } else {
            audio.pause();
        }
    }

    function updatePlayIcons(isPlaying) {
        const pauseSVG = `ICON_PAUSE`;
        const playSVG = `ICON_PLAY`;
        document.getElementById('btn').innerHTML = isPlaying ? pauseSVG : playSVG;
        document.getElementById('mini-play-btn').innerHTML = isPlaying ? pauseSVG : playSVG;
    }

    function playPrev() {
        if (currentQueue.length > 0) {
            currentIndex = (currentIndex - 1 + currentQueue.length) % currentQueue.length;
            let prev = currentQueue[currentIndex];
            playSongOnly(prev.videoId, prev.title, prev.artist, prev.thumb);
        }
    }

    function playNext() {
        if (currentQueue.length > 0) {
            currentIndex = (currentIndex + 1) % currentQueue.length;
            let next = currentQueue[currentIndex];
            playSongOnly(next.videoId, next.title, next.artist, next.thumb);
        }
    }

    function updateProgress() {
        if(audio.duration) {
            let pct = (audio.currentTime / audio.duration) * 100;
            document.getElementById('fill').style.width = pct + '%';
            document.getElementById('knob').style.left = pct + '%';
            document.getElementById('cur').textContent = formatTime(audio.currentTime);
            document.getElementById('dur').textContent = formatTime(audio.duration);
        }
    }

    function formatTime(sec) {
        let mins = Math.floor(sec / 60);
        let secs = Math.floor(sec % 60);
        if (secs < 10) secs = '0' + secs;
        return mins + ':' + secs;
    }

    function seekAudio(event) {
        let container = document.getElementById('progress-container');
        let rect = container.getBoundingClientRect();
        let clickX = event.clientX - rect.left;
        let width = rect.width;
        if(audio.duration && width > 0) {
            let percent = Math.max(0, Math.min(1, clickX / width));
            audio.currentTime = percent * audio.duration;
        }
    }

    function updateLikeButtonsState() {
        let isAdded = playlist.some(p => p.videoId === currentSongData.videoId);
        let miniBtn = document.getElementById('mini-like-btn');
        let fullBtn = document.getElementById('fullscreen-like-btn');
        
        if(miniBtn) miniBtn.classList.toggle('active', isAdded);
        if(fullBtn) fullBtn.classList.toggle('active', isAdded);
    }

    function updateAllAddButtons() {
        currentQueue.forEach(song => {
            let btn = document.getElementById('btn-add-' + song.videoId);
            if (btn) {
                let isAdded = playlist.some(p => p.videoId === song.videoId);
                btn.classList.toggle('active', isAdded);
            }
        });
    }

    function renderPlaylistTracks() {
        let songs = customPlaylists[activePlaylistTab] || [];
        baseQueue = [...songs];
        currentQueue = shuffleMode ? [...baseQueue].sort(() => Math.random() - 0.5) : [...baseQueue];
        let html = '';
        if (songs.length === 0) {
            html = '<p style="text-align: center; color: #94a3b8; margin-top: 40px; font-size: 13px;">Belum ada lagu di playlist ini.</p>';
        } else {
            songs.forEach(song => {
                let isPlaying = currentSongData.videoId === song.videoId ? 'playing' : '';
                let isAdded = playlist.some(p => p.videoId === song.videoId);
                html += `
                <div class="list ${isPlaying}" id="track-item-${song.videoId}">
                    <img src="${song.thumb}" onclick="selectSongAndOpen('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}')" title="Buka Pemutar">
                    <div class="track-meta" onclick="playSongOnly('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}')">
                        <div style="font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${song.title}</div>
                        <div style="color:#9ca3af;font-size:11px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${song.artist}</div>
                    </div>
                    <button class="btn-love ${isAdded ? 'active' : ''}" onclick="openPlaylistModalSheet('${song.videoId}', '${song.title}', '${song.artist}', '${song.thumb}', event)">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-6.5-4.35-9-8.5A5.5 5.5 0 0 1 12 7a5.5 5.5 0 0 1 9 5.5c-2.5 4.15-9 8.5-9 8.5z"/></svg>
                    </button>
                </div>`;
            });
        }
        document.getElementById('track-list-container').innerHTML = html;
    }

    function openFullscreenPlayer() {
        document.getElementById('player-modal').style.display = 'flex';
    }

    function closeFullscreenPlayer() {
        document.getElementById('player-modal').style.display = 'none';
    }
</script>
</body></html>
"""

def inject(s):
    return (s.replace("ICON_SEARCH", ICONS["search"])
             .replace("ICON_HEART", ICONS["heart"])
             .replace("ICON_PLAY", ICONS["play"])
             .replace("ICON_PAUSE", ICONS["pause"])
             .replace("ICON_NEXT", ICONS["next"])
             .replace("ICON_PREV", ICONS["prev"])
             .replace("ICON_SHUFFLE", ICONS["shuffle"])
             .replace("ICON_REPEAT", ICONS["repeat"])
             .replace("ICON_CLOSE", ICONS["close"])
             .replace("ICON_MORE", ICONS["more"])
             .replace("ICON_HOME", ICONS["home"])
             .replace("ICON_COLLECTION", ICONS["collection"]))

@app.route('/', methods=['GET'])
def home():
    query = request.args.get('query', '')
    results = []
    try:
        search_query = query if query else "Indonesia Viral Hits"
        search_res = yt.search(search_query, filter="songs")
        random.shuffle(search_res)
        for s in search_res[:15]:
            thumbnails = s.get('thumbnails', [])
            thumb_url = get_high_res_thumb(thumbnails[0]['url']) if thumbnails else ''
            results.append({
                'videoId': s.get('videoId'),
                'title': s.get('title'),
                'artist': s.get('artists')[0]['name'] if s.get('artists') else 'Unknown',
                'thumb': thumb_url
            })
    except Exception as e:
        print("Error:", e)
    return render_template_string(inject(APP_TEMPLATE), results=results, query=query)

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query', '')
    try:
        search_query = query if query else "Indonesia Viral Hits"
        search_res = yt.search(search_query, filter="songs")
        if not query:
            random.shuffle(search_res)
        data = []
        for s in search_res[:15]:
            thumbnails = s.get('thumbnails', [])
            thumb_url = get_high_res_thumb(thumbnails[0]['url']) if thumbnails else ''
            data.append({
                'videoId': s.get('videoId'),
                'title': s.get('title'),
                'artist': s.get('artists')[0]['name'] if s.get('artists') else 'Unknown',
                'thumb': thumb_url
            })
        return jsonify(data)
    except Exception as e:
        return jsonify([])

@app.route('/api/stream', methods=['GET'])
def api_stream():
    video_id = request.args.get('videoId')
    url = get_direct_audio_url(video_id)
    return jsonify({'url': url})

@app.route('/api/lyrics', methods=['GET'])
def api_lyrics():
    video_id = request.args.get('videoId')
    title = request.args.get('title', 'Lagu')
    artist = request.args.get('artist', 'Artis')
    
    lyrics_text = f"Lirik lagu {title} oleh {artist}.\n\nKualitas Audio: Spatial Audio / 24-bit • Sinkronisasi Otomatis."
    try:
        watch = yt.get_watch_playlist(video_id)
        lyrics_id = watch.get('lyrics')
        if lyrics_id:
            lyrics_data = yt.get_lyrics(lyrics_id)
            if lyrics_data and 'lyrics' in lyrics_data:
                lyrics_text = lyrics_data['lyrics']
    except Exception as e:
        print("Pencarian lirik otomatis:", e)
        
    return jsonify({'lyrics': lyrics_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
