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
#  Tingkat kesulitan ditingkatkan ~10% dari versi sebelumnya
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ══════════════════════════════════════════════════════════
    # LINGKARAN
    # ══════════════════════════════════════════════════════════

    {"p": "Sebuah lingkaran memiliki keliling 88 cm. Luas lingkaran tersebut adalah … (π = 22/7)",
     "o": ["308 cm²", "616 cm²", "154 cm²", "462 cm²"],
     "j": 1},

    {"p": "Luas sebuah lingkaran adalah 616 cm². Keliling lingkaran tersebut adalah … (π = 22/7)",
     "o": ["44 cm", "88 cm", "176 cm", "22 cm"],
     "j": 1},

    {"p": "Sebuah taman berbentuk lingkaran dengan diameter 28 m. Biaya pemasangan pagar keliling taman dengan harga Rp 75.000 per meter adalah … (π = 22/7)",
     "o": ["Rp 5.400.000", "Rp 6.300.000", "Rp 6.600.000", "Rp 4.200.000"],
     "j": 2},

    {"p": "Sebuah roda sepeda memiliki diameter 70 cm. Jarak yang ditempuh roda setelah berputar 100 kali adalah … (π = 22/7)",
     "o": ["2.200 cm", "22.000 cm", "4.400 cm", "11.000 cm"],
     "j": 1},

    {"p": "Luas daerah yang diarsir pada gambar setengah lingkaran dengan jari-jari 14 cm adalah … (π = 22/7)",
     "o": ["154 cm²", "308 cm²", "616 cm²", "77 cm²"],
     "j": 1},

    {"p": "Sebuah kolam renang berbentuk lingkaran dengan jari-jari 21 m. Keliling kolam tersebut adalah … (π = 22/7)",
     "o": ["66 m", "132 m", "198 m", "264 m"],
     "j": 1},

    {"p": "Sebuah pizza berdiameter 28 cm dipotong menjadi 8 bagian sama besar. Luas satu potong pizza tersebut adalah … (π = 22/7)",
     "o": ["38,5 cm²", "77 cm²", "154 cm²", "616 cm²"],
     "j": 1},

    {"p": "Dua lingkaran konsentris memiliki jari-jari 7 cm dan 14 cm. Luas daerah di antara dua lingkaran tersebut adalah … (π = 22/7)",
     "o": ["154 cm²", "308 cm²", "462 cm²", "616 cm²"],
     "j": 2},

    {"p": "Sebuah lapangan berbentuk setengah lingkaran dengan jari-jari 21 m. Keliling lapangan tersebut (termasuk diameter) adalah … (π = 22/7)",
     "o": ["66 m", "108 m", "132 m", "54 m"],
     "j": 1},

    {"p": "Jari-jari sebuah lingkaran diperbesar menjadi 2 kali lipat. Luas lingkaran baru dibandingkan luas lingkaran semula menjadi …",
     "o": ["2 kali", "3 kali", "4 kali", "6 kali"],
     "j": 2},

    {"p": "Sebuah taplak meja berbentuk lingkaran berdiameter 70 cm. Luas taplak meja tersebut adalah … (π = 22/7)",
     "o": ["3.850 cm²", "15.400 cm²", "7.700 cm²", "1.925 cm²"],
     "j": 0},

    {"p": "Keliling sebuah lingkaran adalah 132 cm. Jari-jari lingkaran tersebut adalah … (π = 22/7)",
     "o": ["14 cm", "21 cm", "42 cm", "7 cm"],
     "j": 1},

    {"p": "Luas sebuah lingkaran adalah 1.386 cm². Diameter lingkaran tersebut adalah … (π = 22/7)",
     "o": ["21 cm", "42 cm", "14 cm", "28 cm"],
     "j": 1},

    {"p": "Sebuah roda berdiameter 1,4 m berputar 50 kali. Jarak yang ditempuh roda adalah … (π = 22/7)",
     "o": ["110 m", "220 m", "55 m", "440 m"],
     "j": 1},

    {"p": "Sebuah taman berbentuk tiga perempat lingkaran dengan jari-jari 7 m. Luas taman tersebut adalah … (π = 22/7)",
     "o": ["38,5 m²", "77 m²", "115,5 m²", "154 m²"],
     "j": 2},

    {"p": "Apotema adalah garis yang menghubungkan …",
     "o": ["Pusat lingkaran ke titik pada keliling",
           "Dua titik pada keliling melalui pusat",
           "Pusat lingkaran tegak lurus ke tali busur",
           "Dua titik pada keliling tidak melalui pusat"],
     "j": 2},

    {"p": "Jika luas lingkaran A = 154 cm² dan luas lingkaran B = 616 cm², maka perbandingan jari-jari lingkaran A dan B adalah … (π = 22/7)",
     "o": ["1 : 2", "1 : 4", "2 : 3", "1 : 3"],
     "j": 0},

    {"p": "Sebuah lapangan olahraga berbentuk persegi panjang 30 m × 20 m. Di dalamnya terdapat lingkaran dengan jari-jari 7 m. Luas lapangan di luar lingkaran adalah … (π = 22/7)",
     "o": ["444 m²", "446 m²", "600 m²", "154 m²"],
     "j": 0},

    {"p": "Sebuah jam dinding berbentuk lingkaran memiliki jari-jari 21 cm. Panjang jarum menit yang merupakan jari-jari jam tersebut menyapu luas … setelah berputar 30 menit (setengah putaran). (π = 22/7)",
     "o": ["693 cm²", "1.386 cm²", "346,5 cm²", "2.772 cm²"],
     "j": 0},

    {"p": "Busur lingkaran merupakan …",
     "o": ["Garis lurus yang membagi lingkaran menjadi dua bagian sama besar",
           "Bagian dari keliling lingkaran di antara dua titik",
           "Jarak dari titik pusat ke titik pada keliling",
           "Garis yang menghubungkan pusat ke tali busur secara tegak lurus"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    # BANGUN RUANG – BALOK & KUBUS
    # ══════════════════════════════════════════════════════════

    {"p": "Sebuah balok memiliki luas permukaan 376 cm². Jika panjang = 10 cm dan lebar = 8 cm, maka tinggi balok tersebut adalah …",
     "o": ["5 cm", "6 cm", "7 cm", "8 cm"],
     "j": 1},

    {"p": "Sebuah kotak kayu berbentuk balok berukuran 25 cm × 15 cm × 10 cm akan dicat seluruh permukaannya. Jika biaya pengecatan Rp 500 per cm², total biaya pengecatan adalah …",
     "o": ["Rp 775.000", "Rp 925.000", "Rp 850.000", "Rp 1.150.000"],
     "j": 0},

    {"p": "Sebuah akuarium berbentuk balok berukuran 60 cm × 30 cm × 40 cm. Jika diisi air hingga ¾ penuh, volume air dalam akuarium adalah …",
     "o": ["54.000 cm³", "40.500 cm³", "72.000 cm³", "27.000 cm³"],
     "j": 0},

    {"p": "Sebuah bak mandi berbentuk balok berukuran 120 cm × 80 cm × 60 cm. Jika debit air masuk 2.000 cm³ per menit, waktu yang dibutuhkan untuk mengisi penuh bak tersebut adalah …",
     "o": ["288 menit", "576 menit", "360 menit", "144 menit"],
     "j": 0},

    {"p": "Sebuah kubus memiliki luas permukaan 294 cm². Panjang rusuk kubus tersebut adalah …",
     "o": ["5 cm", "6 cm", "7 cm", "8 cm"],
     "j": 2},

    {"p": "Sebanyak 8 kubus kecil dengan panjang rusuk 3 cm disusun membentuk satu kubus besar. Panjang rusuk kubus besar tersebut adalah …",
     "o": ["6 cm", "9 cm", "12 cm", "24 cm"],
     "j": 0},

    {"p": "Sebuah balok memiliki volume 840 cm³. Jika panjang = 14 cm dan lebar = 6 cm, maka tinggi balok tersebut adalah …",
     "o": ["8 cm", "9 cm", "10 cm", "12 cm"],
     "j": 2},

    {"p": "Dalam sebuah peti berbentuk balok berukuran 60 cm × 40 cm × 30 cm, akan dimasukkan balok kecil berukuran 10 cm × 8 cm × 6 cm. Berapa banyak balok kecil yang dapat dimasukkan?",
     "o": ["100 buah", "120 buah", "150 buah", "180 buah"],
     "j": 2},

    {"p": "Sebuah kubus diperbesar rusuknya menjadi 3 kali lipat. Perbandingan volume kubus baru dengan volume kubus semula adalah …",
     "o": ["3 : 1", "6 : 1", "9 : 1", "27 : 1"],
     "j": 3},

    {"p": "Sebuah bak berbentuk kubus memiliki volume 27.000 cm³. Panjang rusuk bak tersebut adalah …",
     "o": ["20 cm", "27 cm", "30 cm", "25 cm"],
     "j": 2},

    {"p": "Sebuah balok memiliki panjang 15 cm, lebar 10 cm, dan tinggi 8 cm. Jika panjangnya diperpanjang menjadi 20 cm, volume balok baru tersebut adalah …",
     "o": ["1.200 cm³", "1.500 cm³", "1.600 cm³", "2.400 cm³"],
     "j": 2},

    {"p": "Jumlah panjang seluruh rusuk sebuah kubus adalah 60 cm. Volume kubus tersebut adalah …",
     "o": ["25 cm³", "125 cm³", "150 cm³", "625 cm³"],
     "j": 1},

    {"p": "Sebuah kolam ikan berbentuk balok berukuran 3 m × 2 m × 1,5 m berisi air setinggi 1 m. Volume air dalam kolam tersebut adalah …",
     "o": ["3 m³", "6 m³", "9 m³", "4,5 m³"],
     "j": 1},

    {"p": "Diagonal sisi sebuah kubus dengan panjang rusuk 6 cm adalah …",
     "o": ["6√2 cm", "6√3 cm", "12 cm", "6 cm"],
     "j": 0},

    {"p": "Sebuah balok memiliki panjang rusuk-rusuknya dengan perbandingan 3 : 2 : 1. Jika volume balok = 1.536 cm³, panjang rusuk terpanjangnya adalah …",
     "o": ["16 cm", "24 cm", "32 cm", "12 cm"],
     "j": 1},

    {"p": "Sebuah jaring-jaring kubus terbuat dari karton. Jika panjang rusuk kubus = 8 cm, luas karton yang dibutuhkan adalah …",
     "o": ["64 cm²", "192 cm²", "384 cm²", "512 cm²"],
     "j": 2},

    {"p": "Luas permukaan sebuah balok adalah 2(40 + 30 + 24) = 188 cm². Jika panjang = 8 cm dan lebar = 5 cm, maka tinggi balok tersebut adalah …",
     "o": ["3 cm", "4 cm", "5 cm", "6 cm"],
     "j": 3},

    # ══════════════════════════════════════════════════════════
    # BANGUN RUANG – TABUNG, KERUCUT, BOLA
    # ══════════════════════════════════════════════════════════

    {"p": "Sebuah tabung memiliki jari-jari 7 cm dan tinggi 15 cm. Luas permukaan total tabung tersebut adalah … (π = 22/7)",
     "o": ["968 cm²", "660 cm²", "484 cm²", "1.936 cm²"],
     "j": 0},

    {"p": "Volume sebuah tabung adalah 3.080 cm³. Jika jari-jarinya 7 cm, tinggi tabung tersebut adalah … (π = 22/7)",
     "o": ["15 cm", "20 cm", "25 cm", "30 cm"],
     "j": 1},

    {"p": "Sebuah kerucut memiliki jari-jari 21 cm dan tinggi 28 cm. Volume kerucut tersebut adalah … (π = 22/7)",
     "o": ["12.936 cm³", "38.808 cm³", "12.936 cm³", "18.480 cm³"],
     "j": 0},

    {"p": "Sebuah kaleng berbentuk tabung dengan jari-jari 14 cm dan tinggi 30 cm diisi penuh dengan minyak goreng. Jika minyak dipindahkan ke kaleng kedua berdiameter sama tetapi tinggi 20 cm, berapa sisa minyak yang tidak tertampung? (π = 22/7)",
     "o": ["5.280 cm³", "6.160 cm³", "4.400 cm³", "18.480 cm³"],
     "j": 1},

    {"p": "Sebuah bola memiliki jari-jari 7 cm. Luas permukaan bola tersebut adalah … (π = 22/7)",
     "o": ["44 cm²", "154 cm²", "616 cm²", "308 cm²"],
     "j": 2},

    {"p": "Volume sebuah bola adalah 38.808 cm³. Jari-jari bola tersebut adalah … (π = 22/7)",
     "o": ["14 cm", "21 cm", "28 cm", "7 cm"],
     "j": 1},

    {"p": "Sebuah ember berbentuk tabung berdiameter 28 cm dan tinggi 35 cm. Berapa liter air yang dapat ditampung ember tersebut? (π = 22/7, 1 liter = 1.000 cm³)",
     "o": ["21,56 liter", "86,24 liter", "43,12 liter", "28 liter"],
     "j": 0},

    {"p": "Sebuah topi ulang tahun berbentuk kerucut memiliki jari-jari alas 10,5 cm dan tinggi 14 cm. Volume topi tersebut adalah … (π = 22/7)",
     "o": ["1.617 cm³", "4.851 cm³", "808,5 cm³", "3.234 cm³"],
     "j": 0},

    {"p": "Dua buah tabung A dan B memiliki jari-jari sama yaitu 7 cm. Tinggi tabung A = 20 cm dan tinggi tabung B = 15 cm. Selisih volume kedua tabung tersebut adalah … (π = 22/7)",
     "o": ["770 cm³", "1.540 cm³", "2.310 cm³", "3.080 cm³"],
     "j": 1},

    {"p": "Perbandingan volume bola besar dan bola kecil adalah 27 : 8. Jika jari-jari bola kecil = 4 cm, maka jari-jari bola besar adalah …",
     "o": ["6 cm", "8 cm", "12 cm", "9 cm"],
     "j": 0},

    {"p": "Sebuah tabung dan sebuah kerucut memiliki jari-jari dan tinggi yang sama. Jika volume tabung = 4.620 cm³, maka volume kerucut adalah … (π = 22/7)",
     "o": ["1.540 cm³", "2.310 cm³", "3.080 cm³", "924 cm³"],
     "j": 0},

    {"p": "Luas selimut sebuah kerucut dengan jari-jari 7 cm dan garis pelukis 25 cm adalah … (π = 22/7)",
     "o": ["550 cm²", "275 cm²", "1.100 cm²", "154 cm²"],
     "j": 0},

    {"p": "Sebuah bola dimasukkan ke dalam kubus. Jika jari-jari bola = 7 cm, volume kubus minimum yang diperlukan agar bola muat adalah …",
     "o": ["343 cm³", "5.488 cm³", "2.744 cm³", "1.372 cm³"],
     "j": 2},

    {"p": "Volume sebuah tabung adalah 9.240 cm³. Jika tingginya 30 cm, jari-jari tabung tersebut adalah … (π = 22/7)",
     "o": ["7 cm", "10,5 cm", "14 cm", "3,5 cm"],
     "j": 1},

    {"p": "Sebuah bola tenis memiliki jari-jari 3,5 cm. Luas permukaan bola tersebut adalah … (π = 22/7)",
     "o": ["38,5 cm²", "77 cm²", "154 cm²", "308 cm²"],
     "j": 2},

    # ══════════════════════════════════════════════════════════
    # STATISTIKA – MEAN, MEDIAN, MODUS
    # ══════════════════════════════════════════════════════════

    {"p": "Nilai ulangan 8 siswa adalah: 65, 72, 80, 68, 90, 72, 85, 76. Rata-rata nilai tersebut adalah …",
     "o": ["74,5", "75,5", "76,0", "76,5"],
     "j": 1},

    {"p": "Rata-rata nilai 7 siswa adalah 78. Jika seorang siswa baru dengan nilai 92 bergabung, rata-rata nilai 8 siswa tersebut adalah …",
     "o": ["79,5", "80", "80,5", "81"],
     "j": 0},

    {"p": "Data tinggi badan 6 siswa: 142, 148, 145, 152, 148, 155 cm. Rata-rata tinggi badan mereka adalah …",
     "o": ["148 cm", "148,3 cm", "150 cm", "148,5 cm"],
     "j": 3},

    {"p": "Rata-rata nilai ulangan matematika 9 siswa adalah 74. Jika nilai seorang siswa yang semula 60 diperbaiki menjadi 78, rata-rata nilai menjadi …",
     "o": ["74", "76", "78", "72"],
     "j": 1},

    {"p": "Nilai ulangan 10 siswa: 70, 75, 60, 85, 80, 75, 90, 65, 75, 85. Modus dari data tersebut adalah …",
     "o": ["75", "80", "85", "70"],
     "j": 0},

    {"p": "Data: 12, 15, 18, 15, 20, 18, 15, 22, 18, 15. Modus dan median data tersebut adalah …",
     "o": ["Modus = 15, Median = 16,5", "Modus = 18, Median = 15", "Modus = 15, Median = 15", "Modus = 15, Median = 18"],
     "j": 0},

    {"p": "Data nilai ujian: 55, 60, 65, 70, 75, 80, 85, 90. Median dari data tersebut adalah …",
     "o": ["70", "72,5", "75", "77,5"],
     "j": 1},

    {"p": "Rata-rata nilai 5 siswa adalah 82. Jika nilai tertinggi dikeluarkan dan rata-rata menjadi 78, nilai tertinggi siswa tersebut adalah …",
     "o": ["90", "94", "96", "98"],
     "j": 1},

    {"p": "Data: 4, 6, 8, 10, 12, 14, 16. Rata-rata dan median data tersebut adalah …",
     "o": ["Rata-rata = 10, Median = 10", "Rata-rata = 8, Median = 10", "Rata-rata = 10, Median = 12", "Rata-rata = 12, Median = 10"],
     "j": 0},

    {"p": "Nilai ulangan 12 siswa: 55, 60, 65, 70, 70, 75, 75, 80, 80, 85, 90, 95. Median dari data tersebut adalah …",
     "o": ["72,5", "75", "77,5", "80"],
     "j": 1},

    {"p": "Jumlah nilai 6 siswa adalah 480. Jika seorang siswa mendapat nilai 100, rata-rata nilai 7 siswa tersebut adalah …",
     "o": ["80", "82,86", "85", "83,33"],
     "j": 1},

    {"p": "Data berat badan siswa: 35, 38, 40, 40, 42, 44, 45, 48 kg. Rata-rata, median, dan modus berturut-turut adalah …",
     "o": ["41,5 – 41 – 40", "41,75 – 41 – 40", "42 – 40 – 40", "41 – 41,5 – 40"],
     "j": 0},

    {"p": "Rata-rata nilai ulangan 30 siswa adalah 76. Jika 10 siswa yang mendapat nilai di atas 80 memiliki rata-rata 86, maka rata-rata nilai 20 siswa lainnya adalah …",
     "o": ["71", "72", "73", "74"],
     "j": 0},

    {"p": "Data nilai: 60, 65, 70, 75, 75, 80, 80, 80, 85, 90. Pernyataan yang BENAR adalah …",
     "o": ["Mean = Median = Modus",
           "Modus > Median > Mean",
           "Mean < Median < Modus",
           "Median = 77,5 dan Modus = 80"],
     "j": 3},

    {"p": "Rata-rata nilai 4 tes adalah 78. Setelah tes ke-5, rata-rata menjadi 80. Nilai tes ke-5 tersebut adalah …",
     "o": ["84", "86", "88", "90"],
     "j": 2},

    # ══════════════════════════════════════════════════════════
    # STATISTIKA – DIAGRAM BATANG & ANALISIS DATA
    # ══════════════════════════════════════════════════════════

    {"p": "Diagram batang penjualan buku per bulan: Jan=120, Feb=150, Mar=90, Apr=180, Mei=135. Rata-rata penjualan per bulan adalah …",
     "o": ["130 buku", "135 buku", "140 buku", "145 buku"],
     "j": 1},

    {"p": "Data nilai ulangan kelas 6A: 65, 70, 70, 75, 75, 75, 80, 80, 85, 90. Persentase siswa yang mendapat nilai di atas 75 adalah …",
     "o": ["30%", "40%", "50%", "60%"],
     "j": 0},

    {"p": "Diagram batang kehadiran siswa: Senin=38, Selasa=35, Rabu=40, Kamis=37, Jumat=30. Jika total siswa 40 orang, persentase rata-rata kehadiran per hari adalah …",
     "o": ["90%", "92,5%", "93,75%", "95%"],
     "j": 2},

    {"p": "Data penjualan es krim selama 7 hari: 45, 38, 52, 60, 48, 55, 42. Selisih antara penjualan terbanyak dan tersedikit adalah …",
     "o": ["18 buah", "20 buah", "22 buah", "24 buah"],
     "j": 2},

    {"p": "Nilai rata-rata kelas A = 78 dengan 25 siswa dan kelas B = 82 dengan 15 siswa. Nilai rata-rata gabungan kedua kelas tersebut adalah …",
     "o": ["79,5", "80", "79", "80,5"],
     "j": 0},

    {"p": "Data frekuensi nilai: 60 (3 siswa), 70 (8 siswa), 80 (12 siswa), 90 (5 siswa), 100 (2 siswa). Rata-rata nilai kelas tersebut adalah …",
     "o": ["76,67", "78,33", "77", "79"],
     "j": 1},

    {"p": "Dalam suatu kelas, 12 siswa mendapat nilai A, 15 siswa nilai B, 8 siswa nilai C, dan 5 siswa nilai D. Persentase siswa yang mendapat nilai A atau B adalah …",
     "o": ["54%", "67,5%", "70%", "75%"],
     "j": 1},

    {"p": "Data nilai ulangan: 70, 72, 74, 76, 78, 80, 82. Jika nilai 70 diganti 84, perubahan yang terjadi adalah …",
     "o": ["Mean naik 2, Median tetap", "Mean naik 2, Median naik", "Mean naik, Median naik 2", "Mean dan Median sama-sama naik 2"],
     "j": 0},

    {"p": "Dari data: 5, 7, 8, 9, 10, 11, 12, 13, 14, 15 – nilai yang harus ditambahkan agar rata-ratanya menjadi 11 adalah …",
     "o": ["20", "21", "22", "23"],
     "j": 0},

    {"p": "Diagram batang menunjukkan nilai matematika: nilai 6 (2 siswa), nilai 7 (6 siswa), nilai 8 (10 siswa), nilai 9 (7 siswa), nilai 10 (5 siswa). Modus dan median nilai tersebut adalah …",
     "o": ["Modus = 8, Median = 8", "Modus = 8, Median = 9", "Modus = 9, Median = 8", "Modus = 8, Median = 7"],
     "j": 0},

]

# ─────────────────────────────────────────────────────────────
#  POOL ESAI  (15 soal – diambil 5 per sesi secara acak)
#  Tingkat kesulitan ditingkatkan ~10% dari versi sebelumnya
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    # 0
    {"p": "Sebuah lapangan olahraga berbentuk persegi panjang 50 m × 30 m. Di dalam lapangan tersebut terdapat lingkaran besar berdiameter 28 m. Hitunglah: (a) keliling lingkaran, (b) luas lingkaran, dan (c) luas lapangan di luar lingkaran! (π = 22/7)",
     "pedoman": "(a) K = π×d = 22/7 × 28 = 88 m. (b) L = π×r² = 22/7 × 14² = 616 m². (c) Luas persegi panjang = 50×30 = 1.500 m². Luas di luar lingkaran = 1.500 – 616 = 884 m²."},

    # 1
    {"p": "Sebuah kolam renang berbentuk balok memiliki ukuran panjang 15 m, lebar 8 m, dan kedalaman 2 m. (a) Hitunglah volume kolam! (b) Jika kolam diisi air dengan debit 500 liter per menit, berapa lama waktu yang diperlukan untuk mengisi penuh kolam? (1 m³ = 1.000 liter)",
     "pedoman": "(a) Volume = 15 × 8 × 2 = 240 m³ = 240.000 liter. (b) Waktu = 240.000 ÷ 500 = 480 menit = 8 jam."},

    # 2
    {"p": "Data nilai ulangan matematika 12 siswa: 55, 65, 70, 75, 75, 80, 80, 80, 85, 90, 90, 95. Tentukan: (a) mean, (b) median, (c) modus, dan (d) jangkauan (nilai max – nilai min) dari data tersebut!",
     "pedoman": "(a) Mean = (55+65+70+75+75+80+80+80+85+90+90+95)/12 = 940/12 ≈ 78,33. (b) Median = (80+80)/2 = 80 (data ke-6 dan ke-7). (c) Modus = 80 (muncul 3 kali). (d) Jangkauan = 95 – 55 = 40."},

    # 3
    {"p": "Sebuah tabung memiliki jari-jari 14 cm dan tinggi 25 cm. Sebuah kerucut memiliki jari-jari 14 cm dan tinggi 25 cm. (a) Hitunglah volume tabung! (b) Hitunglah volume kerucut! (c) Berapa cm³ pasir yang dibutuhkan untuk mengisi tabung jika sudah ada kerucut di dalamnya? (π = 22/7)",
     "pedoman": "(a) V tabung = π×r²×t = 22/7×14²×25 = 22/7×196×25 = 15.400 cm³. (b) V kerucut = 1/3×15.400 ≈ 5.133,33 cm³. (c) Pasir = 15.400 – 5.133,33 = 10.266,67 cm³."},

    # 4
    {"p": "Sebuah kubus besar dengan panjang rusuk 12 cm akan dipotong menjadi kubus-kubus kecil dengan panjang rusuk 3 cm. (a) Berapa banyak kubus kecil yang terbentuk? (b) Hitunglah total luas permukaan semua kubus kecil! (c) Bandingkan dengan luas permukaan kubus besar semula!",
     "pedoman": "(a) Jumlah = (12/3)³ = 4³ = 64 kubus kecil. (b) Luas 1 kubus kecil = 6×3² = 54 cm². Total = 64×54 = 3.456 cm². (c) Luas kubus besar = 6×12² = 864 cm². Total luas kubus kecil 4× lebih besar dari kubus besar."},

    # 5
    {"p": "Jelaskan perbedaan mean, median, dan modus! Kemudian dari data nilai: 72, 68, 80, 75, 68, 85, 90, 68, 75, 79 – tentukan ketiga ukuran pemusatan data tersebut!",
     "pedoman": "Mean = rata-rata (jumlah ÷ banyak data). Median = nilai tengah data yang sudah diurutkan. Modus = nilai yang paling sering muncul. Data diurutkan: 68,68,68,72,75,75,79,80,85,90. Mean = 760/10 = 76. Median = (75+75)/2 = 75. Modus = 68 (muncul 3 kali)."},

    # 6
    {"p": "Sebuah bola memiliki jari-jari 21 cm. (a) Hitunglah volume bola tersebut! (b) Hitunglah luas permukaan bola! (c) Jika bola diperkecil hingga jari-jarinya menjadi 7 cm, berapa kali volume bola semula dibandingkan volume bola baru? (π = 22/7)",
     "pedoman": "(a) V = 4/3×22/7×21³ = 4/3×22/7×9.261 = 38.808 cm³. (b) L = 4×π×r² = 4×22/7×441 = 5.544 cm². (c) V bola baru = 4/3×22/7×7³ = 1.437,33 cm³. Rasio = 38.808/1.437,33 = 27 kali."},

    # 7
    {"p": "Jelaskan bagian-bagian lingkaran berikut beserta rumusnya: (a) jari-jari dan diameter, (b) luas lingkaran, (c) keliling lingkaran, (d) luas setengah lingkaran, (e) keliling setengah lingkaran (termasuk diameter)!",
     "pedoman": "(a) r = jarak pusat ke keliling; d = 2r. (b) L = π×r². (c) K = 2×π×r = π×d. (d) L½ = ½×π×r². (e) K½ = π×r + 2r = r(π + 2)."},

    # 8
    {"p": "Data kunjungan wisatawan ke suatu tempat wisata dalam 6 bulan: Jan=1.200, Feb=980, Mar=1.450, Apr=1.680, Mei=2.100, Jun=1.790. (a) Tentukan bulan dengan kunjungan tertinggi dan terendah! (b) Hitunglah rata-rata kunjungan per bulan! (c) Bulan mana yang kunjungannya di atas rata-rata?",
     "pedoman": "(a) Tertinggi = Mei (2.100), Terendah = Feb (980). (b) Total = 9.200. Rata-rata = 9.200/6 ≈ 1.533,33. (c) Bulan di atas rata-rata: Mar (1.450 – tidak), Apr (1.680 – ya), Mei (2.100 – ya), Jun (1.790 – ya) → April, Mei, Juni."},

    # 9
    {"p": "Sebuah ember berbentuk tabung berdiameter 28 cm dan tinggi 40 cm diisi air sebanyak ¾ penuh. (a) Hitunglah volume air dalam ember! (b) Air dituangkan ke dalam botol-botol berkapasitas 1.540 cm³. Berapa botol yang dapat diisi penuh? (π = 22/7)",
     "pedoman": "(a) V tabung = π×r²×t = 22/7×14²×40 = 24.640 cm³. V air = ¾×24.640 = 18.480 cm³. (b) Jumlah botol = 18.480 ÷ 1.540 = 12 botol."},

    # 10
    {"p": "Nilai rata-rata ulangan matematika kelas 6 adalah 76. Kelas terdiri dari 30 siswa. (a) Berapakah jumlah seluruh nilai siswa? (b) Jika 5 siswa terbaik dengan rata-rata nilai 95 dikeluarkan dari perhitungan, berapa rata-rata nilai 25 siswa lainnya? (c) Apa yang terjadi pada mean jika semua nilai ditambah 4?",
     "pedoman": "(a) Jumlah = 76 × 30 = 2.280. (b) Jumlah 5 siswa terbaik = 95 × 5 = 475. Jumlah 25 siswa = 2.280 – 475 = 1.805. Rata-rata = 1.805/25 = 72,2. (c) Mean juga bertambah 4 menjadi 80."},

    # 11
    {"p": "Jelaskan sifat-sifat bangun ruang kerucut dan tabung! Sertakan jumlah titik sudut, rusuk, sisi, dan rumus volume masing-masing.",
     "pedoman": "Kerucut: titik sudut = 1 (puncak), rusuk = 1 (tepi alas), sisi = 2 (alas lingkaran + selimut), V = 1/3×π×r²×t. Tabung: titik sudut = 0, rusuk = 2 (tepi atas dan bawah), sisi = 3 (2 alas lingkaran + 1 selimut), V = π×r²×t."},

    # 12
    {"p": "Rata-rata nilai ulangan IPA, Matematika, dan Bahasa Indonesia seorang siswa adalah 82. Nilai IPA = 80 dan nilai Bahasa Indonesia = 78. (a) Berapakah nilai Matematika siswa tersebut? (b) Jika nilai Matematika diperbaiki menjadi 98, berapa rata-rata baru ketiga mata pelajaran tersebut?",
     "pedoman": "(a) Total nilai = 82×3 = 246. Nilai Mat = 246 – 80 – 78 = 88. (b) Total baru = 80 + 98 + 78 = 256. Rata-rata baru = 256/3 ≈ 85,33."},

    # 13
    {"p": "Sebuah setengah lingkaran memiliki diameter 28 cm. Di dalamnya terdapat dua lingkaran kecil yang sama besar dengan diameter masing-masing 7 cm. (a) Hitunglah luas setengah lingkaran besar! (b) Hitunglah total luas kedua lingkaran kecil! (c) Hitunglah luas daerah yang tidak ditutupi lingkaran kecil! (π = 22/7)",
     "pedoman": "(a) r besar = 14 cm. Luas ½ lingkaran = ½×22/7×14² = ½×616 = 308 cm². (b) Luas 1 lingkaran kecil = 22/7×3,5² = 38,5 cm². Total 2 lingkaran = 77 cm². (c) Luas sisa = 308 – 77 = 231 cm²."},

    # 14
    {"p": "Jelaskan perbedaan jaring-jaring kubus dan jaring-jaring balok! Kemudian, sebuah balok memiliki panjang 12 cm, lebar 8 cm, dan tinggi 5 cm. Hitunglah luas permukaan dan panjang seluruh rusuk balok tersebut!",
     "pedoman": "Jaring-jaring kubus: 6 sisi persegi sama besar. Jaring-jaring balok: 6 sisi persegi panjang dengan 3 pasang ukuran berbeda. Luas permukaan = 2(12×8 + 12×5 + 8×5) = 2(96+60+40) = 2×196 = 392 cm². Jumlah rusuk = 4(p+l+t) = 4(12+8+5) = 4×25 = 100 cm."},
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
