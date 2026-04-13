#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian Seni Musik Kelas 6 SD
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
#  WARNA (tema ungu – Seni Musik)
# ─────────────────────────────────────────────────────────────
C = {
    "page":             "#faf5ff",
    "topbar":           "#4c1d95",
    "topbar_text":      "#ffffff",
    "nav_bg":           "#ffffff",
    "nav_todo":         "#ede9fe",
    "nav_todo_fg":      "#6d28d9",
    "nav_done":         "#7c3aed",
    "nav_done_fg":      "#ffffff",
    "nav_curr":         "#f59e0b",
    "nav_curr_fg":      "#ffffff",
    "nav_esai_done":    "#d97706",
    "nav_esai_done_fg": "#ffffff",
    "card":             "#ffffff",
    "q_pg_accent":      "#6d28d9",
    "q_esai_accent":    "#b45309",
    "q_text":           "#1e1b4b",
    "q_sub":            "#6d28d9",
    "opt_bg":           "#f5f3ff",
    "opt_fg":           "#6d28d9",
    "opt_letter_bg":    "#ede9fe",
    "opt_letter_fg":    "#4c1d95",
    "opt_sel_bg":       "#7c3aed",
    "opt_sel_fg":       "#ffffff",
    "opt_sel_lbg":      "#6d28d9",
    "opt_hover":        "#f5f3ff",
    "btn_prev":         "#94a3b8",
    "btn_next":         "#7c3aed",
    "btn_submit":       "#16a34a",
    "btn_exit":         "#e94560",
    "btn_text":         "#ffffff",
    "timer_ok":         "#a78bfa",
    "timer_warn":       "#f59e0b",
    "timer_crit":       "#ef4444",
    "esai_area":        "#fefce8",
    "esai_text":        "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (70 soal – diambil 45 per sesi)
#  Tingkat kesulitan: Mudah (1–40) → Menengah (41–56) → Sulit (57–70)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ══════════════════════════════════════════════════════════
    # MUDAH (1–40)
    # ══════════════════════════════════════════════════════════

    # ── TUTS PIANIKA ──────────────────────────────────────────
    {"p": "Tuts putih pada pianika berfungsi sebagai nada …",
     "o": ["Kromatis", "Variasi", "Asli", "Tambahan"],
     "j": 2},

    {"p": "Tuts hitam pada pianika berfungsi sebagai nada …",
     "o": ["Asli", "Pokok", "Tambahan", "Kromatis"],
     "j": 3},

    {"p": "Pianika dimainkan dengan cara …",
     "o": ["Dipetik", "Digesek", "Dipukul", "Ditiup sambil menekan tuts"],
     "j": 3},

    {"p": "Alat musik melodis yang menggunakan tuts adalah …",
     "o": ["Gitar", "Biola", "Rebana", "Pianika"],
     "j": 3},

    {"p": "Saat memainkan pianika, tuts ditekan menggunakan …",
     "o": ["Kaki", "Jari tangan", "Telapak tangan", "Siku"],
     "j": 1},

    # ── NADA & TANGGA NADA ───────────────────────────────────
    {"p": "Urutan nada pada tangga nada C mayor adalah …",
     "o": ["C-D-E-F#-G-A-B", "C-D-Eb-F-G-A-B", "C-Db-Eb-F-G-Ab-Bb", "C-D-E-F-G-A-B"],
     "j": 3},

    {"p": "Nada ke-5 (sol) pada tangga nada C mayor adalah nada …",
     "o": ["D", "E", "F", "G"],
     "j": 3},

    {"p": "Tangga nada diatonis mayor memiliki … nada pokok.",
     "o": ["5", "6", "7", "8"],
     "j": 2},

    {"p": "Solmisasi nada C dalam tangga nada C mayor adalah …",
     "o": ["Re", "Mi", "Fa", "Do"],
     "j": 3},

    {"p": "Nada ke-4 (fa) pada tangga nada C mayor adalah nada …",
     "o": ["D", "E", "F", "G"],
     "j": 2},

    # ── AKOR POKOK ────────────────────────────────────────────
    {"p": "Tiga akor pokok mayor yang sering digunakan dalam bermain musik adalah …",
     "o": ["Mayor, Minor, Kromatik", "Do, Re, Mi", "Nada, Irama, Harmoni",
           "Tonika, Subdominan, Dominan"],
     "j": 3},

    {"p": "Akor tonika pada tangga nada C mayor terdiri dari nada …",
     "o": ["F – A – C", "G – B – D", "D – F – A", "C – E – G"],
     "j": 3},

    {"p": "Akor subdominan pada tangga nada C mayor terdiri dari nada …",
     "o": ["C – E – G", "G – B – D", "D – F – A", "F – A – C"],
     "j": 3},

    {"p": "Akor dominan pada tangga nada C mayor terdiri dari nada …",
     "o": ["C – E – G", "F – A – C", "D – F – A", "G – B – D"],
     "j": 3},

    {"p": "Akor adalah …",
     "o": ["Satu nada yang dimainkan sendiri", "Tiga nada atau lebih yang dibunyikan bersamaan",
           "Irama ketukan", "Tanda dinamika"],
     "j": 1},

    # ── UNSUR MUSIK ───────────────────────────────────────────
    {"p": "Melodi dalam sebuah lagu berarti …",
     "o": ["Kata-kata yang terdapat dalam lagu", "Keselarasan bunyi",
           "Pola irama/ketukan", "Rangkaian nada yang membentuk lagu"],
     "j": 3},

    {"p": "Lirik dalam sebuah lagu berarti …",
     "o": ["Rangkaian nada yang membentuk lagu", "Irama ketukan",
           "Tangga nada", "Kata-kata yang terdapat dalam lagu"],
     "j": 3},

    {"p": "Harmoni dalam musik berarti …",
     "o": ["Pola panjang pendek bunyi", "Rangkaian melodi",
           "Kata-kata lagu", "Keselarasan bunyi yang dibunyikan bersama"],
     "j": 3},

    {"p": "Ritme dalam musik berarti …",
     "o": ["Keselarasan bunyi", "Rangkaian nada",
           "Pola irama/panjang pendek bunyi", "Lirik lagu"],
     "j": 2},

    # ── TANDA KROMATIS ────────────────────────────────────────
    {"p": "Tanda kromatis yang digunakan untuk mengembalikan nada ke nada semula adalah …",
     "o": ["# (kres)", "b (mol)", "x (kres ganda)", "\u266e (pugar)"],
     "j": 3},

    {"p": "Tanda # (kres) dalam musik berfungsi untuk …",
     "o": ["Menurunkan nada setengah laras", "Mengembalikan nada semula",
           "Memperpanjang nada", "Menaikkan nada setengah laras"],
     "j": 3},

    {"p": "Tanda b (mol) dalam musik berfungsi untuk …",
     "o": ["Menaikkan nada setengah laras", "Mengembalikan nada semula",
           "Menurunkan nada setengah laras", "Memperpanjang nada"],
     "j": 2},

    # ── NOTASI ────────────────────────────────────────────────
    {"p": "Not penuh dalam musik memiliki nilai … ketukan.",
     "o": ["1", "2", "3", "4"],
     "j": 3},

    {"p": "Not setengah dalam musik memiliki nilai … ketukan.",
     "o": ["1", "2", "3", "4"],
     "j": 1},

    {"p": "Not seperempat dalam musik memiliki nilai … ketukan.",
     "o": ["1", "2", "3", "4"],
     "j": 0},

    {"p": "Simbol not yang memiliki nilai 1/8 ketukan dalam notasi musik disebut not …",
     "o": ["Penuh", "Setengah", "Seperempat", "Seperdelapan"],
     "j": 3},

    # ── APRESIASI & KOMPONIS ──────────────────────────────────
    {"p": "Apresiasi karya musik berarti …",
     "o": ["Membuat lagu baru", "Memainkan alat musik",
           "Menghafal lirik lagu", "Menghargai dan menikmati karya musik"],
     "j": 3},

    {"p": "Komponis adalah sebutan untuk …",
     "o": ["Pemain alat musik", "Penyanyi lagu daerah",
           "Pengatur pertunjukan musik", "Pencipta/pengarang karya musik"],
     "j": 3},

    {"p": "Salah satu contoh lagu wajib nasional Indonesia adalah …",
     "o": ["Bintang Kecil", "Pelangi-Pelangi", "Balonku", "Garuda Pancasila"],
     "j": 3},

    {"p": "Lagu 'Indonesia Raya' diciptakan oleh …",
     "o": ["Ismail Marzuki", "Gesang", "H. Mutahar", "W.R. Soepratman"],
     "j": 3},

    # ── MANFAAT BERMAIN PIANIKA ───────────────────────────────
    {"p": "Salah satu manfaat bermain pianika bagi siswa adalah …",
     "o": ["Membuat siswa mengantuk", "Mengurangi konsentrasi",
           "Tidak ada manfaatnya", "Melatih koordinasi tangan dan pernapasan"],
     "j": 3},

    {"p": "Bermain pianika secara rutin dapat mengembangkan …",
     "o": ["Kemampuan berenang", "Kemampuan berlari", "Kemampuan memasak",
           "Kreativitas dan kepekaan musikal"],
     "j": 3},

    # ── BAGIAN PIANIKA ────────────────────────────────────────
    {"p": "Bagian pianika yang digunakan untuk meniupkan udara adalah …",
     "o": ["Tuts putih", "Tuts hitam", "Body pianika", "Corong/bocah tiup"],
     "j": 3},

    {"p": "Bagian pianika yang menghubungkan mulut peniup dengan badan pianika adalah …",
     "o": ["Tuts putih", "Tuts hitam", "Selang/pipa tiup", "Lubang suara"],
     "j": 2},

    {"p": "Tuts pada pianika yang letaknya lebih tinggi dan berwarna hitam menghasilkan nada …",
     "o": ["Asli", "Pokok", "Dasar", "Kromatis"],
     "j": 3},

    # ── CARA BERMAIN ──────────────────────────────────────────
    {"p": "Posisi pianika yang benar saat dimainkan adalah …",
     "o": ["Tuts menghadap ke bawah", "Diletakkan di lantai",
           "Digantung di dinding", "Tuts menghadap ke atas, ditiup lewat selang"],
     "j": 3},

    {"p": "Lagu 'Halo-Halo Bandung' diciptakan oleh …",
     "o": ["W.R. Soepratman", "Gesang", "Cornel Simanjuntak", "Ismail Marzuki"],
     "j": 3},

    {"p": "Pianika termasuk jenis alat musik …",
     "o": ["Perkusi", "Petik", "Gesek", "Tiup berkunci (melodis)"],
     "j": 3},

    {"p": "Urutan nada dari kiri ke kanan pada tuts putih pianika dimulai dari nada …",
     "o": ["G", "F", "A", "C"],
     "j": 3},

    {"p": "Tangga nada yang umum digunakan dalam memainkan pianika adalah …",
     "o": ["Tangga nada pentatonik", "Tangga nada slendro",
           "Tangga nada pelog", "Tangga nada diatonis mayor/minor"],
     "j": 3},

    # ══════════════════════════════════════════════════════════
    # MENENGAH (41–56)
    # ══════════════════════════════════════════════════════════

    {"p": "Akor dominan pada tangga nada Bes (B\u266d) mayor terdiri dari nada …",
     "o": ["Bes – D – F", "Es – G – Bes", "C – E – G", "F – A – C"],
     "j": 3},

    {"p": "Urutan nada pada tangga nada Bes (B\u266d) mayor adalah …",
     "o": ["B\u266d-C-D-E-F-G-A-B\u266d", "B\u266d-C-D\u266d-E\u266d-F-G-A\u266d-B\u266d",
           "B\u266d-C-D-E\u266d-F-G-A-B\u266d", "B\u266d-C-D-E\u266d-F-G-A\u266d-B\u266d"],
     "j": 2},

    {"p": "Posisi jari ibu jari (jari ke-1) saat memainkan akor F mayor pada pianika adalah pada tuts …",
     "o": ["C", "A", "G", "F"],
     "j": 3},

    {"p": "Saat memainkan akor F mayor pada pianika, jari kelingking (jari ke-5) berada pada tuts …",
     "o": ["F", "A", "G", "C"],
     "j": 3},

    {"p": "Pada tangga nada Bes mayor, nada-nada yang terkena tanda mol (b) adalah …",
     "o": ["F dan C", "A dan D", "G dan D", "B dan E"],
     "j": 3},

    {"p": "Dalam notasi angka, not seperdelapan (1/8) dituliskan dengan angka yang diberi …",
     "o": ["Tanda titik di atas", "Tanda lingkaran di atas",
           "Garis bawah satu", "Dua titik di bawah"],
     "j": 2},

    {"p": "Lagu 'Maju Tak Gentar' diciptakan oleh …",
     "o": ["W.R. Soepratman", "Ismail Marzuki", "H. Mutahar", "Cornel Simanjuntak"],
     "j": 3},

    {"p": "Persiapan paling pertama yang harus dilakukan sebelum membuat karya lagu adalah …",
     "o": ["Langsung merekam suara", "Membeli alat musik", "Mencari penyanyi",
           "Menentukan tema lagu"],
     "j": 3},

    {"p": "Apresiasi musik dapat dilakukan dengan cara …",
     "o": ["Mengkritik tanpa dasar", "Mengabaikan pertunjukan",
           "Membuat keributan saat pertunjukan",
           "Mendengarkan dengan seksama dan memberi penilaian positif"],
     "j": 3},

    {"p": "Sebuah lagu memiliki harmoni yang baik jika …",
     "o": ["Dimainkan oleh satu orang saja", "Nada-nadanya tidak selaras",
           "Tidak ada melodi", "Bunyi-bunyinya terdengar selaras saat dibunyikan bersama"],
     "j": 3},

    {"p": "Cara membuat karya lagu yang baik dimulai dengan menentukan …",
     "o": ["Jumlah penyanyi", "Harga alat musik", "Jadwal latihan", "Tema lagu"],
     "j": 3},

    {"p": "Pada pianika standar 32 tuts, jumlah tuts hitam adalah …",
     "o": ["10", "12", "13", "15"],
     "j": 2},

    {"p": "Tanda \u266e (pugar) dalam musik berfungsi untuk …",
     "o": ["Menaikkan nada satu laras", "Menurunkan nada satu laras",
           "Menghentikan bunyi", "Mengembalikan nada ke nada asli"],
     "j": 3},

    {"p": "Nada kromatis pada pianika dihasilkan oleh tuts …",
     "o": ["Putih paling kiri", "Putih paling kanan",
           "Semua tuts putih", "Hitam"],
     "j": 3},

    {"p": "Dalam akor F mayor pada pianika, tiga nada yang ditekan secara bersamaan adalah …",
     "o": ["C – E – G", "G – B – D", "Bes – D – F", "F – A – C"],
     "j": 3},

    {"p": "Salah satu fungsi apresiasi karya musik adalah …",
     "o": ["Mengabaikan karya orang lain", "Merusak instrumen musik",
           "Menolak jenis musik tertentu", "Menghargai kreativitas seniman"],
     "j": 3},

    # ══════════════════════════════════════════════════════════
    # SULIT (57–70)
    # ══════════════════════════════════════════════════════════

    {"p": "Interval nada (jarak antar nada) pada tangga nada C mayor mengikuti pola …",
     "o": ["1-\u00bd-1-1-1-\u00bd-1", "1-1-\u00bd-1-1-\u00bd-1",
           "1-\u00bd-1-1-\u00bd-1-1", "1-1-\u00bd-1-1-1-\u00bd"],
     "j": 3},

    {"p": "Perbedaan not 1/4 dan not 1/8 dalam satu birama 4/4 adalah …",
     "o": ["Not 1/4 = 4 ketukan, Not 1/8 = 2 ketukan",
           "Not 1/4 = 2 ketukan, Not 1/8 = 1 ketukan",
           "Not 1/4 = 3 ketukan, Not 1/8 = 1 ketukan",
           "Not 1/4 = 1 ketukan, Not 1/8 = \u00bd ketukan"],
     "j": 3},

    {"p": "Jika seseorang memainkan akor Bes mayor pada pianika, jari-jari menekan nada …",
     "o": ["F (1) – A (3) – C (5)", "C (1) – E (3) – G (5)",
           "Es (1) – G (3) – Bes (5)", "Bes (1) – D (3) – F (5)"],
     "j": 3},

    {"p": "Persiapan membuat karya lagu mencakup langkah-langkah berikut, KECUALI …",
     "o": ["Menentukan tema", "Membuat melodi",
           "Membuat lirik", "Langsung merekam tanpa persiapan"],
     "j": 3},

    {"p": "Dalam tangga nada diatonis, interval antara nada mi (E) dan fa (F) adalah …",
     "o": ["1 laras (whole step)", "2 laras", "1,5 laras", "\u00bd laras (half step)"],
     "j": 3},

    {"p": "Untuk dapat memainkan lagu sederhana di pianika, kemampuan dasar PERTAMA yang harus dikuasai adalah …",
     "o": ["Membaca notasi balok tingkat lanjut", "Menguasai akor-akor kompleks",
           "Memiliki pianika yang mahal", "Mengenal posisi tuts dan nama nada"],
     "j": 3},

    {"p": "Tanda pugar (\u266e) berlaku selama …",
     "o": ["Sepanjang lagu", "Hanya pada nada itu saja (satu birama)",
           "Dua birama", "Tiga birama"],
     "j": 1},

    {"p": "Dalam persiapan membuat karya lagu, menentukan tangga nada bertujuan untuk …",
     "o": ["Menentukan alat musik yang digunakan", "Menentukan judul lagu",
           "Menentukan jumlah penyanyi", "Menentukan wilayah nada dan suasana lagu"],
     "j": 3},

    {"p": "Ketika bermain pianika, posisi mulut yang benar adalah …",
     "o": ["Mulut terbuka sangat lebar", "Tiup dari jarak jauh",
           "Hanya meniup tanpa menekan tuts",
           "Corong ditiup dengan mulut yang mengatup rapat di sekeliling corong"],
     "j": 3},

    {"p": "Lagu 'Bagimu Negeri' diciptakan oleh …",
     "o": ["W.R. Soepratman", "Ismail Marzuki", "Cornel Simanjuntak", "H. Mutahar"],
     "j": 3},

    {"p": "Apresiasi karya musik memiliki fungsi mengembangkan …",
     "o": ["Kemampuan fisik semata", "Minat berdagang",
           "Kemampuan berhitung", "Kepekaan estetika dan rasa cinta seni"],
     "j": 3},

    {"p": "Jari yang digunakan untuk menekan tuts pertama (tuts paling kiri, nada C) pada pianika biasanya adalah …",
     "o": ["Jari kelingking", "Jari manis", "Jari tengah", "Ibu jari"],
     "j": 3},

    {"p": "Tangga nada Bes mayor memiliki … tanda mol dalam tanda mula.",
     "o": ["1", "2", "3", "4"],
     "j": 1},

    {"p": "Seorang komponis yang baik harus memahami tangga nada karena …",
     "o": ["Tangga nada tidak penting dalam musik",
           "Tangga nada hanya untuk pemula",
           "Semua lagu menggunakan tangga nada yang sama",
           "Tangga nada menentukan suasana dan karakter lagu yang diciptakan"],
     "j": 3},
]

# ─────────────────────────────────────────────────────────────
#  POOL SOAL ESAI  (17 soal – diambil 5 per sesi)
#  Soal ke-17 SELALU keluar di setiap ujian
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    # 1
    {"p": "Sebutkan 3 akor pokok mayor beserta nama dan urutan nadanya pada tangga nada C mayor!",
     "pedoman": "I = Tonika: C-E-G. IV = Subdominan: F-A-C. V = Dominan: G-B-D."},
    # 2
    {"p": "Sebutkan 5 bagian dari alat musik pianika beserta fungsinya!",
     "pedoman": "1. Badan/body pianika (ruang resonansi). 2. Tuts putih (nada asli). 3. Tuts hitam (nada kromatis). 4. Corong/bocah tiup (saluran udara dari mulut). 5. Selang/pipa tiup (penghubung mulut ke badan)."},
    # 3
    {"p": "Jelaskan 3 fungsi apresiasi karya musik!",
     "pedoman": "1. Menghargai kreativitas seniman/pencipta lagu. 2. Mengembangkan kepekaan estetika dan rasa cinta seni. 3. Memperluas wawasan dan pengetahuan tentang seni musik."},
    # 4
    {"p": "Sebutkan 5 persiapan yang harus dilakukan dalam membuat sebuah karya lagu!",
     "pedoman": "1. Menentukan tema lagu. 2. Membuat/menulis lirik. 3. Membuat melodi. 4. Menentukan tangga nada. 5. Menentukan birama/tempo."},
    # 5
    {"p": "Jelaskan tangga nada diatonis mayor yang digunakan untuk memainkan pianika beserta pola intervalnya!",
     "pedoman": "Tangga nada diatonis mayor terdiri dari 7 nada pokok (do-re-mi-fa-sol-la-si) dengan pola interval: 1-1-\u00bd-1-1-1-\u00bd laras. Contoh: C mayor = C-D-E-F-G-A-B-C."},
    # 6
    {"p": "Jelaskan posisi jari yang benar saat memainkan akor F mayor pada pianika!",
     "pedoman": "Ibu jari (jari 1) menekan tuts F, jari tengah (jari 3) menekan tuts A, kelingking (jari 5) menekan tuts C. Ketiga tuts ditekan secara bersamaan."},
    # 7
    {"p": "Jelaskan perbedaan tuts putih dan tuts hitam pada pianika!",
     "pedoman": "Tuts putih menghasilkan nada asli/natural (C-D-E-F-G-A-B). Tuts hitam menghasilkan nada kromatis (C#/Db, D#/Eb, F#/Gb, G#/Ab, A#/Bb)."},
    # 8
    {"p": "Jelaskan 3 jenis tanda kromatis dalam musik dan fungsinya masing-masing!",
     "pedoman": "1. # (kres/sharp): menaikkan nada setengah laras. 2. b (mol/flat): menurunkan nada setengah laras. 3. \u266e (pugar/natural): mengembalikan nada ke nada asli semula."},
    # 9
    {"p": "Tuliskan 7 nada pokok pada tangga nada C mayor beserta solmisasinya!",
     "pedoman": "C=Do, D=Re, E=Mi, F=Fa, G=Sol, A=La, B=Si."},
    # 10
    {"p": "Jelaskan perbedaan harmoni dan ritme dalam musik!",
     "pedoman": "Harmoni = keselarasan bunyi-bunyi yang dibunyikan secara bersamaan. Ritme = pola panjang-pendek bunyi atau ketukan dalam musik."},
    # 11
    {"p": "Sebutkan minimal 5 lagu wajib nasional Indonesia beserta penciptanya!",
     "pedoman": "Indonesia Raya (W.R. Soepratman), Garuda Pancasila (Sudharnoto), Maju Tak Gentar (Cornel Simanjuntak), Halo-Halo Bandung (Ismail Marzuki), Bagimu Negeri (H. Mutahar), Indonesia Pusaka (Ismail Marzuki)."},
    # 12
    {"p": "Jelaskan perbedaan melodi dan lirik dalam sebuah lagu!",
     "pedoman": "Melodi = rangkaian nada yang tersusun membentuk lagu (aspek musikal). Lirik = kata-kata atau teks yang dinyanyikan dalam lagu (aspek sastra/bahasa)."},
    # 13
    {"p": "Jelaskan cara bermain pianika yang benar, mulai dari persiapan hingga memainkan nada!",
     "pedoman": "1. Pegang pianika dengan tuts menghadap ke atas. 2. Pasang selang ke corong tiup. 3. Posisi tubuh tegak dan rileks. 4. Tiup dengan lembut dan merata. 5. Tekan tuts dengan jari yang tepat sesuai notasi lagu."},
    # 14
    {"p": "Jelaskan minimal 4 manfaat bermain alat musik pianika bagi siswa SD!",
     "pedoman": "1. Melatih koordinasi tangan dan pernapasan. 2. Meningkatkan konsentrasi. 3. Mengembangkan kreativitas seni. 4. Menambah rasa percaya diri. 5. Mengenal dan mencintai musik."},
    # 15
    {"p": "Sebutkan minimal 5 nama komponis Indonesia beserta salah satu karya lagu mereka!",
     "pedoman": "W.R. Soepratman \u2013 Indonesia Raya. Ismail Marzuki \u2013 Halo-Halo Bandung. Cornel Simanjuntak \u2013 Maju Tak Gentar. Gesang \u2013 Bengawan Solo. H. Mutahar \u2013 Syukur/Bagimu Negeri."},
    # 16
    {"p": "Jelaskan apa yang dimaksud dengan akor dominan dan berikan contohnya pada tangga nada C mayor!",
     "pedoman": "Akor dominan adalah akor ke-V dari suatu tangga nada. Pada tangga nada C mayor, akor dominan adalah akor G mayor yang terdiri dari nada G-B-D. Akor ini menciptakan ketegangan yang selalu ingin kembali ke tonika."},
    # 17 – SELALU KELUAR
    {"p": "Tuliskan nada-nada pada tangga nada Bes (B\u266d) mayor secara urut dari nada pertama hingga kedelapan, serta sebutkan nada mana saja yang terkena tanda mol!",
     "pedoman": "Urutan nada: B\u266d \u2013 C \u2013 D \u2013 E\u266d \u2013 F \u2013 G \u2013 A \u2013 B\u266d. Nada yang terkena tanda mol: B (menjadi B\u266d) dan E (menjadi E\u266d). Tangga nada ini memiliki 2 tanda mol dalam tanda mula."},
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

    # Pilih 4 esai secara acak dari soal 1–16, tambah soal 17 (selalu keluar)
    pool_acak   = ESAI_POOL[:16]
    selalu      = ESAI_POOL[16]
    selected_4  = random.sample(pool_acak, NUM_ESAI - 1)
    esai_merged = selected_4 + [selalu]
    random.shuffle(esai_merged)

    for q in esai_merged:
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
    tk.Button(d, text="OK", bg="#7c3aed", fg="#fff",
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
    tk.Button(bf, text="Ya, Kumpulkan", bg="#7c3aed", fg="#fff",
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
        r.title("Ujian Seni Musik Kelas 6 SD")
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

        tk.Label(tb, text="\u266b  UJIAN SENI MUSIK  \u2022  KELAS 6 SD  \u266b",
                 bg=C["topbar"], fg="#ddd6fe",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=18, pady=10)

        self._answered_lbl = tk.Label(tb, text="",
                                      bg=C["topbar"], fg="#c4b5fd",
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

        tk.Frame(nb, bg="#ddd6fe", height=1).pack(fill="x")

        inner = tk.Frame(nb, bg=C["nav_bg"])
        inner.pack(pady=6, padx=12)

        self._nav_btns = []

        pg_label_frame = tk.Frame(inner, bg=C["nav_bg"])
        pg_label_frame.pack(anchor="w")
        tk.Label(pg_label_frame, text="PG:",
                 bg=C["nav_bg"], fg="#6d28d9",
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
                 bg=C["nav_bg"], fg="#6d28d9",
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

        tk.Frame(nb, bg="#ddd6fe", height=1).pack(fill="x")

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
                 bg="#f5f3ff", fg="#6d28d9",
                 font=("Segoe UI", 9),
                 padx=4, pady=3).pack(side="left", padx=10)

        prog_frame = tk.Frame(card, bg="#ede9fe", height=5)
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

        prog_frame = tk.Frame(card, bg="#fef3c7", height=5)
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
                 bg=C["card"], fg="#92400e",
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
        fp  = os.path.join(HASIL_DIR, f"hasil_senimusik_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN SENI MUSIK KELAS 6 SD",
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

        tk.Label(f, text="\u266b  UJIAN SELESAI  \u266b",
                 bg=C["page"], fg="#6d28d9",
                 font=("Segoe UI", 34, "bold")).pack(pady=(50, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian Seni Musik!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 15)).pack(pady=(0, 20))

        card = tk.Frame(f, bg="#fff", padx=50, pady=28)
        card.pack()

        pct   = score / NUM_PG * 100
        color = "#6d28d9" if pct >= 70 else "#f59e0b"

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
            tk.Label(f, text="Semua jawaban pilihan ganda benar! \u2605",
                     bg=C["page"], fg="#6d28d9",
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
