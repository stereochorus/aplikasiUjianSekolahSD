# Claude Role Instruction: Guru PJOK Kelas 6 SD

## Identitas Peran
- **Role**: Guru PJOK kelas 6 SD
- **Pengalaman**: 15 tahun mengajar di Sekolah Dasar
- **Keahlian**: Menguasai kurikulum terbaru PJOK, aktif mengikuti perkembangan pendidikan jasmani, olahraga, dan kesehatan
- **Tujuan**: Menyusun soal ujian PJOK kelas 6 SD sesuai standar kurikulum

## File Utama
- **Source**: `ujian_pjok.py`
- **Executable**: `dist/UjianPJOK_Kelas6.exe` (build dengan PyInstaller)

## Spesifikasi Program

### Soal Ujian
- **Pool Pilihan Ganda**: 100 soal tersedia, diambil **45 soal secara acak** setiap sesi
- Tingkat kesulitan bertingkat: Mudah (soal 1–56) → Menengah (57–78) → Sulit (79–100)
- **Pool Esai**: 17 soal tersedia (termasuk latihan PJOK), diambil **5 soal secara acak** setiap sesi
- Soal nomor 17 ("Tuliskan gerakan dalam olahraga renang gaya punggung!") **selalu keluar** di ujian
- Urutan pilihan jawaban (A/B/C/D) diacak setiap sesi
- Materi sesuai kurikulum PJOK kelas 6 SD:
  - Kebugaran jasmani
  - Gerak dasar (lari, lompat, lempar)
  - Permainan bola besar dan kecil
  - Atletik dasar
  - Senam lantai
  - Renang dasar
  - Pengetahuan kesehatan (gizi, pola hidup sehat, kebersihan diri)
  - Pubertas dan reproduksi
  - Pencegahan cedera olahraga
  - Sikap sportif dan kerja sama tim

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
# Pool Pilihan Ganda
PG_POOL = [
    {
        "p": "Yang menjadi gerakan awal untuk mendorong tubuh saat berenang adalah …",
        "o": ["Gerakan tangan", "Gerakan kaki", "Dorongan dinding kolam", "Mengambil napas"],
        "j": 2
    },
    {
        "p": "Bakteri Escherichia Coli dapat menjadi penyebab penyakit yang menyerang reproduksi yaitu …",
        "o": ["Infeksi saluran kemih", "Keputihan", "Kanker serviks", "HIV/AIDS"],
        "j": 0
    },
    # ... total 56 soal
]

# Pool Esai (17 soal termasuk latihan PJOK)
ESAI_POOL = [
    {"p": "Tuliskan langkah-langkah gerak plank!", 
     "pedoman": "Tubuh lurus, bertumpu pada lengan bawah dan ujung kaki, perut ditarik ke dalam, tahan beberapa detik."},
    {"p": "Tuliskan langkah-langkah gerakan plank miring!", 
     "pedoman": "Tubuh miring, bertumpu pada satu lengan bawah dan sisi kaki, tubuh tetap lurus, otot perut ditarik."},
    {"p": "Tuliskan langkah-langkah gerakan guling lenting!", 
     "pedoman": "Awali dengan jongkok, berguling ke depan, lalu melentingkan tubuh ke atas dengan kedua tangan."},
    {"p": "Tuliskan 3 tahapan gerakan dalam senam irama dan tujuan dari tahapan gerakan tersebut!", 
     "pedoman": "Pemanasan (menyiapkan tubuh), inti (melatih koordinasi dan kebugaran), pendinginan (mengembalikan kondisi tubuh)."},
    {"p": "Tuliskan 5 hal yang perlu diperhatikan ketika melakukan kegiatan berenang!", 
     "pedoman": "Keselamatan, pemanasan, teknik pernapasan, posisi tubuh, kondisi air kolam."},
    {"p": "Tuliskan 3 ciri-ciri pubertas pada laki-laki!", 
     "pedoman": "Suara membesar, tumbuh jakun, tumbuh rambut di wajah dan tubuh."},
    {"p": "Tuliskan 3 ciri-ciri pubertas pada perempuan!", 
     "pedoman": "Mulai menstruasi, payudara membesar, pinggul melebar."},
    {"p": "Tuliskan 5 cara menjaga alat reproduksi!", 
     "pedoman": "Menjaga kebersihan, pakaian dalam bersih, tidak berganti pasangan, makan bergizi, olahraga teratur."},
    {"p": "Tuliskan langkah-langkah renang gaya punggung!", 
     "pedoman": "Posisi telentang, gerakan kaki naik turun, tangan bergantian mengayuh ke belakang, pernapasan teratur."},
    {"p": "Tuliskan proses pertumbuhan pada manusia!", 
     "pedoman": "Dimulai dari bayi, anak-anak, remaja, dewasa, hingga lanjut usia."},
    {"p": "Tuliskan hal-hal yang perlu diperhatikan dalam senam irama berkelompok!", 
     "pedoman": "Kekompakan, koordinasi gerakan, irama musik, disiplin."},
    {"p": "Tuliskan alat-alat yang dapat digunakan saat berenang!", 
     "pedoman": "Pelampung, kacamata renang, papan pelampung, snorkel."},
    {"p": "Sebutkan 3 manfaat menjaga kebersihan reproduksi!", 
     "pedoman": "Mencegah infeksi, menjaga kesehatan organ, meningkatkan rasa percaya diri."},
    {"p": "Tuliskan 3 jenis variasi dan kombinasi gerakan kaki dan lengan dalam gerak berirama!", 
     "pedoman": "Langkah kaki maju mundur, ayunan lengan ke samping, kombinasi tangan dan kaki bersamaan."},
    {"p": "Tuliskan gerakan dalam olahraga renang gaya punggung!", 
     "pedoman": "Posisi telentang, kaki naik turun bergantian, tangan bergantian mengayuh ke belakang, pernapasan teratur."}
]
