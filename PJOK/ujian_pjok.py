#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian PJOK Kelas 6 SD
- Langsung masuk soal (tanpa input nama/kelas)
- 45 PG + 5 Esai, diacak setiap sesi
- Soal esai renang gaya punggung SELALU keluar
- Satu soal per tampilan, navigasi prev/next
- Jawaban dapat diubah
- Kode keluar guru: pinewood62
"""

import tkinter as tk
from tkinter import ttk
import ctypes, ctypes.wintypes
import threading, random, os, sys
from datetime import datetime

EXIT_CODE   = "pinewood62"
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
    "page":           "#f0f4f8",
    "topbar":         "#1e3a5f",
    "topbar_text":    "#ffffff",
    "nav_bg":         "#ffffff",
    "nav_todo":       "#dde3ec",
    "nav_todo_fg":    "#64748b",
    "nav_done":       "#22c55e",
    "nav_done_fg":    "#ffffff",
    "nav_curr":       "#f59e0b",
    "nav_curr_fg":    "#ffffff",
    "nav_esai_done":  "#8b5cf6",
    "nav_esai_done_fg": "#ffffff",
    "card":           "#ffffff",
    "q_pg_accent":    "#2563eb",
    "q_esai_accent":  "#7c3aed",
    "q_text":         "#1e293b",
    "q_sub":          "#64748b",
    "opt_bg":         "#f1f5f9",
    "opt_fg":         "#94a3b8",
    "opt_letter_bg":  "#e2e8f0",
    "opt_letter_fg":  "#64748b",
    "opt_sel_bg":     "#2563eb",
    "opt_sel_fg":     "#ffffff",
    "opt_sel_lbg":    "#1d4ed8",
    "opt_hover":      "#eff6ff",
    "btn_prev":       "#94a3b8",
    "btn_next":       "#2563eb",
    "btn_submit":     "#16a34a",
    "btn_exit":       "#e94560",
    "btn_text":       "#ffffff",
    "timer_ok":       "#22c55e",
    "timer_warn":     "#f59e0b",
    "timer_crit":     "#ef4444",
    "esai_area":      "#f8fafc",
    "esai_text":      "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (100 soal – diambil 45 per sesi)
#  Tingkat kesulitan: Mudah (1-56) → Menengah (57-78) → Sulit (79-100)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ── RENANG ──────────────────────────────────────────────
    {"p": "Yang menjadi gerakan awal untuk mendorong tubuh saat berenang adalah …",
     "o": ["Gerakan tangan", "Gerakan kaki", "Dorongan dinding kolam", "Mengambil napas"],
     "j": 2},

    {"p": "Gaya renang yang posisi tubuhnya telentang menghadap ke atas adalah …",
     "o": ["Gaya bebas", "Gaya punggung", "Gaya dada", "Gaya kupu-kupu"],
     "j": 1},

    {"p": "Cara mengambil napas yang benar saat renang gaya bebas adalah …",
     "o": ["Kepala mendongak ke atas setiap saat",
           "Kepala diputar ke samping saat salah satu lengan mengayuh",
           "Menahan napas sepanjang berenang",
           "Mengambil napas setiap dua kayuhan kaki"],
     "j": 1},

    {"p": "Gerakan kaki pada renang gaya dada menyerupai gerakan …",
     "o": ["Gunting", "Katak", "Lumba-lumba", "Kipas"],
     "j": 1},

    {"p": "Alat keselamatan yang wajib tersedia di area kolam renang adalah …",
     "o": ["Pelampung dan tali penyelamat", "Kacamata renang", "Papan pelampung", "Baju renang"],
     "j": 0},

    {"p": "Manfaat utama olahraga renang bagi tubuh adalah …",
     "o": ["Melatih keseimbangan saja",
           "Melatih kekuatan tangan saja",
           "Melatih hampir seluruh otot tubuh secara bersamaan",
           "Melatih kecepatan kaki saja"],
     "j": 2},

    {"p": "Posisi tubuh yang benar saat meluncur dalam renang gaya bebas adalah …",
     "o": ["Badan tegak lurus, kepala mendongak",
           "Badan lurus sejajar permukaan air, wajah ke bawah",
           "Badan miring 45 derajat",
           "Badan melengkung ke atas"],
     "j": 1},

    {"p": "Etika yang benar saat berada di pinggir kolam renang adalah …",
     "o": ["Berlari secepat mungkin menuju air",
           "Mendorong teman ke dalam kolam",
           "Melompat sembarangan ke kolam",
           "Berjalan pelan dan tidak berlari di pinggir kolam"],
     "j": 3},

    # ── KEBUGARAN JASMANI ────────────────────────────────────
    {"p": "Kebugaran jasmani adalah kemampuan seseorang untuk …",
     "o": ["Berlari sejauh mungkin tanpa berhenti",
           "Melakukan aktivitas fisik sehari-hari tanpa merasa kelelahan yang berarti",
           "Mengangkat beban seberat-beratnya",
           "Melompat setinggi-tingginya"],
     "j": 1},

    {"p": "Komponen kebugaran jasmani yang berkaitan dengan kemampuan jantung dan paru-paru adalah …",
     "o": ["Daya tahan kardiorespirasi", "Kekuatan otot", "Kelenturan", "Kecepatan"],
     "j": 0},

    {"p": "Frekuensi berolahraga yang disarankan dalam satu minggu untuk menjaga kebugaran adalah …",
     "o": ["1 kali", "2 kali", "3–5 kali", "7 kali setiap hari tanpa istirahat"],
     "j": 2},

    {"p": "Latihan push-up dan pull-up bertujuan untuk meningkatkan …",
     "o": ["Kelenturan tubuh", "Kekuatan otot lengan dan dada", "Kecepatan lari", "Daya tahan jantung"],
     "j": 1},

    {"p": "Latihan sit-up secara rutin bertujuan untuk melatih kekuatan otot …",
     "o": ["Kaki", "Perut", "Punggung", "Lengan"],
     "j": 1},

    {"p": "Sebelum berolahraga, pemanasan (warming up) dilakukan dengan tujuan …",
     "o": ["Mencegah terjadinya cedera otot dan sendi",
           "Agar cepat lelah saat berolahraga",
           "Mengurangi waktu berolahraga",
           "Meningkatkan rasa kantuk"],
     "j": 0},

    {"p": "Tes yang digunakan untuk mengukur kebugaran jasmani siswa SD di Indonesia disebut …",
     "o": ["Tes lari maraton", "Tes berenang 50 m", "Tes lompat jauh", "Tes Kebugaran Jasmani Indonesia (TKJI)"],
     "j": 3},

    {"p": "Komponen kebugaran jasmani yang dilatih dengan gerakan senam peregangan adalah …",
     "o": ["Kecepatan", "Kekuatan", "Kelenturan (fleksibilitas)", "Daya ledak"],
     "j": 2},

    {"p": "Seseorang dikatakan memiliki daya tahan yang baik apabila …",
     "o": ["Dapat mengangkat beban paling berat",
           "Dapat melakukan aktivitas dalam waktu lama tanpa kelelahan berlebih",
           "Dapat berlari paling cepat",
           "Dapat melompat paling tinggi"],
     "j": 1},

    # ── GERAK DASAR ──────────────────────────────────────────
    {"p": "Start jongkok pada perlombaan lari digunakan untuk nomor lari …",
     "o": ["Lari jarak jauh (marathon)", "Lari estafet saja",
           "Lari jarak pendek (sprint)", "Lari halang rintang"],
     "j": 2},

    {"p": "Pada lompat jauh, tumpuan yang benar dilakukan menggunakan …",
     "o": ["Kedua kaki secara bersamaan", "Satu kaki yang terkuat",
           "Lutut", "Ujung jari kaki saja"],
     "j": 1},

    {"p": "Teknik melempar bola dalam permainan kasti yang menghasilkan lemparan jauh dan akurat adalah …",
     "o": ["Melempar dari depan dada dengan kedua tangan",
           "Melempar dengan ayunan lengan dari bawah",
           "Melempar dengan ayunan lengan dari atas (overhand throw)",
           "Melempar sambil jongkok"],
     "j": 2},

    {"p": "Fase-fase dalam lompat tinggi secara berurutan adalah …",
     "o": ["Mendarat – awalan – tumpuan – melewati mistar",
           "Awalan – tumpuan – melewati mistar – mendarat",
           "Tumpuan – awalan – mendarat – melewati mistar",
           "Melewati mistar – tumpuan – awalan – mendarat"],
     "j": 1},

    {"p": "Posisi tubuh yang benar saat mendarat dalam lompat jauh adalah …",
     "o": ["Mendarat dengan satu kaki lurus",
           "Mendarat dengan kedua kaki dan lutut sedikit ditekuk",
           "Mendarat dengan lutut lurus sepenuhnya",
           "Mendarat dengan tangan menyentuh pasir lebih dulu"],
     "j": 1},

    {"p": "Gerakan dasar yang melatih kecepatan dan koordinasi tubuh adalah …",
     "o": ["Lari sprint", "Berjalan santai", "Duduk bersila", "Berbaring"],
     "j": 0},

    # ── PERMAINAN BOLA BESAR ─────────────────────────────────
    {"p": "Jumlah pemain sepak bola dalam satu regu yang bermain di lapangan adalah …",
     "o": ["11 orang", "9 orang", "12 orang", "10 orang"],
     "j": 0},

    {"p": "Teknik menggiring bola dalam permainan bola basket disebut …",
     "o": ["Passing", "Shooting", "Dribbling", "Blocking"],
     "j": 2},

    {"p": "Ukuran lapangan bola voli yang sesuai standar adalah …",
     "o": ["20 x 10 meter", "18 x 9 meter", "16 x 8 meter", "22 x 11 meter"],
     "j": 1},

    {"p": "Teknik serangan utama dalam permainan bola voli yang dilakukan dengan memukul bola keras ke arah lawan disebut …",
     "o": ["Servis", "Passing", "Blocking", "Smash"],
     "j": 3},

    {"p": "Lama waktu permainan sepak bola dalam satu pertandingan penuh adalah …",
     "o": ["2 x 30 menit", "2 x 45 menit", "4 x 15 menit", "2 x 40 menit"],
     "j": 1},

    {"p": "Pelanggaran dalam bola voli yang menyebabkan poin untuk regu lawan adalah …",
     "o": ["Melakukan servis keras", "Memblok bola lawan",
           "Melompat tinggi saat smash", "Menyentuh net saat bola aktif"],
     "j": 3},

    {"p": "Cara mencetak poin dalam permainan bola basket adalah …",
     "o": ["Membawa bola ke garis belakang lawan",
           "Melempar bola ke tiang gawang",
           "Memasukkan bola ke dalam ring (keranjang) lawan",
           "Memukul bola ke arah lawan"],
     "j": 2},

    {"p": "Posisi pemain sepak bola yang bertugas menjaga gawang disebut …",
     "o": ["Kiper (penjaga gawang)", "Striker", "Gelandang", "Bek"],
     "j": 0},

    # ── PERMAINAN BOLA KECIL ─────────────────────────────────
    {"p": "Jumlah pemain dalam satu regu permainan kasti adalah …",
     "o": ["10 orang", "9 orang", "12 orang", "15 orang"],
     "j": 2},

    {"p": "Cara memukul bola yang benar dalam permainan kasti adalah …",
     "o": ["Menggunakan pemukul kayu dengan satu tangan",
           "Menendang bola dengan kaki",
           "Memukul dengan kedua tangan",
           "Melempar bola ke atas lalu dipukul"],
     "j": 0},

    {"p": "Bentuk lapangan dalam permainan rounders adalah …",
     "o": ["Segi empat", "Segi lima", "Lingkaran", "Segitiga"],
     "j": 1},

    {"p": "Alat yang digunakan dalam olahraga bulu tangkis adalah …",
     "o": ["Raket dan kok (shuttlecock)", "Raket dan bola karet",
           "Tongkat dan bola", "Pemukul dan bola kecil"],
     "j": 0},

    {"p": "Sistem perhitungan poin dalam tenis meja (per set) adalah …",
     "o": ["Hingga 15 poin", "Hingga 7 poin",
           "Hingga 11 poin", "Hingga 21 poin"],
     "j": 2},

    {"p": "Cara mendapatkan nilai dalam permainan kasti adalah …",
     "o": ["Memasukkan bola ke gawang",
           "Mengenai pemukul lawan dengan bola",
           "Melempar bola keluar lapangan",
           "Memukul bola dan berhasil kembali ke ruang bebas"],
     "j": 3},

    # ── ATLETIK DASAR ────────────────────────────────────────
    {"p": "Nomor-nomor yang termasuk dalam lari jarak pendek (sprint) adalah …",
     "o": ["1.500 m, 3.000 m, 5.000 m",
           "100 m, 200 m, 400 m",
           "800 m, 1.000 m, 1.500 m",
           "Marathon, 10.000 m, 5.000 m"],
     "j": 1},

    {"p": "Dalam lari estafet, benda yang diserahkan antar pelari disebut …",
     "o": ["Bendera", "Tongkat estafet", "Gelang", "Tali"],
     "j": 1},

    {"p": "Lompat tinggi gaya straddle dilakukan dengan cara melewati mistar dengan posisi badan …",
     "o": ["Telentang (punggung menghadap mistar)",
           "Miring ke samping",
           "Telungkup (perut menghadap mistar)",
           "Tegak lurus"],
     "j": 2},

    {"p": "Zona serah terima tongkat dalam lari estafet dilakukan pada jarak …",
     "o": ["10 meter", "20 meter", "30 meter", "40 meter"],
     "j": 1},

    # ── SENAM LANTAI ─────────────────────────────────────────
    {"p": "Gerakan berguling ke depan (roll depan) dimulai dengan posisi …",
     "o": ["Jongkok, kedua tangan diletakkan di matras selebar bahu",
           "Berdiri tegak, langsung jatuhkan tubuh",
           "Berbaring telentang terlebih dahulu",
           "Berlari kemudian langsung berguling"],
     "j": 0},

    {"p": "Senam yang gerakannya diiringi irama musik disebut …",
     "o": ["Senam lantai", "Senam artistik",
           "Senam irama (ritmik)", "Senam akrobatik"],
     "j": 2},

    {"p": "Alat pengaman yang wajib digunakan saat latihan senam lantai adalah …",
     "o": ["Helm", "Matras", "Pelindung lutut", "Sepatu roda"],
     "j": 1},

    {"p": "Tujuan utama senam irama adalah …",
     "o": ["Melatih koordinasi gerak tubuh dengan irama",
           "Melatih kekuatan mengangkat beban",
           "Melatih kecepatan berlari",
           "Melatih keseimbangan statis saja"],
     "j": 0},

    {"p": "Posisi tubuh yang benar saat melakukan gerakan plank adalah …",
     "o": ["Tubuh miring, bertumpu pada satu tangan",
           "Tubuh melengkung seperti busur",
           "Tubuh lurus sejajar lantai, bertumpu pada lengan bawah dan ujung kaki",
           "Tubuh tegak, kedua tangan di pinggang"],
     "j": 2},

    {"p": "Gerakan berdiri menggunakan kedua tangan (handstand) melatih …",
     "o": ["Kecepatan lari", "Daya tahan jantung",
           "Keseimbangan dan kekuatan lengan", "Kelenturan punggung saja"],
     "j": 2},

    # ── KESEHATAN & GIZI ─────────────────────────────────────
    {"p": "Fungsi utama protein bagi tubuh manusia adalah …",
     "o": ["Sebagai sumber energi utama",
           "Membangun dan memperbaiki sel serta jaringan tubuh",
           "Mengatur suhu tubuh",
           "Menyimpan cadangan makanan"],
     "j": 1},

    {"p": "Zat gizi yang menjadi sumber energi utama bagi tubuh adalah …",
     "o": ["Protein", "Lemak", "Vitamin", "Karbohidrat"],
     "j": 3},

    {"p": "Kandungan zat besi banyak terdapat pada sayuran berwarna hijau seperti …",
     "o": ["Wortel", "Tomat", "Bayam", "Jagung"],
     "j": 2},

    {"p": "Pola hidup sehat yang benar bagi siswa sekolah dasar adalah …",
     "o": ["Tidur cukup 8–9 jam, makan bergizi, olahraga teratur",
           "Tidur larut malam, makan junk food, main gawai terus",
           "Puasa setiap hari, olahraga berat, kurang minum",
           "Tidur siang seharian, tidak berolahraga"],
     "j": 0},

    {"p": "Bakteri Escherichia Coli dapat menjadi penyebab penyakit yang menyerang organ reproduksi yaitu …",
     "o": ["Infeksi saluran kemih", "Keputihan", "Kanker serviks", "HIV/AIDS"],
     "j": 0},

    {"p": "Cara menjaga kebersihan diri yang benar adalah …",
     "o": ["Mandi sekali seminggu",
           "Mandi minimal 2 kali sehari, sikat gigi, dan mencuci tangan sebelum makan",
           "Hanya mencuci tangan setelah makan",
           "Mandi hanya saat merasa kotor"],
     "j": 1},

    {"p": "Jumlah kebutuhan air minum yang disarankan setiap hari untuk anak-anak adalah …",
     "o": ["1 gelas per hari", "2 gelas per hari",
           "6–8 gelas per hari", "12 gelas per hari"],
     "j": 2},

    # ── PUBERTAS & REPRODUKSI ────────────────────────────────
    {"p": "Berikut yang merupakan ciri pubertas pada laki-laki adalah …",
     "o": ["Pinggul melebar dan suara tetap tinggi",
           "Mulai menstruasi dan payudara membesar",
           "Suara membesar, tumbuh jakun, dan tumbuh rambut di wajah",
           "Kulit menjadi lebih lembut"],
     "j": 2},

    {"p": "Ciri pubertas yang dialami oleh perempuan adalah …",
     "o": ["Mulai menstruasi, payudara membesar, pinggul melebar",
           "Suara membesar dan tumbuh jakun",
           "Tumbuh rambut di wajah dan dada",
           "Bahu melebar dan otot membesar"],
     "j": 0},

    {"p": "Perubahan yang terjadi pada masa pubertas terutama disebabkan oleh …",
     "o": ["Pola makan yang berubah", "Perubahan hormon dalam tubuh",
           "Pengaruh cuaca", "Pengaruh teman sebaya"],
     "j": 1},

    {"p": "Cara menjaga kebersihan organ reproduksi yang benar adalah …",
     "o": ["Jarang mengganti pakaian dalam",
           "Membersihkan organ reproduksi hanya sekali seminggu",
           "Menggunakan sabun berparfum kuat di dalam area intim",
           "Mengganti pakaian dalam setiap hari dan menjaga kebersihan area intim"],
     "j": 3},

    # ── PENCEGAHAN CEDERA & SPORTIVITAS ─────────────────────
    {"p": "Tindakan pertama yang dilakukan jika teman mengalami keseleo saat olahraga adalah …",
     "o": ["Langsung dipijat sekuat-kuatnya",
           "Kompres dengan es, istirahatkan, dan segera hubungi guru",
           "Suruh terus berolahraga agar otot menjadi panas",
           "Diberi minyak panas langsung"],
     "j": 1},

    {"p": "Sikap sportif dalam olahraga berarti …",
     "o": ["Bermain curang agar menang",
           "Menerima kekalahan dengan lapang dada dan menghormati lawan",
           "Marah jika tim sendiri kalah",
           "Tidak mau mengikuti aturan pertandingan"],
     "j": 1},

    {"p": "Pemanasan sebelum olahraga berguna untuk …",
     "o": ["Membuat tubuh lebih berat",
           "Mengulur waktu berolahraga",
           "Mempersiapkan otot dan sendi sehingga mengurangi risiko cedera",
           "Membuat detak jantung langsung menjadi sangat cepat"],
     "j": 2},

    {"p": "Pendinginan (cooling down) setelah berolahraga bertujuan untuk …",
     "o": ["Membuat tubuh menjadi sangat dingin",
           "Mengembalikan detak jantung dan pernapasan ke kondisi normal secara bertahap",
           "Membuat otot semakin tegang",
           "Mempersiapkan latihan berikutnya segera"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    #  SOAL MENENGAH  (57–78)
    # ══════════════════════════════════════════════════════════

    # ── RENANG (menengah) ────────────────────────────────────
    {"p": "Pada renang gaya kupu-kupu, gerakan kedua tangan dilakukan secara …",
     "o": ["Bergantian seperti gaya bebas",
           "Bersamaan dan simetris ke depan lalu ke belakang",
           "Satu tangan diam, satu tangan mengayuh",
           "Bergantian seperti gaya punggung"],
     "j": 1},

    {"p": "Panjang kolam renang standar olimpik adalah …",
     "o": ["25 meter", "40 meter", "50 meter", "100 meter"],
     "j": 2},

    {"p": "Pernapasan pada renang gaya dada dilakukan saat …",
     "o": ["Kepala selalu di atas air sepanjang berenang",
           "Kepala diangkat ke depan ketika kedua tangan mendorong air ke samping",
           "Kepala diputar ke kiri setiap 2 kayuhan",
           "Menahan napas sepanjang jarak renang"],
     "j": 1},

    {"p": "Dalam renang gaya bebas, pola pernapasan yang paling umum digunakan perenang adalah …",
     "o": ["Bernapas setiap 1 kayuhan tangan",
           "Bernapas setiap 3 kayuhan tangan (bilateral breathing)",
           "Bernapas hanya di awal dan akhir jarak",
           "Bernapas hanya ke sisi kanan"],
     "j": 1},

    # ── KEBUGARAN (menengah) ─────────────────────────────────
    {"p": "Komponen kebugaran jasmani yang diukur melalui tes lari 600 meter pada TKJI adalah …",
     "o": ["Kekuatan otot lengan", "Kelenturan tubuh",
           "Daya tahan kardiorespirasi", "Kecepatan reaksi"],
     "j": 2},

    {"p": "Latihan yang paling tepat untuk meningkatkan kelincahan (agility) adalah …",
     "o": ["Lari jarak jauh dengan kecepatan tetap",
           "Latihan zig-zag dan shuttle run",
           "Push-up setiap pagi",
           "Peregangan statis setiap hari"],
     "j": 1},

    {"p": "Apa yang dimaksud dengan daya ledak (power) dalam kebugaran jasmani? …",
     "o": ["Kemampuan otot bekerja dalam waktu lama",
           "Kemampuan tubuh untuk tetap seimbang",
           "Gabungan antara kekuatan dan kecepatan gerak otot",
           "Kemampuan mengubah arah gerak dengan cepat"],
     "j": 2},

    {"p": "Latihan yang paling efektif untuk meningkatkan kekuatan otot kaki adalah …",
     "o": ["Push-up dan pull-up", "Plank dan sit-up",
           "Squat dan lunges", "Lari jarak jauh"],
     "j": 2},

    # ── ATLETIK (menengah) ───────────────────────────────────
    {"p": "Start berdiri (standing start) digunakan pada nomor lari …",
     "o": ["100 meter", "200 meter", "400 meter", "1.500 meter ke atas"],
     "j": 3},

    {"p": "Zona serah terima tongkat dalam lari estafet dinamakan …",
     "o": ["Zona bebas", "Zona transisi", "Zona pergantian (exchange zone)", "Zona akhir"],
     "j": 2},

    {"p": "Teknik lompat tinggi gaya Fosbury Flop melewati mistar dengan posisi punggung …",
     "o": ["Menghadap mistar (tengkurap)", "Menghadap ke atas (telentang)",
           "Tegak lurus ke mistar", "Miring 45 derajat"],
     "j": 1},

    {"p": "Sudut lemparan yang menghasilkan jarak terjauh pada lempar lembing adalah sekitar …",
     "o": ["20–25 derajat", "30–35 derajat", "40–45 derajat", "60–70 derajat"],
     "j": 2},

    # ── PERMAINAN BOLA BESAR (menengah) ─────────────────────
    {"p": "Dalam bola voli, maksimal sentuhan bola oleh satu regu sebelum dikembalikan ke lawan adalah …",
     "o": ["2 kali", "3 kali", "4 kali", "5 kali"],
     "j": 1},

    {"p": "Posisi offside dalam sepak bola terjadi ketika …",
     "o": ["Pemain berada di dalam kotak penalti sendiri",
           "Pemain menerima bola saat posisinya lebih dekat ke gawang lawan dari bola dan pemain belakang terakhir lawan",
           "Pemain menyentuh bola dengan tangan",
           "Pemain berlari melewati garis tengah lapangan"],
     "j": 1},

    {"p": "Teknik bertahan dalam bola basket yang dilakukan untuk menghalangi tembakan lawan disebut …",
     "o": ["Dribbling", "Passing", "Blocking", "Screening"],
     "j": 2},

    # ── PERMAINAN BOLA KECIL (menengah) ─────────────────────
    {"p": "Jumlah poin yang dibutuhkan untuk memenangkan satu set dalam bulu tangkis adalah …",
     "o": ["15 poin", "21 poin", "25 poin", "30 poin"],
     "j": 1},

    {"p": "Dalam tenis meja, bola servis harus memantul di meja sendiri terlebih dahulu sebelum …",
     "o": ["Menyentuh net", "Memantul di meja lawan", "Dipukul balik", "Jatuh ke lantai"],
     "j": 1},

    {"p": "Servis dalam bulu tangkis yang dilakukan dari bawah pinggang dan bola jatuh dekat net disebut …",
     "o": ["Servis panjang (long service)", "Servis pendek (short service)",
           "Servis melambung", "Servis smash"],
     "j": 1},

    # ── KESEHATAN & GIZI (menengah) ──────────────────────────
    {"p": "Kekurangan vitamin C dalam jangka panjang dapat menyebabkan penyakit …",
     "o": ["Rabun jauh", "Rakhitis", "Skorbut (gusi berdarah dan mudah memar)", "Anemia"],
     "j": 2},

    {"p": "Zat gizi yang paling berperan dalam pembentukan tulang dan gigi yang kuat adalah …",
     "o": ["Vitamin A dan D", "Kalsium dan fosfor", "Zat besi dan seng", "Protein dan lemak"],
     "j": 1},

    {"p": "Akibat kekurangan zat besi pada anak-anak adalah …",
     "o": ["Buta warna", "Anemia (kurang darah) sehingga mudah lelah dan lesu",
           "Tulang keropos", "Gigi berlubang"],
     "j": 1},

    {"p": "Kandungan gizi utama pada telur yang bermanfaat untuk pertumbuhan otot adalah …",
     "o": ["Karbohidrat dan serat", "Protein dan lemak sehat",
           "Vitamin C dan kalsium", "Zat besi dan yodium"],
     "j": 1},

    # ── PUBERTAS (menengah) ──────────────────────────────────
    {"p": "Perubahan fisik pada masa pubertas dipengaruhi oleh hormon. Hormon yang mempengaruhi pubertas pada laki-laki adalah …",
     "o": ["Estrogen", "Progesteron", "Testosteron", "Insulin"],
     "j": 2},

    # ══════════════════════════════════════════════════════════
    #  SOAL SULIT  (79–100)
    # ══════════════════════════════════════════════════════════

    # ── RENANG (sulit) ───────────────────────────────────────
    {"p": "Urutan fase gerakan lengan yang benar dalam renang gaya bebas adalah …",
     "o": ["Entry → pull → push → recovery",
           "Recovery → push → pull → entry",
           "Pull → entry → recovery → push",
           "Push → pull → entry → recovery"],
     "j": 0},

    {"p": "Kesalahan teknik yang paling sering menyebabkan tubuh tenggelam saat renang gaya bebas adalah …",
     "o": ["Mengayuh tangan terlalu cepat",
           "Kepala terlalu tinggi terangkat sehingga pinggul turun",
           "Kaki bergerak terlalu cepat",
           "Tangan masuk air terlalu dalam"],
     "j": 1},

    # ── KEBUGARAN (sulit) ────────────────────────────────────
    {"p": "Prinsip latihan yang menyatakan bahwa beban latihan harus terus ditingkatkan secara bertahap disebut prinsip …",
     "o": ["Spesifikasi (Specificity)", "Reversibilitas (Reversibility)",
           "Overload progresif (Progressive Overload)", "Individualitas (Individuality)"],
     "j": 2},

    {"p": "Zona latihan optimal untuk meningkatkan kebugaran kardiorespirasi adalah sekitar … dari denyut nadi maksimal",
     "o": ["20–40%", "40–55%", "60–80%", "85–100%"],
     "j": 2},

    {"p": "Tes kebugaran yang mengukur kelenturan tubuh dengan cara meraih ujung jari kaki sambil duduk disebut …",
     "o": ["Tes push-up", "Tes sit and reach", "Tes Cooper", "Tes lari 12 menit"],
     "j": 1},

    {"p": "Manakah yang BUKAN merupakan komponen kebugaran jasmani yang berkaitan dengan kesehatan (health-related fitness)? …",
     "o": ["Daya tahan kardiorespirasi", "Kekuatan otot",
           "Komposisi tubuh", "Kecepatan reaksi"],
     "j": 3},

    {"p": "Rumus perkiraan denyut nadi maksimal seseorang berdasarkan usianya adalah …",
     "o": ["180 dikurangi usia", "200 dikurangi usia",
           "220 dikurangi usia", "250 dikurangi usia"],
     "j": 2},

    # ── ATLETIK (sulit) ──────────────────────────────────────
    {"p": "Dalam perlombaan lompat jauh, atlet dinyatakan DISKUALIFIKASI apabila …",
     "o": ["Mendarat dengan dua kaki bersamaan",
           "Kaki menginjak atau melewati papan tumpuan saat melompat",
           "Melakukan ancang-ancang terlalu panjang",
           "Mendarat dengan kedua tangan menyentuh pasir"],
     "j": 1},

    {"p": "Teknik peluru pada tolak peluru yang benar adalah meletakkan peluru di …",
     "o": ["Telapak tangan, lengan diluruskan ke depan",
           "Leher di bawah dagu, ditopang jari-jari tangan",
           "Siku, dengan lengan ditekuk 90 derajat",
           "Bahu, dijepit dengan lengan atas"],
     "j": 1},

    # ── SENAM (sulit) ────────────────────────────────────────
    {"p": "Pada gerakan guling lenting (kip), urutan bagian tubuh yang menyentuh matras adalah …",
     "o": ["Kepala → punggung → pinggul → kaki",
           "Tangan → kepala → tengkuk → punggung → kaki melenting ke atas",
           "Kaki → pinggul → punggung → kepala",
           "Bahu → siku → tangan → kaki"],
     "j": 1},

    {"p": "Komponen kebugaran jasmani utama yang dilatih pada gerakan meroda (cartwheel) adalah …",
     "o": ["Daya tahan aerobik dan kekuatan jantung",
           "Kecepatan lari dan kelincahan",
           "Keseimbangan, koordinasi, dan kekuatan lengan",
           "Daya tahan otot kaki dan fleksibilitas pinggul"],
     "j": 2},

    # ── KESEHATAN (sulit) ─────────────────────────────────────
    {"p": "Kekurangan yodium dalam jangka panjang pada anak-anak dapat menyebabkan …",
     "o": ["Anemia dan lesu", "Rakhitis dan tulang lunak",
           "Gondok dan gangguan pertumbuhan otak", "Skorbut dan gusi berdarah"],
     "j": 2},

    {"p": "Pada Pedoman Gizi Seimbang (Tumpeng Gizi), kelompok makanan yang dianjurkan untuk dikonsumsi paling banyak setiap hari adalah …",
     "o": ["Daging dan produk hewani", "Makanan dan minuman manis",
           "Sayuran dan buah-buahan", "Minyak dan lemak"],
     "j": 2},

    {"p": "Cara yang paling tepat untuk mencegah penyebaran penyakit menular saat beraktivitas olahraga bersama adalah …",
     "o": ["Menghindari berolahraga sama sekali",
           "Mencuci tangan, tidak berbagi alat minum/makan, dan menjaga kebersihan diri",
           "Menggunakan masker tebal saat lari",
           "Minum antibiotik setiap hari"],
     "j": 1},

    # ── PUBERTAS & REPRODUKSI (sulit) ───────────────────────
    {"p": "Proses pelepasan sel telur dari ovarium yang terjadi setiap bulan disebut …",
     "o": ["Menstruasi", "Fertilisasi", "Ovulasi", "Implantasi"],
     "j": 2},

    {"p": "Hormon utama yang mengatur siklus menstruasi pada perempuan adalah …",
     "o": ["Testosteron dan androgen", "Insulin dan glukagon",
           "Estrogen dan progesteron", "Adrenalin dan kortisol"],
     "j": 2},

    {"p": "Rata-rata siklus menstruasi yang dianggap normal pada perempuan adalah setiap …",
     "o": ["14 hari", "21–35 hari", "45 hari", "60 hari"],
     "j": 1},

    # ── PENCEGAHAN CEDERA (sulit) ─────────────────────────────
    {"p": "Metode pertolongan pertama cedera olahraga yang dikenal dengan singkatan RICE adalah …",
     "o": ["Run, Isolate, Compress, Evaluate",
           "Rest, Ice, Compression, Elevation",
           "Relax, Inject, Cool, Exercise",
           "Rotate, Immobilize, Cool, Examine"],
     "j": 1},

    {"p": "Kondisi ketika otot berkontraksi secara tiba-tiba, tidak terkendali, dan sangat nyeri saat olahraga disebut …",
     "o": ["Dislokasi", "Fraktur", "Kram otot", "Tendinitis"],
     "j": 2},

    {"p": "Kedaruratan medis akibat terlalu lama terpapar panas matahari yang ditandai dengan suhu tubuh sangat tinggi dan kesadaran menurun disebut …",
     "o": ["Hipotermia", "Heat stroke (sengatan panas)", "Dehidrasi ringan", "Hipoglikemia"],
     "j": 1},

    {"p": "Cara yang PALING TEPAT untuk mencegah cedera saat melakukan lompatan dalam senam lantai adalah …",
     "o": ["Memakai sepatu berhak tinggi",
           "Berlatih di atas lantai keras tanpa alas",
           "Selalu menggunakan matras yang cukup tebal dan berlatih secara bertahap",
           "Langsung berlatih gerakan sulit tanpa pemanasan"],
     "j": 2},

    # ── SPORTIVITAS & ETIKA (sulit) ───────────────────────────
    {"p": "Tindakan 'diving' dalam permainan sepak bola termasuk pelanggaran etika karena …",
     "o": ["Membuat pemain lain jatuh",
           "Pura-pura jatuh atau diberi pelanggaran untuk menipu wasit, melanggar prinsip fair play",
           "Melakukan gerakan akrobatik yang berbahaya",
           "Berlari terlalu cepat hingga jatuh sendiri"],
     "j": 1},

    {"p": "Penggunaan doping dalam olahraga dilarang keras karena …",
     "o": ["Membuat atlet tidak percaya diri",
           "Merusak kesehatan atlet dalam jangka panjang dan melanggar prinsip fair play",
           "Membuat pertandingan berlangsung terlalu lama",
           "Doping adalah zat makanan biasa yang tidak mempengaruhi tubuh"],
     "j": 1},
]

# ─────────────────────────────────────────────────────────────
#  POOL SOAL ESAI  (17 soal – diambil 5 per sesi)
#  Soal indeks 16 ("renang gaya punggung") SELALU keluar
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    {"p": "Tuliskan langkah-langkah gerak plank!",
     "pedoman": "Tubuh lurus, bertumpu pada lengan bawah dan ujung kaki, perut ditarik ke dalam, tahan beberapa detik."},

    {"p": "Tuliskan langkah-langkah gerakan plank miring!",
     "pedoman": "Tubuh miring, bertumpu pada satu lengan bawah dan sisi kaki, tubuh tetap lurus, otot perut ditarik."},

    {"p": "Tuliskan langkah-langkah gerakan guling lenting!",
     "pedoman": "Awali dengan jongkok, berguling ke depan, lalu melentingkan tubuh ke atas dengan kedua tangan."},

    {"p": "Tuliskan 3 tahapan gerakan dalam senam irama dan tujuan dari masing-masing tahapan tersebut!",
     "pedoman": "Pemanasan (menyiapkan tubuh), inti (melatih koordinasi dan kebugaran), pendinginan (mengembalikan kondisi tubuh)."},

    {"p": "Tuliskan 5 hal yang perlu diperhatikan ketika melakukan kegiatan berenang!",
     "pedoman": "Keselamatan, pemanasan, teknik pernapasan, posisi tubuh, kondisi air kolam."},

    {"p": "Tuliskan 3 ciri-ciri pubertas pada laki-laki!",
     "pedoman": "Suara membesar, tumbuh jakun, tumbuh rambut di wajah dan tubuh."},

    {"p": "Tuliskan 3 ciri-ciri pubertas pada perempuan!",
     "pedoman": "Mulai menstruasi, payudara membesar, pinggul melebar."},

    {"p": "Tuliskan 5 cara menjaga kebersihan alat reproduksi!",
     "pedoman": "Menjaga kebersihan, pakaian dalam bersih, tidak berganti pasangan, makan bergizi, olahraga teratur."},

    {"p": "Tuliskan langkah-langkah renang gaya punggung!",
     "pedoman": "Posisi telentang, gerakan kaki naik turun, tangan bergantian mengayuh ke belakang, pernapasan teratur."},

    {"p": "Tuliskan proses pertumbuhan pada manusia secara urut dari lahir hingga dewasa!",
     "pedoman": "Dimulai dari bayi, anak-anak, remaja, dewasa, hingga lanjut usia."},

    {"p": "Tuliskan hal-hal yang perlu diperhatikan dalam senam irama berkelompok!",
     "pedoman": "Kekompakan, koordinasi gerakan, irama musik, disiplin."},

    {"p": "Tuliskan 4 alat yang dapat digunakan saat berenang beserta fungsinya!",
     "pedoman": "Pelampung (menjaga tubuh mengapung), kacamata renang (melindungi mata), papan pelampung (latihan kaki), snorkel (bernapas di air)."},

    {"p": "Sebutkan 3 manfaat menjaga kebersihan organ reproduksi!",
     "pedoman": "Mencegah infeksi, menjaga kesehatan organ, meningkatkan rasa percaya diri."},

    {"p": "Tuliskan 3 jenis variasi dan kombinasi gerakan kaki dan lengan dalam gerak berirama!",
     "pedoman": "Langkah kaki maju mundur, ayunan lengan ke samping, kombinasi tangan dan kaki bersamaan."},

    {"p": "Jelaskan apa yang dimaksud dengan kebugaran jasmani dan sebutkan 3 komponen kebugaran jasmani!",
     "pedoman": "Kebugaran jasmani: kemampuan tubuh melakukan aktivitas tanpa cepat lelah. Komponen: daya tahan, kekuatan otot, kelenturan."},

    {"p": "Tuliskan 3 sikap sportif yang harus ditunjukkan seorang atlet dalam pertandingan olahraga!",
     "pedoman": "Menghormati lawan, menerima kekalahan dengan lapang dada, mengikuti aturan pertandingan dengan jujur."},

    # SOAL 17 — SELALU KELUAR (indeks 16)
    {"p": "Tuliskan gerakan dalam olahraga renang gaya punggung!",
     "pedoman": "Posisi telentang, kaki naik turun bergantian, tangan bergantian mengayuh ke belakang, pernapasan teratur."},
]

ESAI_WAJIB_IDX = 16   # indeks soal renang gaya punggung yang selalu keluar

# ─────────────────────────────────────────────────────────────
#  PERSIAPAN SOAL SESI  (acak setiap kali program dijalankan)
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

    # Pilih esai: soal wajib + 4 acak dari sisanya
    wajib = ESAI_POOL[ESAI_WAJIB_IDX]
    pool_lain = [q for i, q in enumerate(ESAI_POOL) if i != ESAI_WAJIB_IDX]
    selected_esai = random.sample(pool_lain, NUM_ESAI - 1) + [wajib]
    random.shuffle(selected_esai)

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
    tk.Button(d, text="OK", bg="#2563eb", fg="#fff",
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

def dlg_password(parent):
    res = [None]
    d = tk.Toplevel(parent)
    d.title("Kode Keluar"); d.configure(bg="#fff")
    d.attributes("-topmost", True); d.grab_set(); d.resizable(False, False)
    _cx(d, 380, 215)
    tk.Label(d, text="Masukkan kode untuk keluar:", bg="#fff", fg="#1e293b",
             font=("Segoe UI", 12)).pack(pady=(26, 6))
    err = tk.Label(d, text="", bg="#fff", fg="#e94560",
                   font=("Segoe UI", 10)); err.pack()
    var = tk.StringVar()
    ent = tk.Entry(d, textvariable=var, show="*",
                   font=("Segoe UI", 13), width=22,
                   bg="#f1f5f9", fg="#1e293b",
                   insertbackground="#1e293b", relief="flat")
    ent.pack(pady=8, ipady=5); ent.focus_set()
    def _ok(e=None):
        if var.get() == EXIT_CODE:
            res[0] = var.get(); d.destroy()
        else:
            err.config(text="Kode salah! Coba lagi.")
            var.set("")
    ent.bind("<Return>", _ok)
    tk.Button(d, text="OK", bg="#2563eb", fg="#fff",
              font=("Segoe UI", 11), relief="flat",
              command=_ok, padx=22, pady=7).pack(pady=8)
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

        self._nav_btns   = []
        self._q_frame    = None
        self._cur_tw     = None
        self._answered_lbl = None
        self._timer_lbl  = None
        self._timer_secs = WAKTU_MENIT * 60
        self._timer_id   = None

        self._build_exam()
        self._enforce_fg()

    # ── Window setup ─────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.title("Ujian PJOK Kelas 6 SD")
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

        tk.Label(tb, text="UJIAN PJOK  \u2022  KELAS 6 SD",
                 bg=C["topbar"], fg="#93c5fd",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=18, pady=10)

        self._answered_lbl = tk.Label(tb, text="",
                                      bg=C["topbar"], fg="#86efac",
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
        tk.Button(bf, text="Keluar (Guru)",
                  bg=C["btn_exit"], fg="#fff",
                  font=("Segoe UI", 10),
                  relief="flat", cursor="hand2",
                  command=self._try_exit,
                  padx=10, pady=6).pack(side="left", padx=4)

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

        total     = NUM_PG + NUM_ESAI
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
        fp  = os.path.join(HASIL_DIR, f"hasil_pjok_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN PJOK KELAS 6 SD",
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

        # ── outer scrollable container ───────────────────────
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

        # ── header ───────────────────────────────────────────
        tk.Label(f, text="UJIAN SELESAI",
                 bg=C["page"], fg="#16a34a",
                 font=("Segoe UI", 34, "bold")).pack(pady=(50, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 15)).pack(pady=(0, 20))

        # ── score card ───────────────────────────────────────
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

        # ── wrong answers review ──────────────────────────────
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

        tk.Label(f, text="Tekan Ctrl+Alt+Backspace untuk keluar (guru).",
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
