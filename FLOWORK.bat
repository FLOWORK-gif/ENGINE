@echo off
rem File ini sekarang adalah launcher pintar yang akan memeriksa update dan environment.

echo =======================================================
echo          FLOWORK SMART LAUNCHER (DEBUG MODE)
echo =======================================================
echo.

REM *** BARIS PENTING: Pindah ke direktori tempat file .bat ini berada ***
cd /d "%~dp0"

echo [TAHAP 1/4] Memeriksa dan menyiapkan environment (instalasi pertama kali)...
echo -------------------------------------------------------

rem =================================================================
rem === PERUBAHAN DI SINI: Panggil python langsung, bukan lewat poetry run ===
python scripts/setup.py
rem =================================================================

echo -------------------------------------------------------
echo.

echo [TAHAP 2/4] Memeriksa pembaruan dari GitHub...
echo -------------------------------------------------------
rem (Ini adalah skrip updater dari jawaban sebelumnya, jika kamu pakai)
rem python updater.py
echo -------------------------------------------------------
echo.

echo [TAHAP 3/4] Memeriksa lisensi dan versi...
echo [TAHAP 4/4] Menjalankan Flowork...
echo -------------------------------------------------------
rem Menjalankan launcher utama yang akan memulai aplikasi Flowork
poetry run python launcher.py
echo -------------------------------------------------------
echo.

echo Proses selesai. Tekan tombol apa saja untuk keluar.
pause >nul