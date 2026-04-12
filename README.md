# Aplikasi Ujian Sekolah Dasar Kelas 6

Kumpulan program ujian digital berbasis Python untuk siswa kelas 6 SD, mencakup mata pelajaran **IPAS**, **PJOK**, dan **Bahasa Indonesia**. Dirancang untuk dijalankan di komputer sekolah dengan fitur anti-contek bawaan.

---

## Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Struktur Proyek](#struktur-proyek)
- [Spesifikasi Program](#spesifikasi-program)
- [Metode yang Digunakan](#metode-yang-digunakan)
- [Hal-hal yang Perlu Diperhatikan](#hal-hal-yang-perlu-diperhatikan)
- [Cara Menjalankan (Mode Development)](#cara-menjalankan-mode-development)
- [Cara Compile ke EXE](#cara-compile-ke-exe)

---

## Fitur Utama

- Soal **Pilihan Ganda** dan **Esai** diacak setiap sesi ujian
- Urutan pilihan jawaban (A/B/C/D) ikut diacak agar tidak mudah dihafalkan
- Navigasi soal bebas (SEBELUMNYA / BERIKUTNYA / klik grid nomor soal)
- Timer countdown **90 menit** dengan indikator warna
- Skor pilihan ganda dihitung otomatis; hasil disimpan ke file `.txt`
- Fullscreen tanpa title bar — tidak ada tombol minimize/close
- Keluar hanya bisa dilakukan guru via shortcut tersembunyi

---

## Struktur Proyek

```
AssesmentUjianSDkelas6/
├── IPAS/
│   ├── ujian_ipas.py          # Source code ujian IPAS
│   ├── CLAUDE.md              # Spesifikasi soal & role guru IPAS
│   └── materi ipas kelas 6.pdf
├── PJOK/
│   ├── ujian_pjok.py          # Source code ujian PJOK
│   └── CLAUDE.md              # Spesifikasi soal & role guru PJOK
├── BahasaIndonesia/
│   ├── ujian_bahasa_indonesia.py   # Source code ujian Bahasa Indonesia
│   └── CLAUDE.md              # Spesifikasi soal & role guru BI
└── README.md
```

> Folder `dist/` dan `build/` (hasil compile) tidak di-track oleh Git.

---

## Spesifikasi Program

| Mata Pelajaran | Pool PG | PG per Sesi | Pool Esai | Esai per Sesi | Soal Wajib Esai |
|---|---|---|---|---|---|
| IPAS | 100 | 45 | 17 | 5 | Soal no. 17 (renang gaya punggung) |
| PJOK | 100 | 45 | 17 | 5 | Soal no. 17 (renang gaya punggung) |
| Bahasa Indonesia | 56 | 45 | 10 | 5 | — |

**Tingkat kesulitan soal PG (IPAS & PJOK):**
- Mudah : soal 1–56
- Menengah : soal 57–78
- Sulit : soal 79–100

**Format file hasil ujian:**
```
hasil_ipas_20260413_090000.txt
hasil_pjok_20260413_090000.txt
hasil_bahasa_indonesia_20260413_090000.txt
```
File disimpan di folder yang sama dengan file `.exe` atau `.py`.

---

## Metode yang Digunakan

### 1. Pengacakan Soal (Session Randomization)
Setiap sesi ujian, soal dipilih secara acak dari pool menggunakan `random.sample()`. Urutan pilihan jawaban A/B/C/D juga diacak dengan `random.shuffle()`. Kunci jawaban diperbarui secara dinamis mengikuti posisi baru setelah pengacakan, sehingga siswa yang mengulang ujian tidak bisa mengandalkan hafalan posisi jawaban.

```python
correct_text = q["o"][q["j"]]     # simpan teks jawaban benar
opts = q["o"][:]
random.shuffle(opts)               # acak urutan opsi
new_answer = opts.index(correct_text)  # cari posisi baru jawaban benar
```

### 2. Windows Low-Level Keyboard Hook
Program memasang keyboard hook melalui `ctypes.windll.user32.SetWindowsHookExA` di thread terpisah. Hook ini memblokir tombol-tombol berikut **di level sistem operasi**, bukan hanya di jendela aplikasi:

| Virtual Key | Tombol |
|---|---|
| `0x5B`, `0x5C` | Windows key (kiri & kanan) |
| `0x09` | Alt+Tab |
| `0x73` | Alt+F4 |
| `0x1B` | Escape |
| `0x2C` | Print Screen |

### 3. Fullscreen Anti-Contek
```python
r.attributes("-fullscreen", True)   # fullscreen penuh
r.attributes("-topmost", True)      # selalu di atas semua jendela
r.overrideredirect(True)            # hapus title bar & border
r.protocol("WM_DELETE_WINDOW", lambda: None)  # nonaktifkan tombol X
```

### 4. Paksa Fokus Berkala
Setiap 400ms, program memeriksa apakah ada dialog aktif. Jika tidak, fokus dikembalikan paksa ke jendela utama agar siswa tidak bisa berpindah ke aplikasi lain.

```python
def _enforce_fg(self):
    ...
    self.root.focus_force()
    self.root.after(400, self._enforce_fg)
```

### 5. Shortcut Keluar Guru (Tersembunyi)
Tidak ada tombol keluar yang terlihat. Guru keluar dengan **Ctrl+Alt+Backspace**:
```python
r.bind_all("<Control-Alt-BackSpace>", lambda e: self._try_exit())
```

### 6. Antarmuka Tkinter One-Question-Per-View
Setiap navigasi soal, frame soal lama di-`destroy()` dan diganti frame baru. Ini menjaga performa memori dan mencegah siswa scroll untuk melihat soal lain.

### 7. Penyimpanan Jawaban Esai
Jawaban esai disimpan ke dictionary `self.answers` setiap kali siswa berpindah soal, sehingga jawaban tidak hilang saat navigasi.

---

## Hal-hal yang Perlu Diperhatikan

### Sebelum Ujian
- Pastikan Python 3.10+ sudah terinstal jika menjalankan dari source (mode development).
- Jika menggunakan `.exe`, tidak perlu instalasi Python — langsung jalankan.
- **Jalankan sebagai Administrator** agar Windows keyboard hook dapat terpasang dengan benar. Tanpa hak Admin, hook mungkin tidak berfungsi di Windows 11.
- Nonaktifkan antivirus sementara saat menjalankan EXE (beberapa antivirus memblokir program yang memasang keyboard hook).

### Saat Ujian Berlangsung
- Shortcut keluar guru adalah **Ctrl+Alt+Backspace** — jaga agar siswa tidak mengetahuinya.
- File hasil ujian otomatis tersimpan di folder yang sama dengan EXE setelah siswa menekan "KUMPULKAN".
- Jika komputer mati mendadak saat ujian, **jawaban tidak tersimpan** — tidak ada auto-save sesi.
- Timer tidak dapat dijeda; jika program ditutup paksa, waktu tidak tersimpan.

### Kompatibilitas
- Program hanya berjalan di **Windows** (menggunakan `ctypes.windll`).
- Diuji pada Windows 10 dan Windows 11.
- Tidak kompatibel dengan macOS atau Linux.

---

## Cara Menjalankan (Mode Development)

### Prasyarat
```bash
pip install pyinstaller
```

> Tidak ada dependensi pihak ketiga lain — program hanya menggunakan modul bawaan Python (`tkinter`, `ctypes`, `random`, `threading`, `datetime`, `os`, `sys`).

### Jalankan langsung
```bash
cd IPAS
python ujian_ipas.py

cd PJOK
python ujian_pjok.py

cd BahasaIndonesia
python ujian_bahasa_indonesia.py
```

> **Catatan:** Saat berjalan dari terminal, tekan Ctrl+C di terminal untuk keluar darurat jika shortcut Ctrl+Alt+Backspace tidak berfungsi.

---

## Cara Compile ke EXE

Gunakan PyInstaller dengan flag `--onefile` (satu file EXE mandiri) dan `--windowed` (tanpa jendela console).

### IPAS
```bash
cd IPAS
python -m PyInstaller --onefile --windowed --name "UjianIPAS_Kelas6" ujian_ipas.py
```

### PJOK
```bash
cd PJOK
python -m PyInstaller --onefile --windowed --name "UjianPJOK_Kelas6" ujian_pjok.py
```

### Bahasa Indonesia
```bash
cd BahasaIndonesia
python -m PyInstaller --onefile --windowed --name "UjianBahasaIndonesia_Kelas6" ujian_bahasa_indonesia.py
```

### Output
EXE akan berada di folder `dist/` masing-masing mata pelajaran:
```
IPAS/dist/UjianIPAS_Kelas6.exe
PJOK/dist/UjianPJOK_Kelas6.exe
BahasaIndonesia/dist/UjianBahasaIndonesia_Kelas6.exe
```

### Ukuran perkiraan EXE
~10–12 MB per file (sudah termasuk runtime Python dan library tkinter).

### Membersihkan file build
Setelah compile, folder `build/` dan file `.spec` bisa dihapus — hanya `dist/*.exe` yang diperlukan.
```bash
# Contoh untuk IPAS
rd /s /q build
del UjianIPAS_Kelas6.spec
```

---

## Lisensi

Dibuat untuk keperluan internal sekolah. Tidak untuk didistribusikan secara komersial.
