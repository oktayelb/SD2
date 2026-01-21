from generative_approach.benzerlik import benzerlik
from generative_approach.harfkumeler import sesdenkler , yasal_olanlar

if __name__ == "__main__":
    while True:
        try:
            ornek = input("Kelime girin: ").strip().lower()
            if not ornek: continue 
            
            print(f"\nİncelenen Kelime: {ornek}")
            print("-" * 30)
            
            # 1. Adayları Bul (Returns list of tuples: (raw, styled))
            sonuclar = sesdenkler(ornek)
            
            # 2. Yasal Olanları Filtrele 
            # Returns list of tuples: (raw, styled, analyses)
            x = yasal_olanlar(sonuclar)
            
            # --- SIRALAMA İŞLEMİ (New Logic) ---
            
            # Helper for similarity sort (raw words)
            sonuclar.sort(key=lambda aday: benzerlik(ornek, aday[0]), reverse=True)
            
            # Advanced Sort for Legal Results:
            # Priority 1: Does the styled word start with an Uppercase? (Root at start)
            # Priority 2: Similarity Score
            def advanced_sort_key(item):
                raw, styled, _ = item
                starts_upper = styled[0].isupper() if styled else False
                score = benzerlik(ornek, raw)
                return (starts_upper, score)

            x.sort(key=advanced_sort_key, reverse=True)
            
            # Check if specific word exists (checking raw words)
            raw_results = [r[0] for r in sonuclar]
            # print(f"Is 'deniz' in results: {'deniz' in raw_results}")
            
            # --- SONUÇLARI YAZDIRMA ---
            print(f"Toplam Aday Sayısı: {len(sonuclar)}")
            
            # Print styled words for top candidates
            print("Tüm Adaylar (Skora göre ilk 50):")
            print([s[1] for s in sonuclar[:50]]) 
            
            print("\n" + "-" * 30)
            
            print(f"Yasal Olanlar Sayısı: {len(x)}")
            print("Yasal Olanlar (Detaylı):")
            
            print(f"{'KELİME (STYLED)':<20} | {'SKOR':<6} | {'MORFOLOJİK ANALİZ (Kök + Ekler)'}")
            print("-" * 85)

            for raw, styled, analyses in x:
                score = round(benzerlik(ornek, raw), 2)
                
                # Format Morphological Analyses
                morph_display_list = []
                for root, _, chain, _ in analyses:
                    # chain contains Suffix objects, we access .name
                    suffix_names = "+".join([s.name for s in chain])
                    if suffix_names:
                        morph_display_list.append(f"{root}+{suffix_names}")
                    else:
                        morph_display_list.append(f"{root}(yalın)")
                
                # Join multiple possible analyses with " OR "
                morph_str = " | ".join(morph_display_list)
                
                print(f"{styled:<20} | {score:<6} | {morph_str}")
            
            print("\n" + "=" * 30 + "\n")
            
        except KeyboardInterrupt:
            print("\nÇıkış yapılıyor...")
            break
        except Exception as e:
            print(f"Bir hata oluştu: {e}")