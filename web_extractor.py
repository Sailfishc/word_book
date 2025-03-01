import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils import get_app_dirs, get_timestamp_filename, extract_english_words

# Get directories
ATTACHMENT_DIR = get_app_dirs()['ATTACHMENT_DIR']

def extract_words_from_webpage(url):
    """Extract English words from a webpage"""
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract text content and remove HTML tags
        text = soup.get_text()
        
        # Extract unique English words
        words = extract_english_words(text)
        
        return words
    except Exception as e:
        print(f"Error extracting words from webpage: {e}")
        return []

def extract_words_from_html(html_content):
    """Extract English words from HTML content"""
    try:
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract text content and remove HTML tags
        text = soup.get_text()
        
        # Extract unique English words
        words = extract_english_words(text)
        
        return words
    except Exception as e:
        print(f"Error extracting words from HTML: {e}")
        return []

def save_webpage_words(url, words):
    """Save extracted words to a file in the attachment folder"""
    try:
        # Get domain from URL for filename
        domain = urlparse(url).netloc
        if not domain:
            domain = "unknown_domain"
        
        # Create a filename with timestamp
        filename = get_timestamp_filename(domain, "txt")
        file_path = os.path.join(ATTACHMENT_DIR, filename)
        
        # Save words to file
        with open(file_path, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f"{word}\n")
        
        return filename
    except Exception as e:
        print(f"Error saving webpage words: {e}")
        return None
