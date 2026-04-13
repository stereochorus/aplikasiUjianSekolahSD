#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian IPAS Kelas 6 SD
- Langsung masuk soal (tanpa input nama/kelas)
- 45 PG + 5 Esai, diacak setiap sesi
- Satu soal per tampilan, navigasi prev/next
- Jawaban dapat diubah
- Kode keluar guru: pinewood62
"""

import tkinter as tk
from tkinter import ttk
import ctypes, ctypes.wintypes
import threading, random, os, sys
from datetime import datetime

WAKTU_MENIT = 90
HASIL_DIR   = os.path.dirname(os.path.abspath(__file__))
NUM_PG      = 45
NUM_ESAI    = 5

# ─────────────────────────────────────────────────────────────
#  WINDOWS KEYBOARD HOOK
# ─────────────────────────────────────────────────────────────
_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104

BLOCKED_VK = {0x5B, 0x5C, 0x09, 0x73, 0x1B, 0x2C}   # Win,Tab,F4,Esc,PrtScr

class _KBD(ctypes.Structure):
    _fields_ = [("vkCode", ctypes.wintypes.DWORD),
                ("scanCode", ctypes.wintypes.DWORD),
                ("flags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

_HPROC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int,
                           ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
_hook_id = None
_hook_cb = None

def _kb(nCode, wParam, lParam):
    if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
        if ctypes.cast(lParam, ctypes.POINTER(_KBD)).contents.vkCode in BLOCKED_VK:
            return 1
    return _u32.CallNextHookEx(_hook_id, nCode, wParam, lParam)

def _hook_thread():
    global _hook_id, _hook_cb
    _hook_cb = _HPROC(_kb)
    _hook_id = _u32.SetWindowsHookExA(WH_KEYBOARD_LL, _hook_cb,
                                       _k32.GetModuleHandleW(None), 0)
    msg = ctypes.wintypes.MSG()
    while _u32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
        _u32.TranslateMessage(ctypes.byref(msg))
        _u32.DispatchMessageA(ctypes.byref(msg))

def start_hook():
    threading.Thread(target=_hook_thread, daemon=True).start()

def stop_hook():
    if _hook_id:
        _u32.UnhookWindowsHookEx(_hook_id)

# ─────────────────────────────────────────────────────────────
#  WARNA (tema terang & nyaman)
# ─────────────────────────────────────────────────────────────
C = {
    "page":             "#f0f4f8",
    "topbar":           "#14532d",
    "topbar_text":      "#ffffff",
    "nav_bg":           "#ffffff",
    "nav_todo":         "#dde3ec",
    "nav_todo_fg":      "#64748b",
    "nav_done":         "#22c55e",
    "nav_done_fg":      "#ffffff",
    "nav_curr":         "#f59e0b",
    "nav_curr_fg":      "#ffffff",
    "nav_esai_done":    "#8b5cf6",
    "nav_esai_done_fg": "#ffffff",
    "card":             "#ffffff",
    "q_pg_accent":      "#16a34a",
    "q_esai_accent":    "#7c3aed",
    "q_text":           "#1e293b",
    "q_sub":            "#64748b",
    "opt_bg":           "#f1f5f9",
    "opt_fg":           "#94a3b8",
    "opt_letter_bg":    "#e2e8f0",
    "opt_letter_fg":    "#64748b",
    "opt_sel_bg":       "#16a34a",
    "opt_sel_fg":       "#ffffff",
    "opt_sel_lbg":      "#15803d",
    "opt_hover":        "#f0fdf4",
    "btn_prev":         "#94a3b8",
    "btn_next":         "#16a34a",
    "btn_submit":       "#2563eb",
    "btn_exit":         "#e94560",
    "btn_text":         "#ffffff",
    "timer_ok":         "#22c55e",
    "timer_warn":       "#f59e0b",
    "timer_crit":       "#ef4444",
    "esai_area":        "#f8fafc",
    "esai_text":        "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (85 soal – diambil 45 per sesi)
#  Tingkat kesulitan: Mudah (1–45) → Menengah (46–65) → Sulit (66–85)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ══════════════════════════════════════════════════════════
    # MUDAH (1–45)
    # ══════════════════════════════════════════════════════════

    # ── PERTUMBUHAN & PERKEMBANGAN ────────────────────────────
    {"p": "Proses bertambahnya ukuran tinggi dan berat badan manusia disebut …",
     "o": ["Perkembangan", "Pubertas", "Pertumbuhan", "Reproduksi"],
     "j": 2},

    {"p": "Urutan tahap pertumbuhan manusia yang benar dari awal adalah …",
     "o": ["Bayi – Balita – Anak – Remaja – Dewasa – Lansia",
           "Balita – Bayi – Anak – Remaja – Dewasa – Lansia",
           "Anak – Bayi – Balita – Remaja – Dewasa – Lansia",
           "Bayi – Anak – Balita – Remaja – Dewasa – Lansia"],
     "j": 0},

    {"p": "Tahap awal terbentuknya individu baru dalam kandungan dimulai dari …",
     "o": ["Janin", "Embrio", "Bayi", "Zigot"],
     "j": 3},

    {"p": "Organ reproduksi perempuan yang menghasilkan sel telur disebut …",
     "o": ["Rahim", "Tuba falopi", "Vagina", "Ovarium"],
     "j": 3},

    {"p": "Sel yang dihasilkan oleh laki-laki dalam proses reproduksi adalah …",
     "o": ["Ovum", "Zigot", "Embrio", "Sperma"],
     "j": 3},

    {"p": "Masa peralihan dari anak-anak menuju dewasa disebut …",
     "o": ["Remaja", "Pubertas", "Bayi", "Balita"],
     "j": 1},

    {"p": "Salah satu ciri pubertas pada laki-laki adalah …",
     "o": ["Pinggul melebar", "Menstruasi", "Payudara berkembang", "Suara menjadi berat"],
     "j": 3},

    {"p": "Salah satu ciri pubertas pada perempuan adalah …",
     "o": ["Dada melebar", "Suara menjadi besar", "Jakun tumbuh", "Menstruasi"],
     "j": 3},

    {"p": "Pakaian yang sebaiknya digunakan remaja saat pubertas adalah …",
     "o": ["Pakaian terbuka dan tipis",
           "Pakaian ketat agar terlihat keren",
           "Pakaian yang sopan dan menutup aurat",
           "Tidak ada aturan berpakaian"],
     "j": 2},

    {"p": "Faktor internal yang memengaruhi pertumbuhan manusia adalah …",
     "o": ["Makanan bergizi", "Lingkungan tempat tinggal", "Aktivitas fisik", "Gen/keturunan"],
     "j": 3},

    # ── BENDA LANGIT ──────────────────────────────────────────
    {"p": "Benda langit yang mengelilingi matahari dan menjadi tempat tinggal makhluk hidup adalah …",
     "o": ["Mars", "Venus", "Jupiter", "Bumi"],
     "j": 3},

    {"p": "Bulan adalah satelit alami yang mengelilingi …",
     "o": ["Matahari", "Mars", "Jupiter", "Bumi"],
     "j": 3},

    {"p": "Planet yang paling dekat dengan matahari adalah …",
     "o": ["Venus", "Bumi", "Mars", "Merkurius"],
     "j": 3},

    {"p": "Planet yang memiliki cincin indah tersusun dari es dan debu adalah …",
     "o": ["Jupiter", "Uranus", "Neptunus", "Saturnus"],
     "j": 3},

    {"p": "Planet yang berwarna merah dan dikenal sebagai planet merah adalah …",
     "o": ["Venus", "Jupiter", "Merkurius", "Mars"],
     "j": 3},

    {"p": "Planet terbesar dalam tata surya adalah …",
     "o": ["Saturnus", "Neptunus", "Uranus", "Jupiter"],
     "j": 3},

    {"p": "Kelompok planet dalam (inferior) terdiri dari …",
     "o": ["Mars dan Jupiter",
           "Saturnus dan Uranus",
           "Bumi dan Mars",
           "Merkurius dan Venus"],
     "j": 3},

    {"p": "Lapisan paling luar yang membentuk bumi disebut …",
     "o": ["Mantel", "Inti dalam", "Inti luar", "Kerak"],
     "j": 3},

    {"p": "Benda langit yang mengorbit mengelilingi planet disebut …",
     "o": ["Meteor", "Komet", "Asteroid", "Satelit"],
     "j": 3},

    {"p": "Bintang yang menjadi pusat tata surya kita adalah …",
     "o": ["Bulan", "Bumi", "Jupiter", "Matahari"],
     "j": 3},

    # ── KEARIFAN LOKAL ────────────────────────────────────────
    {"p": "Tradisi Sisingaan berasal dari daerah …",
     "o": ["Jawa Tengah", "Bali", "Sumatra Barat", "Subang, Jawa Barat"],
     "j": 3},

    {"p": "Tradisi lompat batu (hombo batu) berasal dari daerah …",
     "o": ["Bali", "Papua", "Kalimantan", "Nias, Sumatra Utara"],
     "j": 3},

    {"p": "Kerak telor adalah makanan khas dari daerah …",
     "o": ["Yogyakarta", "Bandung", "Surabaya", "Betawi/Jakarta"],
     "j": 3},

    {"p": "Manfaat melestarikan kearifan lokal adalah …",
     "o": ["Menghilangkan budaya asing",
           "Membatasi pergaulan",
           "Menutup diri dari dunia luar",
           "Menjaga identitas dan budaya bangsa"],
     "j": 3},

    {"p": "Kearifan lokal masyarakat Indonesia mencerminkan …",
     "o": ["Kelemahan bangsa", "Kemunduran teknologi", "Pertikaian antardaerah",
           "Kekayaan dan keragaman budaya"],
     "j": 3},

    # ── USAHA EKONOMI ─────────────────────────────────────────
    {"p": "Kegiatan ekonomi yang menghasilkan barang disebut …",
     "o": ["Distribusi", "Konsumsi", "Jasa", "Produksi"],
     "j": 3},

    {"p": "Contoh usaha di bidang jasa adalah …",
     "o": ["Pabrik tekstil", "Pertanian padi", "Toko beras", "Salon rambut"],
     "j": 3},

    {"p": "Seorang dokter yang memeriksa pasien termasuk usaha di bidang …",
     "o": ["Perdagangan", "Industri", "Pertanian", "Jasa"],
     "j": 3},

    {"p": "Kegiatan menyalurkan barang dari produsen ke konsumen disebut …",
     "o": ["Produksi", "Konsumsi", "Ekspor", "Distribusi"],
     "j": 3},

    {"p": "Usaha yang mengolah bahan mentah menjadi barang jadi disebut usaha …",
     "o": ["Jasa", "Perdagangan", "Pertanian", "Industri"],
     "j": 3},

    {"p": "Petani yang menanam padi termasuk kegiatan ekonomi di bidang …",
     "o": ["Jasa", "Perdagangan", "Industri", "Pertanian"],
     "j": 3},

    {"p": "Ojek online termasuk usaha di bidang …",
     "o": ["Industri", "Perdagangan", "Pertanian", "Jasa transportasi"],
     "j": 3},

    {"p": "Pabrik yang membuat sepatu dari kulit termasuk usaha …",
     "o": ["Pertanian", "Jasa", "Perdagangan", "Industri"],
     "j": 3},

    {"p": "Tukang las dan montir bengkel termasuk usaha di bidang …",
     "o": ["Perdagangan", "Industri", "Pertanian", "Jasa"],
     "j": 3},

    {"p": "Nelayan yang menangkap ikan di laut termasuk kegiatan ekonomi di bidang …",
     "o": ["Industri", "Jasa", "Perdagangan", "Pertanian/perikanan"],
     "j": 3},

    # ── ENERGI ALTERNATIF ────────────────────────────────────
    {"p": "Kincir air memanfaatkan energi … untuk menghasilkan energi listrik.",
     "o": ["Angin", "Matahari", "Panas bumi", "Air"],
     "j": 3},

    {"p": "Sumber energi yang tidak akan habis dan dapat diperbarui disebut energi …",
     "o": ["Fosil", "Kimia", "Nuklir", "Terbarukan"],
     "j": 3},

    {"p": "Panel surya memanfaatkan energi … untuk menghasilkan listrik.",
     "o": ["Angin", "Air", "Panas bumi", "Matahari"],
     "j": 3},

    {"p": "Bahan bakar minyak (BBM) termasuk sumber energi …",
     "o": ["Terbarukan", "Alternatif", "Nuklir", "Tak terbarukan/fosil"],
     "j": 3},

    {"p": "Kincir angin mengubah energi angin menjadi energi …",
     "o": ["Kimia", "Cahaya", "Panas", "Gerak/listrik"],
     "j": 3},

    # ── KERAJINAN ─────────────────────────────────────────────
    {"p": "Kerajinan gerabah dibuat dari bahan baku …",
     "o": ["Bambu", "Kayu", "Plastik", "Tanah liat"],
     "j": 3},

    {"p": "Kerajinan anyaman tikar dibuat dari bahan baku …",
     "o": ["Tanah liat", "Besi", "Kaca", "Bambu/pandan"],
     "j": 3},

    {"p": "Bahan baku utama untuk membuat batik adalah …",
     "o": ["Kayu", "Bambu", "Tanah liat", "Kain"],
     "j": 3},

    {"p": "Kerajinan wayang kulit dibuat dari bahan baku …",
     "o": ["Tanah liat", "Bambu", "Kain", "Kulit hewan (sapi/kerbau)"],
     "j": 3},

    {"p": "Kerajinan ukiran dari Bali umumnya terbuat dari …",
     "o": ["Tanah liat", "Bambu", "Kain", "Kayu"],
     "j": 3},

    # ══════════════════════════════════════════════════════════
    # MENENGAH (46–65)
    # ══════════════════════════════════════════════════════════

    {"p": "Urutan yang benar tahap pembentukan individu dalam kandungan adalah …",
     "o": ["Embrio → zigot → janin → bayi",
           "Janin → zigot → embrio → bayi",
           "Bayi → zigot → embrio → janin",
           "Zigot → embrio → janin → bayi"],
     "j": 3},

    {"p": "Hormon yang dihasilkan oleh ovarium pada perempuan adalah …",
     "o": ["Testosteron dan androgen",
           "Insulin dan glukagon",
           "Adrenalin dan kortisol",
           "Estrogen dan progesteron"],
     "j": 3},

    {"p": "Faktor eksternal yang memengaruhi perkembangan manusia adalah …",
     "o": ["Gen dari orang tua",
           "Kromosom dalam sel",
           "Hormon dalam tubuh",
           "Makanan bergizi dan lingkungan sosial"],
     "j": 3},

    {"p": "Pembuahan (fertilisasi) terjadi ketika …",
     "o": ["Sel telur berkembang menjadi janin",
           "Zigot menempel di dinding rahim",
           "Embrio terbentuk di ovarium",
           "Sperma bertemu dan menyatu dengan sel telur"],
     "j": 3},

    {"p": "Perubahan pada remaja perempuan saat pubertas yang berhubungan dengan reproduksi adalah …",
     "o": ["Suara membesar", "Jakun tumbuh", "Otot membesar", "Menstruasi"],
     "j": 3},

    {"p": "Bumi dan Mars termasuk kelompok planet …",
     "o": ["Interior", "Inferior", "Eksterior", "Superior/luar"],
     "j": 3},

    {"p": "Lapisan bumi dari luar ke dalam yang benar adalah …",
     "o": ["Mantel → kerak → inti dalam → inti luar",
           "Inti dalam → inti luar → mantel → kerak",
           "Kerak → inti luar → mantel → inti dalam",
           "Kerak → mantel → inti luar → inti dalam"],
     "j": 3},

    {"p": "Yang membedakan planet Mars dari planet lain adalah …",
     "o": ["Berwarna biru dan memiliki air",
           "Terbesar di tata surya",
           "Memiliki cincin",
           "Berwarna merah dan memiliki 2 bulan (Phobos dan Deimos)"],
     "j": 3},

    {"p": "Yang dimaksud dengan planet inferior adalah …",
     "o": ["Planet yang lebih besar dari Bumi",
           "Planet yang orbitnya di luar orbit Bumi",
           "Planet yang tidak memiliki satelit",
           "Planet yang orbitnya di dalam orbit Bumi"],
     "j": 3},

    {"p": "Urutan planet dari terdekat ke matahari yang benar adalah …",
     "o": ["Venus – Merkurius – Bumi – Mars",
           "Bumi – Venus – Merkurius – Mars",
           "Mars – Bumi – Venus – Merkurius",
           "Merkurius – Venus – Bumi – Mars"],
     "j": 3},

    {"p": "Sisingaan adalah tradisi rakyat berupa … yang berasal dari Subang.",
     "o": ["Tarian perang dengan pedang",
           "Upacara adat menangkap ikan",
           "Pertunjukan wayang kulit semalam suntuk",
           "Arak-arakan anak yang diusung di atas patung singa"],
     "j": 3},

    {"p": "Lompat batu (hombo batu) di Nias awalnya berfungsi sebagai …",
     "o": ["Upacara keagamaan",
           "Permainan anak-anak",
           "Pertunjukan seni untuk wisatawan",
           "Latihan perang dan keberanian para pemuda"],
     "j": 3},

    {"p": "Kerak telor adalah makanan khas Betawi yang dibuat dari bahan …",
     "o": ["Tepung terigu, gula, dan susu",
           "Singkong, gula merah, dan kelapa",
           "Sagu, santan, dan garam",
           "Beras ketan, telur bebek, dan ebi"],
     "j": 3},

    {"p": "Salah satu manfaat kearifan lokal bagi masyarakat adalah …",
     "o": ["Membuat masyarakat tertutup dari kemajuan",
           "Menghambat pertumbuhan ekonomi",
           "Menggantikan hukum nasional",
           "Memperkuat persatuan dan jati diri bangsa"],
     "j": 3},

    {"p": "Industri kerajinan tangan berbasis kearifan lokal dapat meningkatkan …",
     "o": ["Pencemaran lingkungan",
           "Pengangguran di desa",
           "Ketergantungan pada produk impor",
           "Pendapatan dan kesejahteraan masyarakat"],
     "j": 3},

    {"p": "Usaha ekonomi yang dilakukan secara bersama-sama dengan modal bersama disebut …",
     "o": ["Usaha perseorangan",
           "Usaha pemerintah",
           "Usaha asing",
           "Usaha bersama (koperasi/CV/PT)"],
     "j": 3},

    {"p": "Guru, dokter, dan tukang cukur merupakan contoh usaha di bidang …",
     "o": ["Perdagangan", "Industri", "Pertanian", "Jasa"],
     "j": 3},

    {"p": "Kegiatan menukar barang atau jasa dengan uang disebut …",
     "o": ["Produksi", "Distribusi", "Konsumsi", "Perdagangan"],
     "j": 3},

    {"p": "BUMN (Badan Usaha Milik Negara) adalah contoh usaha yang dimiliki oleh …",
     "o": ["Perorangan swasta",
           "Koperasi seluruh Indonesia",
           "Perusahaan asing",
           "Pemerintah/negara"],
     "j": 3},

    {"p": "Koperasi adalah usaha bersama yang berasaskan …",
     "o": ["Persaingan bebas", "Keuntungan semata", "Modal besar", "Kekeluargaan"],
     "j": 3},

    # ══════════════════════════════════════════════════════════
    # SULIT (66–85)
    # ══════════════════════════════════════════════════════════

    {"p": "Pernyataan yang BENAR tentang pengertian pertumbuhan adalah …",
     "o": ["Pertumbuhan adalah perubahan perilaku dan kedewasaan seseorang",
           "Pertumbuhan dan perkembangan adalah hal yang sama persis",
           "Pertumbuhan hanya dipengaruhi oleh makanan saja",
           "Pertumbuhan adalah perubahan fisik yang dapat diukur, seperti tinggi dan berat badan"],
     "j": 3},

    {"p": "Faktor yang memengaruhi perkembangan manusia antara lain adalah faktor genetik, nutrisi, dan …",
     "o": ["Cuaca dan iklim",
           "Warna kulit dan ras",
           "Jenis kelamin saja",
           "Lingkungan sosial dan stimulasi"],
     "j": 3},

    {"p": "Pernyataan yang SALAH tentang tradisi Sisingaan adalah …",
     "o": ["Berasal dari Subang, Jawa Barat",
           "Biasa ditampilkan saat khitanan atau acara adat",
           "Menggunakan patung berbentuk singa sebagai properti",
           "Merupakan tradisi tari perang dari Kalimantan"],
     "j": 3},

    {"p": "Pernyataan yang BENAR tentang kerak telor adalah …",
     "o": ["Kerak telor berasal dari Yogyakarta",
           "Kerak telor dibuat dari tepung terigu biasa",
           "Kerak telor adalah minuman tradisional Jawa",
           "Kerak telor adalah makanan khas Betawi dari Jakarta"],
     "j": 3},

    {"p": "Pernyataan yang BENAR tentang usaha di bidang jasa adalah …",
     "o": ["Usaha jasa menghasilkan barang yang dapat disimpan",
           "Usaha jasa selalu membutuhkan bahan baku berupa logam",
           "Usaha jasa tidak memerlukan keahlian khusus",
           "Usaha jasa menghasilkan pelayanan yang dirasakan langsung oleh konsumen"],
     "j": 3},

    {"p": "Kelompok planet inferior yang tepat adalah …",
     "o": ["Mars dan Bumi",
           "Jupiter dan Saturnus",
           "Uranus dan Neptunus",
           "Merkurius dan Venus"],
     "j": 3},

    {"p": "Kelompok planet luar (superior) yang orbitnya di luar orbit Bumi adalah …",
     "o": ["Merkurius dan Venus",
           "Merkurius, Venus, Bumi",
           "Bumi dan Mars",
           "Mars, Jupiter, Saturnus, Uranus, Neptunus"],
     "j": 3},

    {"p": "Lapisan bumi yang berwujud cair dan sangat panas berada di bagian …",
     "o": ["Kerak bumi", "Mantel bumi bagian atas", "Atmosfer bumi", "Inti luar bumi"],
     "j": 3},

    {"p": "Tahap awal terbentuknya individu dalam kandungan setelah terjadi pembuahan adalah …",
     "o": ["Janin", "Bayi", "Embrio", "Zigot"],
     "j": 3},

    {"p": "Organ reproduksi perempuan yang berfungsi sebagai tempat berkembangnya janin adalah …",
     "o": ["Ovarium", "Tuba falopi", "Vagina", "Rahim (uterus)"],
     "j": 3},

    {"p": "Dalam proses reproduksi, sperma akan bertemu sel telur di …",
     "o": ["Rahim", "Ovarium", "Vagina", "Tuba falopi"],
     "j": 3},

    {"p": "Pernyataan yang BENAR tentang masa pubertas adalah …",
     "o": ["Pubertas hanya dialami oleh perempuan",
           "Pubertas adalah masa anak-anak sebelum sekolah",
           "Pubertas tidak disertai perubahan fisik apapun",
           "Pubertas adalah masa peralihan dari anak-anak ke dewasa, disertai perubahan fisik dan emosi"],
     "j": 3},

    {"p": "Kincir air yang digunakan untuk menggerakkan generator memanfaatkan energi alternatif berupa …",
     "o": ["Energi angin",
           "Energi matahari",
           "Energi panas bumi",
           "Energi air (hidroelektrik)"],
     "j": 3},

    {"p": "Manfaat kearifan lokal yang berhubungan dengan penguatan identitas nasional adalah …",
     "o": ["Menghambat masuknya budaya asing secara paksa",
           "Membuat masyarakat tidak mau menerima teknologi baru",
           "Menutup peluang wisata internasional",
           "Menjadi ciri khas yang membedakan Indonesia dari negara lain"],
     "j": 3},

    {"p": "Usaha ekonomi yang paling tepat dikategorikan sebagai usaha jasa adalah …",
     "o": ["Pabrik yang memproduksi sepatu",
           "Toko yang menjual pakaian",
           "Ladang pertanian yang menghasilkan sayuran",
           "Rumah sakit yang merawat pasien"],
     "j": 3},

    {"p": "Bumi merupakan satu-satunya planet yang …",
     "o": ["Mengelilingi matahari",
           "Memiliki satelit alami",
           "Berputar pada porosnya",
           "Diketahui mendukung kehidupan makhluk hidup"],
     "j": 3},

    {"p": "Bahan baku utama untuk membuat kerajinan gerabah tradisional adalah …",
     "o": ["Pasir pantai yang halus",
           "Serbuk kayu dan lem",
           "Bubur kertas (papier-mache)",
           "Tanah liat yang dibakar"],
     "j": 3},

    {"p": "Perbedaan antara pertumbuhan dan perkembangan manusia yang paling tepat adalah …",
     "o": ["Pertumbuhan adalah proses mental, perkembangan adalah proses fisik",
           "Pertumbuhan dan perkembangan sama-sama tidak dapat diukur",
           "Pertumbuhan hanya terjadi pada otak",
           "Pertumbuhan bisa diukur secara fisik (tinggi/berat), perkembangan meliputi kemampuan dan kedewasaan"],
     "j": 3},

    {"p": "Gambar kincir angin besar di ladang terbuka menunjukkan pemanfaatan energi alternatif berupa …",
     "o": ["Energi panas matahari",
           "Energi air terjun",
           "Energi panas bumi (geothermal)",
           "Energi angin (aeolian)"],
     "j": 3},

    {"p": "Tradisi lompat batu (Fahombo) dari suku Nias menunjukkan kearifan lokal berupa …",
     "o": ["Ritual pemujaan dewa alam",
           "Permainan anak-anak yang menghibur",
           "Upacara pernikahan adat Nias",
           "Latihan fisik dan mental untuk kesiapan perang"],
     "j": 3},
]

# ─────────────────────────────────────────────────────────────
#  POOL ESAI  (15 soal – diambil 5 per sesi secara acak)
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    # 0
    {"p": "Sebutkan 3 faktor yang memengaruhi pertumbuhan dan perkembangan manusia!",
     "pedoman": "1. Faktor genetik (gen/keturunan dari orang tua). 2. Faktor nutrisi (makanan bergizi yang cukup, seperti protein, vitamin, dan mineral). 3. Faktor lingkungan (lingkungan sosial, stimulasi belajar, dan kondisi kesehatan)."},
    # 1
    {"p": "Sebutkan 4 contoh benda langit yang ada di tata surya beserta penjelasan singkatnya!",
     "pedoman": "1. Planet – benda langit bulat yang mengelilingi matahari (contoh: Bumi, Mars). 2. Bintang – benda langit yang memancarkan cahayanya sendiri (contoh: Matahari). 3. Satelit – benda langit yang mengelilingi planet (contoh: Bulan). 4. Komet – benda langit berekor panjang yang mengelilingi matahari."},
    # 2
    {"p": "Tuliskan 6 tahap pertumbuhan dan perkembangan manusia secara urut!",
     "pedoman": "1. Bayi (0-2 tahun). 2. Balita (2-5 tahun). 3. Anak-anak (6-11 tahun). 4. Remaja/Pubertas (12-18 tahun). 5. Dewasa (19-60 tahun). 6. Lanjut usia/Lansia (di atas 60 tahun)."},
    # 3
    {"p": "Jelaskan 4 manfaat kearifan lokal bagi masyarakat Indonesia!",
     "pedoman": "1. Memperkuat identitas dan jati diri bangsa Indonesia di tengah pengaruh budaya asing. 2. Menjaga persatuan dan kerukunan masyarakat. 3. Meningkatkan kesejahteraan melalui kerajinan tangan dan pariwisata budaya. 4. Mewariskan nilai dan kearifan nenek moyang kepada generasi berikutnya."},
    # 4
    {"p": "Jelaskan sumber energi alternatif yang dimanfaatkan oleh kincir air dan cara kerjanya!",
     "pedoman": "Kincir air memanfaatkan energi kinetik (gerak) air yang mengalir atau jatuh. Cara kerja: aliran air mengenai bilah kincir sehingga berputar, putaran diteruskan ke generator untuk menghasilkan listrik. Energi ini disebut energi hidroelektrik dan termasuk energi terbarukan."},
    # 5
    {"p": "Sebutkan minimal 3 bahan baku yang digunakan untuk membuat kerajinan tradisional Indonesia beserta contoh produknya!",
     "pedoman": "1. Tanah liat -> gerabah, keramik. 2. Bambu/pandan -> anyaman tikar, bakul. 3. Kayu -> ukiran, patung. 4. Kain -> batik, tenun ikat. 5. Kulit hewan -> wayang kulit, tas. 6. Rotan -> kursi, keranjang."},
    # 6
    {"p": "Jelaskan tahap pertumbuhan manusia yang disebut masa pubertas, termasuk ciri-cirinya!",
     "pedoman": "Pubertas adalah masa peralihan dari anak-anak menuju dewasa (usia 10-18 tahun). Ciri pada laki-laki: suara membesar, tumbuh jakun, rambut di ketiak. Ciri pada perempuan: menstruasi, pinggul melebar, payudara berkembang. Selain fisik, remaja juga mengalami perubahan emosi."},
    # 7
    {"p": "Sebutkan organ reproduksi perempuan yang berfungsi menghasilkan sel telur dan hormon estrogen serta progesteron!",
     "pedoman": "Organ tersebut adalah ovarium (indung telur). Ovarium berjumlah dua buah di rongga panggul. Fungsinya: menghasilkan sel telur (ovum) setiap siklus menstruasi, serta memproduksi hormon estrogen (mengatur ciri kelamin sekunder) dan progesteron (mempersiapkan rahim untuk kehamilan)."},
    # 8
    {"p": "Sebutkan dan jelaskan lapisan-lapisan yang membentuk bumi dari luar ke dalam!",
     "pedoman": "1. Kerak bumi - lapisan terluar, tempat kita berpijak, tersusun dari batuan. 2. Mantel bumi - lapisan tebal di bawah kerak, sebagian berwujud semi-cair (magma). 3. Inti luar bumi - berwujud cair dari besi dan nikel, sangat panas. 4. Inti dalam bumi - bagian terdalam, berwujud padat dari besi dan nikel."},
    # 9
    {"p": "Jelaskan perbedaan planet dalam (inferior) dan planet luar (superior) beserta contoh masing-masing!",
     "pedoman": "Planet inferior adalah planet yang orbitnya di dalam orbit Bumi, yaitu Merkurius dan Venus. Planet superior adalah planet yang orbitnya di luar orbit Bumi, yaitu Mars, Jupiter, Saturnus, Uranus, dan Neptunus."},
    # 10
    {"p": "Jelaskan proses awal terbentuknya individu baru dalam kandungan dari zigot hingga janin!",
     "pedoman": "1. Sperma membuahi sel telur (ovum) di tuba falopi -> terbentuk zigot. 2. Zigot membelah menjadi kumpulan sel (morula). 3. Berkembang menjadi embrio dan menempel di dinding rahim. 4. Embrio berkembang menjadi janin selama sekitar 9 bulan hingga lahir sebagai bayi."},
    # 11
    {"p": "Sebutkan 4 jenis usaha ekonomi di bidang jasa yang kamu ketahui beserta contohnya!",
     "pedoman": "1. Jasa pendidikan - guru, tutor, lembaga kursus. 2. Jasa kesehatan - dokter, perawat, bidan. 3. Jasa transportasi - ojek online, taksi, bus. 4. Jasa perbaikan - montir bengkel, tukang las, teknisi elektronik."},
    # 12
    {"p": "Sebutkan 4 nama planet dalam tata surya beserta satu ciri khasnya masing-masing!",
     "pedoman": "Pilih 4 dari: Merkurius - terkecil, terdekat Matahari. Venus - terpanas, atmosfer CO2 tebal. Bumi - satu-satunya planet berpenghuni. Mars - merah, memiliki gunung berapi terbesar (Olympus Mons). Jupiter - terbesar. Saturnus - memiliki cincin indah. Uranus - berputar miring. Neptunus - terjauh dari Matahari."},
    # 13
    {"p": "Jelaskan apa itu kearifan lokal dan berikan 2 contoh tradisi kearifan lokal dari daerah berbeda di Indonesia!",
     "pedoman": "Kearifan lokal adalah pengetahuan, nilai, dan tradisi turun-temurun yang berkembang dalam suatu masyarakat. Contoh: 1. Sisingaan dari Subang, Jawa Barat - arak-arakan anak di atas patung singa saat khitanan. 2. Lompat batu (Fahombo) dari Nias, Sumatra Utara - melompati batu setinggi sekitar 2 meter sebagai latihan keberanian pemuda."},
    # 14
    {"p": "Jelaskan apa yang dimaksud sel sperma dan apa perannya dalam proses reproduksi manusia!",
     "pedoman": "Sel sperma (spermatozoa) adalah sel reproduksi yang dihasilkan oleh testis pada laki-laki. Perannya: membuahi sel telur (ovum) dari perempuan. Saat satu sperma menyatu dengan sel telur, terbentuklah zigot yang merupakan awal kehidupan individu baru dalam kandungan."},
]

# ─────────────────────────────────────────────────────────────
#  PERSIAPAN SESI
# ─────────────────────────────────────────────────────────────
def prepare_session():
    labels = list("ABCD")

    # Pilih & acak PG
    selected_pg = random.sample(PG_POOL, NUM_PG)
    prepared = []
    for q in selected_pg:
        correct_text = q["o"][q["j"]]
        opts = q["o"][:]
        random.shuffle(opts)
        new_answer = opts.index(correct_text)
        prepared.append({
            "type": "pg",
            "p":    q["p"],
            "o":    [f"{labels[i]}. {opts[i]}" for i in range(4)],
            "j":    labels[new_answer],
        })

    # Pilih 5 esai secara acak dari pool
    selected_esai = random.sample(ESAI_POOL, NUM_ESAI)

    for q in selected_esai:
        prepared.append({
            "type":    "esai",
            "p":       q["p"],
            "pedoman": q.get("pedoman", ""),
        })

    return prepared

# ─────────────────────────────────────────────────────────────
#  DIALOG HELPERS
# ─────────────────────────────────────────────────────────────

def _cx(d, w, h):
    d.geometry(f"{w}x{h}+{(d.winfo_screenwidth()-w)//2}"
               f"+{(d.winfo_screenheight()-h)//2}")

def dlg_warn(parent, title, msg):
    d = tk.Toplevel(parent)
    d.title(title); d.configure(bg="#fff")
    d.attributes("-topmost", True); d.grab_set(); d.resizable(False, False)
    _cx(d, 420, 180)
    tk.Label(d, text=title, bg="#fff", fg="#e94560",
             font=("Segoe UI", 13, "bold")).pack(pady=(22, 6))
    tk.Label(d, text=msg, bg="#fff", fg="#334155",
             font=("Segoe UI", 11), wraplength=370).pack(pady=4)
    tk.Button(d, text="OK", bg="#16a34a", fg="#fff",
              font=("Segoe UI", 11), relief="flat",
              command=d.destroy, padx=22, pady=7).pack(pady=12)
    d.wait_window()

def dlg_confirm(parent, title, msg):
    res = [False]
    d = tk.Toplevel(parent)
    d.title(title); d.configure(bg="#fff")
    d.attributes("-topmost", True); d.grab_set(); d.resizable(False, False)
    _cx(d, 440, 195)
    tk.Label(d, text=title, bg="#fff", fg="#f59e0b",
             font=("Segoe UI", 13, "bold")).pack(pady=(22, 6))
    tk.Label(d, text=msg, bg="#fff", fg="#334155",
             font=("Segoe UI", 11), wraplength=400, justify="center").pack(pady=4)
    bf = tk.Frame(d, bg="#fff"); bf.pack(pady=12)
    def _yes(): res[0] = True; d.destroy()
    tk.Button(bf, text="Ya, Kumpulkan", bg="#16a34a", fg="#fff",
              font=("Segoe UI", 11), relief="flat",
              command=_yes, padx=14, pady=7).pack(side="left", padx=8)
    tk.Button(bf, text="Batal", bg="#e94560", fg="#fff",
              font=("Segoe UI", 11), relief="flat",
              command=d.destroy, padx=14, pady=7).pack(side="left", padx=8)
    d.wait_window(); return res[0]


# ─────────────────────────────────────────────────────────────
#  APLIKASI UTAMA
# ─────────────────────────────────────────────────────────────

class UjianApp:
    def __init__(self):
        self.root = tk.Tk()
        self._setup_window()

        self.questions   = prepare_session()
        self.answers     = {}
        self.current     = 0

        self._nav_btns      = []
        self._q_frame       = None
        self._cur_tw        = None
        self._answered_lbl  = None
        self._timer_lbl     = None
        self._timer_secs    = WAKTU_MENIT * 60
        self._timer_id      = None

        self._build_exam()
        self._enforce_fg()

    # ── Window setup ─────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.title("Ujian IPAS Kelas 6 SD")
        r.configure(bg=C["page"])
        r.attributes("-fullscreen", True)
        r.attributes("-topmost", True)
        r.overrideredirect(True)
        r.protocol("WM_DELETE_WINDOW", lambda: None)
        for seq in ("<Alt-F4>", "<Alt-Tab>", "<Escape>",
                    "<Super_L>", "<Super_R>", "<Control-Escape>"):
            r.bind_all(seq, lambda e: "break")
        r.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())

    def _enforce_fg(self):
        try:
            active_dialogs = [
                w for w in self.root.winfo_children()
                if isinstance(w, tk.Toplevel) and w.winfo_exists()
            ]
            if active_dialogs:
                active_dialogs[-1].lift()
            else:
                self.root.lift()
                if self.root.focus_displayof() is None:
                    self.root.focus_force()
        except Exception:
            pass
        self.root.after(400, self._enforce_fg)

    def _try_exit(self):
        stop_hook()
        self.root.destroy()
        sys.exit(0)

    # ════════════════════════════════════════════════════════
    #  BUILD EXAM
    # ════════════════════════════════════════════════════════
    def _build_exam(self):
        wrap = tk.Frame(self.root, bg=C["page"])
        wrap.pack(fill="both", expand=True)
        self._wrap = wrap

        self._build_topbar(wrap)
        self._build_navbar(wrap)
        self._build_scroll(wrap)
        self._show_question(0)

    # ── Topbar ───────────────────────────────────────────────
    def _build_topbar(self, parent):
        tb = tk.Frame(parent, bg=C["topbar"])
        tb.pack(fill="x")

        tk.Label(tb, text="UJIAN IPAS  \u2022  KELAS 6 SD",
                 bg=C["topbar"], fg="#86efac",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=18, pady=10)

        self._answered_lbl = tk.Label(tb, text="",
                                      bg=C["topbar"], fg="#bbf7d0",
                                      font=("Segoe UI", 11))
        self._answered_lbl.pack(side="left", padx=10)
        self._refresh_counter()

        self._timer_lbl = tk.Label(tb, text="",
                                   bg=C["topbar"], fg=C["timer_ok"],
                                   font=("Segoe UI", 12, "bold"))
        self._timer_lbl.pack(side="left", padx=16)
        self._tick_timer()

        bf = tk.Frame(tb, bg=C["topbar"]); bf.pack(side="right", padx=12)
        tk.Button(bf, text="KUMPULKAN",
                  bg=C["btn_submit"], fg="#fff",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2",
                  command=self._submit_exam,
                  padx=12, pady=6).pack(side="left", padx=4)

    # ── Nav bar ──────────────────────────────────────────────
    def _build_navbar(self, parent):
        nb = tk.Frame(parent, bg=C["nav_bg"])
        nb.pack(fill="x")

        tk.Frame(nb, bg="#e2e8f0", height=1).pack(fill="x")

        inner = tk.Frame(nb, bg=C["nav_bg"])
        inner.pack(pady=6, padx=12)

        self._nav_btns = []

        pg_label_frame = tk.Frame(inner, bg=C["nav_bg"])
        pg_label_frame.pack(anchor="w")
        tk.Label(pg_label_frame, text="PG:",
                 bg=C["nav_bg"], fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 4))

        chunk = 15
        for row_i in range(3):
            row = tk.Frame(inner, bg=C["nav_bg"])
            row.pack(anchor="w", pady=1)
            for i in range(row_i * chunk, (row_i + 1) * chunk):
                btn = tk.Label(row, text=str(i + 1),
                               bg=C["nav_todo"], fg=C["nav_todo_fg"],
                               font=("Segoe UI", 8, "bold"),
                               width=3, padx=2, pady=3,
                               cursor="hand2", relief="flat")
                btn.pack(side="left", padx=1)
                btn.bind("<Button-1>", lambda e, idx=i: self._show_question(idx))
                self._nav_btns.append(btn)

        esai_row = tk.Frame(inner, bg=C["nav_bg"])
        esai_row.pack(anchor="w", pady=(3, 0))
        tk.Label(esai_row, text="Esai:",
                 bg=C["nav_bg"], fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 4))
        for i in range(NUM_PG, NUM_PG + NUM_ESAI):
            ei = i - NUM_PG + 1
            btn = tk.Label(esai_row, text=f"E{ei}",
                           bg=C["nav_todo"], fg=C["nav_todo_fg"],
                           font=("Segoe UI", 8, "bold"),
                           width=3, padx=2, pady=3,
                           cursor="hand2", relief="flat")
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, idx=i: self._show_question(idx))
            self._nav_btns.append(btn)

        tk.Frame(nb, bg="#e2e8f0", height=1).pack(fill="x")

    # ── Scroll area ──────────────────────────────────────────
    def _build_scroll(self, parent):
        cont = tk.Frame(parent, bg=C["page"])
        cont.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(cont, bg=C["page"], highlightthickness=0)
        vsb = ttk.Scrollbar(cont, orient="vertical",
                            command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._scroll_inner = tk.Frame(self._canvas, bg=C["page"])
        self._cw = self._canvas.create_window(
            (0, 0), window=self._scroll_inner, anchor="nw")

        self._scroll_inner.bind("<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cw, width=e.width))

    # ════════════════════════════════════════════════════════
    #  QUESTION DISPLAY
    # ════════════════════════════════════════════════════════
    def _show_question(self, idx):
        self._save_essay()

        self.current = idx

        if self._q_frame:
            self._q_frame.destroy()

        self._canvas.yview_moveto(0)
        self._update_nav()

        q = self.questions[idx]
        card = tk.Frame(self._scroll_inner, bg=C["card"])
        card.pack(fill="x", padx=60, pady=20)
        self._q_frame = card

        if q["type"] == "pg":
            self._render_pg(card, idx)
        else:
            self._render_esai(card, idx)

    # ── PG question ──────────────────────────────────────────
    def _render_pg(self, card, idx):
        q      = self.questions[idx]
        pg_num = idx + 1
        total  = NUM_PG + NUM_ESAI

        badge_row = tk.Frame(card, bg=C["card"])
        badge_row.pack(fill="x", padx=40, pady=(28, 0))
        tk.Label(badge_row,
                 text=f"  PILIHAN GANDA  {pg_num}/{NUM_PG}  ",
                 bg=C["q_pg_accent"], fg="#fff",
                 font=("Segoe UI", 9, "bold"),
                 padx=4, pady=3).pack(side="left")
        answered_count = sum(1 for a in self.answers.values()
                             if a not in (None, ""))
        tk.Label(badge_row,
                 text=f"  {answered_count} dari {total} soal dijawab  ",
                 bg="#f0fdf4", fg="#16a34a",
                 font=("Segoe UI", 9),
                 padx=4, pady=3).pack(side="left", padx=10)

        prog_frame = tk.Frame(card, bg="#e2e8f0", height=5)
        prog_frame.pack(fill="x", padx=40, pady=(10, 0))
        prog_frame.update_idletasks()
        pw    = prog_frame.winfo_width() or 800
        pct_w = max(4, int(pw * pg_num / total))
        tk.Frame(prog_frame, bg=C["q_pg_accent"],
                 height=5, width=pct_w).place(x=0, y=0)

        tk.Label(card, text=q["p"],
                 bg=C["card"], fg=C["q_text"],
                 font=("Segoe UI", 14),
                 wraplength=900, justify="left",
                 anchor="nw").pack(fill="x", padx=40, pady=(20, 8))

        opts_wrap = tk.Frame(card, bg=C["card"])
        opts_wrap.pack(fill="x", padx=40, pady=(4, 0))
        current_answer = self.answers.get(idx)
        for opt in q["o"]:
            self._render_option(opts_wrap, idx, opt[0], opt[3:],
                                is_selected=(current_answer == opt[0]))

        self._render_nav_buttons(card, idx)

    # ── Essay question ────────────────────────────────────────
    def _render_esai(self, card, idx):
        q     = self.questions[idx]
        ei    = idx - NUM_PG + 1
        total = NUM_PG + NUM_ESAI

        badge_row = tk.Frame(card, bg=C["card"])
        badge_row.pack(fill="x", padx=40, pady=(28, 0))
        tk.Label(badge_row,
                 text=f"  ESAI  {ei}/{NUM_ESAI}  ",
                 bg=C["q_esai_accent"], fg="#fff",
                 font=("Segoe UI", 9, "bold"),
                 padx=4, pady=3).pack(side="left")

        prog_frame = tk.Frame(card, bg="#e2e8f0", height=5)
        prog_frame.pack(fill="x", padx=40, pady=(10, 0))
        prog_frame.update_idletasks()
        pw    = prog_frame.winfo_width() or 800
        pct_w = max(4, int(pw * (idx + 1) / total))
        tk.Frame(prog_frame, bg=C["q_esai_accent"],
                 height=5, width=pct_w).place(x=0, y=0)

        tk.Label(card, text=q["p"],
                 bg=C["card"], fg=C["q_text"],
                 font=("Segoe UI", 14),
                 wraplength=900, justify="left",
                 anchor="nw").pack(fill="x", padx=40, pady=(20, 6))

        tk.Label(card, text="Jawaban Anda:",
                 bg=C["card"], fg="#64748b",
                 font=("Segoe UI", 10, "italic")).pack(anchor="w", padx=40)

        txt = tk.Text(card, height=8,
                      bg=C["esai_area"], fg=C["esai_text"],
                      insertbackground=C["esai_text"],
                      font=("Segoe UI", 12),
                      relief="flat", padx=12, pady=10,
                      wrap="word")
        txt.pack(fill="x", padx=40, pady=(4, 0))

        saved = self.answers.get(idx, "")
        if saved:
            txt.insert("1.0", saved)
        self._cur_tw = txt

        self._render_nav_buttons(card, idx)

    # ── Option button ─────────────────────────────────────────
    def _render_option(self, parent, q_idx, letter, text, is_selected):
        if is_selected:
            row_bg = C["opt_sel_bg"]; txt_fg = C["opt_sel_fg"]
            lbg    = C["opt_sel_lbg"]; lfg   = "#ffffff"
        else:
            row_bg = C["opt_bg"]; txt_fg = C["opt_fg"]
            lbg    = C["opt_letter_bg"]; lfg   = C["opt_letter_fg"]

        row = tk.Frame(parent, bg=row_bg, cursor="hand2")
        row.pack(fill="x", pady=5)

        badge = tk.Label(row, text=letter,
                         bg=lbg, fg=lfg,
                         font=("Segoe UI", 12, "bold"),
                         width=2, padx=10, pady=14)
        badge.pack(side="left")

        lbl = tk.Label(row, text=text,
                       bg=row_bg, fg=txt_fg,
                       font=("Segoe UI", 12),
                       anchor="w", padx=16, pady=14,
                       wraplength=820, justify="left")
        lbl.pack(side="left", fill="x", expand=True)

        def _select(let=letter, i=q_idx):
            self.answers[i] = let
            self._refresh_counter()
            self._update_nav()
            self._show_question(i)

        def _hover_in(e):
            if not is_selected:
                row.config(bg=C["opt_hover"])
                lbl.config(bg=C["opt_hover"])

        def _hover_out(e):
            if not is_selected:
                row.config(bg=C["opt_bg"])
                lbl.config(bg=C["opt_bg"])

        for w in (row, badge, lbl):
            w.bind("<Button-1>", lambda e, f=_select: f())
            if not is_selected:
                w.bind("<Enter>", _hover_in)
                w.bind("<Leave>", _hover_out)

    # ── Prev / Next buttons ───────────────────────────────────
    def _render_nav_buttons(self, card, idx):
        total = NUM_PG + NUM_ESAI
        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", padx=40, pady=(24, 32))

        if idx > 0:
            tk.Button(bf, text="\u25c4  SEBELUMNYA",
                      bg=C["btn_prev"], fg="#fff",
                      font=("Segoe UI", 11, "bold"),
                      relief="flat", cursor="hand2",
                      command=lambda: self._show_question(idx - 1),
                      padx=18, pady=10).pack(side="left")

        if idx < total - 1:
            tk.Button(bf, text="BERIKUTNYA  \u25ba",
                      bg=C["btn_next"], fg="#fff",
                      font=("Segoe UI", 11, "bold"),
                      relief="flat", cursor="hand2",
                      command=lambda: self._show_question(idx + 1),
                      padx=18, pady=10).pack(side="right")
        else:
            tk.Button(bf, text="KUMPULKAN UJIAN",
                      bg=C["btn_submit"], fg="#fff",
                      font=("Segoe UI", 11, "bold"),
                      relief="flat", cursor="hand2",
                      command=self._submit_exam,
                      padx=18, pady=10).pack(side="right")

    # ════════════════════════════════════════════════════════
    #  STATE HELPERS
    # ════════════════════════════════════════════════════════
    def _save_essay(self):
        if self._cur_tw is not None and self.current >= NUM_PG:
            self.answers[self.current] = \
                self._cur_tw.get("1.0", "end-1c").strip()
        self._cur_tw = None

    def _refresh_counter(self):
        if self._answered_lbl is None:
            return
        done  = sum(1 for a in self.answers.values() if a not in (None, ""))
        total = NUM_PG + NUM_ESAI
        self._answered_lbl.config(text=f"\u2713 {done} / {total} dijawab")

    def _update_nav(self):
        for i, btn in enumerate(self._nav_btns):
            is_curr = (i == self.current)
            is_done = self.answers.get(i, "") not in (None, "")
            is_esai = (i >= NUM_PG)

            if is_curr:
                btn.config(bg=C["nav_curr"], fg=C["nav_curr_fg"])
            elif is_done and is_esai:
                btn.config(bg=C["nav_esai_done"], fg=C["nav_esai_done_fg"])
            elif is_done:
                btn.config(bg=C["nav_done"], fg=C["nav_done_fg"])
            else:
                btn.config(bg=C["nav_todo"], fg=C["nav_todo_fg"])

    def _tick_timer(self):
        s = self._timer_secs
        h, m, sec = s // 3600, (s % 3600) // 60, s % 60
        if self._timer_lbl:
            if s <= 300:
                color = C["timer_crit"]
            elif s <= 900:
                color = C["timer_warn"]
            else:
                color = C["timer_ok"]
            self._timer_lbl.config(
                text=f"\u23f1  {h:02d}:{m:02d}:{sec:02d}", fg=color)
        if s > 0:
            self._timer_secs -= 1
            self._timer_id = self.root.after(1000, self._tick_timer)
        else:
            dlg_warn(self.root, "Waktu Habis!",
                     "Waktu ujian telah habis.\nJawaban Anda akan dikumpulkan.")
            self._submit_exam()

    # ════════════════════════════════════════════════════════
    #  SUBMIT
    # ════════════════════════════════════════════════════════
    def _submit_exam(self):
        self._save_essay()
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

        total      = NUM_PG + NUM_ESAI
        unanswered = sum(1 for i in range(total)
                         if self.answers.get(i, "") in (None, ""))
        if unanswered > 0:
            if not dlg_confirm(
                self.root, "Soal Belum Selesai",
                f"Masih ada {unanswered} soal yang belum dijawab.\n"
                f"Yakin ingin mengumpulkan ujian?"):
                return

        score    = sum(1 for i in range(NUM_PG)
                       if self.answers.get(i) == self.questions[i]["j"])
        filepath = self._save_file(score)
        self._build_results(score, filepath)

    def _save_file(self, score):
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp  = os.path.join(HASIL_DIR, f"hasil_ipas_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN IPAS KELAS 6 SD",
            "=" * 60,
            f"  Tanggal : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            "-" * 60,
            f"  SKOR PILIHAN GANDA : {score} / {NUM_PG}",
            f"  NILAI (PG)         : {score / NUM_PG * 100:.1f}",
            "-" * 60,
            "", "DETAIL JAWABAN PILIHAN GANDA:",
        ]
        for i in range(NUM_PG):
            q     = self.questions[i]
            siswa = self.answers.get(i, "-")
            kunci = q["j"]
            mark  = "BENAR" if siswa == kunci else f"SALAH (kunci={kunci})"
            lines.append(f"  PG {i+1:2d}. Jawaban: {siswa}  -> {mark}")

        lines += ["", "-" * 60, "", "JAWABAN ESAI:"]
        for i in range(NUM_PG, NUM_PG + NUM_ESAI):
            q   = self.questions[i]
            jwb = self.answers.get(i, "(kosong)")
            ei  = i - NUM_PG + 1
            lines.append(f"\nEsai {ei}.")
            lines.append(f"Soal   : {q['p'][:80]}...")
            lines.append(f"Jawaban: {jwb if jwb else '(kosong)'}")
            if q.get("pedoman"):
                lines.append(f"Pedoman: {q['pedoman']}")

        lines.append("\n" + "=" * 60)
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return fp

    # ════════════════════════════════════════════════════════
    #  RESULTS FRAME
    # ════════════════════════════════════════════════════════
    def _build_results(self, score, filepath):
        for w in self.root.winfo_children():
            w.destroy()

        outer = tk.Frame(self.root, bg=C["page"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=C["page"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        f = tk.Frame(canvas, bg=C["page"])
        win_id = canvas.create_window((0, 0), window=f, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        f.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        tk.Label(f, text="UJIAN SELESAI",
                 bg=C["page"], fg="#16a34a",
                 font=("Segoe UI", 34, "bold")).pack(pady=(50, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian IPAS!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 15)).pack(pady=(0, 20))

        card = tk.Frame(f, bg="#fff", padx=50, pady=28)
        card.pack()

        pct   = score / NUM_PG * 100
        color = "#16a34a" if pct >= 70 else "#f59e0b"

        rows = [
            ("Skor Pilihan Ganda", f"{score} / {NUM_PG}"),
            ("Nilai (PG)",         f"{pct:.1f}"),
            ("Soal Esai",          f"{NUM_ESAI} soal \u2014 sudah dikumpulkan"),
            ("File Tersimpan",     filepath),
        ]
        for r, (lbl, val) in enumerate(rows):
            tk.Label(card, text=f"{lbl:<25}:",
                     bg="#fff", fg="#64748b",
                     font=("Segoe UI", 12)).grid(
                         row=r, column=0, sticky="w", pady=7, padx=6)
            fg = color if "Nilai" in lbl else C["q_text"]
            wt = "bold" if "Nilai" in lbl else "normal"
            tk.Label(card, text=val,
                     bg="#fff", fg=fg,
                     font=("Segoe UI", 12, wt)).grid(
                         row=r, column=1, sticky="w", pady=7, padx=16)

        wrong = [(i, q) for i, q in enumerate(self.questions)
                 if q["type"] == "pg" and self.answers.get(i) != q["j"]]

        if wrong:
            tk.Label(f, text=f"Soal yang Salah ({len(wrong)} soal)",
                     bg=C["page"], fg="#e94560",
                     font=("Segoe UI", 16, "bold")).pack(pady=(32, 6))
            tk.Label(f, text="Pelajari kembali soal-soal berikut:",
                     bg=C["page"], fg=C["q_sub"],
                     font=("Segoe UI", 11)).pack(pady=(0, 10))

            for seq_no, (qi, q) in enumerate(wrong, 1):
                wcard = tk.Frame(f, bg="#fff", padx=24, pady=16,
                                 highlightbackground="#fecaca",
                                 highlightthickness=2)
                wcard.pack(fill="x", padx=40, pady=6)

                tk.Label(wcard,
                         text=f"No. {qi+1}  \u2022  {q['p']}",
                         bg="#fff", fg=C["q_text"],
                         font=("Segoe UI", 11, "bold"),
                         wraplength=900, justify="left",
                         anchor="w").pack(fill="x", pady=(0, 8))

                jawaban_siswa = self.answers.get(qi, "-")
                tk.Label(wcard,
                         text=f"\u2718  Jawaban kamu: {jawaban_siswa}",
                         bg="#fff", fg="#e94560",
                         font=("Segoe UI", 11),
                         anchor="w").pack(fill="x")
                tk.Label(wcard,
                         text=f"\u2714  Jawaban benar: {q['j']}",
                         bg="#fff", fg="#16a34a",
                         font=("Segoe UI", 11),
                         anchor="w").pack(fill="x")
        else:
            tk.Label(f, text="Semua jawaban pilihan ganda benar!",
                     bg=C["page"], fg="#16a34a",
                     font=("Segoe UI", 14, "bold")).pack(pady=(28, 0))

        tk.Label(f, text="Tekan Ctrl + Alt + Backspace untuk keluar.",
                 bg=C["page"], fg="#94a3b8",
                 font=("Segoe UI", 11, "italic")).pack(pady=(28, 40))

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_hook()
    app = UjianApp()
    app.run()
