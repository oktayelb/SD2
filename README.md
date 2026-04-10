# Turkish Phonetic Word Generator & Morphological Analyzer

This project is a computational linguistics pipeline designed to generate phonetically similar variations of a given Turkish word (or non-word) and evaluate them based on morphological validity and phonetic proximity. 

It takes an input string, abstracts it into phonetic groups, introduces controlled mutations (insertions and substitutions), reconstructs possible valid Turkish words, and ranks them against the original input.

## Architecture and Pipeline

The system operates in a multi-stage pipeline across three main modules:

### 1. Phonetic Abstraction & Mutation (`harfkumeler.py`)
* **Encoding (`harfkumele`)**: The input word is translated into a base "Harfküme Kodu". Characters are grouped by phonetic similarity (e.g., `b, p, v, f` become `B`; `g, k, ğ, h` become `G`). The first letter is capitalized to preserve initial consonant properties.
* **Mutation (`başkabiçimler`)**: The pipeline generates variations of this base code. It introduces wildcards (`X` for consonants, `@` for vowels) through systematic substitutions and insertions.
* **Phonotactic Pruning (`sacma`)**: Early-stage filtering discards abstract codes that violate basic Turkish phonotactics (e.g., three consecutive consonants, impossible initial clusters like starting with L/M/R).
* **Decoding (`harfkumeden_kelimeler`)**: The surviving abstract codes are expanded back into raw letter combinations using a Cartesian product of all possible letters in each phonetic group.

### 2. Morphological Validation (`harfkumeler.py` & `util/decomposer.py`)
* **Root & Vowel Harmony Detection (`anlambirimli`)**: Scans the raw combinations for recognizable substrings (roots) and tracks vowel harmony shifts (front vs. back vowels). It stylizes the output by capitalizing identified meaningful roots.
* **Grammatical Verification (`yasal_olanlar`)**: Uses the external `util.decomposer` to verify if the candidate word strictly adheres to Turkish morphology (a valid root followed by a legal suffix chain).

### 3. Similarity Scoring & Ranking (`benzerlik.py` & `main.py`)
* **Sequence Extraction (`extract_chars`)**: Splits words into separate vowel and consonant streams.
* **Matrix Scoring (`calculate_sequence_similarity`)**: Compares the streams index-by-index. It relies on predefined, weighted phonetic distance matrices (`VOWEL_SCORES`, `CONSONANT_SCORES`)—for instance, matching 'b' and 'p' yields a high score (0.9), while 'b' and 'f' yields a lower score (0.3).
* **Final Calculation (`benzerlik`)**: Combines the vowel score (60% weight) and consonant score (40% weight), penalized by the length ratio of the two words.
* **Output Matrix (`main.py`)**: The candidates are sorted primarily by whether the identified root is at the beginning of the word, and secondarily by their similarity score, outputting a detailed morphological breakdown for the top valid candidates.

## Directory Structure
* `main.py`: CLI entry point and orchestration.
* `generative_approach/`: Contains the core generation logic (`harfkumeler.py`) and scoring algorithms (`benzerlik.py`).
* `util/`: Contains the morphological decomposition engine (`decomposer.py`) and suffix rules.
* `data/`: Houses the foundational Turkish word lists used for root validation.