import os
import django
from django.db import connection, reset_queries

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course

def demo_optimization():
    # Pastikan ada data di database (Buat dulu di /admin)
    if not Course.objects.exists():
        print("❌ Error: Belum ada data Course. Silakan isi data di /admin dulu!")
        return

    print("="*50)
    print("DEMO OPTIMASI QUERY DJANGO ORM")
    print("="*50)

    # --- SKENARIO 1: N+1 PROBLEM (BURUK) ---
    reset_queries()
    print("\n[1] Menjalankan Query TANPA Optimasi (N+1 Problem)...")
    courses = Course.objects.all() # Query 1: Ambil semua course
    
    for course in courses:
        # Setiap baris di sini akan memicu query tambahan ke tabel User & Category
        print(f"- Course: {course.title} | Instructor: {course.instructor.username} | Cat: {course.category.name}")
    
    bad_query_count = len(connection.queries)
    print(f"👉 Total Query yang dieksekusi: {bad_query_count}")


    # --- SKENARIO 2: OPTIMIZED (BAGUS) ---
    reset_queries()
    print("\n[2] Menjalankan Query DENGAN Optimasi (select_related)...")
    
    # Menggunakan manager for_listing() yang sudah kita buat (pake select_related)
    optimized_courses = Course.objects.for_listing() 
    
    for course in optimized_courses:
        # Data instructor dan category sudah diambil di awal (JOIN), tidak ada query tambahan
        print(f"- Course: {course.title} | Instructor: {course.instructor.username} | Cat: {course.category.name}")
    
    good_query_count = len(connection.queries)
    print(f"👉 Total Query yang dieksekusi: {good_query_count}")

    print("\n" + "="*50)
    print(f"KESIMPULAN: Optimasi berhasil menghemat {bad_query_count - good_query_count} query!")
    print("="*50)

if __name__ == "__main__":
    demo_optimization()