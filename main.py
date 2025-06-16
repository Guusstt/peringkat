import requests
import os
from http.cookies import SimpleCookie

# --- KONFIGURASI ---
NAMA = "SALSABILA BRILLIANA AZZA RAMADHANI"
SEKOLAH_ID = 1349
JALUR_ID = "1"

# --- TELEGRAM & FILE ---
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FILE_PENYIMPANAN = "peringkat_terakhir.txt"
ENDPOINT = "https://api-spmb.jatengprov.go.id/api/servis/perangkingan"

# --- API KEY & CSRF Token ---
API_KEY = os.environ["API_KEY"]
CSRF_TOKEN = os.environ["CSRF_TOKEN"]

# --- HEADERS ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
    "Referer": "https://spmb.jatengprov.go.id/",
    "Origin": "https://spmb.jatengprov.go.id",
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "csrf-token": CSRF_TOKEN,
}

# --- COOKIES ---
cookie_raw = os.environ["COOKIES"]
simple_cookie = SimpleCookie()
simple_cookie.load(cookie_raw)
COOKIES = {key: morsel.value for key, morsel in simple_cookie.items()}

# --- PAYLOAD ---
PAYLOAD = {
    "jalur_pendaftaran_id": JALUR_ID,
    "sekolah_tujuan_id": SEKOLAH_ID,
}


def ambil_data_perangkingan():
    print("⏳ Mengambil data dari API...")
    try:
        response = requests.post(
            ENDPOINT,
            json=PAYLOAD,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=20
        )
        response.raise_for_status()
        print("✅ Data berhasil diambil dari API.")
        return response.json().get("data", [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            print("❌ Gagal mengambil data: Error 401/403 Forbidden/Unauthorized.")
            print(
                "   -> Kemungkinan besar API_KEY, token, atau cookie sudah tidak valid.")
        else:
            print(f"❌ Gagal mengambil data (HTTP Error): {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Gagal mengambil data (Request Error): {e}")
        return None


def cari_peringkat(data, nama_dicari):
    if data is None:
        return None
    nama_dicari_lower = nama_dicari.strip().lower()
    for i, peserta in enumerate(data, 1):
        if "nama_lengkap" in peserta and peserta["nama_lengkap"].strip().lower() == nama_dicari_lower:
            return i
    return None


def baca_peringkat_terakhir():
    try:
        with open(FILE_PENYIMPANAN, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def simpan_peringkat(peringkat):
    with open(FILE_PENYIMPANAN, "w") as f:
        f.write(str(peringkat))


def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
        print("📬 Notifikasi berhasil dikirim ke Telegram.")
    except Exception as e:
        print(f"❌ Gagal mengirim notifikasi ke Telegram: {e}")


def main():
    data = ambil_data_perangkingan()

    if not data:
        print("🚫 Data tidak tersedia atau gagal diambil.")
        return

    peringkat_baru = cari_peringkat(data, NAMA)
    if peringkat_baru is None:
        print(f"⚠️ Nama '{NAMA}' tidak ditemukan dalam data.")
        return

    peringkat_lama = baca_peringkat_terakhir()

    # Kirim notifikasi hanya jika peringkat berubah
    if peringkat_lama != peringkat_baru:
        perubahan = f"Dari: {peringkat_lama if peringkat_lama else 'Belum tercatat'} ➡️ <b>{peringkat_baru}</b>"
        if peringkat_lama:
            selisih = peringkat_lama - peringkat_baru
            if selisih > 0:
                perubahan += f" (Naik {selisih} 📈)"
            elif selisih < 0:
                perubahan += f" (Turun {abs(selisih)} 📉)"

        pesan = (
            f"📢 <b>UPDATE PERINGKAT PPDB</b>\n\n"
            f"👤 <b>Nama:</b> {NAMA}\n"
            f"📊 <b>Peringkat:</b> {perubahan}\n"
            f"📅 Update otomatis dari sistem PPDB Jateng"
        )
        kirim_telegram(pesan)
        simpan_peringkat(peringkat_baru)
    else:
        print(
            f"ℹ️ Tidak ada perubahan peringkat. Tetap di posisi {peringkat_baru}.")
