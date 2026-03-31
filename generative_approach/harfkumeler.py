import itertools
from util.word_methods import exists, BACK_VOWELS, FRONT_VOWELS
from util.decomposer import decompose

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
    "g": "g", "k": "g", "ğ": "g", "h": "g",
    "l": "l",
    "m": "m", "n": "m",
    "r": "r",
    "s": "s", "ş": "s", "z": "s",
    "y": "y"
}

# =============================================================================
#  BÖLÜM 2: OUTPUT TABLE (Harfküme Kodu -> Olası Gerçek Harfler)
# =============================================================================

TUM_UNLULER = ["a", "e", "o", "ö", "u", "ü", "ı", "i"]

TUM_ARAUNSUZLER = [
    "b", "c", "ç", "d", "g", "ğ", "h", "f", "k",
    "l", "m", "n", "p", "r", "s", "ş", "t", "v", "y", "z"
]
TUM_BASUNSUZLER = [
    "b", "c", "ç", "d", "f", "g", "h", "k",
    "p", "s", "ş", "t", "v", "y"
]

CODE_TO_REAL_CHARS = {
    "A": ["a", "e"],        "a": ["a", "e"],
    "O": ["o", "ö"],        "o": ["o", "ö"],
    "U": ["u", "ü"],        "u": ["u", "ü"],
    "I": ["ı", "i"],        "ı": ["ı", "i"],
    
    "B": ["b", "p", "v", "f"],
    "C": ["c", "ç"],
    "D": ["d", "t"],
    "G": ["g", "k", "h"],
    "L": ["l"],
    "M": ["m", "n"],
    "R": ["r"],
    "S": ["s", "ş"],
    "Y": ["y"],

    "b": ["b", "p", "v"],
    "c": ["c", "ç"],
    "d": ["d", "t"],
    "g": ["g", "k", "ğ", "h"],
    "l": ["l"],
    "m": ["m", "n"],
    "r": ["r"],
    "s": ["s", "ş", "z"],
    "y": ["y"],

    "@": TUM_UNLULER,
    "X": TUM_BASUNSUZLER,
    "x": TUM_ARAUNSUZLER
}

VOWEL_CODES = {"a", "o", "u", "ı", "A", "O", "U", "I", "@"}

# =============================================================================
#  BÖLÜM 3: MİMARİNİN KALBİ (FİLTRE) ve FONKSİYONLAR
# =============================================================================

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

def generate_insertions(base_code):
    """Insert X and @ at every position (0..n). Position 0 uses uppercase."""
    results = set()
    n = len(base_code)
    for i in range(n + 1):
        for wildcard in ("X", "@"):
            if i == 0:
                new = wildcard + base_code[0].lower() + base_code[1:]
            else:
                new = base_code[:i] + wildcard.lower() + base_code[i:]
            results.add(new)
    return results

def generate_substitutions(base_code):
    """Replace each char with X (or @ if the char is a vowel). Position 0 uses uppercase."""
    results = set()
    n = len(base_code)
    for i in range(n):
        replacement = "@" if base_code[i] in VOWEL_CODES else "X"
        if i == 0:
            new = replacement + base_code[1:]
        else:
            new = base_code[:i] + replacement.lower() + base_code[i+1:]
        results.add(new)
    return results

def generate_combinations(base_code):
    """Apply each substitution, then each insertion on the substituted result."""
    results = set()
    for sub in generate_substitutions(base_code):
        results.update(generate_insertions(sub))
    return results

def başkabiçimler(base_code):
    final_varyasyonlar = {base_code}
    final_varyasyonlar.update(generate_insertions(base_code))
    final_varyasyonlar.update(generate_substitutions(base_code))
    final_varyasyonlar.update(generate_combinations(base_code))
    return list(final_varyasyonlar)

def sacma(harfkume_str: str) -> bool:
    if not harfkume_str: return True
    n = len(harfkume_str)
    def is_consonant(c): return c not in VOWEL_CODES
    def is_vowel(c): return c in VOWEL_CODES

    if n >= 2 and is_consonant(harfkume_str[0]) and is_consonant(harfkume_str[1]): return True
    if n >= 3 and is_consonant(harfkume_str[-1]) and is_consonant(harfkume_str[-2]): return True
    if n >= 2 and is_vowel(harfkume_str[0]) and is_vowel(harfkume_str[1]): return True
    if n >= 2 and is_vowel(harfkume_str[-1]) and is_vowel(harfkume_str[-2]): return True

    consecutive_consonants = 0
    for char in harfkume_str:
        if is_consonant(char):
            consecutive_consonants += 1
            if consecutive_consonants > 3: return True
        else:
            consecutive_consonants = 0 

    if harfkume_str[0] in ["L","M","R"]: return True
    return False

def anlambirimli(kelime):
    """
    Returns (True, "StyledWord") or (False, "original").
    """
    shift_count = 0
    last_group = None 

    for char in kelime:
        current_group = None
        if char in FRONT_VOWELS: current_group = 'F'
        elif char in BACK_VOWELS: current_group = 'B'
        
        if current_group:
            if last_group is None: last_group = current_group
            elif current_group != last_group:
                shift_count += 1
                last_group = current_group

    target_hits = shift_count + 1
    found_hits = 0
    uzunluk = len(kelime)
    is_part_of_hit = [False] * uzunluk

    for i in range(uzunluk):
        for j in range(i + 1, uzunluk + 1):
            parca = kelime[i:j]
            if exists(parca):
                found_hits += 1
                for k in range(i, j): is_part_of_hit[k] = True
                
                if found_hits >= target_hits:
                    vurgulu_kelime = ""
                    for idx, char in enumerate(kelime):
                        if is_part_of_hit[idx]: vurgulu_kelime += char.upper()
                        else: vurgulu_kelime += char
                    return True, vurgulu_kelime

    return False, kelime

def harfkumeden_kelimeler(harfkume_str):
    possible_chars_list = []
    for code in harfkume_str:
        chars = CODE_TO_REAL_CHARS.get(code)
        if chars: possible_chars_list.append(chars)
        else: possible_chars_list.append([code])
    return ("".join(c) for c in itertools.product(*possible_chars_list))


def sesdenkler(word):
    print(f"\n{'='*40}\nANALYZING: {word}\n{'='*40}")

    raw_kume = harfkumele(word)
    print(f"1. Main Harfkume Version: {raw_kume}")
    
    tum_varyasyonlar = başkabiçimler(raw_kume)
    print(f"2. Baskabicimler Versions: {tum_varyasyonlar}")
    print("-" * 40)
    
    # Store tuples: (raw_word, styled_word)
    gecerli_sonuclar = set()
    
    for kod in tum_varyasyonlar:
        if sacma(kod):
            continue 
            
        olasi_kelimeler = harfkumeden_kelimeler(kod)
        
        for aday_kelime in olasi_kelimeler:
            is_valid, styled_word = anlambirimli(aday_kelime)
            
            if is_valid:
                gecerli_sonuclar.add((aday_kelime, styled_word))
                
    return list(gecerli_sonuclar) 

def yasal_olanlar(liste):
    """
    Input: List of tuples (raw, styled)
    Output: List of tuples (raw, styled, analyses_list)
    """
    valid_results = []
    for raw, styled in liste:
        analyses = decompose(raw)
        if analyses:
            # analyses is a list of tuples: (root, type, chain, pos)
            valid_results.append((raw, styled, analyses))
    return valid_results