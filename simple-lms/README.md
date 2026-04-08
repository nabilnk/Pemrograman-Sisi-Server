## Progress 2: Database Design & ORM

### Implementasi Models
- **Custom User**: Menggunakan `AbstractUser` dengan field `role` (admin, instructor, student).
- **Relasi Database**: 
    - `Course` ke `User` (Instructor) & `Category` menggunakan ForeignKey.
    - `Enrollment` menggunakan `unique_together` untuk memastikan user tidak mendaftar kursus yang sama dua kali.
    - `Category` menggunakan relasi `self-referencing` untuk mendukung kategori bertingkat (parent-child).

### Optimasi Query (N+1 Problem)
Masalah N+1 terjadi ketika kita mengambil daftar objek (misal: Course) dan memanggil data relasinya (misal: Instructor) di dalam loop, sehingga memicu query database berulang kali.

**Solusi:** Menggunakan `select_related` untuk Foreign Key (SQL JOIN).

#### Perbandingan Hasil Query Demo:
- **Tanpa Optimasi**: `N+1` Query (Makin banyak data, makin berat).
- **Dengan Optimasi (`select_related`)**: Hanya `1` Query (Sangat cepat karena menggunakan JOIN).

### Screenshot Progress 2
1. **Django Admin Interface**:
![Admin Dashboard](screenshots/admin_dashboard.png)
2. **Query Optimization Result**:
![Query Demo](screenshots/query_demo.png)
3. **Data Fixtures JSON**: File tersedia di `courses/fixtures/data.json`.
```

