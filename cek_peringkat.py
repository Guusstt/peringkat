import requests

# --- KONFIGURASI ---
NAMA = "SALSABILA BRILLIANA AZZA RAMADHANI"
SEKOLAH_ID = 1349
JALUR_ID = "1"

# --- TELEGRAM & FILE ---
TELEGRAM_TOKEN = "7934112776:AAHpxxqldO5trY4Dncvs8hmI8nDHA9zzuNU"
TELEGRAM_CHAT_ID = "1347758592"
FILE_PENYIMPANAN = "peringkat_terakhir.txt"
ENDPOINT = "https://api-spmb.jatengprov.go.id/api/servis/perangkingan"

# --- API KEY & CSRF Token ---
API_KEY = "e86087bd-d805-407e-8e1d-a56c96490545"
CSRF_TOKEN = "dN6soihF-GRw6JYWjrw5118b9yvlHS75_WqQ"

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
COOKIES = {
    "_ga": "GA1.1.164135517.1748193783",
    "acw_tc": "a3b5649c17500745659437650e572bcd75f5ba0251be34b98b12a12a82",
    "cdn_sec_tc": "a3b5649c17500745659437650e572bcd75f5ba0251be34b98b12a12a82",
    "_csrf": "462HMcMHtwuO6xh4_y_6wcos",
    "SERVERID": "f8c3467980c546f6f56b0b3eb1ae47f5|1750074751|1750074565",
    "SERVERCORSID": "f8c3467980c546f6f56b0b3eb1ae47f5|1750074751|1750074565",
    "_ga_6JGZQLQ77R": "GS2.1.s1750074559$o24$g1$t1750074749$j59$l0$h0"
}

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

    if data is None:
        print("🚫 Proses dihentikan karena gagal mengambil data.")
        return

    if not data:
        print("ℹ️ Data peringkat dari API kosong. Mungkin belum ada pendaftar.")
        return

    peringkat_baru = cari_peringkat(data, NAMA)
    if peringkat_baru is None:
        print(f"⚠️ Nama '{NAMA}' tidak ditemukan dalam data.")
        return

    peringkat_lama = baca_peringkat_terakhir()
    if peringkat_lama is None or peringkat_lama != peringkat_baru:
        perubahan = f"Dari: {peringkat_lama if peringkat_lama else 'Belum tercatat'} ➡️ Ke: <b>{peringkat_baru}</b>"
        if peringkat_lama:
            selisih = peringkat_lama - peringkat_baru
            if selisih > 0:
                perubahan += f" (Naik {selisih} Peringkat 📈)"
            elif selisih < 0:
                perubahan += f" (Turun {abs(selisih)} Peringkat 📉)"

        pesan = (
            f"📢 <b>UPDATE PERINGKAT PPDB</b> 📢\n\n"
            f"👤 <b>Nama:</b> {NAMA}\n"
            f"📊 <b>Peringkat:</b> {perubahan}\n"
            f"📅 Update via API Jateng"
        )
        kirim_telegram(pesan)
        simpan_peringkat(peringkat_baru)
    else:
        print(
            f"ℹ️ Tidak ada perubahan peringkat. Tetap di posisi {peringkat_baru}.")


if __name__ == "__main__":
    main()
