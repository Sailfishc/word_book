import os
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from utils import get_app_dirs, get_timestamp_filename, extract_english_words

# Get directories
ATTACHMENT_DIR = get_app_dirs()['ATTACHMENT_DIR']
EPUB_DIR = get_app_dirs()['EPUB_DIR']

def parse_epub_file(epub_path):
    """Parse an EPUB file and extract words"""
    try:
        # Create a temporary directory to extract the EPUB contents
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the EPUB file (which is just a ZIP archive)
            with zipfile.ZipFile(epub_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the content files
            all_text = ""
            
            # First, try to find content.opf
            opf_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.opf'):
                        opf_files.append(os.path.join(root, file))
            
            # If we found an OPF file, use it to locate the content files
            content_files = []
            if opf_files:
                for opf_file in opf_files:
                    try:
                        tree = ET.parse(opf_file)
                        root = tree.getroot()
                        
                        # Find the namespace
                        ns = {'opf': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                        
                        # Find all items
                        for item in root.findall('.//{{{0}}}item'.format(ns.get('opf', ''))):
                            media_type = item.get('media-type')
                            href = item.get('href')
                            
                            if (media_type and href and 
                                (media_type == 'application/xhtml+xml' or 
                                 media_type == 'text/html')):
                                # Construct the full path to the content file
                                content_path = os.path.join(os.path.dirname(opf_file), href)
                                content_files.append(content_path)
                    except Exception as e:
                        print(f"Error parsing OPF file: {e}")
            
            # If no content files found via OPF, search for HTML/XHTML files directly
            if not content_files:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.html', '.xhtml', '.htm')):
                            content_files.append(os.path.join(root, file))
            
            # Process all content files
            for content_file in content_files:
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    soup = BeautifulSoup(content, 'lxml')
                    all_text += soup.get_text() + " "
                except Exception as e:
                    print(f"Error processing content file {content_file}: {e}")
            
            # Extract words
            words = extract_english_words(all_text)
            return words
    except Exception as e:
        print(f"Error parsing EPUB file: {e}")
        return []

def save_epub_file(uploaded_file):
    """Save an uploaded EPUB file"""
    try:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(EPUB_DIR, filename)
        uploaded_file.save(file_path)
        return file_path, filename
    except Exception as e:
        print(f"Error saving EPUB file: {e}")
        return None, None

def save_epub_words(epub_filename, words):
    """Save extracted words from an EPUB file to a file in the attachment folder"""
    try:
        # Remove the extension from the filename
        base_name = os.path.splitext(epub_filename)[0]
        
        # Create a filename with timestamp
        filename = get_timestamp_filename(base_name, "txt")
        file_path = os.path.join(ATTACHMENT_DIR, filename)
        
        # Save words to file
        with open(file_path, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f"{word}\n")
        
        return filename
    except Exception as e:
        print(f"Error saving EPUB words: {e}")
        return None
