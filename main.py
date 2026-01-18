from generative_approach.benzerlik import benzerlik
from generative_approach.harfkumeler import sesdenkler , yasal_olanlar
if __name__ == "__main__":
    while True:
        try:
            ornek = input("Kelime girin: ").strip().lower()
            if not ornek: continue # Boş giriş yapılırsa atla
            
            print(f"\nİncelenen Kelime: {ornek}")
            print("-" * 30)
            # 1. Adayları Bul
            sonuclar = sesdenkler(ornek)
            
            # 2. Yasal Olanları Filtrele
            x = yasal_olanlar(sonuclar)
            
            # --- SIRALAMA İŞLEMİ (Burayı ekledik) ---
            # Her iki listeyi de 'benzerlik' fonksiyonundan dönen skora göre (reverse=True -> Büyükten küçüğe) sıralıyoruz.
            sonuclar.sort(key=lambda aday: benzerlik(ornek, aday), reverse=True)
            x.sort(key=lambda aday: benzerlik(ornek, aday), reverse=True)
            print("deniz" in sonuclar)
            # --- SONUÇLARI YAZDIRMA ---
            print(f"Toplam Aday Sayısı: {len(sonuclar)}")
            print("Tüm Adaylar (Skora göre ilk 50):")
            # İstersen puanları da görmek için list comprehension kullanabilirsin, şimdilik sadece kelimeleri yazdırıyoruz
            print(sonuclar[:50])
            
            print("\n" + "-" * 30)
            
            print(f"Yasal Olanlar Sayısı: {len(x)}")
            print("Yasal Olanlar (Skora göre sıralı):")
            print([(k, round(benzerlik(ornek, k), 2)) for k in x])
            
            print("\n" + "=" * 30 + "\n")
            
        except KeyboardInterrupt:
            print("\nÇıkış yapılıyor...")
            break
        except Exception as e:
            print(f"Bir hata oluştu: {e}")