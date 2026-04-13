#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian Matematika Kelas 6 SD
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
#  WARNA (tema biru – Matematika)
# ─────────────────────────────────────────────────────────────
C = {
    "page":             "#f0f4f8",
    "topbar":           "#1e3a8a",
    "topbar_text":      "#ffffff",
    "nav_bg":           "#ffffff",
    "nav_todo":         "#dde3ec",
    "nav_todo_fg":      "#64748b",
    "nav_done":         "#2563eb",
    "nav_done_fg":      "#ffffff",
    "nav_curr":         "#f59e0b",
    "nav_curr_fg":      "#ffffff",
    "nav_esai_done":    "#8b5cf6",
    "nav_esai_done_fg": "#ffffff",
    "card":             "#ffffff",
    "q_pg_accent":      "#2563eb",
    "q_esai_accent":    "#7c3aed",
    "q_text":           "#1e293b",
    "q_sub":            "#64748b",
    "opt_bg":           "#f1f5f9",
    "opt_fg":           "#94a3b8",
    "opt_letter_bg":    "#e2e8f0",
    "opt_letter_fg":    "#64748b",
    "opt_sel_bg":       "#2563eb",
    "opt_sel_fg":       "#ffffff",
    "opt_sel_lbg":      "#1d4ed8",
    "opt_hover":        "#eff6ff",
    "btn_prev":         "#94a3b8",
    "btn_next":         "#2563eb",
    "btn_submit":       "#16a34a",
    "btn_exit":         "#e94560",
    "btn_text":         "#ffffff",
    "timer_ok":         "#60a5fa",
    "timer_warn":       "#f59e0b",
    "timer_crit":       "#ef4444",
    "esai_area":        "#f8fafc",
    "esai_text":        "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (80 soal – diambil 45 per sesi)
#  Materi: Lingkaran, Bangun Ruang, Statistika
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ══════════════════════════════════════════════════════════
    # LINGKARAN
    # ══════════════════════════════════════════════════════════

    {"p": "Rumus untuk menghitung luas lingkaran adalah …",
     "o": ["π × d²", "2 × π × r", "π × r²", "π × d"],
     "j": 2},

    {"p": "Jari-jari sebuah lingkaran adalah 7 cm. Luas lingkaran tersebut adalah … (π = 22/7)",
     "o": ["44 cm²", "154 cm²", "308 cm²", "616 cm²"],
     "j": 1},

    {"p": "Diameter sebuah lingkaran adalah 14 cm. Luas lingkaran tersebut adalah … (π = 22/7)",
     "o": ["154 cm²", "616 cm²", "308 cm²", "44 cm²"],
     "j": 0},

    {"p": "Sebuah lingkaran memiliki jari-jari 10 cm. Luas lingkaran tersebut adalah … (π = 3,14)",
     "o": ["314 cm²", "62,8 cm²", "628 cm²", "31,4 cm²"],
     "j": 0},

    {"p": "Jari-jari sebuah lingkaran adalah 7 cm. Keliling lingkaran tersebut adalah … (π = 22/7)",
     "o": ["22 cm", "44 cm", "88 cm", "154 cm"],
     "j": 1},

    {"p": "Rumus keliling lingkaran adalah …",
     "o": ["π × r²", "2 × π × r", "π × r", "4 × π × r"],
     "j": 1},

    {"p": "Diameter sebuah lingkaran adalah 21 cm. Keliling lingkaran adalah … (π = 22/7)",
     "o": ["66 cm", "33 cm", "132 cm", "44 cm"],
     "j": 0},

    {"p": "Rumus untuk mencari luas seperempat lingkaran adalah …",
     "o": ["1/2 × π × r²", "1/4 × π × r²", "π × r²", "3/4 × π × r²"],
     "j": 1},

    {"p": "Jari-jari lingkaran adalah 14 cm. Luas seperempat lingkaran adalah … (π = 22/7)",
     "o": ["616 cm²", "308 cm²", "154 cm²", "77 cm²"],
     "j": 2},

    {"p": "Rumus keliling setengah lingkaran (termasuk diameter) adalah …",
     "o": ["π × r", "π × r + 2r", "2π × r", "π × d"],
     "j": 1},

    {"p": "Jari-jari sebuah setengah lingkaran adalah 7 cm. Kelilingnya adalah … (π = 22/7)",
     "o": ["36 cm", "22 cm", "14 cm", "44 cm"],
     "j": 0},

    {"p": "Diameter sebuah lingkaran adalah 20 cm. Panjang jari-jari lingkaran tersebut adalah …",
     "o": ["5 cm", "10 cm", "20 cm", "40 cm"],
     "j": 1},

    {"p": "Diameter sebuah lingkaran adalah 28 cm. Jari-jari lingkaran tersebut adalah …",
     "o": ["7 cm", "14 cm", "56 cm", "28 cm"],
     "j": 1},

    {"p": "Keliling sebuah lingkaran adalah 44 cm. Jari-jari lingkaran tersebut adalah … (π = 22/7)",
     "o": ["7 cm", "14 cm", "3,5 cm", "22 cm"],
     "j": 0},

    {"p": "Luas sebuah lingkaran adalah 314 cm². Jari-jari lingkaran tersebut adalah … (π = 3,14)",
     "o": ["5 cm", "10 cm", "15 cm", "20 cm"],
     "j": 1},

    {"p": "Bagian lingkaran yang menghubungkan dua titik pada keliling dan melalui titik pusat disebut …",
     "o": ["Jari-jari", "Tali busur", "Diameter", "Busur"],
     "j": 2},

    {"p": "Bagian lingkaran dari titik pusat ke titik pada keliling disebut …",
     "o": ["Diameter", "Busur", "Apotema", "Jari-jari"],
     "j": 3},

    {"p": "Busur lingkaran adalah …",
     "o": ["Garis lurus melalui pusat lingkaran",
           "Bagian dari keliling lingkaran",
           "Jarak dari pusat ke tepi lingkaran",
           "Luas daerah dalam lingkaran"],
     "j": 1},

    {"p": "Apotema lingkaran adalah …",
     "o": ["Jarak dari pusat ke titik pada keliling",
           "Garis yang menghubungkan dua titik pada keliling",
           "Jarak tegak lurus dari pusat ke tali busur",
           "Setengah diameter"],
     "j": 2},

    {"p": "Pernyataan yang BENAR tentang lingkaran adalah …",
     "o": ["Diameter = jari-jari × 3",
           "Diameter = jari-jari × 2",
           "Jari-jari = diameter × 2",
           "Keliling = π × r"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    # BANGUN RUANG – BALOK & KUBUS
    # ══════════════════════════════════════════════════════════

    {"p": "Rumus luas permukaan balok adalah …",
     "o": ["p × l × t", "2(pl + pt + lt)", "2(p + l) × t", "(p + l + t) × 2"],
     "j": 1},

    {"p": "Sebuah balok berukuran panjang 8 cm, lebar 5 cm, dan tinggi 3 cm. Luas permukaan balok tersebut adalah …",
     "o": ["120 cm²", "79 cm²", "158 cm²", "316 cm²"],
     "j": 2},

    {"p": "Sebuah balok memiliki panjang 10 cm, lebar 4 cm, dan tinggi 6 cm. Luas permukaan balok adalah …",
     "o": ["248 cm²", "240 cm²", "124 cm²", "244 cm²"],
     "j": 0},

    {"p": "Pernyataan yang BENAR tentang balok adalah …",
     "o": ["Memiliki 6 rusuk",
           "Semua sisinya berbentuk persegi",
           "Memiliki 4 sisi",
           "Memiliki 8 titik sudut"],
     "j": 3},

    {"p": "Balok memiliki berapa rusuk?",
     "o": ["8", "10", "12", "6"],
     "j": 2},

    {"p": "Pernyataan yang SALAH tentang balok adalah …",
     "o": ["Balok memiliki 6 sisi",
           "Sisi-sisi balok berbentuk persegi panjang",
           "Balok memiliki 12 rusuk",
           "Semua rusuk balok memiliki panjang yang sama"],
     "j": 3},

    {"p": "Sisi yang saling berhadapan pada sebuah balok memiliki …",
     "o": ["Ukuran berbeda-beda",
           "Ukuran yang sama",
           "Sudut yang berbeda",
           "Tidak memiliki pasangan"],
     "j": 1},

    {"p": "Sebuah balok berukuran 12 cm × 8 cm × 5 cm. Volume balok tersebut adalah …",
     "o": ["240 cm³", "480 cm³", "960 cm³", "120 cm³"],
     "j": 1},

    {"p": "Sebuah kubus memiliki berapa titik sudut?",
     "o": ["6", "7", "8", "4"],
     "j": 2},

    {"p": "Dua buah kubus digabungkan. Jumlah total titik sudut dari kedua kubus tersebut adalah …",
     "o": ["12", "14", "16", "18"],
     "j": 2},

    {"p": "Volume sebuah kubus adalah 216 cm³. Panjang rusuknya adalah …",
     "o": ["4 cm", "5 cm", "6 cm", "7 cm"],
     "j": 2},

    {"p": "Sebuah kubus memiliki volume 512 cm³. Panjang rusuk kubus tersebut adalah …",
     "o": ["7 cm", "8 cm", "9 cm", "6 cm"],
     "j": 1},

    {"p": "Jika panjang rusuk kubus adalah 5 cm, maka volumenya adalah …",
     "o": ["25 cm³", "125 cm³", "150 cm³", "100 cm³"],
     "j": 1},

    {"p": "Sebuah kubus memiliki volume 1.000 cm³. Panjang rusuk kubus tersebut adalah …",
     "o": ["8 cm", "9 cm", "10 cm", "11 cm"],
     "j": 2},

    {"p": "Luas permukaan kubus dengan panjang rusuk 4 cm adalah …",
     "o": ["16 cm²", "64 cm²", "96 cm²", "32 cm²"],
     "j": 2},

    {"p": "Jaring-jaring balok terdiri dari berapa sisi?",
     "o": ["4", "5", "6", "8"],
     "j": 2},

    {"p": "Pada jaring-jaring balok, pasangan sisi yang berhadapan memiliki …",
     "o": ["Ukuran berbeda",
           "Ukuran yang sama",
           "Bentuk berbeda",
           "Tidak ada pasangan"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    # BANGUN RUANG – TABUNG, KERUCUT, BOLA
    # ══════════════════════════════════════════════════════════

    {"p": "Rumus volume tabung adalah …",
     "o": ["π × r² × t", "1/3 × π × r² × t", "4/3 × π × r³", "p × l × t"],
     "j": 0},

    {"p": "Rumus volume kerucut adalah …",
     "o": ["π × r² × t", "1/3 × π × r² × t", "4/3 × π × r³", "2 × π × r × t"],
     "j": 1},

    {"p": "Rumus volume bola adalah …",
     "o": ["π × r² × t", "1/3 × π × r² × t", "4/3 × π × r³", "2/3 × π × r³"],
     "j": 2},

    {"p": "Sebuah tabung memiliki jari-jari 7 cm dan tinggi 10 cm. Volume tabung tersebut adalah … (π = 22/7)",
     "o": ["1.540 cm³", "770 cm³", "3.080 cm³", "440 cm³"],
     "j": 0},

    {"p": "Rumus luas selimut tabung adalah …",
     "o": ["π × r² × t", "2 × π × r × t", "2 × π × r (r + t)", "π × r × t"],
     "j": 1},

    {"p": "Jari-jari tabung adalah 7 cm dan tingginya 10 cm. Luas selimut tabung adalah … (π = 22/7)",
     "o": ["440 cm²", "880 cm²", "220 cm²", "330 cm²"],
     "j": 0},

    {"p": "Sebuah tabung memiliki jari-jari 3,5 cm dan tinggi 10 cm. Luas selimut tabung adalah … (π = 22/7)",
     "o": ["110 cm²", "220 cm²", "330 cm²", "440 cm²"],
     "j": 1},

    {"p": "Jika tabung dan kerucut memiliki jari-jari dan tinggi yang sama, maka perbandingan volume tabung dan volume kerucut adalah …",
     "o": ["1:3", "2:1", "3:1", "1:2"],
     "j": 2},

    {"p": "Perbandingan volume tabung dan volume kerucut yang memiliki jari-jari dan tinggi sama adalah …",
     "o": ["1:3", "2:3", "3:1", "3:2"],
     "j": 2},

    {"p": "Pernyataan yang BENAR tentang perbandingan volume tabung dan kerucut (r dan t sama) adalah …",
     "o": ["Volume kerucut = volume tabung",
           "Volume tabung = 2 × volume kerucut",
           "Volume tabung = 3 × volume kerucut",
           "Volume kerucut = 2 × volume tabung"],
     "j": 2},

    {"p": "Pernyataan yang BENAR tentang bangun ruang kerucut adalah …",
     "o": ["Memiliki 2 rusuk",
           "Memiliki 2 sisi datar",
           "Memiliki 1 titik sudut",
           "Alasnya berbentuk persegi"],
     "j": 2},

    {"p": "Jumlah sisi pada bangun kerucut adalah …",
     "o": ["1", "2", "3", "4"],
     "j": 1},

    {"p": "Kerucut memiliki berapa rusuk?",
     "o": ["0", "1", "2", "3"],
     "j": 1},

    {"p": "Alas bangun kerucut berbentuk …",
     "o": ["Persegi", "Persegi panjang", "Lingkaran", "Segitiga"],
     "j": 2},

    {"p": "Jari-jari sebuah bola adalah 3 cm. Volume bola tersebut adalah … (π = 3,14)",
     "o": ["56,52 cm³", "113,04 cm³", "37,68 cm³", "150,72 cm³"],
     "j": 1},

    {"p": "Volume sebuah bola dengan jari-jari 6 cm adalah … (π = 3,14)",
     "o": ["904,32 cm³", "452,16 cm³", "226,08 cm³", "150,72 cm³"],
     "j": 0},

    # ══════════════════════════════════════════════════════════
    # STATISTIKA – MEAN, MEDIAN, MODUS
    # ══════════════════════════════════════════════════════════

    {"p": "Rumus untuk menghitung rata-rata (mean) adalah …",
     "o": ["Data terbanyak dibagi banyak data",
           "Jumlah seluruh data dibagi banyak data",
           "Data terkecil ditambah data terbesar",
           "Data tengah dibagi 2"],
     "j": 1},

    {"p": "Nilai ulangan 5 siswa adalah: 70, 80, 75, 85, 90. Rata-rata nilai tersebut adalah …",
     "o": ["75", "80", "85", "82"],
     "j": 1},

    {"p": "Rata-rata berat badan 4 siswa adalah 45 kg. Seorang siswa baru dengan berat 50 kg bergabung. Rata-rata berat badan kelima siswa tersebut adalah …",
     "o": ["46 kg", "47 kg", "45,5 kg", "48 kg"],
     "j": 0},

    {"p": "Berat badan 5 siswa adalah: 35, 38, 40, 42, 45 kg. Rata-rata berat badan mereka adalah …",
     "o": ["39 kg", "40 kg", "41 kg", "38 kg"],
     "j": 1},

    {"p": "Rata-rata tinggi badan 4 siswa adalah 135 cm. Jika siswa kelima memiliki tinggi 150 cm, rata-rata tinggi badan kelima siswa tersebut adalah …",
     "o": ["136 cm", "138 cm", "140 cm", "142 cm"],
     "j": 1},

    {"p": "Jika rata-rata nilai 5 siswa adalah 80, maka jumlah nilai kelima siswa tersebut adalah …",
     "o": ["350", "400", "450", "500"],
     "j": 1},

    {"p": "Rata-rata nilai ulangan adalah 75. Jumlah seluruh nilai adalah 600. Banyak siswa yang mengikuti ulangan adalah …",
     "o": ["6", "7", "8", "9"],
     "j": 2},

    {"p": "Rata-rata tinggi badan siswa adalah 130 cm. Jumlah seluruh tinggi badan adalah 1.820 cm. Banyak siswa tersebut adalah …",
     "o": ["12", "14", "15", "16"],
     "j": 1},

    {"p": "Data nilai 8 siswa: 65, 70, 75, 80, 85, 70, 65, 90. Nilai rata-rata adalah …",
     "o": ["72,5", "75", "77,5", "80"],
     "j": 1},

    {"p": "Modus adalah …",
     "o": ["Nilai tertinggi dalam data",
           "Nilai tengah dalam data",
           "Nilai yang paling sering muncul",
           "Rata-rata dari semua data"],
     "j": 2},

    {"p": "Data: 5, 7, 8, 7, 6, 9, 7, 5, 8, 7. Modus dari data tersebut adalah …",
     "o": ["5", "6", "7", "8"],
     "j": 2},

    {"p": "Data nilai: 6, 7, 8, 9, 7, 8, 7, 6, 8, 7. Modus dari data tersebut adalah …",
     "o": ["6", "7", "8", "9"],
     "j": 1},

    {"p": "Data: 5, 3, 7, 3, 8, 3, 9, 4, 3. Modus dari data tersebut adalah …",
     "o": ["3", "4", "5", "7"],
     "j": 0},

    {"p": "Data: 5, 7, 8, 6, 9. Median dari data tersebut adalah …",
     "o": ["7", "8", "6", "9"],
     "j": 0},

    {"p": "Data nilai ulangan: 70, 80, 65, 90, 75, 85, 60. Median dari data tersebut adalah …",
     "o": ["75", "80", "70", "65"],
     "j": 0},

    {"p": "Data: 4, 6, 8, 2, 10, 12. Median dari data tersebut adalah …",
     "o": ["7", "8", "6", "9"],
     "j": 0},

    {"p": "Median dari data: 15, 20, 25, 30, 35 adalah …",
     "o": ["20", "25", "30", "35"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    # STATISTIKA – DIAGRAM BATANG
    # ══════════════════════════════════════════════════════════

    {"p": "Pada diagram batang, sumbu vertikal biasanya menunjukkan …",
     "o": ["Nama kategori",
           "Jenis data",
           "Frekuensi atau jumlah data",
           "Urutan data"],
     "j": 2},

    {"p": "Diagram batang pengunjung museum: Senin=50, Selasa=40, Rabu=60, Kamis=45, Jumat=55. Hari dengan pengunjung paling sedikit adalah …",
     "o": ["Senin", "Selasa", "Kamis", "Jumat"],
     "j": 1},

    {"p": "Berdasarkan data pengunjung museum (Senin=50, Selasa=40, Rabu=60, Kamis=45, Jumat=55), rata-rata pengunjung per hari adalah …",
     "o": ["48", "50", "52", "54"],
     "j": 1},

    {"p": "Diagram batang nilai ulangan: data 5 siswa mendapat nilai 70, 80, 75, 85, 90. Pernyataan yang BENAR adalah …",
     "o": ["Nilai terendah adalah 75",
           "Nilai rata-rata adalah 80",
           "Nilai tertinggi adalah 90",
           "Tidak ada siswa yang mendapat nilai 75"],
     "j": 2},

    {"p": "Data nilai matematika 7 siswa: 60, 70, 80, 75, 90, 85, 70. Pernyataan yang BENAR adalah …",
     "o": ["Rata-rata nilai adalah 75",
           "Modus nilai adalah 80",
           "Nilai tertinggi adalah 90",
           "Nilai terendah adalah 65"],
     "j": 2},

    {"p": "Data nilai: 65, 70, 75, 80, 70, 65, 90, 85. Pernyataan yang BENAR adalah …",
     "o": ["Modus adalah 75",
           "Mean adalah 75",
           "Nilai terbesar adalah 85",
           "Median adalah 70"],
     "j": 1},

    {"p": "Sebuah balok memiliki 8 titik sudut dan 12 rusuk. Jumlah sisi balok tersebut adalah …",
     "o": ["4", "5", "6", "8"],
     "j": 2},

    {"p": "Rumus volume kubus dengan rusuk s adalah …",
     "o": ["s²", "6s²", "s³", "4s²"],
     "j": 2},

]

# ─────────────────────────────────────────────────────────────
#  POOL ESAI  (15 soal – diambil 5 per sesi secara acak)
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    # 0
    {"p": "Jelaskan cara menghitung luas lingkaran! Berikan contoh soal dengan jari-jari 7 cm (π = 22/7).",
     "pedoman": "Rumus: L = π × r². Contoh: L = 22/7 × 7² = 22/7 × 49 = 154 cm²."},

    # 1
    {"p": "Sebuah balok berukuran panjang 12 cm, lebar 8 cm, dan tinggi 5 cm. Hitunglah luas permukaan dan volume balok tersebut!",
     "pedoman": "LP = 2(p×l + p×t + l×t) = 2(96 + 60 + 40) = 2 × 196 = 392 cm². Volume = 12 × 8 × 5 = 480 cm³."},

    # 2
    {"p": "Data nilai ulangan matematika 10 siswa: 70, 80, 65, 75, 90, 80, 70, 85, 75, 80. Tentukan mean, median, dan modus dari data tersebut!",
     "pedoman": "Mean = (70+80+65+75+90+80+70+85+75+80)/10 = 770/10 = 77. Diurutkan: 65,70,70,75,75,80,80,80,85,90. Median = (75+80)/2 = 77,5. Modus = 80 (muncul 3 kali)."},

    # 3
    {"p": "Jelaskan perbedaan rumus volume tabung, kerucut, dan bola! Tuliskan rumusnya masing-masing.",
     "pedoman": "Volume tabung = π×r²×t. Volume kerucut = 1/3×π×r²×t. Volume bola = 4/3×π×r³. Jika r dan t sama, volume tabung = 3 × volume kerucut."},

    # 4
    {"p": "Sebuah kubus memiliki volume 343 cm³. Hitunglah panjang rusuk, luas permukaan, dan jumlah titik sudut kubus tersebut!",
     "pedoman": "s = ∛343 = 7 cm. Luas permukaan = 6 × 7² = 6 × 49 = 294 cm². Jumlah titik sudut = 8."},

    # 5
    {"p": "Jelaskan apa yang dimaksud dengan mean, median, dan modus dalam statistika!",
     "pedoman": "Mean = rata-rata (jumlah seluruh data ÷ banyak data). Median = nilai tengah setelah data diurutkan. Modus = nilai yang paling sering muncul dalam data."},

    # 6
    {"p": "Sebuah tabung memiliki jari-jari 7 cm dan tinggi 20 cm (π = 22/7). Hitunglah: (a) luas selimut, (b) luas alas, (c) volume tabung!",
     "pedoman": "(a) Luas selimut = 2 × 22/7 × 7 × 20 = 880 cm². (b) Luas alas = 22/7 × 7² = 154 cm². (c) Volume = 154 × 20 = 3.080 cm³."},

    # 7
    {"p": "Jelaskan bagian-bagian lingkaran berikut: jari-jari, diameter, busur, tali busur, dan apotema!",
     "pedoman": "Jari-jari: garis dari pusat ke keliling. Diameter: garis melalui pusat = 2 × jari-jari. Busur: bagian dari keliling lingkaran. Tali busur: garis lurus menghubungkan 2 titik di keliling. Apotema: jarak tegak lurus dari pusat ke tali busur."},

    # 8
    {"p": "Data pengunjung perpustakaan selama 5 hari: Senin=30, Selasa=25, Rabu=40, Kamis=35, Jumat=45. Tentukan: hari tersibuk, hari paling sepi, dan rata-rata pengunjung per hari!",
     "pedoman": "Hari tersibuk = Jumat (45 orang). Hari paling sepi = Selasa (25 orang). Total = 30+25+40+35+45 = 175. Rata-rata = 175 ÷ 5 = 35 orang/hari."},

    # 9
    {"p": "Jelaskan cara membaca diagram batang dan informasi apa saja yang dapat diperoleh dari diagram batang!",
     "pedoman": "Diagram batang dibaca dengan melihat tinggi batang pada sumbu vertikal (frekuensi/jumlah) dan kategori pada sumbu horizontal. Informasi yang diperoleh: nilai tertinggi dan terendah, perbandingan antar data, jumlah total, dan rata-rata."},

    # 10
    {"p": "Sebuah bola memiliki jari-jari 3 cm. Hitunglah volume bola tersebut (π = 3,14)!",
     "pedoman": "V = 4/3 × π × r³ = 4/3 × 3,14 × 3³ = 4/3 × 3,14 × 27 = 4/3 × 84,78 = 113,04 cm³."},

    # 11
    {"p": "Jelaskan sifat-sifat bangun ruang kerucut! Sebutkan jumlah titik sudut, rusuk, dan sisinya.",
     "pedoman": "Titik sudut: 1 (puncak kerucut). Rusuk: 1 (tepi alas yang berupa lingkaran). Sisi: 2 (1 alas berbentuk lingkaran + 1 selimut kerucut yang berbentuk juring). Alas kerucut berbentuk lingkaran."},

    # 12
    {"p": "Rata-rata nilai ulangan matematika suatu kelas adalah 75. Jika jumlah seluruh nilai adalah 2.250, berapa banyak siswa di kelas tersebut? Jelaskan caranya!",
     "pedoman": "Banyak siswa = jumlah seluruh nilai ÷ rata-rata = 2.250 ÷ 75 = 30 siswa."},

    # 13
    {"p": "Sebuah setengah lingkaran memiliki jari-jari 14 cm. Hitunglah luas dan keliling setengah lingkaran tersebut (π = 22/7)!",
     "pedoman": "Luas = 1/2 × π × r² = 1/2 × 22/7 × 14² = 1/2 × 616 = 308 cm². Keliling = π×r + 2r = (22/7 × 14) + (2 × 14) = 44 + 28 = 72 cm."},

    # 14
    {"p": "Jelaskan perbedaan antara jaring-jaring kubus dan jaring-jaring balok!",
     "pedoman": "Jaring-jaring kubus: 6 sisi berbentuk persegi dengan ukuran sama. Jaring-jaring balok: 6 sisi berbentuk persegi panjang dengan 3 pasang sisi yang sama ukurannya (sisi berhadapan). Kubus adalah balok khusus di mana semua rusuknya sama panjang."},
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
    tk.Button(bf, text="Ya, Kumpulkan", bg="#2563eb", fg="#fff",
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
        r.title("Ujian Matematika Kelas 6 SD")
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

        tk.Label(tb, text="UJIAN MATEMATIKA  \u2022  KELAS 6 SD",
                 bg=C["topbar"], fg="#bfdbfe",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=18, pady=10)

        self._answered_lbl = tk.Label(tb, text="",
                                      bg=C["topbar"], fg="#dbeafe",
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
                 bg="#eff6ff", fg="#2563eb",
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
        fp  = os.path.join(HASIL_DIR, f"hasil_matematika_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN MATEMATIKA KELAS 6 SD",
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
                 bg=C["page"], fg="#2563eb",
                 font=("Segoe UI", 34, "bold")).pack(pady=(50, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian Matematika!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 15)).pack(pady=(0, 20))

        card = tk.Frame(f, bg="#fff", padx=50, pady=28)
        card.pack()

        pct   = score / NUM_PG * 100
        color = "#2563eb" if pct >= 70 else "#f59e0b"

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
                         bg="#fff", fg="#2563eb",
                         font=("Segoe UI", 11),
                         anchor="w").pack(fill="x")
        else:
            tk.Label(f, text="Semua jawaban pilihan ganda benar!",
                     bg=C["page"], fg="#2563eb",
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
