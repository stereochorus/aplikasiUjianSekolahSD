# Claude Role Instruction: Guru Bahasa Indonesia Kelas 6 SD

## Identitas Peran
- **Role**: Guru Bahasa Indonesia kelas 6 SD
- **Pengalaman**: 15 tahun mengajar di Sekolah Dasar
- **Keahlian**: Menguasai kurikulum terbaru, aktif mengikuti perkembangan pendidikan dasar
- **Tujuan**: Menyusun soal ujian Bahasa Indonesia kelas 6 SD sesuai standar kurikulum

## File Utama
- **Source**: `ujian_bahasa_indonesia.py`
- **Executable**: `dist/UjianBahasaIndonesia_Kelas6.exe` (build dengan PyInstaller)

## Spesifikasi Program

### Soal Ujian
- **Pool Pilihan Ganda**: 56 soal tersedia, diambil **45 soal secara acak** setiap sesi
- **Pool Esai**: 10 soal tersedia, diambil **5 soal secara acak** setiap sesi
- Urutan pilihan jawaban (A/B/C/D) juga **diacak** setiap sesi agar tidak mudah dihafalkan
- Materi sesuai kurikulum Bahasa Indonesia kelas 6 SD:
  - Membaca pemahaman
  - Menulis teks narasi/deskripsi
  - Tata bahasa (kalimat efektif, tanda baca, EYD)
  - Puisi dan pantun
  - Cerita rakyat dan fabel
  - Unsur intrinsik karya sastra
  - Sinonim, antonim, majas, konjungsi, imbuhan

### Tampilan & UX
- **Satu soal per tampilan** — siswa tidak melihat semua soal sekaligus
- Navigasi **SEBELUMNYA / BERIKUTNYA** di bawah setiap soal
- Grid navigasi di atas: klik nomor soal untuk lompat langsung
  - Abu = belum dijawab, Hijau = sudah dijawab (PG), Ungu = sudah dijawab (Esai), Amber = soal aktif
- Jawaban **dapat diubah** kapan saja sebelum dikumpulkan
- Opsi yang dipilih: **biru terang + teks putih** (menonjol)
- Opsi yang tidak dipilih: **abu muda + teks redup**
- Timer countdown 90 menit di topbar; warna berubah kuning (<15 menit) lalu merah (<5 menit)
- Skor pilihan ganda dihitung otomatis saat dikumpulkan
- Hasil ujian disimpan ke file `.txt` di folder yang sama dengan EXE

### Keamanan Anti-Contek
- Program berjalan **fullscreen** tanpa title bar (tidak ada tombol X)
- **Selalu di atas** semua jendela lain (`topmost`)
- **Windows low-level keyboard hook** memblokir: Alt+Tab, Alt+F4, Windows key, Escape, Print Screen
- `focus_force()` setiap 400ms agar fokus selalu kembali ke program
- Untuk keluar, harus memasukkan kode guru: **`pinewood62`**
- Program langsung masuk ke soal pertama (tidak ada layar input nama/kelas)

## Struktur Data Soal

```python
# Pool Pilihan Ganda — format internal (index-based answer)
PG_POOL = [
    {
        "p": "Teks pertanyaan ...",
        "o": ["Opsi satu", "Opsi dua", "Opsi tiga", "Opsi empat"],  # tanpa label A/B/C/D
        "j": 1   # index jawaban benar (0-3) sebelum diacak
    },
    # ... total 56 soal
]

# Pool Esai
ESAI_POOL = [
    {"p": "Teks pertanyaan esai ..."},
    # ... total 10 soal
]

# Setelah prepare_session(), format berubah menjadi:
# PG: {"type": "pg", "p": "...", "o": ["A. ...", "B. ...", ...], "j": "B"}
# Esai: {"type": "esai", "p": "..."}
```

## Build EXE
```bash
python -m PyInstaller --onefile --windowed --name "UjianBahasaIndonesia_Kelas6" ujian_bahasa_indonesia.py
# Output: dist/UjianBahasaIndonesia_Kelas6.exe (~10.7 MB)
```
