#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian IPAS Kelas 6 SD
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
#  POOL SOAL PILIHAN GANDA  (100 soal – diambil 45 per sesi)
#  Tingkat kesulitan: Mudah (1–56) → Menengah (57–78) → Sulit (79–100)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ══════════════════════════════════════════════════════════
    # MUDAH (1–56)
    # ══════════════════════════════════════════════════════════

    # ── PERUBAHAN BENDA ──────────────────────────────────────
    {"p": "Perubahan wujud dari es menjadi air disebut …",
     "o": ["Membeku", "Mencair", "Menyublim", "Mengembun"],
     "j": 1},

    {"p": "Perubahan wujud dari air menjadi uap disebut …",
     "o": ["Mencair", "Membeku", "Menguap", "Mengembun"],
     "j": 2},

    {"p": "Perubahan wujud dari uap air menjadi titik-titik air disebut …",
     "o": ["Menguap", "Membeku", "Mencair", "Mengembun"],
     "j": 3},

    {"p": "Besi yang dibiarkan lama di udara terbuka dan terkena air akan mengalami …",
     "o": ["Pelapukan", "Perkaratan", "Pembusukan", "Penyubliman"],
     "j": 1},

    {"p": "Proses pembusukan pada makanan disebabkan oleh …",
     "o": ["Sinar matahari", "Angin kencang", "Bakteri dan jamur", "Air hujan"],
     "j": 2},

    {"p": "Benda yang dipanaskan akan mengalami …",
     "o": ["Penyusutan", "Pemuaian", "Pembekuan", "Pelapukan"],
     "j": 1},

    {"p": "Kayu yang lapuk di hutan terutama disebabkan oleh …",
     "o": ["Gaya gravitasi", "Udara panas", "Jamur dan air", "Debu dan pasir"],
     "j": 2},

    {"p": "Perubahan yang terjadi pada kertas yang dibakar adalah perubahan …",
     "o": ["Fisika", "Kimia", "Wujud sementara", "Bentuk saja"],
     "j": 1},

    {"p": "Es krim yang dibiarkan di luar kulkas akan …",
     "o": ["Membeku", "Mencair", "Mengembun", "Menyublim"],
     "j": 1},

    {"p": "Faktor yang memengaruhi cepat atau lambatnya perkaratan besi adalah …",
     "o": ["Warna besi", "Berat besi", "Kelembapan udara", "Bentuk besi"],
     "j": 2},

    # ── PEMILIHAN BAHAN ──────────────────────────────────────
    {"p": "Bahan yang bersifat isolator panas adalah …",
     "o": ["Besi", "Tembaga", "Kayu", "Aluminium"],
     "j": 2},

    {"p": "Bahan yang bersifat konduktor panas adalah …",
     "o": ["Plastik", "Karet", "Kain wol", "Besi"],
     "j": 3},

    {"p": "Gagang panci terbuat dari kayu atau plastik karena bahan tersebut …",
     "o": ["Lebih murah", "Merupakan isolator panas", "Lebih ringan", "Lebih kuat"],
     "j": 1},

    {"p": "Bahan yang digunakan untuk membuat payung agar tahan air adalah …",
     "o": ["Kertas", "Kain katun biasa", "Plastik atau nilon", "Wol"],
     "j": 2},

    {"p": "Karet gelang dapat kembali ke bentuk semula setelah direntangkan. Sifat ini disebut …",
     "o": ["Keras", "Elastis", "Konduktif", "Magnetis"],
     "j": 1},

    {"p": "Bahan yang tepat untuk membuat panci memasak adalah aluminium karena …",
     "o": ["Aluminium adalah isolator panas yang baik", "Aluminium adalah konduktor panas yang baik", "Aluminium tidak bisa berkarat", "Aluminium lebih murah dari plastik"],
     "j": 1},

    {"p": "Bahan yang digunakan untuk membuat pakaian agar mudah menyerap keringat adalah …",
     "o": ["Plastik", "Nilon sintetis", "Katun", "Kaca serat"],
     "j": 2},

    {"p": "Sifat bahan yang diperlukan untuk membuat ban kendaraan adalah …",
     "o": ["Keras dan kaku", "Elastis dan kuat", "Rapuh dan ringan", "Konduktor listrik"],
     "j": 1},

    # ── GAYA DAN GERAK ───────────────────────────────────────
    {"p": "Gaya yang menyebabkan benda jatuh ke bawah adalah …",
     "o": ["Gaya gesek", "Gaya gravitasi", "Gaya magnet", "Gaya pegas"],
     "j": 1},

    {"p": "Gaya yang bekerja pada karet ketapel saat direntangkan adalah …",
     "o": ["Gaya gravitasi", "Gaya magnet", "Gaya pegas", "Gaya gesek"],
     "j": 2},

    {"p": "Gaya gesek yang terjadi antara ban mobil dan jalan membuat mobil …",
     "o": ["Bergerak lebih cepat", "Melambat atau berhenti", "Melayang", "Berputar balik"],
     "j": 1},

    {"p": "Magnet dapat menarik benda yang terbuat dari …",
     "o": ["Plastik", "Kayu", "Besi dan baja", "Karet"],
     "j": 2},

    {"p": "Benda bergerak lebih cepat jika diberi gaya yang …",
     "o": ["Lebih kecil", "Sama besar", "Lebih besar", "Berlawanan arah"],
     "j": 2},

    {"p": "Contoh penerapan gaya pegas dalam kehidupan sehari-hari adalah …",
     "o": ["Batu jatuh dari pohon", "Kasur pegas", "Besi berkarat", "Air mengalir"],
     "j": 1},

    {"p": "Gaya yang terjadi antara dua benda yang bersentuhan dan bergerak disebut …",
     "o": ["Gaya gravitasi", "Gaya magnet", "Gaya gesek", "Gaya pegas"],
     "j": 2},

    {"p": "Jika dua gaya yang sama besar bekerja dengan arah berlawanan pada benda, maka benda …",
     "o": ["Bergerak ke kanan", "Bergerak ke kiri", "Bergerak lebih cepat", "Diam atau seimbang"],
     "j": 3},

    {"p": "Buah mangga jatuh dari pohonnya disebabkan oleh …",
     "o": ["Gaya pegas", "Gaya gesek", "Gaya gravitasi bumi", "Gaya magnet"],
     "j": 2},

    {"p": "Permukaan jalan yang kasar akan menghasilkan gaya gesek yang …",
     "o": ["Lebih kecil", "Lebih besar", "Tidak ada", "Sama saja"],
     "j": 1},

    # ── ENERGI LISTRIK ───────────────────────────────────────
    {"p": "Alat yang mengubah energi gerak menjadi energi listrik adalah …",
     "o": ["Aki", "Baterai", "Dinamo/Generator", "Resistor"],
     "j": 2},

    {"p": "Baterai menghasilkan energi listrik dari energi …",
     "o": ["Panas", "Gerak", "Kimia", "Cahaya"],
     "j": 2},

    {"p": "Alat yang digunakan untuk mengukur arus listrik adalah …",
     "o": ["Voltmeter", "Amperemeter", "Ohmmeter", "Termometer"],
     "j": 1},

    {"p": "Alat yang mengubah energi listrik menjadi energi panas adalah …",
     "o": ["Kipas angin", "Lampu LED", "Radio", "Setrika"],
     "j": 3},

    {"p": "Rangkaian listrik di mana semua lampu padam jika salah satu lampu mati disebut rangkaian …",
     "o": ["Paralel", "Campuran", "Seri", "Terbuka"],
     "j": 2},

    {"p": "Bahan yang dapat menghantarkan listrik dengan baik disebut …",
     "o": ["Isolator", "Konduktor", "Semikonduktor", "Resistor"],
     "j": 1},

    {"p": "Bahan yang tidak dapat menghantarkan listrik disebut …",
     "o": ["Konduktor", "Isolator", "Generator", "Transformator"],
     "j": 1},

    {"p": "Contoh isolator listrik yang digunakan dalam kehidupan sehari-hari adalah …",
     "o": ["Kawat tembaga", "Besi", "Aluminium", "Plastik dan karet"],
     "j": 3},

    {"p": "Alat yang mengubah energi listrik menjadi energi gerak adalah …",
     "o": ["Setrika", "Lampu pijar", "Kipas angin", "Pemanas air"],
     "j": 2},

    {"p": "Voltmeter digunakan untuk mengukur …",
     "o": ["Arus listrik", "Hambatan listrik", "Tegangan listrik", "Daya listrik"],
     "j": 2},

    {"p": "Sumber energi listrik yang memanfaatkan aliran air adalah …",
     "o": ["Panel surya", "Generator angin", "PLTA", "Baterai"],
     "j": 2},

    {"p": "Rangkaian listrik di rumah menggunakan rangkaian paralel karena …",
     "o": ["Lebih mudah dipasang", "Jika satu lampu mati, lampu lain tetap menyala", "Lebih hemat listrik", "Lebih aman dari kebakaran"],
     "j": 1},

    # ── PENGHEMATAN ENERGI ───────────────────────────────────
    {"p": "Cara menghemat energi listrik di rumah yang paling tepat adalah …",
     "o": ["Menggunakan semua lampu setiap saat", "Mematikan lampu jika tidak digunakan", "Menambah jumlah lampu", "Menggunakan lampu pijar"],
     "j": 1},

    {"p": "Lampu yang lebih hemat energi dibandingkan lampu pijar biasa adalah …",
     "o": ["Lampu neon kuning", "Lampu pijar besar", "Lampu LED", "Lampu minyak"],
     "j": 2},

    {"p": "Penggunaan energi matahari untuk pemanas air di rumah merupakan contoh pemanfaatan energi …",
     "o": ["Fosil", "Nuklir", "Terbarukan", "Kimia"],
     "j": 2},

    {"p": "Mengapa kita perlu menghemat energi listrik?",
     "o": ["Agar tagihan listrik tetap mahal", "Karena sumber energi terbatas dan lingkungan harus dijaga", "Agar rumah menjadi gelap", "Karena listrik tidak berguna"],
     "j": 1},

    {"p": "Sumber energi yang tidak akan habis jika digunakan terus-menerus disebut energi …",
     "o": ["Fosil", "Nuklir", "Terbarukan", "Batu bara"],
     "j": 2},

    {"p": "Bel listrik mengubah energi listrik menjadi energi …",
     "o": ["Panas", "Cahaya", "Bunyi", "Gerak"],
     "j": 2},

    # ── TATA SURYA ───────────────────────────────────────────
    {"p": "Planet yang paling dekat dengan Matahari adalah …",
     "o": ["Venus", "Bumi", "Merkurius", "Mars"],
     "j": 2},

    {"p": "Planet yang memiliki cincin indah di sekitarnya adalah …",
     "o": ["Mars", "Saturnus", "Venus", "Merkurius"],
     "j": 1},

    {"p": "Benda langit yang mengorbit planet disebut …",
     "o": ["Komet", "Asteroid", "Satelit", "Meteor"],
     "j": 2},

    {"p": "Bumi berada pada urutan ke berapa dari Matahari dalam tata surya?",
     "o": ["Pertama", "Kedua", "Ketiga", "Keempat"],
     "j": 2},

    {"p": "Benda langit yang berpijar sendiri karena menghasilkan panas dan cahaya disebut …",
     "o": ["Planet", "Satelit", "Bintang", "Meteor"],
     "j": 2},

    {"p": "Komet disebut juga bintang …",
     "o": ["Jatuh", "Berekor", "Berpijar", "Berputar"],
     "j": 1},

    # ── ROTASI & REVOLUSI ────────────────────────────────────
    {"p": "Rotasi bumi menyebabkan terjadinya …",
     "o": ["Pergantian musim", "Perbedaan siang dan malam", "Gerhana matahari", "Kalender Hijriyah"],
     "j": 1},

    {"p": "Revolusi bumi mengelilingi matahari membutuhkan waktu …",
     "o": ["24 jam", "30 hari", "365,25 hari", "29,5 hari"],
     "j": 2},

    {"p": "Gerhana bulan terjadi ketika …",
     "o": ["Bulan berada di antara bumi dan matahari",
           "Bumi berada di antara matahari dan bulan",
           "Matahari berada di antara bumi dan bulan",
           "Bulan dan matahari sejajar di langit"],
     "j": 1},

    {"p": "Kalender Masehi didasarkan pada …",
     "o": ["Revolusi bulan", "Rotasi bumi", "Revolusi bumi", "Rotasi bulan"],
     "j": 2},

    # ══════════════════════════════════════════════════════════
    # MENENGAH (57–78) – 22 soal
    # ══════════════════════════════════════════════════════════

    {"p": "Perbedaan utama antara perubahan fisika dan perubahan kimia adalah …",
     "o": ["Perubahan fisika menghasilkan zat baru, kimia tidak",
           "Perubahan kimia menghasilkan zat baru, fisika tidak",
           "Keduanya selalu menghasilkan zat baru",
           "Keduanya tidak menghasilkan zat baru"],
     "j": 1},

    {"p": "Pelapukan yang disebabkan oleh akar tumbuhan yang menembus celah batuan disebut pelapukan …",
     "o": ["Fisika", "Kimia", "Biologi", "Mekanis"],
     "j": 2},

    {"p": "Cara yang tepat untuk mencegah perkaratan pada besi adalah …",
     "o": ["Menyimpan besi di tempat basah", "Mengecat atau melapisi besi dengan bahan anti karat", "Menambah kadar air pada besi", "Memanaskan besi setiap hari"],
     "j": 1},

    {"p": "Besi yang terkubur dalam tanah lembap akan lebih cepat berkarat karena …",
     "o": ["Tanah mengandung bakteri saja",
           "Kelembapan tinggi mempercepat reaksi oksidasi besi",
           "Tanah panas mempercepat pelapukan",
           "Tekanan tanah merusak struktur besi"],
     "j": 1},

    {"p": "Mengapa beton bertulang digunakan untuk membangun jembatan dan gedung tinggi?",
     "o": ["Ringan dan murah", "Kuat menahan beban dan tahan lama", "Mudah dibentuk seperti karet", "Tidak dapat terbakar sama sekali"],
     "j": 1},

    {"p": "Bahan yang tepat untuk membuat kabel listrik adalah tembaga yang dilapisi …",
     "o": ["Besi", "Karet atau plastik", "Aluminium", "Kayu"],
     "j": 1},

    {"p": "Contoh penerapan gaya magnet dalam kehidupan sehari-hari adalah …",
     "o": ["Ban sepeda yang mengerem", "Pintu kulkas yang menutup rapat dengan magnet", "Balon udara yang naik", "Karet yang melentur"],
     "j": 1},

    {"p": "Saat bola sepak ditendang ke atas, gaya yang bekerja saat bola berada di udara adalah …",
     "o": ["Hanya gaya tendangan", "Hanya gaya gravitasi", "Gaya gravitasi dan hambatan udara", "Tidak ada gaya yang bekerja"],
     "j": 2},

    {"p": "Perbedaan gaya sentuh dan gaya tak sentuh adalah …",
     "o": ["Gaya sentuh memerlukan kontak langsung, gaya tak sentuh tidak",
           "Gaya tak sentuh memerlukan kontak langsung, gaya sentuh tidak",
           "Keduanya memerlukan kontak langsung",
           "Keduanya tidak memerlukan kontak"],
     "j": 0},

    {"p": "Perbedaan antara aki dan baterai sebagai sumber listrik adalah …",
     "o": ["Aki sekali pakai, baterai dapat diisi ulang",
           "Baterai sekali pakai, aki dapat diisi ulang",
           "Keduanya tidak dapat diisi ulang",
           "Keduanya selalu dapat diisi ulang"],
     "j": 1},

    {"p": "Energi listrik pada panel surya berasal dari energi …",
     "o": ["Panas bumi", "Cahaya matahari", "Angin", "Air terjun"],
     "j": 1},

    {"p": "Lampu lalu lintas modern menggunakan lampu LED karena …",
     "o": ["Lebih mahal dan mewah",
           "Lebih hemat energi dan tahan lama dibanding lampu pijar",
           "LED menghasilkan lebih banyak panas",
           "LED lebih mudah rusak"],
     "j": 1},

    {"p": "Menggunakan kendaraan umum atau bersepeda merupakan cara menghemat …",
     "o": ["Energi listrik saja",
           "Bahan bakar fosil dan mengurangi polusi",
           "Air bersih",
           "Energi nuklir"],
     "j": 1},

    {"p": "Planet yang dijuluki 'planet merah' adalah …",
     "o": ["Venus", "Yupiter", "Mars", "Saturnus"],
     "j": 2},

    {"p": "Perbedaan antara meteor dan meteorit adalah …",
     "o": ["Meteor sampai ke bumi, meteorit tidak",
           "Meteorit adalah meteor yang sampai ke permukaan bumi",
           "Meteor lebih besar dari meteorit",
           "Meteorit berasal dari komet, meteor dari asteroid"],
     "j": 1},

    {"p": "Mengapa Venus lebih panas dari Merkurius meskipun Venus lebih jauh dari Matahari?",
     "o": ["Venus lebih besar dari Merkurius",
           "Venus memiliki atmosfer tebal dengan efek rumah kaca yang kuat",
           "Venus berputar lebih cepat dari Merkurius",
           "Venus memiliki lebih banyak gunung berapi aktif"],
     "j": 1},

    {"p": "Asteroid dalam tata surya sebagian besar terletak di antara orbit planet …",
     "o": ["Bumi dan Mars", "Mars dan Yupiter", "Yupiter dan Saturnus", "Saturnus dan Uranus"],
     "j": 1},

    {"p": "Kalender Hijriyah memiliki hari lebih sedikit dari kalender Masehi karena …",
     "o": ["Kalender Hijriyah didasarkan pada rotasi bulan",
           "Kalender Hijriyah didasarkan pada revolusi bulan (29,5 hari/bulan = 354 hari/tahun)",
           "Kalender Hijriyah didasarkan pada revolusi bumi",
           "Kalender Hijriyah memiliki 13 bulan"],
     "j": 1},

    {"p": "Akibat revolusi bumi adalah …",
     "o": ["Pergantian siang dan malam",
           "Perbedaan waktu di berbagai daerah",
           "Pergantian musim dan perbedaan lamanya siang dan malam",
           "Terjadinya pasang surut air laut"],
     "j": 2},

    {"p": "Gerhana matahari terjadi ketika …",
     "o": ["Bumi berada di antara matahari dan bulan",
           "Bulan berada di antara bumi dan matahari",
           "Matahari berada di antara bumi dan bulan",
           "Bumi, bulan, dan matahari membentuk segitiga"],
     "j": 1},

    {"p": "Satelit alami bumi adalah …",
     "o": ["Matahari", "Bulan", "Mars", "Venus"],
     "j": 1},

    {"p": "Peristiwa alam yang menyebabkan sebagian wilayah bumi mengalami musim hujan dan sebagian lain musim kemarau disebabkan oleh …",
     "o": ["Rotasi bumi", "Revolusi bumi dan kemiringan sumbu bumi", "Gerhana matahari", "Gravitasi bulan"],
     "j": 1},

    # ══════════════════════════════════════════════════════════
    # SULIT (79–100) – 22 soal
    # ══════════════════════════════════════════════════════════

    {"p": "Proses di mana benda padat langsung berubah menjadi gas tanpa melalui fase cair disebut …",
     "o": ["Menguap", "Menyublim", "Membeku", "Mengembun"],
     "j": 1},

    {"p": "Roti yang ditumbuhi jamur mengalami perubahan kimia karena …",
     "o": ["Hanya berubah warna saja",
           "Terbentuk zat baru yang tidak dapat kembali ke bentuk semula",
           "Hanya berubah bentuk saja",
           "Perubahan dapat dibalik dengan didinginkan"],
     "j": 1},

    {"p": "Faktor lingkungan yang TIDAK memengaruhi kecepatan pelapukan batu adalah …",
     "o": ["Suhu", "Kelembapan", "Warna batu", "Organisme (lumut dan jamur)"],
     "j": 2},

    {"p": "Mengapa kapal laut terbuat dari baja padahal baja lebih berat dari air?",
     "o": ["Karena baja kedap air sehingga tidak tenggelam",
           "Karena bentuk kapal yang berongga membuat volume air yang dipindahkan lebih besar dari berat kapal",
           "Karena baja bersifat mengapung di air laut",
           "Karena air laut memiliki daya dorong yang sangat kuat"],
     "j": 1},

    {"p": "Sifat bahan yang diperlukan untuk membuat peralatan medis seperti jarum suntik adalah …",
     "o": ["Lunak, tidak higienis, dan murah",
           "Keras, steril, tidak berkarat, dan tidak bereaksi dengan zat kimia tubuh",
           "Elastis, mudah dibengkokkan, dan berwarna",
           "Ringan, transparan, dan mudah terurai"],
     "j": 1},

    {"p": "Seorang astronot di luar angkasa melayang karena …",
     "o": ["Di luar angkasa tidak ada udara",
           "Gaya gravitasi di luar angkasa hampir nol",
           "Pakaian astronot sangat ringan",
           "Kecepatan pesawat terlalu tinggi"],
     "j": 1},

    {"p": "Sebuah buku diam di atas meja. Kondisi gaya yang bekerja pada buku tersebut adalah …",
     "o": ["Hanya gaya gravitasi ke bawah",
           "Gaya gravitasi ke bawah dan gaya normal meja ke atas yang seimbang",
           "Tidak ada gaya yang bekerja",
           "Hanya gaya normal meja ke atas"],
     "j": 1},

    {"p": "Mengapa rem pada kendaraan dirancang untuk meningkatkan gaya gesek?",
     "o": ["Agar kendaraan bergerak lebih cepat",
           "Agar roda kendaraan dapat berhenti dengan memperbesar hambatan gerak",
           "Agar kendaraan dapat berbelok lebih mudah",
           "Agar ban tidak cepat aus"],
     "j": 1},

    {"p": "Pada pembangkit listrik tenaga air (PLTA), urutan perubahan energi yang terjadi adalah …",
     "o": ["Energi listrik → energi gerak → energi potensial",
           "Energi potensial air → energi gerak → energi listrik",
           "Energi panas → energi gerak → energi listrik",
           "Energi kimia → energi listrik → energi gerak"],
     "j": 1},

    {"p": "Sebuah setrika memiliki daya 350 watt dan digunakan selama 2 jam. Energi listrik yang terpakai adalah …",
     "o": ["175 Wh", "700 Wh", "0,175 kWh", "0,7 kWh"],
     "j": 3},

    {"p": "Dampak utama penggunaan bahan bakar fosil secara berlebihan adalah …",
     "o": ["Menurunkan harga BBM",
           "Pemanasan global dan perubahan iklim akibat emisi CO₂",
           "Meningkatkan produksi oksigen",
           "Mengurangi polusi udara"],
     "j": 1},

    {"p": "Panel surya mengubah energi cahaya matahari menjadi energi listrik menggunakan efek …",
     "o": ["Elektromagnetik", "Fotolistrik (fotovoltaik)", "Termoelektrik", "Piezoelektrik"],
     "j": 1},

    {"p": "Urutan planet dalam tata surya dari yang terdekat ke terjauh dari Matahari adalah …",
     "o": ["Merkurius, Venus, Bumi, Mars, Yupiter, Saturnus, Uranus, Neptunus",
           "Venus, Merkurius, Bumi, Mars, Yupiter, Saturnus, Uranus, Neptunus",
           "Merkurius, Bumi, Venus, Mars, Yupiter, Saturnus, Uranus, Neptunus",
           "Merkurius, Venus, Mars, Bumi, Yupiter, Saturnus, Uranus, Neptunus"],
     "j": 0},

    {"p": "Mengapa Pluto tidak lagi dikategorikan sebagai planet dalam tata surya?",
     "o": ["Karena Pluto terlalu kecil untuk dilihat dari bumi",
           "Karena Pluto tidak memenuhi syarat planet: tidak membersihkan orbitnya dari benda langit lain",
           "Karena Pluto bergerak terlalu lambat mengelilingi matahari",
           "Karena Pluto tidak memiliki satelit"],
     "j": 1},

    {"p": "Planet Yupiter disebut raksasa tata surya karena …",
     "o": ["Memiliki suhu permukaan paling tinggi",
           "Merupakan planet terbesar dengan massa melebihi gabungan semua planet lain",
           "Paling dekat dengan matahari",
           "Memiliki cincin paling indah"],
     "j": 1},

    {"p": "Gerhana matahari total hanya terlihat dari sebagian kecil wilayah bumi karena …",
     "o": ["Gerhana terjadi sangat singkat sehingga sulit terlihat",
           "Bayangan umbra bulan berukuran kecil dan hanya jatuh pada sebagian kecil permukaan bumi",
           "Gerhana hanya terjadi di belahan bumi utara",
           "Cahaya matahari terlalu kuat untuk tertutup penuh"],
     "j": 1},

    {"p": "Perbedaan umbra dan penumbra dalam gerhana adalah …",
     "o": ["Umbra adalah bayangan terang, penumbra adalah bayangan gelap",
           "Umbra adalah bayangan gelap total, penumbra adalah bayangan setengah gelap",
           "Umbra terjadi saat gerhana bulan, penumbra terjadi saat gerhana matahari",
           "Umbra dan penumbra adalah istilah yang sama"],
     "j": 1},

    {"p": "Mengapa tahun kabisat ditambahkan 1 hari pada bulan Februari setiap 4 tahun?",
     "o": ["Karena kalender Masehi lebih pendek dari kalender Hijriyah",
           "Karena revolusi bumi sebenarnya 365,25 hari sehingga setiap 4 tahun terkumpul 1 hari penuh",
           "Karena bulan Februari selalu memiliki hari paling sedikit",
           "Karena rotasi bumi sedikit melambat setiap 4 tahun"],
     "j": 1},

    {"p": "Pengaruh gravitasi bulan terhadap bumi yang dirasakan di permukaan laut adalah …",
     "o": ["Menyebabkan rotasi bumi lebih cepat",
           "Menyebabkan pasang surut air laut",
           "Menyebabkan gerhana setiap malam purnama",
           "Menyebabkan pergantian musim"],
     "j": 1},

    {"p": "Pernyataan yang BENAR tentang perbedaan kalender Masehi dan Hijriyah adalah …",
     "o": ["Masehi berdasarkan revolusi bulan (354 hari), Hijriyah berdasarkan revolusi bumi (365 hari)",
           "Masehi berdasarkan revolusi bumi (365 hari), Hijriyah berdasarkan revolusi bulan (354 hari)",
           "Keduanya berdasarkan revolusi bumi dengan jumlah hari sama",
           "Keduanya berdasarkan revolusi bulan dengan jumlah hari sama"],
     "j": 1},

    {"p": "Mengapa bumi adalah satu-satunya planet dalam tata surya yang diketahui dihuni makhluk hidup?",
     "o": ["Karena bumi adalah planet terbesar",
           "Karena bumi memiliki suhu yang sesuai, air cair, atmosfer beroksigen, dan lapisan pelindung ozon",
           "Karena bumi paling dekat dengan matahari",
           "Karena bumi memiliki paling banyak satelit alami"],
     "j": 1},

    {"p": "Gerhana matahari cincin terjadi ketika …",
     "o": ["Bulan sepenuhnya menutupi matahari",
           "Bulan terlalu jauh dari bumi sehingga hanya bagian tengah matahari yang tertutup",
           "Bumi menutupi sebagian cahaya matahari ke bulan",
           "Matahari berada di antara bumi dan bulan"],
     "j": 1},
]

# ─────────────────────────────────────────────────────────────
#  POOL ESAI  (17 soal – diambil 5 per sesi)
#  Soal nomor 17 (indeks 16) SELALU keluar
# ─────────────────────────────────────────────────────────────
ESAI_WAJIB_IDX = 16

ESAI_POOL = [
    # 0
    {"p": "Jelaskan faktor-faktor yang memengaruhi perubahan pada benda!",
     "pedoman": "Suhu, tekanan, kelembapan, cahaya matahari, waktu, dan kuman/mikroorganisme (bakteri dan jamur)."},
    # 1
    {"p": "Mengapa kaktus memiliki daun berbentuk duri?",
     "pedoman": "Untuk mengurangi penguapan air sehingga kaktus dapat bertahan hidup di lingkungan gurun yang sangat kering."},
    # 2
    {"p": "Sebutkan contoh benda konduktor dan isolator panas beserta penggunaannya dalam kehidupan sehari-hari!",
     "pedoman": "Konduktor: besi/aluminium (panci, wajan) karena menghantarkan panas dengan baik. Isolator: kayu/plastik (gagang panci) karena menghambat perpindahan panas agar tangan tidak terbakar."},
    # 3
    {"p": "Apa manfaat menghemat energi listrik di rumah?",
     "pedoman": "Mengurangi biaya tagihan listrik, menjaga ketersediaan sumber energi agar tidak cepat habis, dan mengurangi dampak pencemaran lingkungan dari pembangkit listrik."},
    # 4
    {"p": "Jelaskan perbedaan rotasi dan revolusi bumi!",
     "pedoman": "Rotasi: bumi berputar pada porosnya sendiri dalam waktu 24 jam, mengakibatkan siang dan malam. Revolusi: bumi mengelilingi matahari dalam waktu 365,25 hari, mengakibatkan pergantian musim dan perhitungan tahun."},
    # 5
    {"p": "Apa yang menyebabkan terjadinya gerhana matahari?",
     "pedoman": "Gerhana matahari terjadi ketika bulan berada di antara bumi dan matahari sehingga cahaya matahari yang menuju bumi terhalang oleh bayangan bulan."},
    # 6
    {"p": "Tuliskan manfaat mempelajari tata surya!",
     "pedoman": "Mengetahui susunan dan ciri-ciri planet, memahami fenomena alam seperti gerhana dan pasang surut, membantu pengembangan teknologi luar angkasa, dan memperluas pengetahuan ilmu sains."},
    # 7
    {"p": "Jelaskan perbedaan perubahan fisika dan perubahan kimia! Berikan contoh masing-masing!",
     "pedoman": "Perubahan fisika: tidak menghasilkan zat baru dan dapat dikembalikan (contoh: es mencair, kertas dipotong). Perubahan kimia: menghasilkan zat baru dan tidak dapat dikembalikan (contoh: kertas dibakar, makanan membusuk)."},
    # 8
    {"p": "Sebutkan 3 sumber energi terbarukan dan jelaskan cara menghasilkan listriknya!",
     "pedoman": "1. Matahari – panel surya mengubah cahaya menjadi listrik. 2. Air – PLTA menggunakan aliran air untuk memutar turbin generator. 3. Angin – kincir angin memutar generator untuk menghasilkan listrik."},
    # 9
    {"p": "Jelaskan mengapa bumi dapat mendukung kehidupan dibandingkan planet lain dalam tata surya!",
     "pedoman": "Bumi memiliki suhu yang sesuai (rata-rata 22°C), tersedia air dalam wujud cair, memiliki atmosfer yang mengandung oksigen, dan terlindung dari radiasi berbahaya oleh lapisan ozon."},
    # 10
    {"p": "Apa perbedaan antara meteor, meteorit, dan asteroid?",
     "pedoman": "Asteroid: benda langit berbatu yang mengorbit matahari di antara Mars dan Yupiter. Meteor: benda langit yang terbakar saat masuk atmosfer bumi (terlihat sebagai bintang jatuh). Meteorit: meteor yang tidak habis terbakar dan mencapai permukaan bumi."},
    # 11
    {"p": "Jelaskan bagaimana rangkaian listrik seri dan paralel bekerja, serta sebutkan kelebihan masing-masing!",
     "pedoman": "Seri: komponen terhubung berurutan, arus sama di semua komponen, jika satu putus semua padam, kelebihannya sederhana. Paralel: komponen terhubung sejajar, tegangan sama, jika satu putus lainnya tetap menyala – itulah yang digunakan di rumah."},
    # 12
    {"p": "Jelaskan proses terjadinya gerhana bulan!",
     "pedoman": "Gerhana bulan terjadi ketika bumi berada di antara matahari dan bulan sehingga bayangan bumi jatuh ke permukaan bulan. Gerhana total terjadi saat seluruh bulan masuk ke bayangan umbra bumi."},
    # 13
    {"p": "Sebutkan 5 planet dalam tata surya beserta satu ciri khas masing-masing!",
     "pedoman": "Merkurius (terkecil, terdekat Matahari), Venus (terpanas, bintang fajar), Mars (berwarna merah, memiliki 2 satelit), Yupiter (terbesar), Saturnus (memiliki cincin indah dari es dan debu)."},
    # 14
    {"p": "Mengapa bahan yang digunakan untuk membuat alat masak berbeda-beda? Jelaskan berdasarkan sifatnya!",
     "pedoman": "Panci dari aluminium/stainless (konduktor panas baik agar cepat panas), gagang dari kayu/plastik (isolator agar tangan tidak terbakar), wajan berlapis teflon (anti lengket agar makanan tidak menempel), tutup dari kaca (transparan agar bisa melihat makanan)."},
    # 15
    {"p": "Jelaskan mengapa tahun kabisat terjadi setiap 4 tahun sekali!",
     "pedoman": "Karena revolusi bumi sebenarnya membutuhkan 365,25 hari. Seperempat hari yang tersisa setiap tahun dikumpulkan, sehingga setiap 4 tahun terkumpul 1 hari penuh yang ditambahkan pada bulan Februari sehingga menjadi 29 hari."},
    # 16 – SELALU KELUAR
    {"p": "Jelaskan gerakan dalam olahraga renang gaya punggung!",
     "pedoman": "Posisi tubuh telentang menghadap ke atas, kedua kaki bergerak naik turun bergantian (flutter kick), kedua tangan mengayuh bergantian ke belakang seperti baling-baling, kepala tetap di atas permukaan air, pernapasan dilakukan secara teratur."},
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
