# Mengimpor fungsi dari masing-masing modul
# Kita mengimpor fungsinya langsung untuk kemudahan pemanggilan
from penambahan import tambah
from pengurangan import kurang
from perkalian import kali
from pembagian import bagi

def main():
    # Bagian (a) dan (b): Meminta input angka dari pengguna
    try:
        angka1 = float(input("Masukkan angka pertama: "))
        angka2 = float(input("Masukkan angka kedua: "))
    except ValueError:
        print("Input tidak valid. Harap masukkan angka.")
        return # Menghentikan eksekusi jika input bukan angka

    # Bagian (c): Melakukan dan menampilkan hasil perhitungan

    # Penambahan
    hasil_tambah = tambah(angka1, angka2)
    print(f"\nPenambahan dari {angka1} dan {angka2} adalah {hasil_tambah}")

    # Pengurangan
    hasil_kurang = kurang(angka1, angka2)
    print(f"Pengurangan dari {angka1} dan {angka2} adalah {hasil_kurang}")

    # Perkalian
    hasil_kali = kali(angka1, angka2)
    print(f"Perkalian dari {angka1} dan {angka2} adalah {hasil_kali}")

    # Pembagian
    hasil_bagi = bagi(angka1, angka2)
    # Catatan: Fungsi bagi() sudah menangani pembagian dengan nol
    print(f"Pembagian dari {angka1} dan {angka2} adalah {hasil_bagi}")

# Memastikan fungsi main() dijalankan saat script dieksekusi
if __name__ == "__main__":
    main()