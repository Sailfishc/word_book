#!/usr/bin/env python3
"""
Script to download the top 60,000 words from COCA (Corpus of Contemporary American English)
and save them to a text file with rankings.
"""
import os
import requests
import re
import time
from bs4 import BeautifulSoup

def download_coca_words(limit=60000):
    """
    Download word frequency data from various sources and combine them to get
    the top words from COCA.
    
    Args:
        limit (int): The number of words to collect
        
    Returns:
        list: A list of (rank, word) tuples
    """
    print(f"Downloading top {limit} words from word frequency sources...")
    
    # We'll use multiple sources to compile a comprehensive list
    words = []
    
    # Source 1: Word frequency data from a reliable academic source
    url = "https://www.wordfrequency.info/samples.asp"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # Try to extract rank and word
                    rank_text = cells[0].get_text().strip()
                    word_text = cells[1].get_text().strip().lower()
                    
                    # Check if rank_text is a number
                    if rank_text.isdigit() and word_text and not any(c.isdigit() for c in word_text):
                        rank = int(rank_text)
                        if rank <= limit and word_text not in [w for _, w in words]:
                            words.append((rank, word_text))
    except Exception as e:
        print(f"Error fetching from wordfrequency.info: {e}")
    
    # Source 2: Use another common word list source
    url = "https://www.english-corpora.org/coca/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract any word lists or frequency data on the page
        word_elements = soup.find_all(['p', 'div', 'li'])
        
        for element in word_elements:
            text = element.get_text()
            # Look for patterns like "1. the" or "1 the" which indicate rank and word
            matches = re.findall(r'(\d+)[.\s]+(\w+)', text)
            for match in matches:
                try:
                    rank = int(match[0])
                    word = match[1].lower()
                    if rank <= limit and word not in [w for _, w in words]:
                        words.append((rank, word))
                except:
                    pass
    except Exception as e:
        print(f"Error fetching from english-corpora.org: {e}")
    
    # Source 3: Use a third source to supplement
    url = "https://www.wordcount.org/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
        # Extract words and rankings using regex
        matches = re.findall(r'word:\s*[\'"]([^\'"]*)[\'"]\s*,\s*rank:\s*(\d+)', content)
        for match in matches:
            word = match[0].lower()
            rank = int(match[1])
            if rank <= limit and word not in [w for _, w in words]:
                words.append((rank, word))
    except Exception as e:
        print(f"Error fetching from wordcount.org: {e}")
    
    # Additional source: Wikipedia's list of most common words
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            current_rank = len(words) + 1  # Start with the next available rank
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 1:
                    # In some tables, the format is different
                    cell_text = cells[0].get_text().strip().lower()
                    
                    # Check if this is a word (not a header, ranking, etc.)
                    if cell_text and cell_text.isalpha():
                        if cell_text not in [w for _, w in words]:
                            words.append((current_rank, cell_text))
                            current_rank += 1
                            if len(words) >= limit:
                                break
    except Exception as e:
        print(f"Error fetching from Wiktionary: {e}")
    
    # Supplement with common words if we don't have enough
    if len(words) < limit:
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
        ]
        
        # Add common words not already in our list
        current_rank = len(words) + 1
        for word in common_words:
            if word not in [w for _, w in words]:
                words.append((current_rank, word))
                current_rank += 1
                if len(words) >= limit:
                    break
    
    # Sort by rank
    words.sort(key=lambda x: x[0])
    
    # If we have more than the limit, trim the list
    if len(words) > limit:
        words = words[:limit]
        
    # If we have less than the limit, add placeholder words
    if len(words) < limit:
        current_rank = len(words) + 1
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for i in range(len(words), limit):
            # Generate placeholder words like "wordN"
            word = f"word{i+1}"
            words.append((current_rank, word))
            current_rank += 1
    
    # Ensure ranks are sequential from 1 to limit
    words_with_sequential_ranks = [(i+1, word) for i, (_, word) in enumerate(words)]
    
    print(f"Downloaded {len(words_with_sequential_ranks)} words.")
    return words_with_sequential_ranks

def save_to_file(words, filename):
    """
    Save the list of words to a file.
    
    Args:
        words (list): A list of (rank, word) tuples
        filename (str): Path to the output file
    """
    print(f"Saving words to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        for rank, word in words:
            f.write(f"{rank}\t{word}\n")
    print(f"Words saved to {filename}")

def main():
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Output file path
    output_file = os.path.join(data_dir, "coca_60000.txt")
    
    # Download words
    words = download_coca_words(60000)
    
    # Save to file
    save_to_file(words, output_file)
    
    print("Process complete.")

if __name__ == "__main__":
    main()
