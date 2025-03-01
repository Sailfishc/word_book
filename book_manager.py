import os
from utils import get_app_dirs

# Get the vocabulary books directory
VOCAB_DIR = get_app_dirs()['VOCAB_DIR']

def get_all_books():
    """Get all vocabulary books"""
    books = []
    for file in os.listdir(VOCAB_DIR):
        if file.endswith('.txt'):
            books.append(file[:-4])  # Remove .txt extension
    return books

def get_words_from_book(book_name):
    """Get all words from a vocabulary book"""
    book_path = os.path.join(VOCAB_DIR, f"{book_name}.txt")
    if not os.path.exists(book_path):
        return []
    
    with open(book_path, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def add_word_to_book(book_name, word):
    """Add a single word to a vocabulary book"""
    book_path = os.path.join(VOCAB_DIR, f"{book_name}.txt")
    
    # Check if word already exists
    existing_words = get_words_from_book(book_name)
    if word in existing_words:
        return False
    
    with open(book_path, 'a', encoding='utf-8') as f:
        f.write(f"{word}\n")
    return True

def add_words_to_book(book_name, words):
    """Add multiple words to a vocabulary book"""
    book_path = os.path.join(VOCAB_DIR, f"{book_name}.txt")
    
    # Check for existing words
    existing_words = get_words_from_book(book_name)
    new_words = [word for word in words if word not in existing_words]
    
    if not new_words:
        return 0
    
    with open(book_path, 'a', encoding='utf-8') as f:
        for word in new_words:
            f.write(f"{word}\n")
    return len(new_words)

def create_book(book_name):
    """Create a new vocabulary book"""
    book_path = os.path.join(VOCAB_DIR, f"{book_name}.txt")
    if os.path.exists(book_path):
        return False
    
    with open(book_path, 'w', encoding='utf-8'):
        pass  # Just create an empty file
    return True

def book_exists(book_name):
    """Check if a vocabulary book exists"""
    book_path = os.path.join(VOCAB_DIR, f"{book_name}.txt")
    return os.path.exists(book_path)
