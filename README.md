# 🤖 Bot Almo Farcaster

### **SCRIPT AUTO FARMING GRATIS**

![✅ REQUEST DIKABULKAN! Buatin Bot Almo Farcaster Untuk Subscriber  Auto Like, Recast   Reply!](https://github.com/user-attachments/assets/bfec4bbf-1fcb-4f90-91b3-34abf872ba48)

Sebuah tool canggih yang dirancang untuk mengotomatisasi interaksi Anda
di platform **Almo Farcaster**.\
Maksimalkan efisiensi dan farming poin dengan fitur lengkap + TUI modern
berbasis `rich`.

------------------------------------------------------------------------

## ✨ Fitur Utama

-   **\[+\] Auto Like** --- Menyukai cast yang muncul di dashboard
    secara otomatis.\
-   **\[+\] Auto Recast** --- Melakukan recast sesuai kebutuhan task.\
-   **\[+\] Auto Follow** --- Mengikuti akun pembuat cast secara
    otomatis.\
-   **\[+\] Auto Reply** --- Mengirim balasan custom yang diambil dari
    `config.json`.\
-   **\[+\] TUI Canggih** --- Tampilan terminal modern, interaktif, dan
    real-time (`rich`).\
-   **\[+\] Konfigurasi Simpel** --- Semua pengaturan tersentral di satu
    file.\
-   **\[+\] Live Activity Log** --- Pantau seluruh aksi bot secara
    langsung.\
-   **\[+\] Anti-Deteksi** --- Menggunakan delay acak seperti manusia
    asli.

------------------------------------------------------------------------

## 🛠️ Instalasi & Konfigurasi

### 1. Kebutuhan Sistem

-   Python 3.x\
-   Git

------------------------------------------------------------------------

### 2. Langkah Instalasi

#### **Clone Repository**

``` bash
git clone https://github.com/airdrop-888/nama-repo-anda.git
cd nama-repo-anda
```

> Ganti `nama-repo-anda` sesuai repository Anda.

------------------------------------------------------------------------

#### **Buat File `requirements.txt`**

Isi dengan:

    requests
    rich
    pyfiglet
    colorama

#### **Install Dependencies**

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 3. Konfigurasi Akun

-   Ganti nama `main-BackupCode.py` → `main.py`
-   Buat file baru: **config.json**
-   Masukkan struktur berikut:

``` json
{
  "fid": "MASUKKAN_FID_ANDA",
  "username": "MASUKKAN_USERNAME_ANDA",
  "do_like": true,
  "do_recast": true,
  "do_follow": true,
  "do_reply": true,
  "delay_min": 10,
  "delay_max": 25,
  "custom_reply": [
    "LFG!",
    "This is amazing!",
    "Great project!",
    "To the moon!",
    "Awesome work team!"
  ]
}
```

#### Penjelasan:

-   **fid** → ID unik Farcaster Anda (WAJIB)\
-   **username** → Username untuk tampilan statistik\
-   **do_like / recast / follow / reply** → Aktifkan atau matikan fitur\
-   **delay_min / delay_max** → Delay acak agar tidak terdeteksi sistem\
-   **custom_reply** → List balasan acak untuk reply otomatis

------------------------------------------------------------------------

## 🚀 Cara Menjalankan Bot

``` bash
python main.py
```

Bot akan mulai bekerja dan menampilkan log + statistik secara
**real-time**.

Untuk menghentikan bot:

    CTRL + C

------------------------------------------------------------------------

## ⚠️ PERINGATAN KERAS

Bot otomatis **berpotensi melanggar ToS Farcaster**.\
Risiko: - Rate limit\
- Shadowban\
- Suspensi akun

Gunakan dengan bijak.\
**DWYOR (Do With Your Own Risk).**

------------------------------------------------------------------------

### 👨‍💻 Kredit

Script dikembangkan oleh **@balveerxyz**\
Didistribusikan oleh **Airdrop 888**
