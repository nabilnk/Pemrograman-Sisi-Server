# Progress 1: Simple LMS - Docker & Django Foundation

Proyek ini adalah tahap awal pengembangan sistem **Simple Learning Management System (LMS)**. Fokus pada tahap ini adalah melakukan *containerization* menggunakan Docker, konfigurasi database PostgreSQL, dan inisialisasi proyek Django dengan struktur *best practice*.

## 🎯 Learning Objectives
- Memahami containerization dengan Docker dan Docker Compose.
- Implementasi Dockerfile untuk aplikasi Django (Python).
- Konfigurasi database PostgreSQL di dalam lingkungan isolasi Docker.
- Setup proyek Django menggunakan struktur folder `config/` (best practice).

## 📦 Project Structure
Struktur folder proyek ini disusun mengikuti standar profesional untuk memisahkan konfigurasi utama dengan aplikasi:

```text
simple-lms/
├── config/                 # Folder inti konfigurasi Django
│   ├── settings.py         # Pengaturan database, app, middleware, dll
│   ├── urls.py             # Routing utama
│   ├── wsgi.py             # Entry point untuk server WSGI
│   └── asgi.py             # Entry point untuk server ASGI
├── screenshots/            # Bukti pengerjaan (Images)
├── .env.example            # Contoh konfigurasi environment variables
├── docker-compose.yml      # Orchestration untuk service Web dan DB
├── Dockerfile              # Blueprint untuk image aplikasi Django
├── manage.py               # Utility command-line Django
├── requirements.txt        # Daftar dependensi Python
└── README.md               # Dokumentasi proyek
```

## 🛠️ Docker Services
Proyek ini menggunakan dua service utama yang saling terhubung dalam satu network:
1. **Web**: Menjalankan aplikasi Django (Python 3.11-slim) pada port `8000`.
2. **Database (DB)**: Menjalankan PostgreSQL 15-alpine untuk penyimpanan data persisten.

## 🚀 Cara Menjalankan Project

1. **Clone Repository**
   ```bash
   git clone <url-repository-anda>
   cd simple-lms
   ```

2. **Build dan Jalankan Container**
   Pastikan Docker Desktop sudah aktif, lalu jalankan:
   ```bash
   docker-compose up -d
   ```

3. **Jalankan Migrasi Database**
   Lakukan perintah ini untuk membuat tabel sistem Django di PostgreSQL:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Akses Aplikasi**
   Buka browser dan akses: [http://localhost:8000](http://localhost:8000)

## 🔑 Environment Variables Explanation
Konfigurasi sensitif dikelola melalui environment variables di dalam `docker-compose.yml`. Berikut penjelasannya:

| Variabel | Keterangan |
|---|---|
| `DEBUG` | Set ke `1` untuk mode pengembangan (menampilkan error detail). |
| `SECRET_KEY` | Kunci keamanan unik untuk enkripsi Django. |
| `DB_NAME` | Nama database PostgreSQL yang digunakan (`lms_db`). |
| `DB_USER` | Username untuk akses database (`lms_user`). |
| `DB_PASS` | Password untuk akses database (`lms_password`). |
| `DB_HOST` | Nama service database di network Docker (`db`). |
| `DB_PORT` | Port default PostgreSQL (`5432`). |

## ⚙️ Django Configuration Details
- **Database Connection**: Django dikonfigurasi untuk terhubung ke PostgreSQL menggunakan engine `django.db.backends.postgresql`.
- **Static Files**: Telah dikonfigurasi menggunakan `STATIC_URL` dan `STATIC_ROOT` untuk persiapan manajemen file statis (CSS/JS) di tahap selanjutnya.
- **Allowed Hosts**: Dikonfigurasi `['*']` untuk mengizinkan akses dari browser host ke dalam container Docker.

## 📸 Dokumentasi & Screenshot

### 1. Django Welcome Page
![Django Welcome Page](screenshots/welcome_django.png)

### 2. Docker Containers Running
![Docker PS](screenshots/docker_ps.png)

### 3. Database Migration Success
![Migration Success](screenshots/migration.png)

---
**Dibuat Oleh:** Muhammad Nabil Nazhmi Kurniali
**NIM:** A11.2023.1536  
```

