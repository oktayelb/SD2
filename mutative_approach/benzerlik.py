import random

# =============================================================================
#  FONETİK MATRİSLER (Ağırlıklı Komşuluklar)
# =============================================================================

# Varsayılan değer (Tanımlanmamış çiftler için)
DEFAULT_SCORE = 0.0

# ÜNLÜLER (VOWELS) - Genişletilmiş ve Simetrik
# Skor ne kadar yüksekse (1.0'a yakın), o harfin o harfe dönüşme ihtimali artar.
VOWEL_SCORES = {
    'a': {'e': 0.6, 'ı': 0.8, 'o': 0.5, 'u': 0.4},
    'e': {'a': 0.6, 'i': 0.8, 'ö': 0.5, 'ü': 0.4},
    'ı': {'i': 0.6, 'a': 0.8, 'u': 0.7},
    'i': {'ı': 0.6, 'e': 0.8, 'ü': 0.7},
    'o': {'ö': 0.8, 'u': 0.7, 'a': 0.5},
    'ö': {'o': 0.8, 'ü': 0.7, 'e': 0.5},
    'u': {'ü': 0.8, 'o': 0.7, 'ı': 0.6},
    'ü': {'u': 0.8, 'ö': 0.7, 'i': 0.6},
}

# ÜNSÜZLER (CONSONANTS) - Dudak, Diş, Damak yakınlıkları
CONSONANT_SCORES = {
    # Dudak (Labials)
    'b': {'p': 0.8, 'm': 0.6, 'v': 0.5},
    'p': {'b': 0.8, 'f': 0.4, 't': 0.2},
    'm': {'n': 0.7, 'b': 0.6},
    'v': {'f': 0.8, 'b': 0.5},
    'f': {'v': 0.8, 'p': 0.4},

    # Diş/Damak (Dentals/Alveolars)
    'd': {'t': 0.9, 'z': 0.3},
    't': {'d': 0.9, 'k': 0.3, 'ç': 0.3},
    'n': {'m': 0.7, 'l': 0.4, 'r': 0.3},
    's': {'ş': 0.8, 'z': 0.7, 'c': 0.3},
    'z': {'s': 0.7, 'j': 0.6, 'd': 0.3},
    'c': {'ç': 0.9, 'j': 0.7, 's': 0.3},
    'ç': {'c': 0.9, 'ş': 0.6, 't': 0.3},
    'j': {'c': 0.7, 'z': 0.6, 'ş': 0.5},
    'ş': {'s': 0.8, 'ç': 0.6, 'j': 0.5},

    # Damak/Gırtlak (Velars/Glottals)
    'g': {'k': 0.9, 'ğ': 0.8, 'y': 0.4},
    'k': {'g': 0.9, 'q': 0.5, 't': 0.3},
    'ğ': {'g': 0.8, 'y': 0.7, 'h': 0.4},
    'h': {'ğ': 0.4, 'k': 0.2},
    'y': {'ğ': 0.7, 'g': 0.4},

    # Akıcılar (Liquids)
    'l': {'n': 0.4, 'r': 0.5},
    'r': {'l': 0.5, 'n': 0.3}
}

def normalize_matrix(matrix):
    """
    Matrisi simetrik hale getirir. 
    Eğer A->B tanımlı ama B->A değilse, B->A'yı ekler.
    """
    keys = list(matrix.keys())
    for k1 in keys:
        for k2, score in matrix[k1].items():
            if k2 not in matrix:
                matrix[k2] = {}
            if k1 not in matrix[k2]:
                matrix[k2][k1] = score
    return matrix

# Başlangıçta matrisleri normalize et
VOWEL_SCORES = normalize_matrix(VOWEL_SCORES)
CONSONANT_SCORES = normalize_matrix(CONSONANT_SCORES)

def get_weighted_candidate(char, is_vowel, mutation_strength=1.0):
    """
    Bir harf için ağırlıklı rastgele bir benzer harf seçer.
    mutation_strength: 1.0 normal, daha yüksek değerler daha uzak harfleri seçebilir.
    """
    matrix = VOWEL_SCORES if is_vowel else CONSONANT_SCORES
    
    # Harf matriste yoksa kendisini döndür
    if char not in matrix:
        return char

    candidates = list(matrix[char].keys())
    weights = list(matrix[char].values())
    
    # Orijinal harfi de listeye ekle (Değişmeme ihtimali)
    # Skorlar 0-1 arası olduğu için, değişmeme ihtimalini 
    # (1.0 / mutation_strength) gibi bir mantıkla yönetebiliriz.
    candidates.append(char)
    # Orijinal harfin ağırlığı: Diğerlerinin toplamından biraz yüksek olsun ki çok bozulmasın
    keep_prob = max(1.0, sum(weights)) * (1.5 / mutation_strength)
    weights.append(keep_prob)
    
    # Seçim yap
    return random.choices(candidates, weights=weights, k=1)[0]

def get_similarity_ratio(char1, char2, matrix):
    if char1 == char2: return 1.0
    if char1 in matrix and char2 in matrix[char1]:
        return matrix[char1][char2]
    return 0.0