import itertools
import sys

# --- IMPORT: word_methods.py ---
try:
    from word_methods import exists ,BACK_VOWELS, FRONT_VOWELS
except ImportError:
    def exists(w): return True

# =============================================================================
#  BÖLÜM 1: INPUT MAPPING (Sözcük -> Harfküme Kodu)
# =============================================================================

CHAR_TO_BASE_CODE = {
    "a": "a", "e": "a",
    "o": "o", "ö": "o",
    "u": "u", "ü": "u",
    "ı": "ı", "i": "ı",
    "b": "b", "p": "b", "v": "b", "f": "b", 
    "c": "c", "ç": "c", "j": "c",
    "d": "d", "t": "d",
    "g": "g", "k": "g", "ğ": "g","h": "g",
    "l": "l",
    "m": "m", "n": "m",
    "r": "r", "z": "r",
    "s": "s", "ş": "s",
    "y": "y"
}

# =============================================================================
#  BÖLÜM 2: OUTPUT TABLE (Harfküme Kodu -> Olası Gerçek Harfler)
# =============================================================================

# -- Yardımcı Listeler --
TUM_UNLULER = ["a", "e", "o", "ö", "u", "ü", "ı", "i"]

# Tüm ünsüzler listesi (İstediğin gibi toplu tanımlı)
TUM_ARAUNSUZLER = [
    "ç", "d", "ğ", "h", "k", 
    "l", "m", "n", "p", "r", "s", "ş", "t", "v", "y", "z"
]
TUM_BASUNSUZLER = [
    "b", "c", "ç", "d", "f", "g","h",  "k", 
    "p",  "s", "ş", "t", "v", "y", "z"
]
CODE_TO_REAL_CHARS = {
    # --- ÜNLÜLER ---
    "A": ["a", "e"],        "a": ["a", "e"],
    "O": ["o", "ö"],        "o": ["o", "ö"],
    "U": ["u", "ü"],        "u": ["u", "ü"],
    "I": ["ı", "i"],        "ı": ["ı", "i"],
    
    # --- ÜNSÜZLER (BAŞLANGIÇ - Büyük Harf) ---
    "B": ["b", "p", "v", "f"], 
    "C": ["c", "ç"],
    "D": ["d", "t"],
    "G": ["g", "k","h"],           
    "L": ["l"],
    "M": ["m", "n"],
    "R": ["r"],
    "S": ["s", "ş"],
    "Y": ["y"],

    # --- ÜNSÜZLER (GENEL - Küçük Harf) ---
    "b": ["b", "p", "v"],
    "c": ["c", "ç"],
    "d": ["d", "t"],
    "g": ["g", "k", "ğ","h"],
    "l": ["l"],
    "m": ["m", "n"],
    "r": ["r", "z"],
    "s": ["s", "ş"],
    "y": ["y"],

    # --- JOKERLER ---
    "@": TUM_UNLULER,  # Ünlü Jokeri
    "X": TUM_BASUNSUZLER, # Başlangıç/Ek Ünsüz Jokeri
    "x": TUM_ARAUNSUZLER  # Genel Ünsüz Jokeri
}

# Fonotaktik yardımcı seti
VOWEL_CODES = {"a", "o", "u", "ı", "A", "O", "U", "I", "@"} 


# =============================================================================
#  BÖLÜM 3: MİMARİNİN KALBİ (FİLTRE) ve FONKSİYONLAR
# =============================================================================

def sacmasoz_savar(harfkume_str: str) -> bool:
    """
    Harfküme kodunu inceler. Mantıksız dizilimleri eler.
    True -> Geçerli, False -> Saçma (At gitsin)
    """
    # Boş ise zaten saçmadır
    if not harfkume_str:
        return False

    n = len(harfkume_str)
    
    # Yardımcılar
    # VOWEL_CODES global setini kullanıyoruz: {"a", "o", "u", "ı", "A", "O", "U", "I", "@"}
    def is_consonant(c):
        return c not in VOWEL_CODES

    def is_vowel(c):
        return c in VOWEL_CODES


    # 1. KURAL: İlk iki karakter ünsüz ise saçma (Örn: 'TR..')
    if n >= 2 and is_consonant(harfkume_str[0]) and is_consonant(harfkume_str[1]):
        return False

    # 2. KURAL: Son üç karakter ünsüz ise saçma (Örn: '..TRK')
    if n >= 3 and is_consonant(harfkume_str[-1]) and is_consonant(harfkume_str[-2]):
        return False

    # 3. KURAL: Başta iki ardışık ünlü varsa saçma (Örn: 'AA..')
    if n >= 2 and is_vowel(harfkume_str[0]) and is_vowel(harfkume_str[1]):
        return False

    # 4. KURAL: Sonda iki ardışık ünlü varsa saçma (Örn: '..II')
    if n >= 2 and is_vowel(harfkume_str[-1]) and is_vowel(harfkume_str[-2]):
        return False

    # 5. KURAL: İçinde üçten fazla (yani 4 ve üzeri) ardışık ünsüz varsa saçma
    consecutive_consonants = 0
    for char in harfkume_str:
        if is_consonant(char):
            consecutive_consonants += 1
            if consecutive_consonants > 3: # 4. ünsüz geldiği an elenir
                return False
        else:
            consecutive_consonants = 0 # Ünlü gelince sayacı sıfırla

    if harfkume_str[0] in ["L","M","R"]:
        return False
    # Tüm testlerden geçtiyse mantıklıdır
    return True


def harfkumele(word):
    """Sözcük -> Harfküme Kodu (İlk harf BÜYÜK)"""
    result = []
    clean_word = word.lower()
    for index, char in enumerate(clean_word):
        base_code = CHAR_TO_BASE_CODE.get(char)
        if base_code:
            if index == 0: result.append(base_code.upper())
            else: result.append(base_code.lower())
    return "".join(result)

def başkabiçimler(base_code):
    """
    DÜZELTİLMİŞ FONKSİYON: 
    @ ve X/x varyasyonları birbirine karışmaz.
    Her iki işlem de temiz 'base_code' üzerinden ayrı ayrı yapılır.
    """
    
    # Tüm sonuçları toplayacağımız tek küme (base_code'un kendisiyle başlar)
    final_varyasyonlar = {base_code}
    
    # Yardımcı: Kodun ünlü mü ünsüz mü olduğu (Global scope'ta VOWEL_CODES olduğu varsayılıyor)
    def is_consonant(c): return c not in VOWEL_CODES

    # ------------------------------------------------
    # YOL 1: Fonotaktik (@ Ekleme)
    # Sadece base_code analiz edilir.
    # ------------------------------------------------
    if len(base_code) >= 2:
        # Başta Çift Ünsüz (Örn: TR -> T@R, @TR)
        if is_consonant(base_code[0]) and is_consonant(base_code[1]):
            final_varyasyonlar.add(base_code[0] + "@" + base_code[1:]) # Araya
            final_varyasyonlar.add("@" + base_code)                   # Başa

        # Sonda Çift Ünsüz (Örn: RT -> R@T)
        if is_consonant(base_code[-2]) and is_consonant(base_code[-1]):
            final_varyasyonlar.add(base_code[:-1] + "@" + base_code[-1])

    # ------------------------------------------------
    # YOL 2: X ve x (Ünsüz Denemeleri)
    # Sadece base_code analiz edilir (Yol 1'in çıktıları buraya girmez).
    # ------------------------------------------------
    n = len(base_code)
    
    # A. INSERTION (Ekleme)
    for i in range(n + 1):
        if i == 0:
            # Başa 'X' ekle, orijinal baş harfi küçült (User logic)
            new = "X" + base_code[0].lower() + base_code[1:]
        else:
            # Araya/Sona 'x' ekle
            new = base_code[:i] + "x" + base_code[i:]
        
        final_varyasyonlar.add(new)
            
    # B. SUBSTITUTION (Değiştirme)
    for i in range(n):
        if i == 0:
            # Başı 'X' ile değiştir
            new = "X" + base_code[1:]
        else:
            # Arayı 'x' ile değiştir
            new = base_code[:i] + "x" + base_code[i+1:]
        
        final_varyasyonlar.add(new)
            
    return list(final_varyasyonlar)


##ünlü uyumu kısmını hallet
def anlambirimli(kelime):
    """
    1. Önce kelimedeki harmoni geçişlerini sayar (Target Hit belirler).
    2. Sonra kelimenin TÜM alt parçalarında (substring) kaç tane anlamlı kelime olduğuna bakar.
    3. Bulunan sayı >= Hedef sayı ise True döner.
    """
    
    # --- 1. AŞAMA: Harmoni Analizi (Hedef Belirleme) ---
    shift_count = 0
    last_group = None  # 'F' (Front/İnce) veya 'B' (Back/Kalın)

    for char in kelime:
        current_group = None
        if char in FRONT_VOWELS:
            current_group = 'F'
        elif char in BACK_VOWELS:
            current_group = 'B'
        
        # Eğer harf ünlü değilse (current_group None ise) atla
        if current_group:
            # İlk ünlüyü gördüğümüzde grubu set et
            if last_group is None:
                last_group = current_group
            # Grup değişimi varsa (İnce -> Kalın veya tam tersi)
            elif current_group != last_group:
                shift_count += 1
                last_group = current_group

    # Temel kural: Kelime sayısı = Geçiş sayısı + 1
    # Hiç geçiş yoksa (0) -> En az 1 kelime bulmalı (Normal durum)
    # 1 geçiş varsa (Örn: Elma) -> En az 2 hit bulmalı
    target_hits = shift_count + 1

    # --- 2. AŞAMA: Tarama ve Sayma (Substring Mantığı) ---
    found_hits = 0
    uzunluk = len(kelime)

    # Sözcüğün başından sonuna tüm olası parçaları tarıyoruz
    for i in range(uzunluk):
        for j in range(i + 1, uzunluk + 1):
            parca = kelime[i:j]
            
            if exists(parca):
                found_hits += 1
                
                # OPTİMİZASYON: Hedefe ulaştığımız an durabiliriz.
                # Gereksiz yere sonuna kadar taramaya gerek yok.
                if found_hits >= target_hits:
                    return True

    # Döngü bitti ve hala yeterli hit yoksa
    return False

def harfkumeden_kelimeler(harfkume_str):
    """Kodu gerçek kelimelere açar."""
    possible_chars_list = []
    for code in harfkume_str:
        chars = CODE_TO_REAL_CHARS.get(code)
        if chars: possible_chars_list.append(chars)
        else: possible_chars_list.append([code])
    
    # Cartesian Product
    return ("".join(c) for c in itertools.product(*possible_chars_list))


def sesdenkler(word):
    # 1. Ham Kodu Al
    raw_kume = harfkumele(word)
    
    # 2. Tüm Varyasyonları Üret (@, X, x dahil)
    tum_varyasyonlar = başkabiçimler(raw_kume)
    
    gecerli_sonuclar = []
    
    # 3. DÖNGÜ: Filtrele ve İşle
    for kod in tum_varyasyonlar:
        
        # --- ERKEN ELEME (SAÇMASÖZ SAVAR) ---
        if not sacmasoz_savar(kod):
            continue # Bu kod saçma, hiç işlem yapma, sonrakine geç.
            
        # Kod mantıklıysa kelimeleri oluştur
        olasi_kelimeler = harfkumeden_kelimeler(kod)
        
        for aday_kelime in olasi_kelimeler:
            # 4. Son Kontrol (Sözlükte var mı?)
            if anlambirimli(aday_kelime):
                gecerli_sonuclar.append(aday_kelime)
                
    return list(set(gecerli_sonuclar)) 


if __name__ == "__main__":
    # Test
    ornek = "jandarma"
    print(f"Kelime: {ornek}")
    
    sonuclar = sesdenkler(ornek)
    
    print(f"Toplam Aday: {len(sonuclar)}")
    print(sonuclar[:50])