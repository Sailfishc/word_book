"""
English Vocabulary Count Test Module

This module provides functionality to estimate a user's English vocabulary size
based on word frequency data from the COCA (Corpus of Contemporary American English)
word frequency list.

The implementation follows these key principles:
1. Divides the vocabulary into 10 equal frequency bands
2. Selects random words from each band for testing
3. Estimates vocabulary size based on the proportion of known words in each band
"""

import os
import random
import json
import math
from utils import get_app_dirs

# Get directory paths
DIRS = get_app_dirs()
APP_DIR = DIRS.get('APP_DIR', '')
DATA_DIR = os.path.join(APP_DIR, 'data')

# Path to COCA word frequency list
COCA_FILE = os.path.join(DATA_DIR, 'COCA60000.txt')

# Number of frequency bands to divide the word list into
NUM_BANDS = 10

# Total number of words to consider in the COCA list
TOTAL_WORDS = 60000

# Words per band (assuming equal distribution)
WORDS_PER_BAND = TOTAL_WORDS // NUM_BANDS

# Cache for the loaded word list
_word_list = None

def load_word_list():
    """
    Load the COCA word frequency list
    
    Returns:
        list: List of words with their frequency rank
    """
    global _word_list
    
    if _word_list is not None:
        return _word_list
    
    words = []
    
    if os.path.exists(COCA_FILE):
        with open(COCA_FILE, 'r') as f:
            for i, line in enumerate(f):
                word = line.strip()
                if word:  # Skip empty lines
                    words.append({
                        'word': word,
                        'rank': i + 1  # 1-based ranking
                    })
    
    _word_list = words
    return words

def get_frequency_band(rank):
    """
    Determine which frequency band a word belongs to based on its rank
    
    Args:
        rank (int): The frequency rank of the word
        
    Returns:
        int: The frequency band (1-10, where 1 is highest frequency)
    """
    if rank <= 0:
        return 1
        
    band = math.ceil(rank / WORDS_PER_BAND)
    return min(band, NUM_BANDS)  # Ensure we don't exceed NUM_BANDS

def get_band_range(band):
    """
    Get the rank range for a frequency band
    
    Args:
        band (int): The frequency band (1-10)
        
    Returns:
        tuple: (start_rank, end_rank) for the band
    """
    band = max(1, min(band, NUM_BANDS))  # Ensure band is between 1 and NUM_BANDS
    start_rank = (band - 1) * WORDS_PER_BAND + 1
    end_rank = band * WORDS_PER_BAND
    return (start_rank, end_rank)

def get_test_words(session, words_per_band=10):
    """
    Generate a set of test words for a specific test session
    
    Args:
        session (int): Test session number (1-3)
        words_per_band (int): Number of words to select from each band
        
    Returns:
        list: Selected test words with rank and band information
    """
    word_list = load_word_list()
    if not word_list:
        return []
    
    # Divide words into bands
    bands = {}
    for word_data in word_list:
        rank = word_data['rank']
        band = get_frequency_band(rank)
        
        if band not in bands:
            bands[band] = []
        
        bands[band].append(word_data)
    
    # Generate seed based on session for consistent randomization
    random.seed(f"vocab_test_session_{session}")
    
    # Select words for this session
    selected_words = []
    for band in range(1, NUM_BANDS + 1):
        band_words = bands.get(band, [])
        
        # Calculate slice for this session to avoid overlap
        # Each session gets a different slice of words from each band
        total_selections = words_per_band * 3  # 3 sessions
        if len(band_words) >= total_selections:
            start_idx = (session - 1) * words_per_band
            end_idx = start_idx + words_per_band
            session_slice = band_words[start_idx:end_idx]
        else:
            # If we don't have enough words, just randomly select with replacement
            session_slice = random.sample(band_words, min(words_per_band, len(band_words)))
        
        # Add band information to each word
        for word_data in session_slice:
            word_data = word_data.copy()  # Create a copy to avoid modifying the original
            word_data['band'] = band
            selected_words.append(word_data)
    
    # Shuffle the words
    random.shuffle(selected_words)
    
    return selected_words

def calculate_vocab_size(answers):
    """
    Calculate estimated vocabulary size based on test answers
    
    Args:
        answers (dict): User's answers to test questions
        
    Returns:
        dict: Vocabulary size estimate and detailed results by band
    """
    # Initialize counters for each band
    band_stats = {band: {'tested': 0, 'known': 0} for band in range(1, NUM_BANDS + 1)}
    
    # Process answers from all completed sessions
    for session, session_answers in answers.items():
        for word, answer_data in session_answers.items():
            band = answer_data.get('band', 1)
            band_stats[band]['tested'] += 1
            
            if answer_data.get('known', False):
                band_stats[band]['known'] += 1
    
    # Calculate results for each band
    band_results = []
    total_vocab_size = 0
    
    for band, stats in band_stats.items():
        if stats['tested'] > 0:
            # Calculate percentage of known words in this band
            percentage = (stats['known'] / stats['tested']) * 100
            
            # Get the range of ranks for this band
            start_rank, end_rank = get_band_range(band)
            
            # Calculate estimated number of known words in this band
            band_size = WORDS_PER_BAND
            estimated_known = round(band_size * (stats['known'] / stats['tested']))
            
            # Add to total vocabulary size estimate
            total_vocab_size += estimated_known
            
            # Add band results
            band_results.append({
                'band': band,
                'range': f"{start_rank}-{end_rank}",
                'tested': stats['tested'],
                'known': stats['known'],
                'percentage': round(percentage, 1),
                'estimated_known': estimated_known
            })
    
    # Sort band results by band number
    band_results.sort(key=lambda x: x['band'])
    
    return {
        'total_vocab_size': total_vocab_size,
        'band_results': band_results
    }
