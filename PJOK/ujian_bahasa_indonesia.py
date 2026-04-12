#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian Bahasa Indonesia Kelas 6 SD
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
    "page":           "#f0f4f8",   # latar utama abu-biru muda
    "topbar":         "#1e3a5f",   # navy gelap
    "topbar_text":    "#ffffff",
    "nav_bg":         "#ffffff",   # nav putih bersih
    "nav_todo":       "#dde3ec",   # belum dijawab: abu
    "nav_todo_fg":    "#64748b",
    "nav_done":       "#22c55e",   # sudah dijawab: hijau
    "nav_done_fg":    "#ffffff",
    "nav_curr":       "#f59e0b",   # soal aktif: amber
    "nav_curr_fg":    "#ffffff",
    "nav_esai_done":  "#8b5cf6",   # esai dijawab: ungu
    "nav_esai_done_fg": "#ffffff",
    "card":           "#ffffff",   # kartu soal putih
    "q_pg_accent":    "#2563eb",   # aksen PG: biru
    "q_esai_accent":  "#7c3aed",   # aksen Esai: ungu
    "q_text":         "#1e293b",   # teks soal hitam gelap
    "q_sub":          "#64748b",   # teks keterangan abu
    # Opsi PG
    "opt_bg":         "#f1f5f9",   # unselected bg
    "opt_fg":         "#94a3b8",   # unselected text (redup)
    "opt_letter_bg":  "#e2e8f0",   # badge huruf unselected
    "opt_letter_fg":  "#64748b",
    "opt_sel_bg":     "#2563eb",   # selected bg biru terang
    "opt_sel_fg":     "#ffffff",   # selected text putih
    "opt_sel_lbg":    "#1d4ed8",   # badge huruf selected
    "opt_hover":      "#eff6ff",   # hover
    # Tombol
    "btn_prev":       "#94a3b8",
    "btn_next":       "#2563eb",
    "btn_submit":     "#16a34a",
    "btn_exit":       "#e94560",
    "btn_text":       "#ffffff",
    # Timer
    "timer_ok":       "#22c55e",
    "timer_warn":     "#f59e0b",
    "timer_crit":     "#ef4444",
    # Essay
    "esai_area":      "#f8fafc",
    "esai_text":      "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (55 soal – diambil 45 per sesi)
# ─────────────────────────────────────────────────────────────
PG_POOL = [
    {"p": "Kalimat yang menggunakan tanda baca koma dengan benar adalah ...",
     "o": ["Ayah ibu dan adik pergi ke pasar.",
           "Ayah, ibu, dan adik pergi ke pasar.",
           "Ayah, ibu dan, adik pergi ke pasar.",
           "Ayah ibu, dan adik, pergi ke pasar."], "j": 1},

    {"p": "Penulisan huruf kapital yang benar terdapat pada kalimat ...",
     "o": ["Kami akan pergi ke Danau toba minggu depan.",
           "Kami akan pergi ke Danau Toba minggu depan.",
           "kami akan pergi ke danau toba minggu depan.",
           "Kami Akan Pergi ke Danau toba Minggu depan."], "j": 1},

    {"p": "Kata yang merupakan kata baku adalah ...",
     "o": ["Bis", "Nopember", "Apotek", "Jadual"], "j": 2},

    {"p": "Penulisan kata 'di' yang benar sebagai imbuhan terdapat pada kalimat ...",
     "o": ["Dia pergi di sekolah setiap hari.",
           "Buku itu di baca oleh Budi.",
           "Buku itu dibaca oleh Budi.",
           "Di baca lah buku itu oleh Budi."], "j": 2},

    {"p": "Kalimat efektif yang benar adalah ...",
     "o": ["Para siswa-siswa mengerjakan soal ujian.",
           "Para siswa mengerjakan soal ujian.",
           "Semua para siswa mengerjakan soal ujian.",
           "Para siswa-siswa semua mengerjakan soal ujian."], "j": 1},

    {"p": "Sinonim kata 'cantik' adalah ...",
     "o": ["Jelek", "Elok", "Buruk", "Kusam"], "j": 1},

    {"p": "Antonim kata 'rajin' adalah ...",
     "o": ["Giat", "Tekun", "Malas", "Semangat"], "j": 2},

    {"p": "Makna kata 'bersahaja' dalam kalimat 'Pak Hasan adalah orang yang bersahaja' adalah ...",
     "o": ["Sombong dan angkuh",
           "Sederhana dan rendah hati",
           "Kaya raya dan dermawan",
           "Pandai dan bijaksana"], "j": 1},

    {"p": "Ciri-ciri pantun yang benar adalah ...",
     "o": ["Terdiri dari 6 baris dan bersajak a-b-c",
           "Terdiri dari 4 baris, baris 1-2 sampiran, baris 3-4 isi",
           "Terdiri dari 4 baris, baris 1-2 isi, baris 3-4 sampiran",
           "Terdiri dari 8 baris dan bersajak a-a-b-b"], "j": 1},

    {"p": ("Perhatikan pantun berikut!\n"
           "    Buah mangga buah nangka,\n"
           "    Dibeli di pasar Senen.\n"
           "    Rajin belajar rajin membaca,\n"
           "    Supaya pintar di kemudian.\n\n"
           "Bagian sampiran pantun tersebut adalah ..."),
     "o": ["Baris 1 dan 2", "Baris 3 dan 4",
           "Baris 2 dan 3", "Baris 1 dan 4"], "j": 0},

    {"p": "Pantun yang berisi tentang nasihat atau petuah disebut ...",
     "o": ["Pantun jenaka", "Pantun teka-teki",
           "Pantun nasihat", "Pantun adat"], "j": 2},

    {"p": "Pola sajak (rima) yang benar dalam sebuah pantun adalah ...",
     "o": ["a-a-a-a", "a-b-a-b", "a-a-b-b", "a-b-c-d"], "j": 1},

    {"p": "Berikut yang BUKAN merupakan unsur puisi adalah ...",
     "o": ["Rima", "Irama", "Alur cerita", "Diksi (pilihan kata)"], "j": 2},

    {"p": "Kalimat 'Angin berbisik lembut di telingaku' menggunakan majas ...",
     "o": ["Metafora", "Simile", "Personifikasi", "Hiperbola"], "j": 2},

    {"p": "Kalimat 'Wajahnya secerah matahari pagi' menggunakan majas ...",
     "o": ["Metafora", "Simile", "Personifikasi", "Litotes"], "j": 1},

    {"p": "Gambaran tempat, waktu, dan suasana dalam sebuah cerita disebut ...",
     "o": ["Tema", "Alur", "Latar", "Amanat"], "j": 2},

    {"p": "Pesan moral yang ingin disampaikan pengarang melalui sebuah cerita disebut ...",
     "o": ["Tema", "Tokoh", "Latar", "Amanat"], "j": 3},

    {"p": "Tokoh yang memiliki sifat baik dan menjadi panutan dalam cerita disebut ...",
     "o": ["Antagonis", "Protagonis", "Tritagonis", "Figuran"], "j": 1},

    {"p": "Rangkaian peristiwa yang membentuk jalan cerita disebut ...",
     "o": ["Tema", "Latar", "Alur", "Sudut pandang"], "j": 2},

    {"p": "Cerita yang menggunakan tokoh hewan yang berperilaku seperti manusia disebut ...",
     "o": ["Legenda", "Mitos", "Fabel", "Sage"], "j": 2},

    {"p": "Pesan moral yang dapat kita ambil dari fabel 'Kancil dan Buaya' adalah ...",
     "o": ["Jangan pernah berbohong kepada siapapun",
           "Jadilah orang yang cerdik dalam menghadapi masalah",
           "Selalu patuh kepada orang yang lebih tua",
           "Jangan tamak dan serakah terhadap milik orang lain"], "j": 1},

    {"p": "Cerita rakyat yang menceritakan asal-usul suatu tempat atau benda disebut ...",
     "o": ["Mitos", "Legenda", "Sage", "Fabel"], "j": 1},

    {"p": "Dalam cerita 'Malin Kundang', amanat yang dapat diambil adalah ...",
     "o": ["Carilah kekayaan sebanyak mungkin agar dihormati",
           "Jangan durhaka kepada orang tua",
           "Jadilah pedagang yang sukses dan kaya",
           "Tinggalkan kampung halaman untuk mencari peruntungan"], "j": 1},

    {"p": "Teks yang menceritakan suatu kejadian secara berurutan berdasarkan waktu disebut ...",
     "o": ["Teks deskripsi", "Teks eksposisi",
           "Teks narasi", "Teks persuasi"], "j": 2},

    {"p": "Teks yang menggambarkan suatu objek sehingga pembaca seolah-olah melihat langsung disebut ...",
     "o": ["Teks narasi", "Teks deskripsi",
           "Teks argumentasi", "Teks prosedur"], "j": 1},

    {"p": ("Perhatikan paragraf berikut!\n"
           "'Indonesia adalah negara kepulauan yang kaya akan sumber daya alam.\n"
           "Hutan-hutannya menyimpan berbagai jenis flora dan fauna.\n"
           "Lautannya mengandung hasil laut yang melimpah.\n"
           "Tanahnya subur untuk berbagai jenis tanaman.'\n\n"
           "Kalimat utama paragraf tersebut adalah ..."),
     "o": ["Hutan-hutannya menyimpan berbagai jenis flora dan fauna.",
           "Tanahnya subur untuk berbagai jenis tanaman.",
           "Indonesia adalah negara kepulauan yang kaya akan sumber daya alam.",
           "Lautannya mengandung hasil laut yang melimpah."], "j": 2},

    {"p": "Ide pokok suatu paragraf biasanya ditemukan pada ...",
     "o": ["Kalimat penjelas", "Kalimat utama",
           "Kalimat penutup saja", "Kalimat pembuka saja"], "j": 1},

    {"p": "Kata yang menggunakan imbuhan 'me-' dengan benar adalah ...",
     "o": ["Membawa buku ke sekolah",
           "Mentidur siang hari",
           "Mepukul meja dengan keras",
           "Mepergi ke pasar pagi-pagi"], "j": 0},

    {"p": "Kata berimbuhan yang bermakna 'hasil melakukan sesuatu' terdapat pada kalimat ...",
     "o": ["Budi membuang sampah sembarangan.",
           "Tulisan Ani sangat rapi dan indah.",
           "Ibu sedang memasak di dapur.",
           "Ayah membaca koran setiap pagi."], "j": 1},

    {"p": "Kalimat pasif yang benar adalah ...",
     "o": ["Budi memakan nasi goreng itu.",
           "Nasi goreng itu dimakan oleh Budi.",
           "Budi dan nasi goreng itu dimakan.",
           "Memakan nasi goreng Budi itu."], "j": 1},

    {"p": "Penggunaan kata ulang yang benar terdapat pada kalimat ...",
     "o": ["Anak-anak itu bermain di halaman sekolah.",
           "Para anak-anak bermain di halaman sekolah.",
           "Semua anak-anak bermain di halaman sekolah.",
           "Banyak anak-anak bermain di halaman sekolah."], "j": 0},

    {"p": "Konjungsi yang menyatakan 'pertentangan' terdapat pada kalimat ...",
     "o": ["Andi belajar karena besok ada ujian.",
           "Siti pergi ke sekolah dan Budi pergi ke pasar.",
           "Rini rajin belajar tetapi nilainya tetap rendah.",
           "Dia datang ketika hujan turun deras."], "j": 2},

    {"p": ("Perhatikan teks berikut!\n"
           "'Setiap pagi, Pak Tani pergi ke sawah. Ia membajak tanah dengan\n"
           "kerbau kesayangannya. Setelah membajak, ia menanam padi.\n"
           "Pak Tani merawat padinya dengan penuh kesabaran dan ketekunan.'\n\n"
           "Watak Pak Tani dalam teks tersebut adalah ..."),
     "o": ["Malas dan ceroboh", "Rajin dan tekun",
           "Sombong dan angkuh", "Kikir dan tamak"], "j": 1},

    {"p": "Berdasarkan teks pada soal nomor 33, pekerjaan tokoh utamanya adalah ...",
     "o": ["Peternak", "Nelayan", "Petani", "Pedagang"], "j": 2},

    {"p": "Kalimat 'Dia adalah singa di medan perang' menggunakan majas ...",
     "o": ["Simile", "Metafora", "Personifikasi", "Hiperbola"], "j": 1},

    {"p": "Kalimat 'Suaranya menggelegar memecah langit' menggunakan majas ...",
     "o": ["Litotes", "Personifikasi", "Hiperbola", "Metafora"], "j": 2},

    {"p": "Penggunaan tanda titik dua (:) yang benar terdapat pada kalimat ...",
     "o": ["Ibu membeli: sayuran di pasar.",
           "Bahan yang diperlukan: tepung, gula, dan telur.",
           "Hari ini: adalah hari yang menyenangkan.",
           "Dia berkata: selamat datang kepada semua."], "j": 1},

    {"p": "Kalimat yang menyatakan permintaan atau ajakan disebut kalimat ...",
     "o": ["Kalimat berita", "Kalimat tanya",
           "Kalimat perintah", "Kalimat seru"], "j": 2},

    {"p": "Pemenggalan kata yang benar untuk kata 'membaca' adalah ...",
     "o": ["mem-ba-ca", "me-mba-ca", "mem-bac-a", "m-em-ba-ca"], "j": 0},

    {"p": "Penulisan singkatan gelar dokter umum yang benar adalah ...",
     "o": ["Dr. Budi Santoso", "dr. Budi Santoso",
           "DR. Budi Santoso", "Dr Budi Santoso"], "j": 1},

    # ── Soal tambahan untuk pool ──────────────────────────────
    {"p": "Pokok pikiran atau gagasan utama yang mendasari seluruh cerita disebut ...",
     "o": ["Alur", "Latar", "Tema", "Amanat"], "j": 2},

    {"p": "Cerita yang menggunakan sudut pandang orang pertama ditandai dengan penggunaan kata ...",
     "o": ["Dia", "Mereka", "Aku / Saya", "Beliau"], "j": 2},

    {"p": "Penulisan kata 'ke' yang benar sebagai kata depan (preposisi) adalah ...",
     "o": ["Ani pergi kesekolah pagi ini.",
           "Ani pergi ke sekolah pagi ini.",
           "Ani ke-pergi sekolah pagi ini.",
           "Ani pergi Ke Sekolah pagi ini."], "j": 1},

    {"p": "Pemenggalan kata yang benar untuk kata 'menulis' adalah ...",
     "o": ["me-nu-lis", "men-u-lis", "me-nul-is", "men-ul-is"], "j": 0},

    {"p": "Kalimat yang mengandung kalimat utama di akhir paragraf disebut paragraf ...",
     "o": ["Deduktif", "Induktif", "Campuran", "Ineratif"], "j": 1},

    {"p": "Kata yang memiliki bunyi dan tulisan sama tetapi makna berbeda disebut ...",
     "o": ["Sinonim", "Antonim", "Homonim", "Polisemi"], "j": 2},

    {"p": ("Perhatikan kalimat berikut!\n"
           "'Bisa ular itu sangat berbahaya.'\n"
           "'Kamu bisa mengerjakan soal ini dengan mudah.'\n\n"
           "Kata 'bisa' pada kedua kalimat di atas merupakan contoh ..."),
     "o": ["Sinonim", "Antonim", "Homonim", "Polisemi"], "j": 2},

    {"p": "Kalimat langsung yang penulisannya benar adalah ...",
     "o": ['Ibu berkata, ayo kita segera berangkat.',
           'Ibu berkata, "Ayo kita segera berangkat."',
           '"Ibu berkata, ayo kita segera berangkat."',
           'Ibu berkata "ayo kita segera berangkat".'], "j": 1},

    {"p": "Ungkapan 'naik daun' memiliki arti ...",
     "o": ["Sedang memanjat pohon",
           "Sedang sakit keras",
           "Sedang terkenal / populer",
           "Sedang mengalami kerugian"], "j": 2},

    {"p": "Kata berimbuhan ber- yang bermakna 'memakai atau menggunakan' terdapat pada kalimat ...",
     "o": ["Ayah berlari pagi setiap hari.",
           "Adik berseragam putih merah ke sekolah.",
           "Ibu berbicara dengan tetangga.",
           "Kakak bersepeda ke kampus."], "j": 1},

    {"p": "Cerita yang tokoh dan peristiwanya adalah rekaan pengarang disebut karya ...",
     "o": ["Nonfiksi", "Fiksi", "Biografi", "Laporan"], "j": 1},

    {"p": "Kalimat majemuk setara yang menggunakan kata penghubung 'dan' menyatakan hubungan ...",
     "o": ["Pertentangan", "Penjumlahan / penambahan",
           "Pemilihan", "Sebab-akibat"], "j": 1},

    {"p": "Kata tanya yang digunakan untuk menanyakan alasan atau sebab disebut ...",
     "o": ["Apa", "Siapa", "Mengapa", "Bagaimana"], "j": 2},

    {"p": "Kalimat yang kalimat utamanya terletak di awal paragraf disebut paragraf ...",
     "o": ["Induktif", "Deduktif", "Campuran", "Deskriptif"], "j": 1},

    {"p": "Tanda baca yang digunakan untuk mengakhiri kalimat tanya adalah ...",
     "o": ["Titik (.)", "Koma (,)", "Tanda tanya (?)", "Tanda seru (!)"], "j": 2},

    {"p": "Kata 'berlari' dan 'berjalan' merupakan contoh ...",
     "o": ["Kata ulang", "Kata berimbuhan", "Kata majemuk", "Kata sifat"], "j": 1},
]

# ─────────────────────────────────────────────────────────────
#  POOL SOAL ESAI  (10 soal – diambil 5 per sesi)
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    {"p": ("Ceritakan kembali isi cerita rakyat 'Malin Kundang' "
           "dengan bahasamu sendiri dalam 3–5 kalimat!")},
    {"p": ("Buatlah sebuah pantun nasihat yang terdiri dari 4 baris "
           "dengan pola sajak a-b-a-b!\n"
           "(Baris 1–2 = sampiran, Baris 3–4 = isi)")},
    {"p": ("Tuliskan sebuah paragraf deskripsi (3–5 kalimat) yang "
           "menggambarkan suasana pagi hari di lingkungan sekolahmu!")},
    {"p": ("Bacalah cerita singkat berikut, kemudian tentukan "
           "tema, tokoh, latar, dan amanat cerita!\n\n"
           "'Si Kecil adalah seekor semut yang rajin. Setiap hari ia mengumpulkan "
           "makanan untuk persiapan musim dingin. Berbeda dengan belalang yang hanya "
           "bermain-main. Ketika musim dingin tiba, si Kecil memiliki cukup makanan, "
           "sementara belalang kelaparan.'")},
    {"p": ("Perbaikilah kalimat-kalimat berikut menjadi kalimat efektif!\n"
           "a. 'Para hadirin-hadirin sekalian dimohon untuk berdiri.'\n"
           "b. 'Dia pergi ke sekolah dengan berjalan kaki.'\n"
           "c. 'Saya sangat amat senang sekali mendapat hadiah itu.'")},
    {"p": ("Tulislah sebuah paragraf narasi singkat (4–6 kalimat) tentang "
           "pengalamanmu yang paling berkesan! Gunakan ejaan yang benar!")},
    {"p": ("Analisislah puisi berikut!\n\n"
           "    'Guruku'\n"
           "    Kau bagai lilin yang menerangi\n"
           "    Dalam gelap kau selalu hadir\n"
           "    Ilmumu mengalir tiada henti\n"
           "    Jasamu takkan pernah terhapus\n\n"
           "a. Majas apa yang digunakan pada baris pertama?\n"
           "b. Apa tema puisi di atas?\n"
           "c. Apa amanat yang terkandung dalam puisi tersebut?")},
    {"p": ("Jelaskan perbedaan antara teks narasi dan teks deskripsi! "
           "Berikan masing-masing satu contoh kalimat!")},
    {"p": ("Tentukan kalimat utama dan kalimat-kalimat penjelas dari paragraf berikut!\n\n"
           "'Lingkungan sekolah yang bersih sangat penting bagi kesehatan siswa. "
           "Lingkungan yang bersih membuat siswa nyaman dalam belajar. "
           "Udara segar di lingkungan bersih juga membuat siswa lebih sehat. "
           "Selain itu, lingkungan bersih mencerminkan kedisiplinan warga sekolah.'")},
    {"p": ("Buatlah 5 kalimat menggunakan konjungsi/kata hubung yang berbeda "
           "dari daftar berikut:\n(karena, tetapi, sehingga, dan, meskipun)\n\n"
           "Setiap kalimat harus menggunakan satu konjungsi yang berbeda!")},
]

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
        new_answer = opts.index(correct_text)  # index 0-3 after shuffle
        prepared.append({
            "type":    "pg",
            "p":       q["p"],
            "o":       [f"{labels[i]}. {opts[i]}" for i in range(4)],
            "j":       labels[new_answer],   # correct letter A/B/C/D
        })

    # Pilih & acak Esai
    selected_esai = random.sample(ESAI_POOL, NUM_ESAI)
    for i, q in enumerate(selected_esai):
        prepared.append({"type": "esai", "p": q["p"]})

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
        self.answers     = {}      # {idx: "A"/"B"/"C"/"D" or essay string}
        self.current     = 0

        self._nav_btns   = []      # list of nav button Labels
        self._q_frame    = None    # current question frame (destroyed on navigate)
        self._cur_tw     = None    # active essay Text widget
        self._answered_lbl = None  # "X dijawab" label ref
        self._timer_lbl  = None
        self._timer_secs = WAKTU_MENIT * 60
        self._timer_id   = None

        self._build_exam()
        self._enforce_fg()

    # ── Window setup ─────────────────────────────────────────
    def _setup_window(self):
        r = self.root
        r.title("Ujian Bahasa Indonesia Kelas 6 SD")
        r.configure(bg=C["page"])
        r.attributes("-fullscreen", True)
        r.attributes("-topmost", True)
        r.overrideredirect(True)
        r.protocol("WM_DELETE_WINDOW", lambda: None)
        for seq in ("<Alt-F4>", "<Alt-Tab>", "<Escape>",
                    "<Super_L>", "<Super_R>", "<Control-Escape>"):
            r.bind_all(seq, lambda e: "break")

    def _enforce_fg(self):
        try:
            self.root.focus_force()
            self.root.lift()
        except Exception:
            pass
        self.root.after(400, self._enforce_fg)

    def _try_exit(self):
        if dlg_password(self.root) == EXIT_CODE:
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

        tk.Label(tb, text="UJIAN BAHASA INDONESIA  •  KELAS 6 SD",
                 bg=C["topbar"], fg="#93c5fd",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=18, pady=10)

        # answered counter
        self._answered_lbl = tk.Label(tb, text="",
                                      bg=C["topbar"], fg="#86efac",
                                      font=("Segoe UI", 11))
        self._answered_lbl.pack(side="left", padx=10)
        self._refresh_counter()

        # timer
        self._timer_lbl = tk.Label(tb, text="",
                                   bg=C["topbar"], fg=C["timer_ok"],
                                   font=("Segoe UI", 12, "bold"))
        self._timer_lbl.pack(side="left", padx=16)
        self._tick_timer()

        # buttons
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

        # Separator line
        tk.Frame(nb, bg="#e2e8f0", height=1).pack(fill="x")

        inner = tk.Frame(nb, bg=C["nav_bg"])
        inner.pack(pady=6, padx=12)

        self._nav_btns = []

        # PG rows: 3 rows of 15
        pg_label_frame = tk.Frame(inner, bg=C["nav_bg"])
        pg_label_frame.pack(anchor="w")
        tk.Label(pg_label_frame, text="PG:",
                 bg=C["nav_bg"], fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0,4))

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

        # Essay row
        esai_row = tk.Frame(inner, bg=C["nav_bg"])
        esai_row.pack(anchor="w", pady=(3, 0))
        tk.Label(esai_row, text="Esai:",
                 bg=C["nav_bg"], fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0,4))
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
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

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
        self._save_essay()            # save essay text before leaving
        self.current = idx

        # destroy old question frame
        if self._q_frame:
            self._q_frame.destroy()

        self._canvas.yview_moveto(0)  # scroll to top
        self._update_nav()

        q = self.questions[idx]
        # Outer card
        card = tk.Frame(self._scroll_inner, bg=C["card"])
        card.pack(fill="x", padx=60, pady=20)
        self._q_frame = card

        if q["type"] == "pg":
            self._render_pg(card, idx)
        else:
            self._render_esai(card, idx)

    # ── PG question ──────────────────────────────────────────
    def _render_pg(self, card, idx):
        q = self.questions[idx]
        pg_num = idx + 1
        total  = NUM_PG + NUM_ESAI

        # Badge row
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

        # Thin progress bar
        prog_frame = tk.Frame(card, bg="#e2e8f0", height=5)
        prog_frame.pack(fill="x", padx=40, pady=(10, 0))
        prog_frame.update_idletasks()
        pw = prog_frame.winfo_width() or 800
        pct_w = max(4, int(pw * pg_num / total))
        tk.Frame(prog_frame, bg=C["q_pg_accent"],
                 height=5, width=pct_w).place(x=0, y=0)

        # Question text
        tk.Label(card, text=q["p"],
                 bg=C["card"], fg=C["q_text"],
                 font=("Segoe UI", 14),
                 wraplength=900, justify="left",
                 anchor="nw").pack(fill="x", padx=40, pady=(20, 8))

        # Options
        opts_wrap = tk.Frame(card, bg=C["card"])
        opts_wrap.pack(fill="x", padx=40, pady=(4, 0))
        current_answer = self.answers.get(idx)
        for opt in q["o"]:
            self._render_option(opts_wrap, idx, opt[0], opt[3:],
                                is_selected=(current_answer == opt[0]))

        # Nav buttons
        self._render_nav_buttons(card, idx)

    # ── Essay question ────────────────────────────────────────
    def _render_esai(self, card, idx):
        q     = self.questions[idx]
        ei    = idx - NUM_PG + 1
        total = NUM_PG + NUM_ESAI

        # Badge row
        badge_row = tk.Frame(card, bg=C["card"])
        badge_row.pack(fill="x", padx=40, pady=(28, 0))
        tk.Label(badge_row,
                 text=f"  ESAI  {ei}/{NUM_ESAI}  ",
                 bg=C["q_esai_accent"], fg="#fff",
                 font=("Segoe UI", 9, "bold"),
                 padx=4, pady=3).pack(side="left")

        # Progress bar
        prog_frame = tk.Frame(card, bg="#e2e8f0", height=5)
        prog_frame.pack(fill="x", padx=40, pady=(10, 0))
        prog_frame.update_idletasks()
        pw = prog_frame.winfo_width() or 800
        pct_w = max(4, int(pw * (idx + 1) / total))
        tk.Frame(prog_frame, bg=C["q_esai_accent"],
                 height=5, width=pct_w).place(x=0, y=0)

        # Question text
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

        # Nav buttons
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
            self._show_question(i)   # redraw to reflect selection

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
            tk.Button(bf, text="◀  SEBELUMNYA",
                      bg=C["btn_prev"], fg="#fff",
                      font=("Segoe UI", 11, "bold"),
                      relief="flat", cursor="hand2",
                      command=lambda: self._show_question(idx - 1),
                      padx=18, pady=10).pack(side="left")

        if idx < total - 1:
            tk.Button(bf, text="BERIKUTNYA  ▶",
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
        done = sum(1 for a in self.answers.values() if a not in (None, ""))
        total = NUM_PG + NUM_ESAI
        self._answered_lbl.config(
            text=f"✓ {done} / {total} dijawab")

    def _update_nav(self):
        for i, btn in enumerate(self._nav_btns):
            real_idx = i if i < NUM_PG else i  # nav index == question index
            is_curr  = (real_idx == self.current)
            is_done  = self.answers.get(real_idx, "") not in (None, "")
            is_esai  = (real_idx >= NUM_PG)

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
                text=f"⏱  {h:02d}:{m:02d}:{sec:02d}", fg=color)
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

        total   = NUM_PG + NUM_ESAI
        unanswered = sum(1 for i in range(total)
                         if self.answers.get(i, "") in (None, ""))
        if unanswered > 0:
            if not dlg_confirm(
                self.root, "Soal Belum Selesai",
                f"Masih ada {unanswered} soal yang belum dijawab.\n"
                f"Yakin ingin mengumpulkan ujian?"):
                return

        score   = sum(1 for i in range(NUM_PG)
                      if self.answers.get(i) == self.questions[i]["j"])
        filepath = self._save_file(score)
        self._build_results(score, filepath)

    def _save_file(self, score):
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp   = os.path.join(HASIL_DIR, f"hasil_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN BAHASA INDONESIA KELAS 6 SD",
            "=" * 60,
            f"  Tanggal : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            "-" * 60,
            f"  SKOR PILIHAN GANDA : {score} / {NUM_PG}",
            f"  NILAI (PG)         : {score/NUM_PG*100:.1f}",
            "-" * 60,
            "", "DETAIL JAWABAN PILIHAN GANDA:",
        ]
        for i in range(NUM_PG):
            q      = self.questions[i]
            siswa  = self.answers.get(i, "-")
            kunci  = q["j"]
            mark   = "BENAR" if siswa == kunci else f"SALAH (kunci={kunci})"
            lines.append(f"  PG {i+1:2d}. Jawaban: {siswa}  -> {mark}")

        lines += ["", "-" * 60, "", "JAWABAN ESAI:"]
        for i in range(NUM_PG, NUM_PG + NUM_ESAI):
            q   = self.questions[i]
            jwb = self.answers.get(i, "(kosong)")
            ei  = i - NUM_PG + 1
            lines.append(f"\nEsai {ei}.")
            lines.append(f"Soal   : {q['p'][:80]}...")
            lines.append(f"Jawaban: {jwb if jwb else '(kosong)'}")

        lines.append("\n" + "=" * 60)
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return fp

    # ════════════════════════════════════════════════════════
    #  RESULTS FRAME
    # ════════════════════════════════════════════════════════
    def _build_results(self, score, filepath):
        # Replace everything
        for w in self.root.winfo_children():
            w.destroy()

        f = tk.Frame(self.root, bg=C["page"])
        f.pack(fill="both", expand=True)

        tk.Label(f, text="UJIAN SELESAI",
                 bg=C["page"], fg="#16a34a",
                 font=("Segoe UI", 36, "bold")).pack(pady=(70, 6))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 16)).pack(pady=(0, 36))

        card = tk.Frame(f, bg="#fff", padx=50, pady=32)
        card.pack()

        pct   = score / NUM_PG * 100
        color = "#16a34a" if pct >= 70 else "#f59e0b"

        rows = [
            ("Skor Pilihan Ganda", f"{score} / {NUM_PG}"),
            ("Nilai (PG)", f"{pct:.1f}"),
            ("Soal Esai", f"{NUM_ESAI} soal — sudah dikumpulkan"),
            ("File Tersimpan", filepath),
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

        tk.Label(f, text="Silakan panggil guru untuk menutup program ini.",
                 bg=C["page"], fg="#94a3b8",
                 font=("Segoe UI", 11, "italic")).pack(pady=(28, 8))
        tk.Button(f, text="Keluar (Masukkan Kode Guru)",
                  bg=C["btn_exit"], fg="#fff",
                  font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2",
                  command=self._try_exit,
                  padx=18, pady=10).pack(pady=8)

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_hook()
    app = UjianApp()
    app.run()
