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
#  POOL SOAL PILIHAN GANDA  (100 soal – diambil 45 per sesi)
# ─────────────────────────────────────────────────────────────
PG_POOL = [
    # ── KALIMAT MAJEMUK (8 soal) ─────────────────────────────
    {"p": "Kalimat majemuk setara adalah kalimat yang ...",
     "o": ["Hanya memiliki satu klausa tanpa kata hubung",
           "Terdiri dari dua klausa atau lebih yang berkedudukan setara, dihubungkan kata hubung koordinatif",
           "Memiliki induk kalimat dan anak kalimat yang tidak setara",
           "Terdiri dari satu subjek dan satu predikat saja"],
     "j": 1},

    {"p": "Kata penghubung yang digunakan dalam kalimat majemuk setara penjumlahan adalah ...",
     "o": ["Tetapi, namun, akan tetapi",
           "Karena, sebab, oleh karena itu",
           "Dan, serta, lalu",
           "Jika, apabila, andaikan"],
     "j": 2},

    {"p": "Kalimat 'Andi belajar keras karena ingin lulus ujian' adalah contoh kalimat majemuk ...",
     "o": ["Setara penjumlahan",
           "Setara pertentangan",
           "Bertingkat sebab-akibat",
           "Setara pilihan"],
     "j": 2},

    {"p": "Manakah yang merupakan kalimat majemuk setara pertentangan?",
     "o": ["Rini belajar dan adiknya bermain.",
           "Ibu memasak serta ayah membaca koran.",
           "Dia rajin belajar tetapi nilainya kurang memuaskan.",
           "Siti pergi ke sekolah karena ada ujian."],
     "j": 2},

    {"p": "Kalimat majemuk bertingkat memiliki ciri ...",
     "o": ["Kedua klausa berkedudukan setara",
           "Terdiri dari satu klausa saja tanpa kata hubung",
           "Terdapat induk kalimat dan anak kalimat yang tidak setara",
           "Tidak pernah menggunakan kata hubung"],
     "j": 2},

    {"p": "'Walaupun hujan deras, Budi tetap berangkat sekolah.' Kata 'walaupun' menunjukkan hubungan ...",
     "o": ["Sebab",
           "Syarat",
           "Waktu",
           "Pertentangan / konsesif"],
     "j": 3},

    {"p": "Kalimat majemuk setara pilihan ditandai dengan kata hubung ...",
     "o": ["Dan, serta",
           "Tetapi, namun",
           "Atau",
           "Karena, sebab"],
     "j": 2},

    {"p": "Manakah kalimat majemuk bertingkat dengan anak kalimat syarat?",
     "o": ["Ibu memasak dan ayah mencuci piring.",
           "Dia tidak hadir karena sakit demam tinggi.",
           "Jika kamu rajin belajar, kamu pasti berhasil.",
           "Rina suka membaca tetapi adiknya suka bermain."],
     "j": 2},

    # ── MAKNA KATA DALAM TEKS (6 soal) ──────────────────────
    {"p": "Kata 'gigih' bermakna ...",
     "o": ["Mudah menyerah dan cepat putus asa",
           "Tidak mau berusaha sama sekali",
           "Teguh hati dan tidak mudah menyerah dalam berjuang",
           "Lambat dalam bekerja"],
     "j": 2},

    {"p": "Makna kata 'bersahaja' dalam kalimat 'Pak Lurah dikenal sebagai orang yang bersahaja' adalah ...",
     "o": ["Sombong dan suka pamer",
           "Sederhana dan tidak berlebihan",
           "Kaya raya dan berpengaruh",
           "Pintar dan cerdas"],
     "j": 1},

    {"p": "Kata 'cekatan' bermakna ...",
     "o": ["Lamban dan malas bekerja",
           "Ceroboh dan tidak teliti",
           "Cepat dan terampil dalam melakukan sesuatu",
           "Tidak mau membantu orang lain"],
     "j": 2},

    {"p": "Perhatikan kalimat: 'Nenek itu bertutur dengan lemah lembut kepada cucunya.' Makna kata 'bertutur' adalah ...",
     "o": ["Berjalan perlahan",
           "Berbicara",
           "Bernyanyi merdu",
           "Menulis surat"],
     "j": 1},

    {"p": "Kata 'dermawan' bermakna ...",
     "o": ["Kikir dan tidak mau berbagi",
           "Suka memberi dan membantu orang lain",
           "Kaya raya dan berpengaruh",
           "Pintar berdagang"],
     "j": 1},

    {"p": "Kata 'gigih' dan 'ulet' dalam bahasa Indonesia memiliki hubungan makna ...",
     "o": ["Antonim — makna berlawanan",
           "Homonim — bunyi sama, makna beda",
           "Sinonim — makna serupa",
           "Polisemi — satu kata banyak makna"],
     "j": 2},

    # ── PUISI (8 soal) ───────────────────────────────────────
    {"p": "Berikut yang BUKAN merupakan unsur pembangun puisi adalah ...",
     "o": ["Rima dan irama",
           "Diksi (pilihan kata)",
           "Alur cerita dan latar",
           "Majas (gaya bahasa)"],
     "j": 2},

    {"p": ("Perhatikan kutipan puisi berikut!\n"
           "'Hijau daunmu menyejukkan mata\n"
           " Akarmu menancap kuat di bumi\n"
           " Buahmu manis menyegarkan rasa\n"
           " Kau berguna bagi kami'\n\n"
           "Tema puisi tersebut adalah ..."),
     "o": ["Keindahan laut dan pantai",
           "Jasa seorang guru",
           "Kegunaan pohon bagi manusia",
           "Keindahan pemandangan pegunungan"],
     "j": 2},

    {"p": "Amanat puisi adalah ...",
     "o": ["Gambaran tempat dan waktu dalam puisi",
           "Pesan atau nasihat yang ingin disampaikan penyair melalui puisinya",
           "Gaya bahasa yang digunakan penyair",
           "Pilihan kata-kata indah dalam puisi"],
     "j": 1},

    {"p": "Kalimat 'Ombak berlari mengejar pantai' menggunakan majas ...",
     "o": ["Simile",
           "Metafora",
           "Personifikasi",
           "Hiperbola"],
     "j": 2},

    {"p": "Kalimat 'Wajahnya bagaikan rembulan di malam hari' menggunakan majas ...",
     "o": ["Metafora",
           "Personifikasi",
           "Hiperbola",
           "Simile"],
     "j": 3},

    {"p": "Kalimat 'Dia adalah bintang kelas kami' menggunakan majas ...",
     "o": ["Simile",
           "Metafora",
           "Personifikasi",
           "Litotes"],
     "j": 1},

    {"p": "Persamaan bunyi pada akhir baris-baris puisi disebut ...",
     "o": ["Irama",
           "Sajak / rima",
           "Bait",
           "Larik"],
     "j": 1},

    {"p": "Satu kesatuan beberapa baris dalam puisi disebut ...",
     "o": ["Larik",
           "Sajak",
           "Bait",
           "Rima"],
     "j": 2},

    # ── PANTUN (8 soal) ──────────────────────────────────────
    {"p": "Jumlah baris dalam satu bait pantun adalah ...",
     "o": ["2 baris",
           "6 baris",
           "4 baris",
           "8 baris"],
     "j": 2},

    {"p": "Dalam pantun, baris ke-1 dan ke-2 disebut ...",
     "o": ["Isi",
           "Sampiran",
           "Penutup",
           "Pembuka"],
     "j": 1},

    {"p": "Pola sajak (rima) yang benar dalam sebuah pantun adalah ...",
     "o": ["a-a-a-a",
           "a-b-a-b",
           "a-a-b-b",
           "a-b-b-a"],
     "j": 1},

    {"p": ("Perhatikan pantun berikut!\n"
           "'Pohon mangga di tepi kali,\n"
           " Buahnya lebat berwarna merah.\n"
           " Kalau ingin jadi anak berbakti,\n"
           " Hormatilah ibu dan ayah.'\n\n"
           "Pantun tersebut termasuk jenis pantun ..."),
     "o": ["Pantun jenaka",
           "Pantun teka-teki",
           "Pantun nasihat",
           "Pantun adat"],
     "j": 2},

    {"p": "Perbedaan utama antara pantun dan syair adalah ...",
     "o": ["Pantun bersajak a-b-a-b; syair bersajak a-a-a-a",
           "Pantun berasal dari Jawa; syair berasal dari Arab",
           "Pantun terdiri dari 6 baris; syair terdiri dari 4 baris",
           "Pantun tidak memiliki sampiran; syair memiliki sampiran"],
     "j": 0},

    {"p": ("Perhatikan pantun berikut!\n"
           "'Kalau ada jarum yang patah,\n"
           " Jangan simpan di dalam peti.\n"
           " Kalau ada kata yang salah,\n"
           " Jangan simpan di dalam hati.'\n\n"
           "Makna isi pantun tersebut adalah ..."),
     "o": ["Simpanlah patahan jarum dengan baik di peti",
           "Jangan memendam rasa sakit hati; maafkanlah kesalahan orang lain",
           "Jangan bicara sembarangan kepada orang lain",
           "Jaga barang-barang berharga dengan hati-hati"],
     "j": 1},

    {"p": "Jumlah suku kata yang benar pada tiap baris pantun adalah ...",
     "o": ["4–6 suku kata",
           "8–12 suku kata",
           "13–15 suku kata",
           "2–3 suku kata"],
     "j": 1},

    {"p": ("Perhatikan pantun berikut!\n"
           "'Pergi ke pasar beli terasi,\n"
           " Beli juga asam dan garam.\n"
           " Rajin belajar setiap hari,\n"
           " Agar cita-cita tidak padam.'\n\n"
           "Bagian isi pantun di atas terdapat pada baris ..."),
     "o": ["Baris 1 dan 2",
           "Baris 2 dan 3",
           "Baris 3 dan 4",
           "Baris 1 dan 3"],
     "j": 2},

    # ── IDE POKOK & PARAGRAF (8 soal) ───────────────────────
    {"p": "Ide pokok (gagasan utama) paragraf adalah ...",
     "o": ["Kalimat yang mengakhiri sebuah paragraf",
           "Gagasan yang menjadi dasar atau inti dari sebuah paragraf",
           "Kalimat yang memberikan penjelasan pada kalimat lain",
           "Kata-kata sulit yang ada dalam paragraf"],
     "j": 1},

    {"p": ("Perhatikan paragraf berikut!\n"
           "'Membaca sangat bermanfaat bagi kehidupan. Dengan membaca, kita mendapat\n"
           "banyak pengetahuan baru. Membaca juga dapat melatih konsentrasi dan daya\n"
           "ingat. Selain itu, membaca dapat memperluas wawasan kita.'\n\n"
           "Ide pokok paragraf tersebut adalah ..."),
     "o": ["Membaca melatih konsentrasi dan daya ingat",
           "Membaca dapat memperluas wawasan kita",
           "Membaca sangat bermanfaat bagi kehidupan",
           "Membaca memberikan banyak pengetahuan baru"],
     "j": 2},

    {"p": "Kalimat utama suatu paragraf adalah kalimat yang ...",
     "o": ["Paling panjang di antara kalimat lainnya dalam paragraf",
           "Berisi gagasan pokok atau inti dari paragraf",
           "Selalu terletak di akhir paragraf",
           "Mengandung kata hubung sebab-akibat"],
     "j": 1},

    {"p": "Kalimat penjelas dalam paragraf berfungsi untuk ...",
     "o": ["Memperkenalkan topik baru dalam paragraf",
           "Menyimpulkan seluruh isi paragraf",
           "Menjelaskan, merinci, atau mendukung ide pokok",
           "Membuka paragraf berikutnya"],
     "j": 2},

    {"p": "Paragraf yang kalimat utamanya terletak di awal paragraf disebut paragraf ...",
     "o": ["Induktif",
           "Campuran",
           "Deduktif",
           "Ineratif"],
     "j": 2},

    {"p": ("Perhatikan paragraf berikut!\n"
           "'Sungai Ciliwung terkenal dengan keindahannya. Di sepanjang alirannya\n"
           "terdapat tumbuhan hijau yang rindang. Airnya jernih mengalir deras.\n"
           "Ikan-ikan berenang bebas di dalamnya.'\n\n"
           "Paragraf di atas termasuk jenis paragraf ..."),
     "o": ["Induktif — kalimat utama di akhir",
           "Deduktif — kalimat utama di awal",
           "Campuran — kalimat utama di awal dan akhir",
           "Deskriptif tanpa kalimat utama"],
     "j": 1},

    {"p": "Paragraf induktif adalah paragraf yang ...",
     "o": ["Kalimat utamanya berada di awal paragraf",
           "Tidak memiliki kalimat utama sama sekali",
           "Kalimat utamanya berada di akhir paragraf",
           "Kalimat utamanya berada di tengah paragraf"],
     "j": 2},

    {"p": ("Perhatikan paragraf berikut!\n"
           "'Budi selalu mengerjakan PR tepat waktu. Ia tidak pernah terlambat masuk\n"
           "sekolah. Nilai-nilainya selalu bagus dan memuaskan. Budi adalah siswa\n"
           "yang teladan di kelasnya.'\n\n"
           "Kalimat utama paragraf tersebut adalah ..."),
     "o": ["Budi selalu mengerjakan PR tepat waktu.",
           "Nilai-nilainya selalu bagus dan memuaskan.",
           "Ia tidak pernah terlambat masuk sekolah.",
           "Budi adalah siswa yang teladan di kelasnya."],
     "j": 3},

    # ── SINONIM & ANTONIM (6 soal) ───────────────────────────
    {"p": "Sinonim kata 'gembira' adalah ...",
     "o": ["Sedih",
           "Senang",
           "Marah",
           "Takut"],
     "j": 1},

    {"p": "Sinonim kata 'pandai' adalah ...",
     "o": ["Bodoh",
           "Lambat",
           "Cerdas",
           "Malas"],
     "j": 2},

    {"p": "Sinonim kata 'indah' adalah ...",
     "o": ["Jelek",
           "Elok",
           "Rusak",
           "Kotor"],
     "j": 1},

    {"p": "Antonim kata 'rajin' adalah ...",
     "o": ["Giat",
           "Tekun",
           "Malas",
           "Semangat"],
     "j": 2},

    {"p": "Antonim kata 'berani' adalah ...",
     "o": ["Gagah",
           "Kuat",
           "Penakut",
           "Perkasa"],
     "j": 2},

    {"p": "Antonim kata 'terang' adalah ...",
     "o": ["Bersinar",
           "Gelap",
           "Cerah",
           "Bercahaya"],
     "j": 1},

    # ── TEKS DESKRIPSI (6 soal) ──────────────────────────────
    {"p": "Teks deskripsi adalah teks yang ...",
     "o": ["Menceritakan peristiwa secara berurutan berdasarkan waktu",
           "Menggambarkan suatu objek secara detail agar pembaca seolah melihat langsung",
           "Meyakinkan pembaca tentang suatu pendapat",
           "Menjelaskan cara melakukan sesuatu langkah demi langkah"],
     "j": 1},

    {"p": "Ciri utama teks deskripsi adalah ...",
     "o": ["Menggunakan kata hubung waktu seperti lalu dan kemudian",
           "Menggunakan kalimat-kalimat yang bersifat argumentatif",
           "Menggunakan kata-kata yang melukiskan keadaan objek secara rinci dan detail",
           "Menggunakan banyak kalimat perintah"],
     "j": 2},

    {"p": "Tujuan penulisan teks deskripsi adalah ...",
     "o": ["Menghibur pembaca dengan cerita lucu",
           "Memengaruhi pendapat pembaca",
           "Membuat pembaca seolah-olah melihat, merasakan, atau mengalami langsung objek yang digambarkan",
           "Menjelaskan proses terjadinya sesuatu secara ilmiah"],
     "j": 2},

    {"p": "Manakah kalimat yang merupakan ciri khas teks deskripsi?",
     "o": ["Lalu ia berjalan menuju sekolah dengan tergesa-gesa.",
           "Sebaiknya kita rajin berolahraga setiap pagi.",
           "Kucing itu berbulu putih bersih, bermata biru jernih, dan bertubuh gemuk menggemaskan.",
           "Pertama, panaskan minyak goreng di dalam wajan."],
     "j": 2},

    {"p": ("Perhatikan kalimat berikut!\n"
           "'Pantai itu memiliki pasir putih yang lembut, air biru jernih yang tenang,\n"
           "dan dihiasi pohon kelapa yang melambai-lambai.'\n\n"
           "Kalimat di atas merupakan contoh kalimat dalam teks ..."),
     "o": ["Narasi",
           "Persuasi",
           "Deskripsi",
           "Prosedur"],
     "j": 2},

    {"p": "Objek yang dapat dijadikan bahan tulisan teks deskripsi adalah ...",
     "o": ["Hanya benda mati saja",
           "Hanya tempat wisata yang terkenal",
           "Segala sesuatu yang dapat diamati, seperti tempat, orang, hewan, atau benda",
           "Hanya tokoh-tokoh terkenal dalam sejarah"],
     "j": 2},

    # ── TEKS NARASI (6 soal) ─────────────────────────────────
    {"p": "Teks narasi adalah teks yang ...",
     "o": ["Menggambarkan suatu objek secara rinci dan detail",
           "Meyakinkan pembaca tentang suatu pendapat",
           "Menceritakan rangkaian peristiwa secara berurutan berdasarkan waktu",
           "Menjelaskan cara membuat atau melakukan sesuatu"],
     "j": 2},

    {"p": "Ciri utama teks narasi yang membedakannya dari teks lain adalah ...",
     "o": ["Memuat pendapat dan argumen yang kuat",
           "Memuat langkah-langkah kegiatan secara urut",
           "Peristiwanya tersusun berdasarkan urutan waktu (kronologis)",
           "Banyak menggunakan kata-kata sifat untuk melukiskan"],
     "j": 2},

    {"p": "Kata hubung yang sering digunakan dalam teks narasi untuk menyatakan urutan waktu adalah ...",
     "o": ["Tetapi, namun, akan tetapi",
           "Pertama, kemudian, lalu, akhirnya, setelah itu",
           "Jika, apabila, andaikan, seandainya",
           "Karena, sebab, sehingga, akibatnya"],
     "j": 1},

    {"p": "Teks narasi fiksi adalah teks narasi yang ...",
     "o": ["Berdasarkan kejadian nyata yang benar-benar pernah terjadi",
           "Berisi laporan berita yang sebenarnya",
           "Merupakan karangan imajinatif atau rekaan pengarang",
           "Menjelaskan fakta ilmiah secara runtut"],
     "j": 2},

    {"p": "Teks narasi nonfiksi adalah teks narasi yang ...",
     "o": ["Sepenuhnya berdasarkan imajinasi pengarang",
           "Tidak mengandung nilai kebenaran apapun",
           "Berdasarkan kejadian atau peristiwa nyata yang benar-benar terjadi",
           "Menggunakan tokoh hewan sebagai pelaku utama"],
     "j": 2},

    {"p": ("Perhatikan teks berikut!\n"
           "'Pagi itu Budi bangun pukul 05.00. Setelah mandi, ia sarapan bersama\n"
           "keluarga. Kemudian ia berpamitan kepada orang tua lalu berangkat ke sekolah.'\n\n"
           "Teks tersebut termasuk jenis teks ..."),
     "o": ["Deskripsi",
           "Narasi",
           "Persuasi",
           "Prosedur"],
     "j": 1},

    # ── UNSUR INTRINSIK CERITA (10 soal) ────────────────────
    {"p": "Ide atau gagasan yang menjadi inti dan mendasari seluruh isi cerita disebut ...",
     "o": ["Alur",
           "Latar",
           "Tema",
           "Amanat"],
     "j": 2},

    {"p": "Rangkaian peristiwa yang membentuk jalan cerita dari awal hingga akhir disebut ...",
     "o": ["Tema",
           "Alur",
           "Latar",
           "Sudut pandang"],
     "j": 1},

    {"p": "Gambaran tentang tempat, waktu, dan suasana terjadinya peristiwa dalam cerita disebut ...",
     "o": ["Tema",
           "Alur",
           "Latar",
           "Amanat"],
     "j": 2},

    {"p": ("Perhatikan kutipan cerita:\n"
           "'Kejadian itu berlangsung di sebuah desa kecil pada sore hari\n"
           "ketika suasana sunyi senyap dan angin berhembus sepoi-sepoi.'\n\n"
           "Yang termasuk latar suasana pada kutipan cerita tersebut adalah ..."),
     "o": ["Desa kecil",
           "Sore hari",
           "Sunyi senyap",
           "Angin berhembus"],
     "j": 2},

    {"p": "Tokoh yang berwatak baik dan biasanya menjadi tokoh utama yang diperjuangkan nasibnya disebut ...",
     "o": ["Antagonis",
           "Tritagonis",
           "Figuran",
           "Protagonis"],
     "j": 3},

    {"p": "Tokoh yang berwatak jahat dan biasanya menjadi penentang tokoh utama dalam cerita disebut ...",
     "o": ["Protagonis",
           "Antagonis",
           "Tritagonis",
           "Figuran"],
     "j": 1},

    {"p": "Pesan moral yang ingin disampaikan pengarang kepada pembaca melalui ceritanya disebut ...",
     "o": ["Tema",
           "Alur",
           "Latar",
           "Amanat"],
     "j": 3},

    {"p": ("Perhatikan cerita berikut!\n"
           "'Meskipun hidup dalam kemiskinan, Dina tidak pernah menyerah.\n"
           "Ia terus belajar dengan giat hingga akhirnya berhasil meraih beasiswa.'\n\n"
           "Amanat yang dapat diambil dari cerita tersebut adalah ..."),
     "o": ["Kemiskinan adalah halangan terbesar dalam hidup",
           "Jangan mengharapkan beasiswa dari siapapun",
           "Ketekunan dan semangat pantang menyerah akan membawa keberhasilan",
           "Orang miskin tidak akan bisa meraih cita-cita"],
     "j": 2},

    {"p": "Cerita yang menggunakan sudut pandang orang pertama ditandai dengan penggunaan kata ...",
     "o": ["Dia, ia, mereka",
           "Kamu, kalian, Anda",
           "Aku, saya",
           "Beliau, mereka, ia"],
     "j": 2},

    {"p": ("Perhatikan cerita singkat:\n"
           "'Pak Guru selalu sabar mengajar murid-muridnya. Setiap hari ia datang\n"
           "tepat waktu. Ia tidak pernah marah meski muridnya nakal sekalipun.'\n\n"
           "Tema cerita tersebut adalah ..."),
     "o": ["Kemalasan seorang murid di sekolah",
           "Kesabaran dan keteladanan seorang guru",
           "Kenakalan anak-anak di sekolah",
           "Pentingnya datang tepat waktu ke sekolah"],
     "j": 1},

    # ── FABEL, LEGENDA, CERITA RAKYAT (5 soal) ──────────────
    {"p": "Cerita yang tokoh-tokohnya adalah hewan yang berperilaku dan berbicara seperti manusia disebut ...",
     "o": ["Legenda",
           "Mitos",
           "Fabel",
           "Sage"],
     "j": 2},

    {"p": "Cerita rakyat yang menceritakan asal-usul suatu tempat, benda, atau peristiwa disebut ...",
     "o": ["Mitos",
           "Legenda",
           "Fabel",
           "Dongeng"],
     "j": 1},

    {"p": "Ciri utama fabel yang membedakannya dari cerita lain adalah ...",
     "o": ["Tokohnya manusia biasa dengan kehidupan sehari-hari",
           "Berlatar di istana kerajaan pada zaman dahulu",
           "Tokohnya binatang yang bisa berpikir dan berbicara seperti manusia",
           "Selalu berakhir dengan kebahagiaan tokoh utama"],
     "j": 2},

    {"p": "Amanat yang dapat diambil dari fabel 'Semut dan Belalang' adalah ...",
     "o": ["Bermainlah sebanyak mungkin selagi masih muda",
           "Bekerja keraslah dan bersiaplah untuk menghadapi masa depan",
           "Mintalah bantuan kepada teman jika dalam kesulitan",
           "Jangan berteman dengan orang yang berbeda sifatnya"],
     "j": 1},

    {"p": "Dalam cerita 'Malin Kundang', pesan moral yang paling utama adalah ...",
     "o": ["Merantaulah sejauh mungkin untuk mencari kekayaan",
           "Jadilah pedagang yang sukses dan kaya raya",
           "Jangan durhaka kepada orang tua",
           "Carilah pasangan hidup yang cantik dan kaya"],
     "j": 2},

    # ── KALIMAT EFEKTIF (5 soal) ─────────────────────────────
    {"p": "Kalimat efektif adalah kalimat yang ...",
     "o": ["Panjang dan menggunakan banyak kata agar jelas",
           "Menggunakan kata-kata asing agar terdengar ilmiah",
           "Mengandung unsur yang lengkap, tidak berlebihan, dan tidak berulang",
           "Menggunakan kata-kata kiasan sebanyak mungkin"],
     "j": 2},

    {"p": "Kalimat 'Banyak siswa-siswa yang hadir dalam upacara' tidak efektif karena ...",
     "o": ["Tidak memiliki subjek yang jelas",
           "Terdapat pemborosan kata: 'banyak' dan 'siswa-siswa' sama-sama menyatakan jamak",
           "Menggunakan kata yang salah penulisannya",
           "Tidak memiliki predikat"],
     "j": 1},

    {"p": "'Para hadirin-hadirin sekalian dimohon untuk berdiri.' Perbaikan kalimat efektifnya adalah ...",
     "o": ["Para hadirin-hadirin dimohon berdiri.",
           "Para hadirin dimohon untuk berdiri.",
           "Hadirin-hadirin dimohon untuk berdiri.",
           "Semua para hadirin dimohon berdiri."],
     "j": 1},

    {"p": "Manakah kalimat yang efektif di bawah ini?",
     "o": ["Saya sangat amat senang sekali mendapat hadiah itu.",
           "Para tamu-tamu undangan sudah hadir semua.",
           "Saya sangat senang mendapat hadiah itu.",
           "Kami semua para guru mengucapkan selamat."],
     "j": 2},

    {"p": "Kalimat 'Dia pergi ke sekolah dengan cara berjalan kaki' tidak efektif. Perbaikan yang tepat adalah ...",
     "o": ["Dia berjalan kaki dengan cara ke sekolah.",
           "Dengan cara berjalan dia pergi ke sekolah.",
           "Dia ke sekolah dengan cara berjalan.",
           "Dia pergi ke sekolah dengan berjalan kaki."],
     "j": 3},

    # ── EYD / TANDA BACA / HURUF KAPITAL (5 soal) ───────────
    {"p": "Penulisan huruf kapital yang benar untuk nama geografi terdapat pada kalimat ...",
     "o": ["Kami berlibur ke pantai Parangtritis kemarin.",
           "Kami berlibur ke Pantai Parangtritis kemarin.",
           "Kami berlibur ke pantai parangtritis kemarin.",
           "Kami berlibur ke PANTAI PARANGTRITIS kemarin."],
     "j": 1},

    {"p": "Penggunaan tanda koma yang benar terdapat pada kalimat ...",
     "o": ["Ibu membeli sayur, ikan, dan tempe di pasar.",
           "Ibu membeli sayur, ikan dan, tempe di pasar.",
           "Ibu membeli, sayur ikan dan tempe di pasar.",
           "Ibu, membeli sayur ikan dan tempe di pasar."],
     "j": 0},

    {"p": "Penggunaan tanda titik dua (:) yang benar terdapat pada kalimat ...",
     "o": ["Hari ini: adalah hari yang paling menyenangkan.",
           "Dia berkata: mari kita mulai belajar bersama.",
           "Barang yang perlu dibawa: tenda, matras, dan kompor.",
           "Ibu: sedang memasak nasi goreng di dapur."],
     "j": 2},

    {"p": "Kata baku yang penulisannya benar adalah ...",
     "o": ["Apotik",
           "Ijazah",
           "Aktifitas",
           "Nopember"],
     "j": 1},

    {"p": "Penulisan gelar dokter dan magister yang benar adalah ...",
     "o": ["Dr. Andi Wijaya, M.Pd.",
           "dr. Andi Wijaya M.Pd",
           "DR. Andi Wijaya, M.PD.",
           "dr. Andi Wijaya, M.Pd."],
     "j": 3},

    # ── IMBUHAN (7 soal) ─────────────────────────────────────
    {"p": "Kata 'membawa' mendapat imbuhan me- yang berubah menjadi 'mem-' karena kata dasarnya diawali huruf ...",
     "o": ["s, t, k, p (luluh)",
           "b, p, f, v",
           "c, j, d, sy",
           "g, h, kh, vokal"],
     "j": 1},

    {"p": "Imbuhan me- berubah menjadi 'men-' apabila kata dasarnya diawali huruf ...",
     "o": ["b, p, f, v",
           "g, h, kh",
           "d, t, c, j",
           "l, r, m, n"],
     "j": 2},

    {"p": "Kata berimbuhan 'ber-' yang menyatakan makna 'memakai atau menggunakan' terdapat pada kalimat ...",
     "o": ["Ayah berlari pagi setiap hari.",
           "Ibu berbicara dengan tamu di ruang tamu.",
           "Adik berseragam putih merah ke sekolah.",
           "Kakak berterima kasih kepada gurunya."],
     "j": 2},

    {"p": "Makna imbuhan 'ter-' pada kata 'terjatuh' dalam kalimat 'Bukunya terjatuh dari meja' adalah ...",
     "o": ["Melakukan dengan sengaja dan penuh kesadaran",
           "Kejadian yang tidak disengaja",
           "Sedang dalam proses melakukan",
           "Sudah selesai dilakukan"],
     "j": 1},

    {"p": "Imbuhan 'ke-an' yang menyatakan makna 'keadaan atau sifat' terdapat pada kata ...",
     "o": ["Ketua",
           "Kesatu",
           "Kegiatan",
           "Kebaikan"],
     "j": 3},

    {"p": "Kata 'penulisan' mendapat imbuhan 'pe-an' yang bermakna ...",
     "o": ["Orang yang menulis",
           "Hasil dari menulis",
           "Proses atau cara menulis",
           "Tempat khusus untuk menulis"],
     "j": 2},

    {"p": "Kalimat 'Buku itu dibaca oleh Rini.' merupakan kalimat pasif yang menggunakan imbuhan ...",
     "o": ["me-",
           "ber-",
           "ter-",
           "di-"],
     "j": 3},

    # ── HOMONIM (4 soal) ─────────────────────────────────────
    {"p": "Homonim adalah kata yang ...",
     "o": ["Memiliki makna yang berlawanan satu sama lain",
           "Memiliki makna yang sama atau hampir sama",
           "Memiliki ejaan atau bunyi yang sama tetapi maknanya berbeda",
           "Memiliki banyak makna berbeda dalam satu kata"],
     "j": 2},

    {"p": ("Perhatikan dua kalimat berikut!\n"
           "1. 'Bisa ular itu sangat berbahaya bagi manusia.'\n"
           "2. 'Kamu bisa menyelesaikan soal ini dengan mudah.'\n\n"
           "Kata 'bisa' pada dua kalimat tersebut adalah contoh ..."),
     "o": ["Sinonim",
           "Antonim",
           "Homonim",
           "Polisemi"],
     "j": 2},

    {"p": "Kata 'buku' pada kalimat 'Buku jarinya memar terkena pukulan' bermakna ...",
     "o": ["Kitab atau buku tulis pelajaran",
           "Ruas atau sendi pada jari tangan",
           "Bagian keras dari pohon",
           "Tulang belakang manusia"],
     "j": 1},

    {"p": ("Perhatikan dua kalimat:\n"
           "1. 'Rapat hari ini membahas tentang kegiatan sekolah.'\n"
           "2. 'Jahitan bajunya sangat rapat dan kuat.'\n\n"
           "Kata 'rapat' pada kedua kalimat di atas merupakan contoh ..."),
     "o": ["Sinonim",
           "Antonim",
           "Polisemi",
           "Homonim"],
     "j": 3},

    # ── KONJUNGSI (4 soal) ───────────────────────────────────
    {"p": "Konjungsi yang menyatakan hubungan sebab terdapat pada kalimat ...",
     "o": ["Rina rajin belajar tetapi nilainya tetap rendah.",
           "Budi tidak masuk sekolah karena sakit demam.",
           "Apakah kamu mau pergi atau tinggal di rumah?",
           "Ketika hujan turun, kami berteduh di teras."],
     "j": 1},

    {"p": "Konjungsi yang menyatakan pertentangan terdapat pada kalimat ...",
     "o": ["Ibu memasak dan ayah membaca koran di teras.",
           "Siti pergi ke sekolah karena ada ujian hari ini.",
           "Andi rajin belajar namun nilainya masih kurang memuaskan.",
           "Dia datang ketika hujan mulai turun dengan deras."],
     "j": 2},

    {"p": "Konjungsi yang menyatakan hubungan waktu terdapat pada kalimat ...",
     "o": ["Ia belajar keras karena ada ujian besok pagi.",
           "Dia pergi atau tinggal, itu terserah kamu.",
           "Rani menangis tetapi tidak mau menceritakan masalahnya.",
           "Ketika bel berbunyi, semua siswa langsung masuk kelas."],
     "j": 3},

    {"p": "Konjungsi yang menyatakan hubungan pilihan terdapat pada kalimat ...",
     "o": ["Ayah dan ibu pergi berbelanja ke pasar.",
           "Ia tidak hadir ke sekolah karena sakit.",
           "Apakah kamu mau minum teh atau kopi pagi ini?",
           "Meskipun hujan deras, dia tetap berangkat sekolah."],
     "j": 2},

    # ── MAJAS (4 soal) ───────────────────────────────────────
    {"p": "Kalimat 'Angin berbisik lembut di telingaku' menggunakan majas personifikasi karena ...",
     "o": ["Membandingkan angin dengan manusia menggunakan kata 'seperti'",
           "Melebih-lebihkan kekuatan dan sifat angin",
           "Memberikan sifat atau perilaku manusia (berbisik) kepada benda mati (angin)",
           "Menggunakan angin sebagai lambang kelemahan"],
     "j": 2},

    {"p": "'Suaranya menggelegar bak guntur yang membelah langit.' Majas yang digunakan adalah ...",
     "o": ["Metafora",
           "Personifikasi",
           "Simile",
           "Hiperbola"],
     "j": 2},

    {"p": "Kalimat 'Air matanya mengalir bagai sungai yang tak pernah kering' menggunakan majas ...",
     "o": ["Metafora",
           "Hiperbola",
           "Personifikasi",
           "Simile"],
     "j": 3},

    {"p": "Kalimat 'Dia adalah cahaya dalam kegelapan hidupku' menggunakan majas ...",
     "o": ["Hiperbola",
           "Simile",
           "Metafora",
           "Personifikasi"],
     "j": 2},

    # ── Teks Pidato ──────────────────────────────────────────
    {"p": "Bagian pembuka pidato yang baik biasanya berisi ...",
     "o": ["Pesan utama yang ingin disampaikan pembicara",
           "Kesimpulan dan ajakan kepada pendengar",
           "Salam, sapaan hormat, dan ucapan puji syukur",
           "Permohonan maaf dan salam penutup"],
     "j": 2},

    {"p": "Urutan struktur pidato yang benar adalah ...",
     "o": ["Isi – Pembukaan – Penutup",
           "Pembukaan – Isi – Penutup",
           "Penutup – Pembukaan – Isi",
           "Pembukaan – Penutup – Isi"],
     "j": 1},

    {"p": ("Perhatikan penggalan pidato berikut!\n"
           "'Oleh karena itu, saya mengajak teman-teman untuk disiplin "
           "dalam melaksanakan piket dan membuang sampah pada tempatnya.'\n"
           "Penggalan pidato di atas termasuk bagian ..."),
     "o": ["Pembukaan",
           "Isi",
           "Penutup",
           "Sapaan hormat"],
     "j": 1},

    {"p": ("Kalimat 'Demikian pidato singkat ini, mohon maaf bila ada "
           "kesalahan. Terima kasih.' termasuk bagian ... dari pidato."),
     "o": ["Pembukaan",
           "Isi",
           "Penutup",
           "Pendahuluan"],
     "j": 2},

    {"p": "Tujuan utama bagian isi dalam sebuah pidato adalah ...",
     "o": ["Menyampaikan salam dan sapaan kepada hadirin",
           "Menyampaikan pesan utama dan ajakan kepada pendengar",
           "Mengucapkan terima kasih kepada semua hadirin",
           "Memperkenalkan diri kepada hadirin"],
     "j": 1},

    {"p": ("Pada pidato tentang kebersihan lingkungan sekolah, kalimat "
           "'Lingkungan yang bersih akan membuat belajar menjadi nyaman "
           "dan jauh dari penyakit.' merupakan ..."),
     "o": ["Salam pembuka pidato",
           "Permohonan maaf pembicara",
           "Pesan inti/isi pidato",
           "Sapaan hormat kepada hadirin"],
     "j": 2},

    {"p": "Sapaan yang tepat untuk memulai pidato di hadapan kepala sekolah, guru, dan siswa adalah ...",
     "o": ["'Hai semuanya, apa kabar hari ini?'",
           "'Yang saya hormati Bapak Kepala Sekolah, Bapak/Ibu Guru, serta teman-teman yang saya sayangi.'",
           "'Tolong semua diam dulu, saya mau bicara!'",
           "'Kepada siapa pun yang hadir di sini.'"],
     "j": 1},

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
        # Shortcut keluar guru — Ctrl+Alt+Backspace (tidak terlihat siswa)
        r.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())

    def _enforce_fg(self):
        try:
            # Jika ada dialog (Toplevel) milik program yang sedang terbuka,
            # jangan lift root — biarkan dialog tetap di atas dan bisa diklik.
            active_dialogs = [
                w for w in self.root.winfo_children()
                if isinstance(w, tk.Toplevel) and w.winfo_exists()
            ]
            if active_dialogs:
                # Pastikan dialog-nya yang di atas, bukan root
                active_dialogs[-1].lift()
            else:
                self.root.lift()
                # Paksa fokus hanya jika app sama sekali tidak aktif
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
        for w in self.root.winfo_children():
            w.destroy()
        # re-bind shortcut setelah winfo_children dihapus
        self.root.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())

        pct   = score / NUM_PG * 100
        color = "#16a34a" if pct >= 70 else "#ef4444"

        # ── Wrapper scrollable ────────────────────────────────
        outer = tk.Frame(self.root, bg=C["page"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=C["page"], highlightthickness=0)
        vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        f = tk.Frame(canvas, bg=C["page"])
        cw = canvas.create_window((0, 0), window=f, anchor="nw")
        f.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cw, width=e.width))

        # ── Header ───────────────────────────────────────────
        tk.Label(f, text="UJIAN SELESAI",
                 bg=C["page"], fg="#16a34a",
                 font=("Segoe UI", 30, "bold")).pack(pady=(36, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 14)).pack(pady=(0, 20))

        # ── Kartu skor ───────────────────────────────────────
        card = tk.Frame(f, bg="#fff", padx=50, pady=22)
        card.pack()

        rows = [
            ("Skor Pilihan Ganda", f"{score} / {NUM_PG}"),
            ("Nilai (PG)",         f"{pct:.1f}"),
            ("Soal Esai",          f"{NUM_ESAI} soal — sudah dikumpulkan"),
            ("File Tersimpan",     filepath),
        ]
        for r, (lbl, val) in enumerate(rows):
            tk.Label(card, text=f"{lbl:<25}:",
                     bg="#fff", fg="#64748b",
                     font=("Segoe UI", 12)).grid(
                         row=r, column=0, sticky="w", pady=6, padx=6)
            fg = color if "Nilai" in lbl else C["q_text"]
            wt = "bold" if "Nilai" in lbl else "normal"
            tk.Label(card, text=val, bg="#fff", fg=fg,
                     font=("Segoe UI", 12, wt)).grid(
                         row=r, column=1, sticky="w", pady=6, padx=16)

        # ── Kumpulan soal yang salah ──────────────────────────
        wrong = []
        for i in range(NUM_PG):
            q     = self.questions[i]
            siswa = self.answers.get(i, "-")
            kunci = q["j"]
            if siswa != kunci:
                opt_siswa = next(
                    (o for o in q["o"] if o.startswith(siswa + ".")),
                    f"{siswa}. (tidak dijawab)")
                opt_benar = next(
                    (o for o in q["o"] if o.startswith(kunci + ".")), kunci)
                wrong.append((i + 1, q["p"], opt_siswa, opt_benar))

        if wrong:
            tk.Label(f,
                     text=f"Soal yang Perlu Dipelajari Lagi  —  {len(wrong)} soal salah",
                     bg=C["page"], fg="#dc2626",
                     font=("Segoe UI", 13, "bold")).pack(pady=(28, 2))
            tk.Label(f,
                     text="Pelajari kembali soal-soal berikut dan perhatikan jawaban yang benar.",
                     bg=C["page"], fg="#64748b",
                     font=("Segoe UI", 11, "italic")).pack(pady=(0, 10))

            for no, soal_text, opt_siswa, opt_benar in wrong:
                wcard = tk.Frame(f, bg="#fff")
                wcard.pack(fill="x", padx=60, pady=5)

                # Header soal
                hdr = tk.Frame(wcard, bg="#dc2626")
                hdr.pack(fill="x")
                tk.Label(hdr, text=f"  Soal No. {no}  ",
                         bg="#dc2626", fg="#fff",
                         font=("Segoe UI", 10, "bold"),
                         pady=6).pack(side="left")

                # Teks pertanyaan
                tk.Label(wcard, text=soal_text,
                         bg="#fff", fg=C["q_text"],
                         font=("Segoe UI", 12),
                         wraplength=880, justify="left",
                         anchor="w").pack(fill="x", padx=18, pady=(10, 6))

                # Jawaban siswa (merah)
                tk.Label(wcard,
                         text=f"✗  Jawaban kamu   :  {opt_siswa}",
                         bg="#fff5f5", fg="#dc2626",
                         font=("Segoe UI", 11),
                         anchor="w", padx=18, pady=8).pack(fill="x", padx=18, pady=(0, 3))

                # Jawaban benar (hijau)
                tk.Label(wcard,
                         text=f"✓  Jawaban benar  :  {opt_benar}",
                         bg="#f0fdf4", fg="#16a34a",
                         font=("Segoe UI", 11, "bold"),
                         anchor="w", padx=18, pady=8).pack(fill="x", padx=18, pady=(0, 14))
        else:
            tk.Label(f,
                     text="Selamat!  Semua soal pilihan ganda dijawab dengan benar!",
                     bg=C["page"], fg="#16a34a",
                     font=("Segoe UI", 13, "bold")).pack(pady=24)

        # ── Footer hint ───────────────────────────────────────
        tk.Label(f,
                 text="Tekan  Ctrl + Alt + Backspace  untuk keluar  (khusus guru)",
                 bg=C["page"], fg="#cbd5e1",
                 font=("Segoe UI", 10, "italic")).pack(pady=(24, 20))

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_hook()
    app = UjianApp()
    app.run()
