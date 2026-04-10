from functools import lru_cache

# Varsayılan değer (Tanımlanmamış çiftler için):
DEFAULT_MISMATCH_SCORE = 0.0 
# Changed to set for O(1) lookups during sequence extraction
TUM_UNLULER = {"a", "e", "o", "ö", "u", "ü", "ı", "i"}

VOWEL_SCORES = {
    'a': {'e': 0.9, 'ı': 0.8, 'i': 0.7,'u': 0.6,'ü': 0.5,'o': 0.4, 'ö': 0.3 }, 
    'e': {'a': 0.9, 'i': 0.8, 'ı': 0.7,'ü': 0.6,'u': 0.5,'ö': 0.4, 'o': 0.3 },   
    'ı': {'i': 0.9, 'u': 0.8, 'ü': 0.7,'e': 0.6,'o': 0.5,'a': 0.4, 'ö': 0.3 },
    'i': {'ı': 0.9, 'ü': 0.8, 'u': 0.7,'a': 0.6,'ö': 0.5,'e': 0.4, 'o': 0.3 },
    'o': {'ö': 0.9, 'u': 0.8, 'ü': 0.7,'ı': 0.6,'i': 0.5,'a': 0.4, 'e': 0.3 },
    'ö': {'o': 0.9, 'ü': 0.8, 'u': 0.7,'i': 0.6,'ı': 0.5,'e': 0.4, 'a': 0.3 },
    'u': {'ü': 0.9, 'ı': 0.8, 'i': 0.7,'o': 0.6,'ö': 0.5,'a': 0.4, 'e': 0.3 },
    'ü': {'u': 0.9, 'i': 0.8, 'ı': 0.7,'ö': 0.6,'o': 0.5,'e': 0.4, 'a': 0.3 },
}


"DOR"


# ÜNSÜZLER ARASI PUANLAMA (Örnekleri çoğaltmalısın)
CONSONANT_SCORES = {
    # --- Dudak Ünsüzleri Grubu (b, p, v, f) ---
    'b': {'p': 0.9, 'v': 0.6, 'f': 0.3}, 
    'p': {'b': 0.9, 'v': 0.6, 'f': 0.3,"k":0.3 ,"t":0.3 }, 
    'v': {'b': 0.9, 'p': 0.6, 'f': 0.3}, 
    'f': {'v': 0.9, 'b': 0.6, 'p': 0.3}, 

    # --- C/Ç Grubu ---
    'c': {'ç': 0.9, "j":0.4}, 
    'ç': {'c': 0.9, "t":0.4}, 

    # --- D/T Grubu ---
    'd': {'t': 0.9, "y":0.4}, 
    't': {'d': 0.9, "ç":0.4 ,"k":0.3 ,"p":0.3 }, 

    # --- Yumuşak/Sert Damak Grubu (g, k, h, ğ) ---
    'g': {'k': 0.9, 'h': 0.9, 'ğ': 0.9}, 
    'k': {'g': 0.9, 'h': 0.9, 'ğ': 0.9,"t":0.3 ,"p":0.3 }, 
    'h': {'g': 0.9, 'k': 0.9, 'ğ': 0.9}, 
    'ğ': {'g': 0.9, 'k': 0.9, 'h': 0.9}, 

    # --- M/N Grubu ---
    'm': {'n': 0.9}, 
    'n': {'m': 0.9}, 

    # --- S/Ş/Z Grubu ---
    's': {'ş': 0.9, 'z': 0.9}, 
    'ş': {'s': 0.9, 'z': 0.9}, 
    'z': {'s': 0.9, 'ş': 0.9}, 

    # --- Tekil Kalanlar (Kendi grupları yok) ---
    'j': {"c": 0.8}, 
    'r': {}, 
    'y': {}, 
    'l': {}
}

def get_similarity_ratio(char1, char2, matrix):
    """
    İki harf arasındaki benzerlik oranını (0.0 - 1.0) döner.
    """
    if char1 == char2:
        return 1.0 
    
    if char1 in matrix and char2 in matrix[char1]:
        return matrix[char1][char2]
    
    if char2 in matrix and char1 in matrix[char2]:
        return matrix[char2][char1]
        
    return DEFAULT_MISMATCH_SCORE

def extract_chars(word, is_vowel_mode):
    """Kelimenin sadece ünlülerini veya sadece ünsüzlerini liste olarak döner."""
    if is_vowel_mode:
        return [c for c in word if c in TUM_UNLULER]
    else:
        return [c for c in word if c not in TUM_UNLULER and c.isalpha()]

def calculate_sequence_similarity(list1, list2, score_matrix):
    """
    İki listeyi (ünlüler veya ünsüzler) sırasıyla karşılaştırır.
    Puanlama: (Eşleşme Puanı) * (100 / Maksimum Harf Sayısı)
    """
    len1 = len(list1)
    len2 = len(list2)
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 0.0 
    
    point_per_char = 100.0 / max_len
    total_score = 0.0
    
    for i in range(max_len):
        c1 = list1[i] if i < len1 else None
        c2 = list2[i] if i < len2 else None
        
        if c1 and c2:
            ratio = get_similarity_ratio(c1, c2, score_matrix)
            total_score += ratio * point_per_char
        else:
            pass 
            
    return total_score

@lru_cache(maxsize=100000)
def sesli_benzerlik(ana_kelime, yeni_kelime):
    v1 = extract_chars(ana_kelime, is_vowel_mode=True)
    v2 = extract_chars(yeni_kelime, is_vowel_mode=True)
    return calculate_sequence_similarity(v1, v2, VOWEL_SCORES)

@lru_cache(maxsize=100000)
def sessiz_benzerlik(ana_kelime, yeni_kelime):
    c1 = extract_chars(ana_kelime, is_vowel_mode=False)
    c2 = extract_chars(yeni_kelime, is_vowel_mode=False)
    return calculate_sequence_similarity(c1, c2, CONSONANT_SCORES)

def benzerlik(ana_kelime, yeni_kelime):
    len1 = len(ana_kelime)
    len2 = len(yeni_kelime)
    if len1 == 0 or len2 == 0:
        return 0.0
    if len1 <= len2:
        uzunluk_oranı = len1 / len2
    else:
        uzunluk_oranı = len2 / len1

    return uzunluk_oranı * (sesli_benzerlik(ana_kelime, yeni_kelime) * 0.6 + sessiz_benzerlik(ana_kelime, yeni_kelime) * 0.4)


if __name__ == "__main__":
    kelime1 = "çakıl"
    kelime2 = "yakın"
    
    print(f"'{kelime1}' ve '{kelime2}' arasındaki sesli benzerlik: {sesli_benzerlik(kelime1, kelime2)}")
    print(f"'{kelime1}' ve '{kelime2}' arasındaki sessiz benzerlik: {sessiz_benzerlik(kelime1, kelime2)}")
    print(f"'{kelime1}' ve '{kelime2}' arasındaki toplam benzerlik: {benzerlik(kelime1, kelime2)}")