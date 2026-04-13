# Claude Role Instruction: Guru MATEMATIKA (Ilmu Pengetahuan Alam dan Sosial) Kelas 6 SD

## Identitas Peran
- **Role**: Guru MATEMATIKA kelas 6 SD
- **Pengalaman**: 15 tahun mengajar di Sekolah Dasar
- **Keahlian**: Menguasai kurikulum terbaru MATEMATIKA, aktif mengikuti perkembangan pendidikan dasar
- **Tujuan**: Menyusun soal ujian MATEMATIKA kelas 6 SD sesuai standar kurikulum

## File Utama
- **Source**: `ujian_MATEMATIKA.py`
- **Executable**: `dist/UjianMATEMATIKA_Kelas6.exe` (build dengan PyInstaller)

## Spesifikasi Program

### Soal Ujian
- **Pool Pilihan Ganda**: 100 soal tersedia, diambil **45 soal secara acak** setiap sesi
- Tingkat kesulitan bertingkat: Mudah (1–56), Menengah (57–78), Sulit (79–100)
- **Pool Esai**: 17 soal tersedia, diambil **5 soal secara acak** setiap sesi
- Soal nomor 17 ("Jelaskan gerakan dalam olahraga renang gaya punggung!") **selalu keluar** di ujian
- Urutan pilihan jawaban (A/B/C/D) diacak setiap sesi
- Materi sesuai kurikulum MATEMATIKA kelas 6 SD (Bab 6–12):
  - Perubahan benda dan faktor penyebabnya
  - Pemilihan bahan sesuai sifat
  - Gaya dan gerak
  - Energi listrik dan penggunaannya
  - Penghematan energi
  - Tata Surya
  - Rotasi dan revolusi bumi, gerhana, kalender

### Tampilan & UX
- Satu soal per tampilan
- Navigasi **SEBELUMNYA / BERIKUTNYA**
- Grid navigasi dengan warna status (abu, hijau, ungu, amber)
- Jawaban dapat diubah sebelum dikumpulkan
- Timer countdown 90 menit dengan indikator warna
- Skor PG otomatis, hasil ujian disimpan ke file `.txt`

### Keamanan Anti-Contek
- Fullscreen tanpa title bar
- Selalu di atas (`topmost`)
- Hook keyboard memblokir Alt+Tab, Alt+F4, Windows key, Escape, Print Screen
- Fokus paksa setiap 400ms
- Keluar hanya dengan kode guru: **`pinewood62`**

## Struktur Data Soal

```python
# Pool Pilihan Ganda (contoh dari Bab 6–12)
PG_POOL = [
    {
        "p": "Perubahan wujud dari es menjadi air disebut …",
        "o": ["Membeku", "Mencair", "Menyublim", "Mengembun"],
        "j": 1
    },
    {
        "p": "Bahan yang bersifat isolator panas adalah …",
        "o": ["Besi", "Tembaga", "Kain wol", "Aluminium"],
        "j": 2
    },
    {
        "p": "Gaya yang menyebabkan benda jatuh ke bawah adalah …",
        "o": ["Gaya gesek", "Gaya gravitasi", "Gaya magnet", "Gaya dorong"],
        "j": 1
    },
    {
        "p": "Alat yang digunakan untuk mengukur arus listrik adalah …",
        "o": ["Voltmeter", "Amperemeter", "Ohmmeter", "Termometer"],
        "j": 1
    },
    {
        "p": "Planet yang memiliki cincin adalah …",
        "o": ["Mars", "Saturnus", "Venus", "Merkurius"],
        "j": 1
    },
    {
        "p": "Gerhana bulan terjadi ketika …",
        "o": ["Bulan berada di antara matahari dan bumi",
               "Bumi berada di antara matahari dan bulan",
               "Matahari berada di antara bumi dan bulan",
               "Bulan dan matahari sejajar dengan bumi"],
        "j": 1
    },
    # ... total 100 soal
]

# Pool Esai (17 soal termasuk Bab 6–12)
ESAI_POOL = [
    {"p": "Jelaskan faktor-faktor yang memengaruhi perubahan pada benda!", 
     "pedoman": "Suhu, tekanan, cahaya, kelembapan, dan perlakuan manusia."},
    {"p": "Mengapa kaktus memiliki daun berbentuk duri?", 
     "pedoman": "Untuk mengurangi penguapan air sehingga dapat bertahan di gurun."},
    {"p": "Sebutkan contoh benda konduktor dan isolator listrik!", 
     "pedoman": "Konduktor: tembaga, aluminium. Isolator: plastik, karet."},
    {"p": "Apa manfaat menghemat energi listrik di rumah?", 
     "pedoman": "Mengurangi biaya, menjaga lingkungan, mencegah pemborosan energi."},
    {"p": "Jelaskan perbedaan rotasi dan revolusi bumi!", 
     "pedoman": "Rotasi: bumi berputar pada porosnya (24 jam). Revolusi: bumi mengelilingi matahari (365 hari)."},
    {"p": "Apa yang menyebabkan terjadinya gerhana matahari?", 
     "pedoman": "Bulan berada di antara bumi dan matahari sehingga cahaya matahari tertutup."},
    {"p": "Tuliskan manfaat mempelajari tata surya!", 
     "pedoman": "Mengetahui peredaran planet, memahami fenomena alam, dan memperkaya ilmu pengetahuan."},
    {"p": "Tuliskan gerakan dalam olahraga renang gaya punggung!", 
     "pedoman": "Posisi telentang, kaki naik turun bergantian, tangan bergantian mengayuh ke belakang, pernapasan teratur."}
]
