#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Ujian Pancasila Kelas 6 SD
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

BLOCKED_VK = {0x5B, 0x5C, 0x09, 0x73, 0x1B, 0x2C}

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
#  WARNA
# ─────────────────────────────────────────────────────────────
C = {
    "page":             "#f0f4f8",
    "topbar":           "#14532d",   # hijau gelap (warna khas Pancasila)
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
    "q_pg_accent":      "#16a34a",   # hijau
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
    "btn_submit":       "#15803d",
    "btn_exit":         "#e94560",
    "btn_text":         "#ffffff",
    "timer_ok":         "#22c55e",
    "timer_warn":       "#f59e0b",
    "timer_crit":       "#ef4444",
    "esai_area":        "#f8fafc",
    "esai_text":        "#1e293b",
}

# ─────────────────────────────────────────────────────────────
#  POOL SOAL PILIHAN GANDA  (60 soal – diambil 45 per sesi)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ── 1. NILAI LUHUR PANCASILA ─────────────────────────────
    {"p": "Nilai luhur Pancasila yang perlu dilestarikan oleh setiap warga negara Indonesia adalah ...",
     "o": ["Hanya mementingkan kepentingan golongan sendiri",
           "Menjaga persatuan, gotong royong, dan toleransi antar sesama",
           "Menganggap budaya asing lebih baik dari budaya sendiri",
           "Bersikap acuh tak acuh terhadap lingkungan sekitar"],
     "j": 1},

    {"p": "Nilai luhur Pancasila yang paling mencerminkan kepribadian bangsa Indonesia adalah ...",
     "o": ["Individualisme dan persaingan bebas tanpa batas",
           "Materialisme dan mengutamakan keuntungan pribadi",
           "Gotong royong, musyawarah, dan toleransi antar sesama",
           "Kapitalisme dan liberalisme dalam kehidupan bermasyarakat"],
     "j": 2},

    # ── 2. KEWAJIBAN SEHARI-HARI DI SEKOLAH ─────────────────
    {"p": "Berikut yang merupakan kewajiban siswa di lingkungan sekolah adalah ...",
     "o": ["Mendapat nilai sempurna di semua mata pelajaran",
           "Menggunakan fasilitas sekolah sesuka hati",
           "Hadir tepat waktu, mematuhi tata tertib, dan menjaga kebersihan sekolah",
           "Meminta guru menjelaskan ulang setiap materi pelajaran"],
     "j": 2},

    {"p": "Sebagai siswa kelas 6 SD, kewajiban yang harus dilakukan di sekolah antara lain ...",
     "o": ["Memilih teman yang disukai saja untuk belajar bersama",
           "Mengerjakan tugas tepat waktu dan menghormati semua guru",
           "Menggunakan handphone selama pelajaran berlangsung",
           "Pulang lebih awal jika tugas sudah selesai dikerjakan"],
     "j": 1},

    # ── 3. MEMBANGUN MASYARAKAT HARMONIS ────────────────────
    {"p": "Cara yang paling tepat untuk membangun masyarakat agar tetap harmonis adalah ...",
     "o": ["Tidak bergaul dengan tetangga agar tidak ada konflik",
           "Mengikuti semua pendapat mayoritas tanpa berpikir kritis",
           "Saling menghormati, toleransi, dan gotong royong antar warga",
           "Menghindari perbedaan pendapat dengan cara apapun"],
     "j": 2},

    {"p": "Manakah tindakan yang dapat merusak keharmonisan masyarakat?",
     "o": ["Ikut serta dalam kegiatan gotong royong membersihkan lingkungan",
           "Menghormati perbedaan suku, agama, dan budaya tetangga",
           "Menyebarkan berita bohong dan menghasut warga untuk bertikai",
           "Menghadiri acara pertemuan RT secara rutin setiap bulannya"],
     "j": 2},

    # ── 4. SIKAP TERHADAP TEMAN BERBEDA AGAMA ───────────────
    {"p": "Sikap yang paling tepat terhadap teman yang beragama berbeda adalah ...",
     "o": ["Menghindari berteman dengan mereka agar tidak terpengaruh",
           "Memaksa teman untuk mengikuti agama yang kita anut",
           "Menghormati dan berteman baik meski berbeda keyakinan",
           "Hanya mau berteman dengan orang yang seagama saja"],
     "j": 2},

    {"p": "Saat teman sedang melaksanakan ibadah sesuai agamanya, sikap yang benar adalah ...",
     "o": ["Mengganggunya dengan membuat keributan di sekitarnya",
           "Menertawakan dan mengejek tata cara ibadahnya",
           "Menghormati dan tidak mengganggu ibadah teman",
           "Mengajaknya bermain karena sedang jam istirahat"],
     "j": 2},

    # ── 5. NILAI SALAH SATU SILA PANCASILA ──────────────────
    {"p": "Nilai yang terkandung dalam sila ke-2 Pancasila 'Kemanusiaan yang Adil dan Beradab' adalah ...",
     "o": ["Percaya dan takwa kepada Tuhan Yang Maha Esa",
           "Menjunjung tinggi harkat dan martabat manusia serta persamaan derajat",
           "Mengutamakan kepentingan bersama di atas kepentingan pribadi",
           "Bermusyawarah untuk mencapai mufakat bersama"],
     "j": 1},

    {"p": "Nilai yang terkandung dalam sila ke-3 Pancasila 'Persatuan Indonesia' adalah ...",
     "o": ["Mengakui persamaan hak setiap warga negara Indonesia",
           "Beribadah sesuai agama dan kepercayaan masing-masing",
           "Cinta tanah air dan bangsa serta mengutamakan persatuan",
           "Mengutamakan musyawarah dalam pengambilan setiap keputusan"],
     "j": 2},

    # ── 6. PENERAPAN NILAI SILA PANCASILA ───────────────────
    {"p": "Penerapan nilai sila ke-1 Pancasila 'Ketuhanan Yang Maha Esa' dalam kehidupan sehari-hari adalah ...",
     "o": ["Memaksakan keyakinan agama kepada orang lain",
           "Hanya mau berteman dengan orang yang seagama",
           "Melaksanakan ibadah sesuai agama dan menghormati ibadah agama lain",
           "Menganggap agama sendiri paling benar dan merendahkan agama lain"],
     "j": 2},

    {"p": "Penerapan nilai sila ke-5 Pancasila 'Keadilan Sosial bagi Seluruh Rakyat Indonesia' dalam kehidupan adalah ...",
     "o": ["Memberikan semua fasilitas hanya kepada orang yang mampu",
           "Memperlakukan semua orang secara adil tanpa diskriminasi",
           "Mengutamakan kepentingan orang-orang yang berkuasa",
           "Tidak peduli dengan kesulitan yang dialami orang lain"],
     "j": 1},

    # ── 7. NILAI KEADILAN DI SEKOLAH ────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Di kelas 6A, Pak Guru selalu memberikan kesempatan yang sama kepada semua\n'
           'siswa untuk menjawab pertanyaan. Siswa yang berprestasi mendapat penghargaan,\n'
           'sedangkan yang belum mahir mendapat bimbingan tambahan."\n\n'
           'Penerapan nilai keadilan yang terdapat dalam bacaan di atas adalah ...'),
     "o": ["Pak Guru hanya memberikan perhatian kepada siswa berprestasi saja",
           "Semua siswa mendapat tugas berbeda sesuai kemampuan masing-masing",
           "Semua siswa diperlakukan adil dan mendapat kesempatan yang setara",
           "Hanya siswa yang pintar yang berhak mendapat penghargaan"],
     "j": 2},

    {"p": "Contoh penerapan nilai keadilan dalam kehidupan bersama di sekolah adalah ...",
     "o": ["Guru hanya menjelaskan materi kepada siswa yang sering bertanya",
           "Ketua kelas mendapat hak istimewa yang tidak dimiliki siswa lain",
           "Semua siswa mendapat giliran piket yang sama dan tugas yang setara",
           "Siswa yang kaya dibebaskan dari tugas membersihkan kelas"],
     "j": 2},

    # ── 8. AKIBAT TIDAK MELAKSANAKAN KEWAJIBAN DI JALAN ────
    {"p": "Akibat yang ditimbulkan jika pengendara tidak mematuhi rambu lalu lintas di jalan raya adalah ...",
     "o": ["Perjalanan menjadi lebih lancar dan cepat sampai tujuan",
           "Tidak ada dampak buruk karena rambu hanya bersifat saran",
           "Membahayakan keselamatan diri sendiri dan pengguna jalan lain",
           "Mendapat pujian dari polisi lalu lintas setempat"],
     "j": 2},

    {"p": "Seseorang yang berkendara tanpa memakai helm di jalan raya telah melanggar kewajibannya. Akibat yang paling mungkin terjadi adalah ...",
     "o": ["Perjalanan menjadi lebih menyenangkan karena bebas",
           "Ditilang polisi dan membahayakan keselamatan diri sendiri",
           "Mendapat pujian dari sesama pengendara di jalan",
           "Tidak ada akibat selama tidak terjadi kecelakaan"],
     "j": 1},

    # ── 9. KEWAJIBAN WARGA NEGARA ───────────────────────────
    {"p": "Pernyataan yang BENAR berkaitan dengan kewajiban warga negara Indonesia adalah ...",
     "o": ["Warga negara berhak tidak membayar pajak jika tidak ingin",
           "Kewajiban hanya berlaku bagi pejabat dan pegawai negeri",
           "Setiap warga negara wajib membela negara, membayar pajak, dan mematuhi hukum",
           "Kewajiban warga negara hanya mencoblos saat pemilihan umum saja"],
     "j": 2},

    {"p": "Kewajiban warga negara yang diatur dalam UUD 1945 antara lain adalah ...",
     "o": ["Mendapat pekerjaan yang layak dari pemerintah",
           "Memilih presiden sesuai keinginan tanpa syarat apapun",
           "Membela negara dan tunduk kepada hukum yang berlaku di Indonesia",
           "Mendapat pendidikan gratis hingga perguruan tinggi negeri"],
     "j": 2},

    # ── 10. PERSATUAN DAN KESATUAN ───────────────────────────
    {"p": "Manakah yang merupakan contoh sikap persatuan dan kesatuan di lingkungan sekolah?",
     "o": ["Hanya mau berteman dengan teman dari suku yang sama",
           "Menolak belajar kelompok dengan teman yang berbeda agama",
           "Bersama-sama membersihkan sekolah tanpa membeda-bedakan teman",
           "Mengejek teman yang berasal dari daerah yang berbeda"],
     "j": 2},

    {"p": "Manfaat persatuan dan kesatuan bagi bangsa Indonesia adalah ...",
     "o": ["Mempermudah satu kelompok untuk berkuasa atas kelompok lain",
           "Menjaga stabilitas negara, mempererat hubungan, dan memperkuat pertahanan bangsa",
           "Menghilangkan semua perbedaan yang ada di masyarakat Indonesia",
           "Mengutamakan kepentingan satu suku di atas kepentingan bangsa"],
     "j": 1},

    # ── 11. SILA KE-4 PANCASILA ──────────────────────────────
    {"p": "Penerapan nilai-nilai sila ke-4 Pancasila dalam kehidupan di sekolah adalah ...",
     "o": ["Memaksakan pendapat pribadi kepada semua teman di kelas",
           "Mengambil keputusan dengan cara musyawarah dan mufakat",
           "Keputusan diambil oleh guru saja tanpa melibatkan siswa",
           "Menolak hasil musyawarah jika tidak sesuai keinginan pribadi"],
     "j": 1},

    {"p": "Contoh pengamalan sila ke-4 'Kerakyatan yang Dipimpin oleh Hikmat Kebijaksanaan dalam Permusyawaratan/Perwakilan' adalah ...",
     "o": ["Memilih ketua kelas dengan cara tunjuk langsung oleh guru",
           "Memenangkan perdebatan dengan cara memaksakan pendapat",
           "Bermusyawarah untuk menentukan tema pentas seni kelas",
           "Mengabaikan pendapat teman yang dianggap tidak penting"],
     "j": 2},

    # ── 12. SILA KE-2 KEMANUSIAAN ────────────────────────────
    {"p": "Pengamalan nilai-nilai Pancasila sila 'Kemanusiaan yang Adil dan Beradab' dalam kehidupan sehari-hari adalah ...",
     "o": ["Membantu teman hanya jika ada imbalan yang akan diberikan",
           "Menghormati orang tua saja, tidak perlu menghormati teman",
           "Menolong orang yang kesulitan tanpa memandang perbedaan suku atau agama",
           "Hanya bergaul dengan orang yang status sosialnya setara"],
     "j": 2},

    {"p": "Perilaku yang mencerminkan sila ke-2 Pancasila adalah ...",
     "o": ["Menghina teman yang memiliki kekurangan fisik",
           "Tidak mau duduk berdekatan dengan teman yang berbeda suku",
           "Mengumpat kepada teman yang membuat kesalahan",
           "Memperlakukan semua teman dengan sopan dan tidak merendahkan siapapun"],
     "j": 3},

    # ── 13. HAK DAN KEWAJIBAN TIDAK SEIMBANG ────────────────
    {"p": "Akibat yang ditimbulkan jika hak dan kewajiban tidak seimbang dalam kehidupan bermasyarakat adalah ...",
     "o": ["Kehidupan masyarakat menjadi lebih adil dan sejahtera",
           "Setiap orang semakin giat melaksanakan kewajibannya",
           "Timbul ketidakadilan, konflik, dan keharmonisan masyarakat terganggu",
           "Pemerintah makin mudah mengatur kehidupan masyarakat"],
     "j": 2},

    # SOAL SULIT (1 dari 6)
    {"p": ('Seorang siswa selalu menuntut haknya untuk bermain tetapi tidak mau\n'
           'melaksanakan kewajibannya mengerjakan PR dan membantu orang tua.\n\n'
           'Akibat yang paling tepat dari perilaku tersebut adalah ...'),
     "o": ["Siswa tersebut akan semakin pintar karena banyak bermain",
           "Tidak ada akibat negatif selama orang tuanya tidak marah",
           "Prestasi belajarnya menurun dan tanggung jawabnya tidak terpenuhi",
           "Guru akan memahami dan tetap memberikan nilai yang bagus"],
     "j": 2},

    # ── 14. HAK ANAK DI RUMAH ────────────────────────────────
    {"p": "Berikut yang merupakan hak anak di rumah adalah ...",
     "o": ["Boleh tidak mengerjakan tugas sekolah jika merasa lelah",
           "Memerintah orang tua untuk melakukan apapun yang diinginkan",
           "Mendapat kasih sayang, perlindungan, dan kebutuhan dasar dari orang tua",
           "Bebas keluar malam tanpa seijin orang tua"],
     "j": 2},

    {"p": "Hak anak yang wajib dipenuhi oleh orang tua di rumah antara lain adalah ...",
     "o": ["Mendapat uang jajan sebanyak yang diinginkan anak",
           "Mendapat pendidikan yang baik, kasih sayang, dan perlindungan dari bahaya",
           "Bebas menggunakan gadget sepanjang hari tanpa batasan apapun",
           "Tidak harus membantu pekerjaan rumah tangga sama sekali"],
     "j": 1},

    # ── 15. SIKAP PARA PAHLAWAN ──────────────────────────────
    {"p": "Sikap-sikap para pahlawan dalam memperjuangkan kemerdekaan Indonesia yang patut diteladani antara lain ...",
     "o": ["Mementingkan keuntungan pribadi dalam setiap perjuangan",
           "Rela berkorban, pantang menyerah, dan bersatu padu demi bangsa",
           "Berjuang hanya jika mendapat imbalan dari pemerintah",
           "Mengutamakan kepentingan suku sendiri di atas kepentingan bangsa"],
     "j": 1},

    {"p": "Nilai yang dapat diteladani dari sikap para pahlawan kemerdekaan dalam kehidupan sehari-hari adalah ...",
     "o": ["Keberanian menyerang siapa saja yang dianggap sebagai musuh",
           "Menghalalkan segala cara demi mencapai tujuan yang diinginkan",
           "Semangat perjuangan, rela berkorban, dan cinta tanah air",
           "Menganggap kekuatan fisik adalah satu-satunya cara menyelesaikan masalah"],
     "j": 2},

    # ── 16. TANGGUNG JAWAB DI MASYARAKAT ────────────────────
    {"p": "Contoh sikap yang merupakan penerapan tanggung jawab di lingkungan masyarakat adalah ...",
     "o": ["Membuang sampah sembarangan karena sudah membayar retribusi",
           "Membiarkan lingkungan kotor karena itu tugas petugas kebersihan",
           "Aktif mengikuti kegiatan gotong royong dan menjaga kebersihan lingkungan",
           "Hanya mau menjaga kebersihan di depan rumah sendiri saja"],
     "j": 2},

    {"p": "Penerapan tanggung jawab warga di lingkungan RT adalah ...",
     "o": ["Hanya hadir dalam rapat RT jika ada kepentingan pribadi",
           "Ikut serta dalam kegiatan ronda malam dan menjaga keamanan lingkungan",
           "Membiarkan tetangga menyelesaikan masalah lingkungan sendiri",
           "Tidak perlu ikut kegiatan bersama karena sudah membayar iuran"],
     "j": 1},

    # ── 17. NORMA DALAM MASYARAKAT ───────────────────────────
    {"p": "Norma yang berlaku sebagai warga negara dalam masyarakat terdiri dari ...",
     "o": ["Norma agama, norma kesusilaan, norma kesopanan, dan norma hukum",
           "Norma belajar, norma bermain, norma bekerja, dan norma beribadah",
           "Norma formal, norma informal, norma tertulis, dan norma lisan",
           "Norma nasional, norma daerah, norma kelompok, dan norma pribadi"],
     "j": 0},

    {"p": "Fungsi norma dalam kehidupan masyarakat adalah ...",
     "o": ["Membatasi kreativitas dan kebebasan individu dalam berekspresi",
           "Mengatur perilaku anggota masyarakat agar tercipta ketertiban dan keharmonisan",
           "Hanya berlaku bagi orang dewasa, bukan anak-anak sekolah",
           "Diciptakan untuk menguntungkan pihak-pihak tertentu saja"],
     "j": 1},

    # ── 18. PELAKSANAAN TANGGUNG JAWAB WARGA MASYARAKAT ─────
    {"p": "Bentuk tanggung jawab warga terhadap lingkungan masyarakatnya adalah ...",
     "o": ["Hanya menjaga kebersihan rumah dan halaman sendiri",
           "Membayar pajak tepat waktu dan mengikuti kegiatan sosial kemasyarakatan",
           "Menyerahkan semua urusan lingkungan kepada pengurus RT dan RW",
           "Tidak perlu mengikuti kegiatan masyarakat karena terlalu sibuk bekerja"],
     "j": 1},

    {"p": "Tanggung jawab warga dalam kegiatan gotong royong adalah ...",
     "o": ["Hadir jika ada keuntungan yang dapat diperoleh dari kegiatan",
           "Hanya ikut memimpin, tidak perlu ikut bekerja secara langsung",
           "Ikut berpartisipasi aktif dan menyelesaikan pekerjaan bersama-sama",
           "Menitipkan uang saja tanpa harus hadir secara langsung"],
     "j": 2},

    # ── 19. TOLERANSI (BACAAN) ───────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Di sekolah Bina Bangsa, murid-murid berasal dari berbagai agama dan suku.\n'
           'Setiap hari raya keagamaan, teman-teman saling mengucapkan selamat dan\n'
           'menghormati teman yang sedang berpuasa dengan tidak makan di depannya.\n'
           'Mereka semua saling menghargai dan hidup rukun."\n\n'
           'Sikap toleransi yang terdapat dalam bacaan di atas adalah ...'),
     "o": ["Murid-murid memaksakan teman mengikuti agama mayoritas",
           "Saling mengucapkan selamat hari raya dan menghormati teman yang berpuasa",
           "Teman-teman tidak mau bergaul dengan yang berbeda agama",
           "Hanya berurusan dengan teman yang berasal dari suku yang sama"],
     "j": 1},

    {"p": "Contoh sikap toleransi dalam kehidupan sehari-hari di lingkungan sekolah adalah ...",
     "o": ["Mengganggu teman yang sedang melaksanakan ibadah agamanya",
           "Mengejek cara berpakaian teman yang berbeda budaya",
           "Tidak mempermasalahkan perbedaan agama dan suku dalam berteman",
           "Hanya mau berbagi makanan dengan teman yang seagama"],
     "j": 2},

    # ── 20. KERAGAMAN BUDAYA ─────────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Indonesia memiliki lebih dari 300 suku bangsa dengan budaya dan adat\n'
           'istiadat yang berbeda-beda. Keragaman ini merupakan kekayaan bangsa yang\n'
           'harus dijaga. Dengan menghargai perbedaan, bangsa Indonesia semakin kuat."\n\n'
           'Sikap yang tepat dalam menghadapi keragaman budaya di masyarakat adalah ...'),
     "o": ["Menganggap budaya sendiri paling baik dan meremehkan budaya lain",
           "Menghapus semua budaya daerah agar hanya ada satu budaya nasional",
           "Menghargai dan melestarikan keragaman budaya sebagai kekayaan bangsa",
           "Meniru semua budaya asing karena lebih modern dan menarik"],
     "j": 2},

    {"p": "Manfaat keragaman budaya bagi bangsa Indonesia adalah ...",
     "o": ["Menjadi sumber perpecahan yang harus segera diselesaikan",
           "Membuat bangsa Indonesia sulit bersatu karena terlalu berbeda",
           "Menjadi kekayaan dan daya tarik bangsa yang memperkuat identitas nasional",
           "Hanya bermanfaat bagi sektor pariwisata, tidak ada manfaat lainnya"],
     "j": 2},

    # ── 21. LAMBANG NILAI PANCASILA CINTA TANAH AIR ─────────
    {"p": "Lambang sila ke-3 Pancasila 'Persatuan Indonesia' adalah ...",
     "o": ["Bintang emas",
           "Rantai emas",
           "Pohon beringin",
           "Kepala banteng"],
     "j": 2},

    {"p": "Arti lambang pohon beringin pada sila ke-3 Pancasila adalah ...",
     "o": ["Melambangkan kekuatan dan keberanian bangsa Indonesia",
           "Melambangkan tempat berteduh dan persatuan seluruh rakyat Indonesia",
           "Melambangkan kesuburan tanah Indonesia yang sangat kaya",
           "Melambangkan kebijaksanaan dalam pengambilan keputusan bersama"],
     "j": 1},

    # ── 22. SILA YANG SESUAI DENGAN KEGIATAN ────────────────
    {"p": "Kegiatan musyawarah untuk menentukan ketua kelas mencerminkan pengamalan sila ke ...",
     "o": ["Sila ke-1 (Ketuhanan Yang Maha Esa)",
           "Sila ke-2 (Kemanusiaan yang Adil dan Beradab)",
           "Sila ke-3 (Persatuan Indonesia)",
           "Sila ke-4 (Kerakyatan yang Dipimpin oleh Hikmat Kebijaksanaan)"],
     "j": 3},

    {"p": "Kegiatan melaksanakan ibadah shalat Jumat bagi umat Islam mencerminkan pengamalan sila ke ...",
     "o": ["Sila ke-1 (Ketuhanan Yang Maha Esa)",
           "Sila ke-2 (Kemanusiaan yang Adil dan Beradab)",
           "Sila ke-3 (Persatuan Indonesia)",
           "Sila ke-5 (Keadilan Sosial bagi Seluruh Rakyat Indonesia)"],
     "j": 0},

    # ── 23. TANGGUNG JAWAB TERHADAP KEPUTUSAN BERSAMA ───────
    {"p": "Bentuk tanggung jawab yang tepat terhadap hasil keputusan musyawarah adalah ...",
     "o": ["Menolak melaksanakan keputusan yang tidak sesuai keinginan pribadi",
           "Menerima dan melaksanakan keputusan dengan penuh tanggung jawab meski berbeda pendapat",
           "Hanya melaksanakan bagian keputusan yang menguntungkan diri sendiri",
           "Memprotes keputusan musyawarah kepada pihak yang lebih tinggi"],
     "j": 1},

    {"p": "Setelah keputusan musyawarah kelas diambil, sikap yang benar adalah ...",
     "o": ["Melaksanakan keputusan hanya jika diawasi langsung oleh guru",
           "Mengabaikan keputusan karena tidak ikut hadir dalam musyawarah",
           "Melaksanakan keputusan dengan ikhlas dan penuh tanggung jawab",
           "Mencari celah untuk tidak melaksanakan keputusan tersebut"],
     "j": 2},

    # ── 24. TEKS BACAAN – PERNYATAAN YANG SESUAI ────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Pancasila lahir pada tanggal 1 Juni 1945. Pada tanggal itu, Ir. Soekarno\n'
           'menyampaikan pidatonya yang berisi lima dasar negara. Kelima dasar tersebut\n'
           'kemudian ditetapkan pada tanggal 18 Agustus 1945 oleh PPKI sebagai dasar negara."\n\n'
           'Pernyataan yang SESUAI dengan teks bacaan di atas adalah ...'),
     "o": ["Pancasila lahir pada tanggal 18 Agustus 1945",
           "Lima dasar negara disampaikan oleh Mohammad Hatta",
           "Pancasila ditetapkan oleh BPUPKI pada tanggal 1 Juni 1945",
           "Ir. Soekarno menyampaikan konsep lima dasar negara pada tanggal 1 Juni 1945"],
     "j": 3},

    {"p": ('Bacalah teks berikut!\n'
           '"Gotong royong adalah kegiatan bekerja bersama-sama untuk mencapai tujuan\n'
           'yang diinginkan. Kegiatan ini sudah menjadi budaya asli bangsa Indonesia\n'
           'sejak nenek moyang. Gotong royong mencerminkan nilai kebersamaan dan saling\n'
           'membantu yang merupakan inti kepribadian bangsa Indonesia."\n\n'
           'Pernyataan yang SESUAI dengan isi bacaan adalah ...'),
     "o": ["Gotong royong berasal dari budaya luar yang masuk ke Indonesia",
           "Gotong royong hanya dilakukan oleh masyarakat pedesaan saja",
           "Gotong royong adalah budaya asli Indonesia yang mencerminkan kebersamaan",
           "Gotong royong baru mulai dikenal sejak Indonesia merdeka pada 1945"],
     "j": 2},

    # ── 25. TEMPAT IBADAH (BACAAN) ───────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Indonesia mengakui enam agama resmi. Umat Islam beribadah di masjid,\n'
           'umat Kristen di gereja, umat Katolik di gereja, umat Hindu di pura,\n'
           'umat Buddha di vihara, dan umat Konghucu di klenteng. Semua tempat ibadah\n'
           'dilindungi dan dijamin oleh negara."\n\n'
           'Berdasarkan bacaan di atas, tempat ibadah umat Hindu adalah ...'),
     "o": ["Masjid",
           "Vihara",
           "Pura",
           "Klenteng"],
     "j": 2},

    {"p": "Pasangan agama dan tempat ibadah yang TEPAT berdasarkan bacaan di atas adalah ...",
     "o": ["Islam — Gereja",
           "Buddha — Pura",
           "Hindu — Klenteng",
           "Konghucu — Klenteng"],
     "j": 3},

    # ── 26. KEGIATAN PERSATUAN DAN KESATUAN (BACAAN) ────────
    {"p": ('Bacalah teks berikut!\n'
           '"Setiap Sabtu pagi, warga Desa Maju Bersama mengadakan kerja bakti\n'
           'membersihkan lingkungan. Semua warga turut berpartisipasi, tidak ada yang\n'
           'membeda-bedakan suku, agama, maupun profesi. Mereka bersatu menjaga\n'
           'kebersihan dan keindahan desa bersama-sama."\n\n'
           'Kegiatan yang mencerminkan persatuan dan kesatuan dalam bacaan tersebut adalah ...'),
     "o": ["Hanya warga yang kaya yang membersihkan lingkungan desa",
           "Kerja bakti yang dilakukan seluruh warga tanpa membeda-bedakan latar belakang",
           "Pemuda saja yang aktif berpartisipasi dalam kegiatan kerja bakti",
           "Kegiatan kerja bakti hanya dilakukan pada hari-hari tertentu saja"],
     "j": 1},

    {"p": "Contoh kegiatan yang mencerminkan persatuan dan kesatuan di lingkungan sekolah adalah ...",
     "o": ["Memilih anggota kelompok belajar hanya dari suku yang sama",
           "Menolak teman yang berbeda agama masuk dalam kelompok belajar",
           "Mengadakan pentas seni budaya yang menampilkan keragaman daerah",
           "Hanya merayakan hari besar dari satu agama saja di sekolah"],
     "j": 2},

    # ── SOAL TAMBAHAN (variasi dan pendalaman materi) ────────
    {"p": "Pancasila terdiri dari dua kata bahasa Sansekerta, yaitu 'Panca' dan 'Sila'. Artinya adalah ...",
     "o": ["Lima peraturan yang wajib ditaati",
           "Lima dasar atau lima asas negara",
           "Lima ketentuan hukum negara",
           "Lima perintah dari pemimpin negara"],
     "j": 1},

    # SOAL SULIT (2 dari 6)
    {"p": ('Perhatikan pernyataan berikut!\n'
           '1. Semua warga negara berhak mendapat pendidikan\n'
           '2. Semua warga negara wajib membela negara\n'
           '3. Pemerintah wajib melindungi setiap warga negara\n'
           '4. Semua warga negara wajib membayar pajak\n\n'
           'Dari pernyataan di atas, yang termasuk KEWAJIBAN warga negara adalah ...'),
     "o": ["Pernyataan 1 dan 3",
           "Pernyataan 1 dan 2",
           "Pernyataan 2 dan 4",
           "Pernyataan 3 dan 4"],
     "j": 2},

    {"p": "Urutan sila-sila Pancasila dari sila pertama hingga kelima yang BENAR adalah ...",
     "o": ["Ketuhanan – Kemanusiaan – Kerakyatan – Persatuan – Keadilan",
           "Ketuhanan – Kemanusiaan – Persatuan – Kerakyatan – Keadilan",
           "Kemanusiaan – Ketuhanan – Persatuan – Kerakyatan – Keadilan",
           "Ketuhanan – Persatuan – Kemanusiaan – Kerakyatan – Keadilan"],
     "j": 1},

    # SOAL SULIT (3 dari 6)
    {"p": ('Rapat kelas sedang berlangsung untuk menentukan jadwal piket. Rani menginginkan\n'
           'jadwal hari Senin, tetapi hasil musyawarah memutuskan jadwal piket Rani adalah\n'
           'hari Kamis.\n\n'
           'Sikap yang PALING sesuai dengan nilai Pancasila sila ke-4 adalah ...'),
     "o": ["Menolak melaksanakan piket karena jadwalnya tidak sesuai keinginan",
           "Menerima hasil keputusan dengan lapang dada dan melaksanakan piket di hari Kamis",
           "Memaksa anggota lain untuk mengubah hasil keputusan musyawarah",
           "Hanya ikut piket jika ada yang mengajak dan mengingatkan"],
     "j": 1},

    {"p": "Lambang sila ke-1 Pancasila 'Ketuhanan Yang Maha Esa' adalah ...",
     "o": ["Rantai emas",
           "Bintang emas",
           "Pohon beringin",
           "Kepala banteng"],
     "j": 1},

    {"p": "Lambang sila ke-2 Pancasila 'Kemanusiaan yang Adil dan Beradab' adalah ...",
     "o": ["Padi dan kapas",
           "Kepala banteng",
           "Rantai emas",
           "Bintang emas"],
     "j": 2},

    # SOAL SULIT (4 dari 6)
    {"p": ('Bu Guru memberikan tugas berbeda berdasarkan kemampuan siswa. Siswa yang\n'
           'sudah mahir mendapat soal lebih sulit, sedangkan yang belum mahir mendapat\n'
           'soal lebih mudah. Tindakan Bu Guru ini paling mencerminkan nilai ...\n'),
     "o": ["Sila ke-1 karena menyesuaikan dengan kepercayaan siswa",
           "Sila ke-2 karena memperlakukan siswa secara adil sesuai keadaannya",
           "Sila ke-3 karena mempererat persatuan antar siswa di kelas",
           "Sila ke-5 karena memberikan fasilitas berbeda kepada setiap siswa"],
     "j": 1},

    # SOAL SULIT (5 dari 6)
    {"p": ('Kegiatan "Warga desa bergotong royong membangun jembatan agar semua\n'
           'warga bisa menyeberangi sungai dengan aman" paling mencerminkan sila\n'
           'yang dilambangkan oleh ...'),
     "o": ["Bintang emas — sila ke-1",
           "Rantai emas — sila ke-2",
           "Padi dan kapas — sila ke-5",
           "Pohon beringin — sila ke-3"],
     "j": 3},

    # SOAL SULIT (6 dari 6)
    {"p": ('Perhatikan perilaku berikut!\n'
           'A. Berdoa sebelum belajar\n'
           'B. Membantu teman yang terjatuh\n'
           'C. Mengikuti upacara bendera dengan khidmat\n'
           'D. Bermusyawarah dalam menentukan jadwal piket\n\n'
           'Perilaku yang mencerminkan sila ke-3 Pancasila adalah ...'),
     "o": ["Perilaku A",
           "Perilaku B",
           "Perilaku C",
           "Perilaku D"],
     "j": 2},

]

# ─────────────────────────────────────────────────────────────
#  POOL SOAL ESAI  (10 soal – diambil 5 per sesi)
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    {"p": ('Tuliskan teks Sumpah Pemuda dengan benar dan lengkap!\n\n'
           'Setelah itu, jelaskan makna Sumpah Pemuda bagi persatuan dan\n'
           'kesatuan bangsa Indonesia!')},

    {"p": ('Bacalah teks berikut!\n\n'
           '"Pancasila adalah dasar negara dan pandangan hidup bangsa Indonesia.\n'
           'Nilai-nilai Pancasila harus diterapkan dalam kehidupan sehari-hari\n'
           'oleh setiap warga negara, baik di lingkungan keluarga, sekolah,\n'
           'maupun masyarakat."\n\n'
           'Berdasarkan bacaan di atas, sebutkan dan jelaskan 5 nilai-nilai\n'
           'Pancasila dalam kehidupan sehari-hari beserta contoh nyatanya!')},

    {"p": ('Jelaskan 5 cara yang dapat dilakukan untuk menjaga persatuan dan\n'
           'kesatuan bangsa Indonesia dalam kehidupan sehari-hari!\n\n'
           'Tuliskan jawabanmu dalam kalimat yang lengkap!')},

    {"p": ('Sebagai warga negara Indonesia, kita memiliki hak dan kewajiban\n'
           'yang diatur dalam UUD 1945.\n\n'
           'Sebutkan 5 hak warga negara Indonesia yang diatur dalam UUD 1945\n'
           'dan jelaskan masing-masing secara singkat!')},

    {"p": ('Jelaskan nilai-nilai yang terkandung dalam setiap sila Pancasila\n'
           '(sila ke-1 hingga sila ke-5) dan berikan satu contoh penerapannya\n'
           'dalam kehidupan di sekolah!')},

    {"p": ('Jelaskan perbedaan antara HAK dan KEWAJIBAN!\n\n'
           'Kemudian sebutkan:\n'
           'a. 3 contoh hak siswa di sekolah\n'
           'b. 3 contoh kewajiban siswa di sekolah\n\n'
           'Mengapa hak dan kewajiban harus dilaksanakan secara seimbang?')},

    {"p": ('Bacalah teks berikut!\n\n'
           '"Setiap hari Minggu, warga perumahan Griya Asri mengadakan kegiatan\n'
           'gotong royong membersihkan lingkungan. Semua warga dari berbagai\n'
           'latar belakang suku, agama, dan pekerjaan turut serta dengan penuh\n'
           'semangat tanpa ada yang merasa enggan."\n\n'
           'a. Nilai-nilai Pancasila apa saja yang terdapat dalam teks tersebut?\n'
           'b. Mengapa gotong royong penting bagi kehidupan bermasyarakat?\n'
           'c. Sebutkan 3 manfaat gotong royong bagi warga masyarakat!')},

    {"p": ('a. Apa yang dimaksud dengan toleransi dalam kehidupan beragama?\n'
           'b. Mengapa toleransi sangat penting bagi bangsa Indonesia\n'
           '   yang memiliki banyak agama dan suku?\n'
           'c. Berikan 3 contoh nyata sikap toleransi yang dapat kamu\n'
           '   terapkan di sekolah!')},

    {"p": ('Jelaskan mengapa Pancasila sangat penting sebagai dasar negara\n'
           'dan pandangan hidup bangsa Indonesia!\n\n'
           'Apa yang akan terjadi jika bangsa Indonesia tidak memiliki Pancasila\n'
           'sebagai dasar negara? Jelaskan dengan alasanmu!')},

    {"p": ('Ceritakan pengalamanmu dalam menerapkan salah satu nilai Pancasila\n'
           'di lingkungan sekolah atau masyarakat!\n\n'
           'Tuliskan:\n'
           'a. Nilai Pancasila apa yang kamu terapkan\n'
           'b. Bagaimana cara kamu menerapkannya\n'
           'c. Apa manfaat yang kamu rasakan dari penerapan nilai tersebut')},
]

# ─────────────────────────────────────────────────────────────
#  PERSIAPAN SOAL SESI
# ─────────────────────────────────────────────────────────────

def prepare_session():
    labels = list("ABCD")
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
    selected_esai = random.sample(ESAI_POOL, NUM_ESAI)
    for q in selected_esai:
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
    tk.Button(d, text="OK", bg="#16a34a", fg="#fff",
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
        self._nav_lock   = False
        self._build_exam()
        self._enforce_fg()

    def _setup_window(self):
        r = self.root
        r.title("Ujian Pancasila Kelas 6 SD")
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
            active_dialogs = [w for w in self.root.winfo_children()
                              if isinstance(w, tk.Toplevel) and w.winfo_exists()]
            if active_dialogs:
                active_dialogs[-1].lift()
            else:
                self.root.lift()
                if self.root.focus_displayof() is None:
                    self.root.focus_force()
        except Exception:
            pass
        self.root.after(600, self._enforce_fg)

    def _try_exit(self):
        stop_hook()
        self.root.destroy()
        sys.exit(0)

    def _build_exam(self):
        wrap = tk.Frame(self.root, bg=C["page"])
        wrap.pack(fill="both", expand=True)
        self._wrap = wrap
        self._build_topbar(wrap)
        self._build_navbar(wrap)
        self._build_scroll(wrap)
        self._show_question(0)

    def _build_topbar(self, parent):
        tb = tk.Frame(parent, bg=C["topbar"])
        tb.pack(fill="x")
        tk.Label(tb, text="UJIAN PANCASILA  •  KELAS 6 SD",
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

    def _build_navbar(self, parent):
        nb = tk.Frame(parent, bg=C["nav_bg"])
        nb.pack(fill="x")
        tk.Frame(nb, bg="#e2e8f0", height=1).pack(fill="x")
        inner = tk.Frame(nb, bg=C["nav_bg"])
        inner.pack(pady=6, padx=12)
        self._nav_btns = []
        pg_lf = tk.Frame(inner, bg=C["nav_bg"])
        pg_lf.pack(anchor="w")
        tk.Label(pg_lf, text="PG:",
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

    def _build_scroll(self, parent):
        cont = tk.Frame(parent, bg=C["page"])
        cont.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(cont, bg=C["page"], highlightthickness=0)
        vsb = ttk.Scrollbar(cont, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self._scroll_inner = tk.Frame(self._canvas, bg=C["page"])
        self._cw = self._canvas.create_window((0, 0), window=self._scroll_inner, anchor="nw")
        self._scroll_inner.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cw, width=e.width))

    def _show_question(self, idx):
        if self._nav_lock:
            return
        self._nav_lock = True
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
        self.root.after(250, self._release_nav_lock)

    def _release_nav_lock(self):
        self._nav_lock = False

    def _render_pg(self, card, idx):
        q = self.questions[idx]
        pg_num = idx + 1
        total  = NUM_PG + NUM_ESAI
        badge_row = tk.Frame(card, bg=C["card"])
        badge_row.pack(fill="x", padx=40, pady=(28, 0))
        tk.Label(badge_row,
                 text=f"  PILIHAN GANDA  {pg_num}/{NUM_PG}  ",
                 bg=C["q_pg_accent"], fg="#fff",
                 font=("Segoe UI", 9, "bold"),
                 padx=4, pady=3).pack(side="left")
        answered_count = sum(1 for a in self.answers.values() if a not in (None, ""))
        tk.Label(badge_row,
                 text=f"  {answered_count} dari {total} soal dijawab  ",
                 bg="#f0fdf4", fg="#15803d",
                 font=("Segoe UI", 9),
                 padx=4, pady=3).pack(side="left", padx=10)
        prog_frame = tk.Frame(card, bg="#e2e8f0", height=5)
        prog_frame.pack(fill="x", padx=40, pady=(10, 0))
        pw = 800
        pct_w = max(4, int(pw * pg_num / total))
        tk.Frame(prog_frame, bg=C["q_pg_accent"], height=5, width=pct_w).place(x=0, y=0)
        tk.Label(card, text=q["p"],
                 bg=C["card"], fg=C["q_text"],
                 font=("Segoe UI", 14),
                 wraplength=900, justify="left",
                 anchor="nw").pack(fill="x", padx=40, pady=(20, 8))
        opts_wrap = tk.Frame(card, bg=C["card"])
        opts_wrap.pack(fill="x", padx=40, pady=(4, 0))

        opt_widgets = {}

        def _apply_style(ws, selected):
            if selected:
                ws["row"].config(bg=C["opt_sel_bg"])
                ws["badge"].config(bg=C["opt_sel_lbg"], fg="#ffffff")
                ws["lbl"].config(bg=C["opt_sel_bg"], fg=C["opt_sel_fg"])
                for w in ws.values():
                    w.unbind("<Enter>")
                    w.unbind("<Leave>")
            else:
                ws["row"].config(bg=C["opt_bg"])
                ws["badge"].config(bg=C["opt_letter_bg"], fg=C["opt_letter_fg"])
                ws["lbl"].config(bg=C["opt_bg"], fg=C["opt_fg"])
                r, l = ws["row"], ws["lbl"]
                def h_in(e, r=r, l=l):
                    r.config(bg=C["opt_hover"]); l.config(bg=C["opt_hover"])
                def h_out(e, r=r, l=l):
                    r.config(bg=C["opt_bg"]); l.config(bg=C["opt_bg"])
                for w in ws.values():
                    w.bind("<Enter>", h_in)
                    w.bind("<Leave>", h_out)

        def _select(letter):
            if self.answers.get(idx) == letter:
                return
            self.answers[idx] = letter
            self._refresh_counter()
            self._update_nav()
            for let, ws in opt_widgets.items():
                _apply_style(ws, let == letter)

        current_answer = self.answers.get(idx)
        for opt in q["o"]:
            letter = opt[0]
            text   = opt[3:]
            sel    = (current_answer == letter)

            row_bg = C["opt_sel_bg"] if sel else C["opt_bg"]
            txt_fg = C["opt_sel_fg"] if sel else C["opt_fg"]
            lbg    = C["opt_sel_lbg"] if sel else C["opt_letter_bg"]
            lfg    = "#ffffff" if sel else C["opt_letter_fg"]

            row = tk.Frame(opts_wrap, bg=row_bg, cursor="hand2")
            row.pack(fill="x", pady=5)

            badge = tk.Label(row, text=letter, bg=lbg, fg=lfg,
                             font=("Segoe UI", 12, "bold"),
                             width=2, padx=10, pady=14)
            badge.pack(side="left")

            lbl = tk.Label(row, text=text, bg=row_bg, fg=txt_fg,
                           font=("Segoe UI", 12), anchor="w",
                           padx=16, pady=14, wraplength=820, justify="left")
            lbl.pack(side="left", fill="x", expand=True)

            ws = {"row": row, "badge": badge, "lbl": lbl}
            opt_widgets[letter] = ws

            click = (lambda let=letter: lambda e: _select(let))()
            for w in (row, badge, lbl):
                w.bind("<Button-1>", click)

            if not sel:
                r, l = row, lbl
                def h_in(e, r=r, l=l):
                    r.config(bg=C["opt_hover"]); l.config(bg=C["opt_hover"])
                def h_out(e, r=r, l=l):
                    r.config(bg=C["opt_bg"]); l.config(bg=C["opt_bg"])
                for w in (row, badge, lbl):
                    w.bind("<Enter>", h_in)
                    w.bind("<Leave>", h_out)

        self._render_nav_buttons(card, idx)

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
        pw = 800
        pct_w = max(4, int(pw * (idx + 1) / total))
        tk.Frame(prog_frame, bg=C["q_esai_accent"], height=5, width=pct_w).place(x=0, y=0)
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
                row.config(bg=C["opt_hover"]); lbl.config(bg=C["opt_hover"])
        def _hover_out(e):
            if not is_selected:
                row.config(bg=C["opt_bg"]); lbl.config(bg=C["opt_bg"])
        for w in (row, badge, lbl):
            w.bind("<Button-1>", lambda e, f=_select: f())
            if not is_selected:
                w.bind("<Enter>", _hover_in)
                w.bind("<Leave>", _hover_out)

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

    def _save_essay(self):
        if self._cur_tw is not None and self.current >= NUM_PG:
            self.answers[self.current] = self._cur_tw.get("1.0", "end-1c").strip()
        self._cur_tw = None

    def _refresh_counter(self):
        if self._answered_lbl is None:
            return
        done  = sum(1 for a in self.answers.values() if a not in (None, ""))
        total = NUM_PG + NUM_ESAI
        self._answered_lbl.config(text=f"✓ {done} / {total} dijawab")

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
            color = C["timer_crit"] if s <= 300 else C["timer_warn"] if s <= 900 else C["timer_ok"]
            self._timer_lbl.config(text=f"⏱  {h:02d}:{m:02d}:{sec:02d}", fg=color)
        if s > 0:
            self._timer_secs -= 1
            self._timer_id = self.root.after(1000, self._tick_timer)
        else:
            dlg_warn(self.root, "Waktu Habis!",
                     "Waktu ujian telah habis.\nJawaban Anda akan dikumpulkan.")
            self._submit_exam()

    def _submit_exam(self):
        self._save_essay()
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        total = NUM_PG + NUM_ESAI
        unanswered = sum(1 for i in range(total) if self.answers.get(i, "") in (None, ""))
        if unanswered > 0:
            if not dlg_confirm(self.root, "Soal Belum Selesai",
                               f"Masih ada {unanswered} soal yang belum dijawab.\n"
                               f"Yakin ingin mengumpulkan ujian?"):
                return
        score    = sum(1 for i in range(NUM_PG)
                       if self.answers.get(i) == self.questions[i]["j"])
        filepath = self._save_file(score)
        self._build_results(score, filepath)

    def _save_file(self, score):
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp  = os.path.join(HASIL_DIR, f"hasil_pancasila_{ts}.txt")
        lines = [
            "=" * 60,
            "  HASIL UJIAN PANCASILA KELAS 6 SD",
            "=" * 60,
            f"  Tanggal : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            "-" * 60,
            f"  SKOR PILIHAN GANDA : {score} / {NUM_PG}",
            f"  NILAI (PG)         : {score/NUM_PG*100:.1f}",
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
        lines.append("\n" + "=" * 60)
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return fp

    def _build_results(self, score, filepath):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())
        pct   = score / NUM_PG * 100
        color = "#16a34a" if pct >= 70 else "#ef4444"
        outer  = tk.Frame(self.root, bg=C["page"])
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=C["page"], highlightthickness=0)
        vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        f  = tk.Frame(canvas, bg=C["page"])
        cw = canvas.create_window((0, 0), window=f, anchor="nw")
        f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        tk.Label(f, text="UJIAN SELESAI",
                 bg=C["page"], fg="#16a34a",
                 font=("Segoe UI", 30, "bold")).pack(pady=(36, 4))
        tk.Label(f, text="Terima kasih telah mengerjakan ujian!",
                 bg=C["page"], fg=C["q_text"],
                 font=("Segoe UI", 14)).pack(pady=(0, 20))
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
                     font=("Segoe UI", 12)).grid(row=r, column=0, sticky="w", pady=6, padx=6)
            fg = color if "Nilai" in lbl else C["q_text"]
            wt = "bold" if "Nilai" in lbl else "normal"
            tk.Label(card, text=val, bg="#fff", fg=fg,
                     font=("Segoe UI", 12, wt)).grid(row=r, column=1, sticky="w", pady=6, padx=16)
        wrong = []
        for i in range(NUM_PG):
            q     = self.questions[i]
            siswa = self.answers.get(i, "-")
            kunci = q["j"]
            if siswa != kunci:
                opt_siswa = next((o for o in q["o"] if o.startswith(siswa + ".")),
                                 f"{siswa}. (tidak dijawab)")
                opt_benar = next((o for o in q["o"] if o.startswith(kunci + ".")), kunci)
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
                hdr = tk.Frame(wcard, bg="#dc2626")
                hdr.pack(fill="x")
                tk.Label(hdr, text=f"  Soal No. {no}  ",
                         bg="#dc2626", fg="#fff",
                         font=("Segoe UI", 10, "bold"), pady=6).pack(side="left")
                tk.Label(wcard, text=soal_text,
                         bg="#fff", fg=C["q_text"],
                         font=("Segoe UI", 12),
                         wraplength=880, justify="left",
                         anchor="w").pack(fill="x", padx=18, pady=(10, 6))
                tk.Label(wcard,
                         text=f"✗  Jawaban kamu   :  {opt_siswa}",
                         bg="#fff5f5", fg="#dc2626",
                         font=("Segoe UI", 11),
                         anchor="w", padx=18, pady=8).pack(fill="x", padx=18, pady=(0, 3))
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
