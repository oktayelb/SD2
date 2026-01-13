import random
from mutative_approach.benzerlik import get_weighted_candidate, VOWEL_SCORES, CONSONANT_SCORES

# --- BAĞIMLILIKLAR ---
# Eğer bu dosyalar yoksa hata vermemesi için try-except veya mock kullanabilirsin.
try:
    from util.word_methods import exists
    # Ünlüleri buradan alalım, yoksa elle tanımlayalım
    from util.word_methods import BACK_VOWELS, FRONT_VOWELS
except ImportError:
    # Fallback (Yedek) Tanımlar
    BACK_VOWELS = {'a', 'ı', 'o', 'u'}
    FRONT_VOWELS = {'e', 'i', 'ö', 'ü'}
    def exists(word): return False # Varsayılan olarak kelime yok sayılır

TUM_UNLULER = BACK_VOWELS.union(FRONT_VOWELS)

def is_vowel(char):
    return char in TUM_UNLULER

def check_vowel_harmony(prev_vowel, current_vowel):
    """
    Basit Büyük Ünlü Uyumu kontrolü.
    Önceki harf Kalın ise şimdiki de Kalın olmalı.
    """
    if prev_vowel is None: 
        return True # İlk ünlü serbesttir
    
    prev_is_back = prev_vowel in BACK_VOWELS
    curr_is_back = current_vowel in BACK_VOWELS
    
    return prev_is_back == curr_is_back

def mutate_word(word, mutation_rate=0.4, force_harmony=True):
    """
    Kelimeyi fonetik olarak mutasyona uğratır.
    
    Args:
        word (str): Girdi kelimesi
        mutation_rate (float): 0.0 - 1.0 arası. Harfin değişme olasılığı.
        force_harmony (bool): True ise Büyük Ünlü Uyumuna zorlar.
    """
    word = word.lower()
    new_chars = []
    last_vowel = None
    
    for i, char in enumerate(word):
        # 1. ZAR AT: Değişim olacak mı?
        if random.random() > mutation_rate:
            # Değişim YOK, harfi koru.
            chosen_char = char
        else:
            # Değişim VAR, benzerini bul.
            chosen_char = get_weighted_candidate(char, is_vowel(char), mutation_strength=1.2)

        # 2. ÜNLÜ UYUMU KONTROLÜ (Backtracking basit versiyon)
        if is_vowel(chosen_char) and force_harmony:
            # Eğer bu kelimenin ilk ünlüsü ise, bunu 'last_vowel' yap
            if last_vowel is None:
                # Orijinal kelimenin köküne sadık kalmak için bazen 
                # ilk ünlüyü değiştirmeyi engelleyebiliriz veya serbest bırakırız.
                # Şimdilik serbest bırakıyoruz.
                pass 
            else:
                # Önceki ünlüyle uyumlu mu?
                max_attempts = 5
                attempt = 0
                while not check_vowel_harmony(last_vowel, chosen_char) and attempt < max_attempts:
                    # Uyumsuzsa, yeniden zar at (sadece ünlüler arasından)
                    chosen_char = get_weighted_candidate(char, True)
                    attempt += 1
                
                # Eğer hala uymuyorsa, zorla orijinal harfi veya uyumlu bir harfi koy
                if not check_vowel_harmony(last_vowel, chosen_char):
                     chosen_char = char # Risk alma, orijinali koy.

            last_vowel = chosen_char
        
        # Eğer harf ünsüzse ama biz ünlü takibi yapıyorsak, last_vowel değişmez.
        new_chars.append(chosen_char)
        
    return "".join(new_chars)

def generate_neologisms(seed_word, count=20, mutation_rate=0.3):
    """
    Verilen kelimeden, sözlükte OLMAYAN ama Türkçeye benzeyen kelimeler türetir.
    """
    results = set()
    attempts = 0
    max_attempts = count * 5 # Sonsuz döngüden kaçınmak için
    
    while len(results) < count and attempts < max_attempts:
        attempts += 1
        
        # 1. Mutasyon yarat
        candidate = mutate_word(seed_word, mutation_rate=mutation_rate)
        
        # 2. Orijinal kelimeyle aynı olmasın
        if candidate == seed_word:
            continue
            
        # 3. Sözlükte VARSA at (Biz olmayan kelime arıyoruz)
        # Not: exists fonksiyonun gerçek bir sözlük kontrolü yapmalı.
        if exists(candidate):
            continue
            
        # 4. Fonotaktik Basit Kontrol (İsteğe bağlı)
        # Yan yana 3 ünsüz veya 3 ünlü olmasın
        if "aaa" in candidate or "eee" in candidate: # Basit örnek
            continue
            
        results.add(candidate)
        
    return list(results)

if __name__ == "__main__":
    test_words = ["kalem", "bilgisayar", "okyanus", "gökyüzü"]
    
    print(f"{'ORİJİNAL':<15} | {'TÜRETİLEN (YENİ)':<30}")
    print("-" * 50)
    
    for w in test_words:
        # 10 tane üret
        uretimler = generate_neologisms(w, count=5, mutation_rate=0.4)
        print(f"{w:<15} | {', '.join(uretimler)}")