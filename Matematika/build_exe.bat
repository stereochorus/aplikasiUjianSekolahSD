@echo off
echo ============================================
echo  Build Ujian Matematika Kelas 6 SD - EXE
echo ============================================

:: Install PyInstaller jika belum ada
pip install pyinstaller --quiet

:: Build exe
pyinstaller --onefile ^
  --windowed ^
  --name "UjianMatematika_Kelas6" ^
  --icon NONE ^
  unjian_matematika.py

echo.
echo ============================================
if exist "dist\UjianMatematika_Kelas6.exe" (
    echo  SUKSES! File exe tersimpan di:
    echo  dist\UjianMatematika_Kelas6.exe
) else (
    echo  GAGAL! Periksa error di atas.
)
echo ============================================
pause
