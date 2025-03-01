import os
import re
from werkzeug.utils import secure_filename

# Configuration constants
def get_app_dirs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'VOCAB_DIR': os.path.join(base_dir, 'vocabulary_books'),
        'ATTACHMENT_DIR': os.path.join(base_dir, 'attachment'),
        'EPUB_DIR': os.path.join(base_dir, 'epub')
    }

# Create necessary directories
def create_directories():
    dirs = get_app_dirs()
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    return dirs

# File upload settings
ALLOWED_EXTENSIONS = {'epub'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_timestamp_filename(base_name, extension):
    """Generate a filename with timestamp"""
    import time
    timestamp = int(time.time())
    safe_name = secure_filename(base_name)
    return f"{safe_name}_{timestamp}.{extension}"

def extract_english_words(text):
    """Extract English words from text"""
    # Regular expression to match English words
    # Including contractions and hyphenated words
    pattern = r'\b[a-zA-Z]+-?[a-zA-Z]*\'?[a-zA-Z]*\b'
    words = re.findall(pattern, text)
    
    # Convert to lowercase and remove duplicates
    unique_words = list(set([word.lower() for word in words]))
    
    # Sort the words alphabetically
    unique_words.sort()
    
    return unique_words
