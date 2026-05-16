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
#  POOL SOAL PILIHAN GANDA  (60 soal – diambil 45 per sesi)
# ─────────────────────────────────────────────────────────────
PG_POOL = [

    # ── 1. TEKS EKSPLANASI ───────────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Gempa bumi adalah getaran yang terjadi di permukaan bumi akibat\n'
           'pergerakan lempeng tektonik yang saling berbenturan. Energi yang\n'
           'dihasilkan sangat besar sehingga dapat merusak bangunan di atasnya.\n'
           'Daerah yang paling sering mengalami gempa disebut zona ring of fire."\n\n'
           'Informasi yang terdapat dalam teks eksplanasi di atas adalah ...'),
     "o": ["Gempa bumi tidak berbahaya bagi bangunan di permukaan bumi",
           "Gempa bumi disebabkan oleh pergerakan lempeng tektonik yang saling berbenturan",
           "Daerah ring of fire tidak pernah mengalami gempa bumi",
           "Energi gempa bumi sangat kecil sehingga tidak terasa oleh manusia"],
     "j": 1},

    {"p": "Tujuan utama penulisan teks eksplanasi adalah ...",
     "o": ["Menghibur pembaca dengan cerita yang menarik dan penuh imajinasi",
           "Meyakinkan pembaca untuk setuju dengan pendapat penulis",
           "Menjelaskan proses terjadinya suatu fenomena alam atau sosial secara ilmiah",
           "Menceritakan pengalaman pribadi penulis secara kronologis"],
     "j": 2},

    # ── 2. KALIMAT EFEKTIF ───────────────────────────────────
    {"p": "Manakah kalimat yang efektif di bawah ini?",
     "o": ["Para hadirin-hadirin dimohon untuk duduk dengan tertib sekalian.",
           "Kami sangat amat bahagia sekali merayakan hari ulang tahun ini.",
           "Budi pergi ke sekolah setiap hari dengan berjalan kaki.",
           "Kami semua para guru mengucapkan terima kasih banyak sekali."],
     "j": 2},

    {"p": 'Kalimat "Banyak anak-anak bermain di lapangan itu" tidak efektif karena ...',
     "o": ["Tidak memiliki subjek yang jelas dalam kalimat",
           'Terdapat pemborosan kata: "banyak" dan "anak-anak" sama-sama menyatakan jamak',
           "Tidak ada kata kerja (predikat) dalam kalimat tersebut",
           "Kata 'lapangan' tidak tepat digunakan dalam konteks ini"],
     "j": 1},

    # ── 3. OBJEK HASIL PENGAMATAN ────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Tanaman padi tumbuh di sawah. Tingginya sekitar 80–100 cm.\n'
           'Daunnya berwarna hijau panjang dan ramping. Batangnya berbuku-buku\n'
           'dan berongga. Buahnya yang matang berwarna kuning keemasan."\n\n'
           'Objek yang diamati dalam teks laporan hasil pengamatan di atas adalah ...'),
     "o": ["Sawah dan lingkungan sekitarnya yang subur",
           "Tanaman padi",
           "Petani yang menanam padi di sawah",
           "Proses pemanenan padi saat musim panen"],
     "j": 1},

    {"p": "Teks laporan hasil pengamatan berbeda dari teks narasi karena ...",
     "o": ["Teks laporan menggunakan banyak kata kiasan dan gaya bahasa",
           "Teks laporan mendeskripsikan objek berdasarkan fakta hasil pengamatan secara sistematis",
           "Teks laporan selalu berisi cerita yang dialami oleh penulisnya sendiri",
           "Teks laporan hanya menceritakan peristiwa berdasarkan urutan waktu"],
     "j": 1},

    # ── 4. KOSAKATA BERMAKNA DENOTATIF ───────────────────────
    {"p": "Kosakata yang bermakna denotatif adalah kosakata yang memiliki makna ...",
     "o": ["Kiasan atau makna yang diubah dari makna sebenarnya",
           "Tersirat dan perlu ditafsirkan berdasarkan konteks kalimat",
           "Sebenarnya atau makna sesungguhnya sesuai kamus bahasa",
           "Ambigu dan memiliki banyak tafsiran yang berbeda-beda"],
     "j": 2},

    {"p": "Kalimat yang menggunakan kosakata baru bermakna denotatif adalah ...",
     "o": ["Gadis itu adalah bunga desa yang paling cantik di kampungnya.",
           "Ayah mencuci tangan dengan sabun sebelum makan siang.",
           "Perutnya sudah keroncongan minta diisi nasi goreng.",
           "Hatiku berbunga-bunga mendengar kabar gembira itu."],
     "j": 1},

    # ── 5. RANGKUMAN INFORMASI ───────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Banjir sering melanda Jakarta setiap musim hujan. Penyebab utamanya\n'
           'adalah saluran air tersumbat sampah dan alih fungsi lahan hijau menjadi\n'
           'pemukiman. Pemerintah berupaya mengatasinya dengan membuat waduk dan\n'
           'normalisasi sungai."\n\n'
           'Rangkuman yang paling tepat dari teks di atas adalah ...'),
     "o": ["Jakarta selalu banjir karena warganya membuang sampah sembarangan ke sungai",
           "Pemerintah membuat waduk untuk memenuhi kebutuhan air bersih warga Jakarta",
           "Banjir di Jakarta disebabkan saluran tersumbat dan alih fungsi lahan, dan pemerintah berupaya mengatasinya",
           "Curah hujan tinggi adalah satu-satunya penyebab banjir yang terjadi di Jakarta"],
     "j": 2},

    {"p": "Langkah yang tepat untuk membuat rangkuman teks bacaan adalah ...",
     "o": ["Menyalin semua kalimat dalam teks secara lengkap tanpa pengurangan",
           "Mencatat bagian yang menarik saja tanpa memperhatikan isi utama",
           "Mengambil kalimat pertama setiap paragraf dan menggabungkannya begitu saja",
           "Membaca teks, menentukan gagasan pokok setiap paragraf, lalu merangkainya menjadi paragraf singkat"],
     "j": 3},

    # ── 6. KALIMAT BERMAKNA DENOTATIF ────────────────────────
    {"p": "Di antara kalimat-kalimat berikut, manakah yang bermakna denotatif?",
     "o": ["Dia adalah tulang punggung keluarganya sejak ayahnya pergi.",
           "Rudi mendapat nilai merah di rapor semester ini.",
           "Ibu membeli dua kilogram daging sapi di pasar pagi ini.",
           "Anak itu menjadi buah bibir satu sekolah karena prestasinya."],
     "j": 2},

    {"p": 'Makna denotatif dari kata "kaki" terdapat dalam kalimat ...',
     "o": ["Ia adalah kaki tangan penjahat yang ditangkap oleh polisi.",
           "Di kaki bukit itu terdapat sebuah desa yang sangat indah.",
           "Kaki tangannya gemetar saat mendengar kabar buruk tersebut.",
           "Budi berlari menggunakan kakinya yang kuat saat olahraga pagi."],
     "j": 3},

    # ── 7. KATA BERMAKNA KONOTATIF ───────────────────────────
    {"p": '"Pemuda itu adalah bintang harapan bangsa."\nKata yang bermakna konotatif dalam kalimat tersebut adalah ...',
     "o": ["Pemuda",
           "Harapan",
           "Bangsa",
           "Bintang"],
     "j": 3},

    {"p": "Manakah kalimat yang mengandung kata bermakna konotatif?",
     "o": ["Adik membeli tiga buah apel merah di warung dekat sekolah.",
           "Para pahlawan telah gugur dalam mempertahankan kemerdekaan bangsa.",
           "Dokter memeriksa pasien yang datang ke puskesmas itu.",
           "Petani memanen padi di sawah ketika musim kemarau tiba."],
     "j": 1},

    # ── 8. TEKS IMAJINASI / FIKSI ────────────────────────────
    {"p": "Teks berikut yang termasuk teks imajinasi (fiksi) adalah ...",
     "o": ["Gunung Merapi meletus pada tahun 2010 dan menelan banyak korban jiwa.",
           "Di sebuah negeri antah berantah, hiduplah seorang putri baik hati bernama Ayu.",
           "Laporan cuaca hari ini menyebutkan suhu Jakarta mencapai 32 derajat Celsius.",
           "Presiden Indonesia pertama adalah Ir. Soekarno yang lahir tahun 1901."],
     "j": 1},

    {"p": "Ciri khas teks fiksi yang membedakannya dari teks nonfiksi adalah ...",
     "o": ["Menggunakan data dan fakta yang dapat diverifikasi kebenarannya",
           "Ditulis berdasarkan hasil penelitian ilmiah yang dapat diuji",
           "Berisi cerita yang bersumber dari imajinasi pengarang, bukan kejadian nyata",
           "Selalu menggunakan bahasa formal dan kaku sesuai aturan EYD"],
     "j": 2},

    # ── 9. GAGASAN POKOK TEKS LAPORAN ────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Lebah madu adalah serangga yang hidup berkoloni. Seekor koloni terdiri\n'
           'atas ratu lebah, lebah pekerja, dan lebah jantan. Lebah pekerja bertugas\n'
           'mencari nektar bunga untuk diolah menjadi madu sebagai cadangan makanan."\n\n'
           'Gagasan pokok teks laporan di atas adalah ...'),
     "o": ["Lebah pekerja bertugas mencari nektar dari bunga-bunga di sekitar sarang",
           "Madu digunakan sebagai cadangan makanan koloni lebah",
           "Lebah madu adalah serangga yang hidup berkoloni",
           "Ratu lebah memimpin seluruh anggota koloni lebah madu"],
     "j": 2},

    {"p": "Gagasan pokok (ide pokok) suatu paragraf biasanya terdapat pada ...",
     "o": ["Setiap kalimat dalam paragraf secara merata dan sama rata",
           "Kalimat yang paling panjang di antara kalimat-kalimat dalam paragraf",
           "Kalimat utama yang dapat berada di awal, akhir, atau awal dan akhir paragraf",
           "Kalimat terakhir setiap paragraf tanpa pengecualian"],
     "j": 2},

    # ── 10. MAKNA KATA DALAM KARYA SASTRA ───────────────────
    {"p": ('Dalam cerpen, seorang tokoh digambarkan "seperti ksatria tanpa\n'
           'senjata di medan perang." Makna ungkapan tersebut adalah ...'),
     "o": ["Tokoh tersebut adalah seorang prajurit militer yang gagah berani",
           "Tokoh berani namun tidak memiliki kemampuan yang cukup untuk menghadapi masalah",
           "Tokoh adalah seorang pemanah terampil yang kehilangan busurnya",
           "Tokoh tersebut seorang pengecut yang tidak mau berjuang sama sekali"],
     "j": 1},

    {"p": 'Kata "layu" dalam kalimat sastra "Senyumnya telah layu sejak kepergian ibunya" bermakna ...',
     "o": ["Tanaman yang kekurangan air dan mulai menguning daunnya",
           "Tidak semangat, sedih, dan kehilangan keceriaan dalam hidup",
           "Sakit keras sehingga harus berbaring di ranjang terus-menerus",
           "Tidak mau makan karena dilanda kesedihan yang sangat mendalam"],
     "j": 1},

    # ── 11. CIRI TEKS FIKSI ATAU NONFIKSI ───────────────────
    {"p": "Manakah yang merupakan ciri-ciri teks nonfiksi?",
     "o": ["Ditulis berdasarkan imajinasi pengarang dan bersifat menghibur",
           "Mengandung tokoh-tokoh yang sepenuhnya dibuat-buat oleh pengarang",
           "Berdasarkan fakta, data nyata, dan dapat dibuktikan kebenarannya",
           "Memiliki alur cerita yang penuh konflik dan ketegangan dramatik"],
     "j": 2},

    {"p": ('Bacaan: "Buku Laskar Pelangi karya Andrea Hirata menceritakan\n'
           'perjuangan anak-anak di Pulau Belitung. Tokoh seperti Ikal dan Lintang\n'
           'merupakan rekaan pengarang meski terinspirasi dari kehidupan nyata."\n\n'
           'Berdasarkan ciri-cirinya, karya yang dijelaskan teks di atas adalah ...'),
     "o": ["Nonfiksi ilmiah karena berisi fakta tentang Pulau Belitung",
           "Fiksi karena tokoh-tokohnya merupakan rekaan pengarang",
           "Teks laporan karena mendeskripsikan keadaan di Pulau Belitung",
           "Nonfiksi karena terinspirasi penuh dari kehidupan nyata"],
     "j": 1},

    # ── 12. UNSUR INTRINSIK KARYA SASTRA ────────────────────
    {"p": ('Bacalah kutipan berikut!\n'
           '"Malam itu hujan deras mengguyur kota. Di sebuah gubuk reot di pinggir\n'
           'sungai, Sinta duduk memeluk lututnya. Ia teringat ayahnya yang belum\n'
           'pulang. Air matanya menetes, namun ia tetap bersabar menanti."\n\n'
           'Latar tempat yang terdapat dalam kutipan cerita di atas adalah ...'),
     "o": ["Kota yang sedang diguyur hujan deras",
           "Sungai yang meluap karena hujan deras",
           "Gubuk reot di pinggir sungai",
           "Rumah Sinta yang terletak di tengah kota"],
     "j": 2},

    # SOAL SULIT (1 dari 6)
    {"p": ('Bacalah kutipan cerita berikut!\n'
           '"Pak Hasan selalu berbagi nasi bungkus untuk pengemis setiap Jumat.\n'
           'Meski gajinya pas-pasan, ia tidak pernah absen. Tetangganya berkata,\n'
           '"Buat apa susah-susah berbagi, toh mereka tidak berterima kasih?"\n'
           'Pak Hasan hanya tersenyum, "Kebaikan tidak perlu dibalas, Pak."\n\n'
           'Watak tokoh Pak Hasan yang paling tepat berdasarkan kutipan di atas adalah ...'),
     "o": ["Sombong dan suka pamer kepada tetangga sekitar rumahnya",
           "Kikir karena bergaji kecil namun tetap mengeluarkan uangnya",
           "Dermawan, ikhlas, dan tidak mengharapkan imbalan dari kebaikannya",
           "Sederhana namun kurang peduli terhadap kondisi lingkungannya"],
     "j": 2},

    # ── 13. PESAN MORAL CERPEN ───────────────────────────────
    {"p": ('Bacalah cerpen berikut!\n'
           '"Rara selalu mencontek saat ujian karena malas belajar. Suatu hari,\n'
           'ia tertangkap guru dan mendapat nilai nol. Rara sangat malu di depan\n'
           'teman-temannya. Sejak itu, ia berjanji tidak akan mencontek lagi\n'
           'dan mulai rajin belajar setiap malam."\n\n'
           'Pesan moral yang terkandung dalam cerpen di atas adalah ...'),
     "o": ["Janganlah malu ketika melakukan kesalahan di depan teman",
           "Mencontek adalah cara pintar untuk mendapat nilai bagus",
           "Kejujuran dan kerja keras dalam belajar adalah kunci keberhasilan",
           "Guru seharusnya tidak menghukum siswa yang mencontek di kelas"],
     "j": 2},

    # SOAL SULIT (2 dari 6)
    {"p": ('Bacalah cerpen berikut!\n'
           '"Pak Budi dikenal sebagai petani gigih. Meski lahannya kecil dan sering\n'
           'dicemooh tetangga, ia tetap diam dan tekun merawat tanamannya. Saat\n'
           'panen tiba, ladang Pak Budi menghasilkan dua kali lipat dibanding petani\n'
           'lain. Tetangga yang pernah mencemooh kini malah meminta ilmunya."\n\n'
           'Pesan moral yang paling tepat dari cerpen tersebut adalah ...'),
     "o": ["Kita harus membalas ejekan orang lain dengan memamerkan kesuksesan",
           "Lahan yang besar adalah syarat utama menjadi petani yang berhasil",
           "Kerja keras, ketekunan, dan tidak mudah terprovokasi omongan orang akan membuahkan hasil",
           "Sebaiknya kita meminta maaf kepada orang yang pernah kita ejek"],
     "j": 2},

    # ── 14. ANTONIM DAN SINONIM ─────────────────────────────
    {"p": 'Sinonim kata "bijaksana" adalah ...',
     "o": ["Ceroboh",
           "Gegabah",
           "Arif",
           "Angkuh"],
     "j": 2},

    {"p": 'Antonim kata "hemat" dalam kalimat "Ayah adalah orang yang hemat dalam mengelola keuangan" adalah ...',
     "o": ["Cermat",
           "Boros",
           "Teliti",
           "Rajin"],
     "j": 1},

    # ── 15. FAKTA DAN OPINI ──────────────────────────────────
    {"p": "Manakah kalimat yang merupakan fakta?",
     "o": ["Menurutku, olahraga renang adalah olahraga yang paling menyenangkan.",
           "Sebaiknya pelajar Indonesia lebih giat membaca buku di waktu luang.",
           "Indonesia merdeka pada tanggal 17 Agustus 1945.",
           "Sepertinya cuaca hari ini akan hujan deras di sore hari."],
     "j": 2},

    {"p": "Manakah kalimat yang merupakan opini?",
     "o": ["Gunung Everest adalah gunung tertinggi di dunia dengan ketinggian 8.849 meter.",
           "Samudra Pasifik adalah samudra terluas di permukaan bumi.",
           "Menurut saya, pendidikan karakter lebih penting daripada pendidikan akademis.",
           "Air mendidih pada suhu 100 derajat Celsius pada tekanan udara normal."],
     "j": 2},

    # ── 16. TIPE STRUKTUR TEKS ───────────────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Suatu pagi, Budi terbangun terlambat. Ia bergegas mandi, kemudian\n'
           'sarapan dalam tergesa-gesa. Lalu ia berlari ke halte bus agar tidak\n'
           'terlambat sampai di sekolah."\n\n'
           'Teks tersebut termasuk tipe teks ...'),
     "o": ["Eksposisi",
           "Argumentasi",
           "Deskripsi",
           "Naratif"],
     "j": 3},

    {"p": "Teks yang berisi pendapat dan alasan-alasan untuk meyakinkan pembaca disebut teks ...",
     "o": ["Naratif",
           "Deskripsi",
           "Eksposisi",
           "Argumentasi"],
     "j": 3},

    # ── 17. IDE POKOK DAN IDE PENDUKUNG ─────────────────────
    {"p": ('Bacalah paragraf berikut!\n'
           '"Pohon mangrove sangat bermanfaat bagi lingkungan pesisir. Akarnya\n'
           'yang kuat mencegah erosi pantai. Daunnya yang lebat menjadi tempat\n'
           'hidup berbagai jenis burung. Selain itu, buahnya dapat diolah menjadi\n'
           'makanan oleh masyarakat sekitar."\n\n'
           'Ide pokok paragraf tersebut adalah ...'),
     "o": ["Akar pohon mangrove yang kuat mencegah abrasi pantai",
           "Daun pohon mangrove menjadi tempat hidup berbagai jenis burung",
           "Pohon mangrove sangat bermanfaat bagi lingkungan pesisir",
           "Buah mangrove dapat diolah menjadi berbagai jenis makanan"],
     "j": 2},

    {"p": ('Berdasarkan paragraf tentang mangrove di atas, kalimat\n'
           '"Akarnya yang kuat mencegah erosi pantai" berfungsi sebagai ...'),
     "o": ["Ide pokok yang menjadi inti dari paragraf",
           "Ide pendukung yang menjelaskan manfaat pohon mangrove",
           "Kesimpulan dari seluruh isi paragraf tersebut",
           "Kalimat penghubung antara dua paragraf berbeda"],
     "j": 1},

    # ── 18. KALIMAT LANGSUNG DAN TIDAK LANGSUNG ─────────────
    {"p": "Manakah yang merupakan kalimat langsung?",
     "o": ["Guru bertanya apakah murid-murid sudah mengerjakan PR mereka.",
           "Ibu menyuruh adik untuk segera mandi dan siap-siap ke sekolah.",
           '"Apakah kalian sudah mengerjakan PR?" tanya Pak Guru kepada murid-muridnya.',
           "Dokter mengatakan bahwa pasien itu harus beristirahat selama seminggu."],
     "j": 2},

    {"p": 'Kalimat langsung "Rini berkata, \'Aku akan datang ke pesta ulang tahunmu besok.\'" jika diubah menjadi kalimat tidak langsung menjadi ...',
     "o": ["Rini berkata bahwa aku akan datang ke pesta ulang tahunmu besok.",
           "Rini berkata bahwa ia akan datang ke pesta ulang tahun itu besok.",
           "Rini berkata, \"Dia akan datang ke pesta ulang tahunmu besok.\"",
           "Rini bilang kalau aku mau datang ke pesta ulang tahunnya besok."],
     "j": 1},

    # ── 19. KOSAKATA BARU MEMBENTUK TEKS ────────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Kegiatan mendaur ulang sampah plastik sangat ... bagi lingkungan.\n'
           'Dengan mendaur ulang, kita mengurangi ... sampah yang menumpuk\n'
           'di tempat pembuangan akhir."\n\n'
           'Kosakata yang tepat untuk melengkapi teks tersebut secara berurutan adalah ...'),
     "o": ["berbahaya — kelebihan",
           "merugikan — jumlah",
           "bermanfaat — volume",
           "berguna — permasalahan"],
     "j": 2},

    {"p": 'Kosakata yang tepat untuk melengkapi kalimat "Pemerintah daerah sedang ... pembangunan jalan baru yang menghubungkan dua kecamatan" adalah ...',
     "o": ["menghentikan",
           "merencanakan",
           "menolak",
           "melupakan"],
     "j": 1},

    # ── 20. PENDAPAT TERHADAP TEKS NARATIF ──────────────────
    {"p": ('Bacalah teks berikut!\n'
           '"Edi adalah anak yang nakal. Setiap hari ia mengganggu teman-temannya.\n'
           'Gurunya sudah berkali-kali menasihati, namun Edi tidak mengubah sikapnya.\n'
           'Akibatnya, Edi tidak memiliki teman dan selalu merasa kesepian."\n\n'
           'Pendapat yang tepat terhadap teks naratif di atas adalah ...'),
     "o": ["Edi adalah anak yang baik hati dan suka menolong teman-temannya",
           "Sikap nakal Edi perlu diubah karena membuat dirinya sendiri menderita dan tidak memiliki teman",
           "Teman-teman Edi yang salah karena tidak mau bermain dengannya",
           "Guru harus bersabar meskipun Edi terus mengulangi kenakalan yang sama"],
     "j": 1},

    {"p": "Memberikan pendapat terhadap teks naratif berarti ...",
     "o": ["Menyalin kembali isi teks dengan kata-kata sendiri secara lengkap",
           "Mengubah alur cerita sesuai keinginan pembaca",
           "Menyampaikan penilaian atau tanggapan terhadap isi teks berdasarkan alasan yang logis",
           "Menghafal semua dialog tokoh yang ada dalam teks tersebut"],
     "j": 2},

    # ── 21. TUJUAN POSTER LINGKUNGAN ─────────────────────────
    {"p": 'Poster bertuliskan "Jaga Kebersihan Sungai, Buang Sampah pada Tempatnya!" bertujuan untuk ...',
     "o": ["Memberitahu warga tentang jadwal pengangkutan sampah di daerahnya",
           "Mengajak masyarakat menjaga kebersihan sungai dengan tidak membuang sampah sembarangan",
           "Mempromosikan produk tempat sampah yang dijual di pasaran",
           "Melaporkan kondisi sungai yang sudah tercemar kepada pemerintah"],
     "j": 1},

    {"p": "Pernyataan yang BENAR tentang poster lingkungan adalah ...",
     "o": ["Poster lingkungan hanya boleh dipasang di kantor pemerintah",
           "Poster lingkungan bertujuan untuk menjual produk-produk ramah lingkungan",
           "Poster lingkungan menggunakan gambar dan kalimat singkat untuk mengajak masyarakat menjaga lingkungan",
           "Poster lingkungan harus ditulis dengan bahasa ilmiah yang formal dan sangat panjang"],
     "j": 2},

    # ── 22. ARTI KATA BERCETAK TEBAL (TEKS EKSPLANASI) ──────
    {"p": ('Bacalah teks berikut!\n'
           '"Proses evaporasi terjadi ketika air di permukaan bumi menguap\n'
           'akibat panas matahari. Air yang menguap berubah menjadi uap air\n'
           'yang naik ke atmosfer dan membentuk awan."\n\n'
           'Arti kata evaporasi pada teks eksplanasi di atas adalah ...'),
     "o": ["Proses turunnya air hujan dari awan ke permukaan bumi",
           "Proses penguapan air dari permukaan bumi akibat panas matahari",
           "Proses pembentukan awan dari uap air yang ada di udara",
           "Proses mengalirnya air sungai dari hulu menuju lautan"],
     "j": 1},

    {"p": ('Bacalah teks berikut!\n'
           '"Banjir sering terjadi akibat deforestasi yang tidak terkendali.\n'
           'Hutan yang gundul tidak mampu menyerap air hujan sehingga air\n'
           'langsung mengalir ke dataran rendah dan menyebabkan banjir."\n\n'
           'Makna kata deforestasi pada teks tersebut adalah ...'),
     "o": ["Penanaman pohon secara besar-besaran di daerah yang gundul",
           "Pembangunan perumahan di area hutan yang masih lebat",
           "Penggundulan atau penebangan hutan secara besar-besaran",
           "Program penghijauan kembali hutan yang telah rusak"],
     "j": 2},

    # ── 23. UNSUR-UNSUR PUISI ────────────────────────────────
    {"p": ('Bacalah puisi berikut!\n\n'
           '    Pagi harum semerbak bunga\n'
           '    Embun menetes di dedaunan\n'
           '    Mentari menyinari alam raya\n'
           '    Ciptaan Tuhan yang menawan\n\n'
           'Rima (sajak) yang digunakan dalam puisi di atas adalah ...'),
     "o": ["a-a-a-a",
           "a-b-c-d",
           "a-b-a-b",
           "a-a-b-b"],
     "j": 2},

    {"p": 'Unsur yang menunjukkan "pesan yang ingin disampaikan penyair" dalam sebuah puisi disebut ...',
     "o": ["Rima",
           "Diksi",
           "Amanat",
           "Larik"],
     "j": 2},

    # ── 24. MAJAS METAFORA ───────────────────────────────────
    {"p": '"Waktu adalah uang yang tidak bisa dikembalikan." Kalimat tersebut adalah contoh majas ...',
     "o": ["Simile",
           "Personifikasi",
           "Hiperbola",
           "Metafora"],
     "j": 3},

    {"p": 'Arti dari kalimat bermajas metafora "Dia adalah pagar makan tanaman dalam keluarga itu" adalah ...',
     "o": ["Dia adalah orang yang pandai bercocok tanam untuk keluarganya",
           "Dia justru merugikan atau mengkhianati orang-orang yang seharusnya dilindunginya",
           "Dia adalah pelindung setia yang menjaga semua anggota keluarganya",
           "Dia adalah orang yang suka berkebun dan menanam pagar di sekitar rumah"],
     "j": 1},

    # ── 25. ISTILAH DALAM WAWANCARA ──────────────────────────
    {"p": "Dalam kegiatan wawancara, orang yang mengajukan pertanyaan disebut ...",
     "o": ["Narasumber",
           "Moderator",
           "Pewawancara",
           "Reporter utama"],
     "j": 2},

    {"p": "Pernyataan yang BENAR tentang narasumber dalam kegiatan wawancara adalah ...",
     "o": ["Narasumber adalah orang yang mengajukan pertanyaan kepada pewawancara",
           "Narasumber adalah orang yang memiliki keahlian atau pengetahuan tentang topik yang diwawancara",
           "Narasumber harus selalu menjawab setiap pertanyaan tanpa boleh menolak",
           "Narasumber dan pewawancara selalu merupakan orang yang sama"],
     "j": 1},

    # ── 26. JUDUL CERITA FIKSI ───────────────────────────────
    {"p": "Manakah yang termasuk judul cerita fiksi di bawah ini?",
     "o": ["Laporan Tahunan Kependudukan Kota Jakarta 2024",
           "Cara Mudah Menanam Sayuran Organik di Rumah",
           "Si Kancil dan Buaya",
           "Sejarah Kemerdekaan Indonesia 17 Agustus 1945"],
     "j": 2},

    # SOAL SULIT (3 dari 6)
    {"p": ('Di antara judul-judul berikut, manakah yang BUKAN merupakan cerita fiksi?\n'
           '(Pilih berdasarkan pengetahuanmu tentang jenis karya sastra Indonesia)'),
     "o": ["Petualangan Sherina (film anak-anak)",
           "Harimau! Harimau! karya Mochtar Lubis",
           "Bumi Manusia karya Pramoedya Ananta Toer",
           "Catatan Seorang Demonstran karya Soe Hok Gie"],
     "j": 3},

    # ── 27. MEMPERBAIKI KALIMAT EFEKTIF ──────────────────────
    {"p": 'Perbaikan yang tepat untuk kalimat "Kami semua para siswa-siswa hadir dalam upacara bendera itu" adalah ...',
     "o": ["Kami semua para siswa hadir dalam upacara bendera itu.",
           "Kami semua siswa hadir dalam upacara bendera itu.",
           "Para siswa hadir dalam upacara bendera itu.",
           "Kami para siswa-siswa hadir dalam upacara bendera itu."],
     "j": 2},

    # SOAL SULIT (4 dari 6)
    {"p": 'Kalimat "Dengan membaca buku ilmu pengetahuan kita akan bertambah" mengandung kelemahan karena ...',
     "o": ["Tidak memiliki subjek yang jelas dalam kalimat",
           "Tidak memiliki predikat sama sekali",
           'Ambigu: "ilmu pengetahuan" bisa dipahami sebagai keterangan "buku" atau subjek klausa kedua',
           "Menggunakan kata yang tidak baku menurut KBBI"],
     "j": 2},

    # ── 28. FUNGSI IMBUHAN ME- ───────────────────────────────
    {"p": 'Kata "menulis" mendapat imbuhan me- yang berfungsi sebagai ...',
     "o": ["Kata sifat yang menjelaskan keadaan subjek kalimat",
           "Kata kerja aktif yang menunjukkan subjek melakukan tindakan",
           "Kata benda yang menunjukkan hasil dari suatu pekerjaan",
           "Kata keterangan yang menjelaskan cara kerja predikat"],
     "j": 1},

    {"p": 'Imbuhan me- pada kata "mempelajari" dalam kalimat "Siswa mempelajari materi Bahasa Indonesia" berfungsi untuk ...',
     "o": ["Membentuk kata sifat dari kata dasar 'pelajar'",
           "Membentuk kata benda dari kata dasar 'belajar'",
           "Membentuk kata kerja aktif yang menunjukkan kegiatan yang dilakukan subjek",
           "Membentuk kata keterangan dari kata dasar 'ajar'"],
     "j": 2},

    # ── 29. UNSUR EKSTRINSIK TEKS SASTRA ────────────────────
    {"p": "Unsur ekstrinsik karya sastra adalah unsur yang berasal dari ...",
     "o": ["Dalam karya sastra itu sendiri, seperti tema dan alur cerita",
           "Luar karya sastra, seperti latar belakang pengarang dan kondisi sosial saat karya dibuat",
           "Struktur bahasa yang digunakan dalam karya sastra tersebut",
           "Dialog antar tokoh yang terdapat dalam karya sastra"],
     "j": 1},

    {"p": "Manakah yang termasuk unsur ekstrinsik dalam sebuah novel?",
     "o": ["Tokoh protagonis dan antagonis dalam cerita novel",
           "Latar tempat dan waktu terjadinya peristiwa dalam novel",
           "Latar belakang pendidikan dan kehidupan pengarangnya",
           "Alur cerita dari awal hingga akhir novel tersebut"],
     "j": 2},

    # ── 30. JENIS MAJAS ──────────────────────────────────────
    {"p": '"Suaranya menggelegar membelah langit hingga bumi bergetar." Kalimat tersebut menggunakan majas ...',
     "o": ["Metafora",
           "Personifikasi",
           "Simile",
           "Hiperbola"],
     "j": 3},

    # SOAL SULIT (5 dari 6)
    {"p": '"Saya punya sebuah gubuk kecil untuk berteduh," kata pemilik rumah mewah itu dengan rendah hati.\nKalimat tersebut menggunakan majas ...',
     "o": ["Hiperbola",
           "Litotes",
           "Metafora",
           "Eufemisme"],
     "j": 1},

    # ── SOAL TAMBAHAN (variasi materi) ───────────────────────
    {"p": 'Kalimat "Angin berbisik lembut di telingaku" menggunakan majas personifikasi karena ...',
     "o": ["Membandingkan angin dengan manusia menggunakan kata 'seperti'",
           "Melebih-lebihkan kekuatan dan sifat angin",
           "Memberikan sifat atau perilaku manusia (berbisik) kepada benda mati (angin)",
           "Menggunakan angin sebagai lambang kelemahan dan kelembutan"],
     "j": 2},

    # SOAL SULIT (6 dari 6)
    {"p": ('Bacalah dua kalimat berikut!\n'
           '(1) Dedi adalah murid yang cerdas sehingga selalu juara kelas.\n'
           '(2) Sepertinya Dedi adalah murid yang paling pintar di sekolah ini.\n\n'
           'Pernyataan yang TEPAT tentang kedua kalimat di atas adalah ...'),
     "o": ["Kalimat (1) adalah opini karena menggunakan kata 'sehingga'",
           "Kalimat (2) adalah fakta karena menyebutkan nama seseorang",
           "Kalimat (1) adalah fakta dan kalimat (2) adalah opini",
           "Kedua kalimat tersebut sama-sama merupakan fakta yang dapat dibuktikan"],
     "j": 2},

    {"p": "Kalimat yang menggunakan kalimat tidak langsung adalah ...",
     "o": ['"Tolong tutup jendelanya!" seru Ibu kepada adik.',
           "Ayah berkata bahwa ia akan pulang lebih awal hari ini.",
           '"Aku sangat senang bertemu denganmu," kata Sari sambil tersenyum.',
           '"Kapan ujian semester ini dimulai?" tanya Budi kepada gurunya.'],
     "j": 1},

    {"p": "Teks eksplanasi biasanya memiliki struktur yang terdiri atas ...",
     "o": ["Orientasi – Komplikasi – Resolusi",
           "Pernyataan umum – Deretan penjelas – Interpretasi",
           "Pembuka – Isi – Penutup",
           "Tesis – Argumentasi – Penegasan ulang"],
     "j": 1},

    {"p": ('Bacalah teks berikut!\n'
           '"Terumbu karang adalah ekosistem laut yang kaya. Di dalamnya hidup\n'
           'ribuan jenis ikan, moluska, dan tumbuhan laut. Terumbu karang juga\n'
           'berfungsi sebagai pelindung pantai dari abrasi ombak laut."\n\n'
           'Jenis teks di atas termasuk teks ...'),
     "o": ["Naratif karena menceritakan peristiwa berurutan",
           "Eksposisi karena menjelaskan informasi tentang terumbu karang",
           "Argumentasi karena berisi pendapat tentang terumbu karang",
           "Deskripsi karena menggambarkan keadaan pantai secara rinci"],
     "j": 1},

    {"p": 'Dalam teks laporan hasil pengamatan, kalimat "Pohon cemara memiliki daun berbentuk jarum yang berwarna hijau gelap" termasuk bagian ...',
     "o": ["Simpulan dari hasil pengamatan",
           "Deskripsi bagian (penjelasan ciri-ciri objek)",
           "Pernyataan umum atau definisi objek",
           "Tujuan dilakukannya pengamatan"],
     "j": 1},

    {"p": 'Sinonim kata "antusias" dalam kalimat "Siswa sangat antusias mengikuti kegiatan pramuka" adalah ...',
     "o": ["Malas",
           "Bersemangat",
           "Terpaksa",
           "Enggan"],
     "j": 1},

    {"p": 'Antonim kata "transparan" dalam konteks pemerintahan yang baik adalah ...',
     "o": ["Terbuka",
           "Jelas",
           "Tertutup",
           "Bersih"],
     "j": 2},

]

# ─────────────────────────────────────────────────────────────
#  POOL SOAL ESAI  (10 soal – diambil 5 per sesi)
# ─────────────────────────────────────────────────────────────
ESAI_POOL = [
    {"p": ('Bacalah teks eksplanasi singkat berikut!\n\n'
           '"Hujan terjadi melalui beberapa tahap. Pertama, air di laut, sungai, dan '
           'danau menguap akibat panas matahari (evaporasi). Uap air naik ke atmosfer '
           'dan mendingin, lalu membentuk awan (kondensasi). Ketika awan sudah '
           'penuh, terjadilah hujan (presipitasi)."\n\n'
           'a. Sebutkan tiga informasi penting yang terdapat dalam teks eksplanasi di atas!\n'
           'b. Jelaskan dengan bahasamu sendiri apa yang dimaksud dengan evaporasi!')},

    {"p": ('Perbaikilah kalimat-kalimat berikut menjadi kalimat efektif dan jelaskan alasannya!\n\n'
           'a. "Para hadirin-hadirin sekalian dimohon untuk berdiri."\n'
           'b. "Banyak anak-anak yang bermain bola di lapangan itu."\n'
           'c. "Saya sangat amat senang sekali mendapat hadiah itu."\n\n'
           'Tuliskan perbaikannya dan jelaskan kesalahan pada setiap kalimat!')},

    {"p": ('Bacalah kutipan cerpen berikut!\n\n'
           '"Matahari belum sepenuhnya terbit ketika Lani sudah berada di kebun. '
           'Dengan tangan mungilnya ia menyiram tanaman cabai satu per satu. '
           '"Kalau rajin merawat, pasti hasilnya bagus," gumamnya sambil tersenyum. '
           'Lani adalah anak bungsu dari keluarga petani yang sederhana di lereng '
           'Gunung Merbabu. Meski hidup pas-pasan, semangatnya tak pernah padam."\n\n'
           'Tentukan unsur intrinsik berikut dari kutipan cerpen di atas:\n'
           'a. Tokoh dan watak tokoh\n'
           'b. Latar (tempat, waktu, suasana)\n'
           'c. Pesan moral yang terkandung dalam kutipan tersebut')},

    {"p": ('Bacalah paragraf berikut dan jawablah pertanyaan-pertanyaan di bawah ini!\n\n'
           '"Membaca buku sangat penting bagi perkembangan anak. Dengan membaca, '
           'anak dapat memperluas wawasan dan pengetahuannya. Selain itu, membaca '
           'melatih kemampuan berpikir kritis. Buku juga merupakan jendela dunia '
           'yang dapat membawa pembaca menjelajahi berbagai tempat tanpa harus pergi."\n\n'
           'a. Tentukan ide pokok paragraf tersebut!\n'
           'b. Tuliskan dua kalimat yang berfungsi sebagai ide pendukung!\n'
           'c. Termasuk tipe teks apakah paragraf di atas? Jelaskan alasanmu!')},

    {"p": ('Perhatikan pernyataan-pernyataan berikut:\n\n'
           '1. Pulau Jawa adalah pulau terpadat di Indonesia.\n'
           '2. Menurut saya, belajar di pagi hari lebih efektif daripada malam hari.\n'
           '3. Presiden Soekarno lahir pada 6 Juni 1901 di Surabaya.\n'
           '4. Sepertinya tim sepak bola kita akan menang dalam pertandingan besok.\n'
           '5. Bahasa Indonesia ditetapkan sebagai bahasa nasional pada tahun 1945.\n\n'
           'a. Tentukan mana yang termasuk fakta dan mana yang opini!\n'
           'b. Jelaskan perbedaan antara fakta dan opini!')},

    {"p": ('Ubahlah kalimat langsung berikut menjadi kalimat tidak langsung!\n\n'
           'a. Bu Guru berkata, "Kalian harus belajar lebih giat untuk menghadapi ujian."\n'
           'b. Ayah berkata, "Aku akan membelikan sepeda baru untukmu jika nilaimu bagus."\n'
           'c. Kepala Sekolah mengumumkan, "Besok semua siswa wajib hadir tepat waktu."\n\n'
           'Tuliskan hasilnya dan perhatikan perubahan kata ganti!')},

    {"p": ('Bacalah puisi berikut dengan seksama!\n\n'
           '    Guruku\n'
           '    Kau bagai lilin yang menerangi\n'
           '    Dalam gelap kau selalu hadir\n'
           '    Ilmumu mengalir tiada henti\n'
           '    Jasamu takkan pernah terlupakan\n\n'
           'a. Majas apa yang digunakan pada baris pertama? Jelaskan!\n'
           'b. Apa tema puisi di atas?\n'
           'c. Apa amanat yang terkandung dalam puisi tersebut?\n'
           'd. Bagaimana pola rima puisi tersebut?')},

    {"p": ('a. Jelaskan apa yang dimaksud dengan narasumber dan pewawancara dalam kegiatan wawancara!\n'
           'b. Sebutkan tiga pertanyaan yang baik untuk diajukan saat mewawancarai seorang dokter '
           'tentang cara menjaga kesehatan!\n'
           'c. Tuliskan 5 judul cerita fiksi yang kamu ketahui (boleh cerita rakyat, novel, atau cerpen)!')},

    {"p": ('Bacalah teks berikut!\n\n'
           '"Pemerintah mengimbau masyarakat untuk menanam pohon di sekitar rumah. '
           'Pohon yang rimbun dapat menyejukkan udara dan menyerap polusi. '
           'Selain itu, akar pohon membantu menyerap air hujan sehingga mencegah banjir."\n\n'
           'a. Tentukan unsur ekstrinsik apa yang bisa mempengaruhi penulisan teks tersebut! '
           'Jelaskan!\n'
           'b. Temukan kata-kata berimbuhan me- dalam teks di atas dan jelaskan fungsi '
           'imbuhan me- pada setiap kata!')},

    {"p": ('Bacalah cerpen singkat berikut!\n\n'
           '"Hari itu Doni sedang berjalan pulang sekolah. Di tengah jalan, ia melihat '
           'dompet terjatuh dari saku seorang Bapak tua. Doni segera mengambil dompet itu '
           'dan berlari memanggil sang Bapak. Dengan wajah terkejut dan bersyukur, '
           'Bapak itu berterima kasih kepada Doni. Doni hanya tersenyum dan berkata, '
           '\'Ini kewajiban saya, Pak.\'".\n\n'
           'a. Tentukan unsur intrinsik: tokoh, watak tokoh, latar, dan tema!\n'
           'b. Simpulkan pesan moral cerpen tersebut!\n'
           'c. Tentukan jenis majas apa yang terdapat dalam cerpen (jika ada) dan jelaskan!')},
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

        tk.Label(tb, text="UJIAN BAHASA INDONESIA  •  KELAS 6 SD",
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
        pw = prog_frame.winfo_width() or 800
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
        pw = prog_frame.winfo_width() or 800
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
            real_idx = i if i < NUM_PG else i
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
        self.root.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())

        pct   = score / NUM_PG * 100
        color = "#16a34a" if pct >= 70 else "#ef4444"

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
                     font=("Segoe UI", 12)).grid(
                         row=r, column=0, sticky="w", pady=6, padx=6)
            fg = color if "Nilai" in lbl else C["q_text"]
            wt = "bold" if "Nilai" in lbl else "normal"
            tk.Label(card, text=val, bg="#fff", fg=fg,
                     font=("Segoe UI", 12, wt)).grid(
                         row=r, column=1, sticky="w", pady=6, padx=16)

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

                hdr = tk.Frame(wcard, bg="#dc2626")
                hdr.pack(fill="x")
                tk.Label(hdr, text=f"  Soal No. {no}  ",
                         bg="#dc2626", fg="#fff",
                         font=("Segoe UI", 10, "bold"),
                         pady=6).pack(side="left")

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

