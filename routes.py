from flask import Blueprint, request, jsonify, render_template, send_from_directory, session
import os
import uuid
from utils import allowed_file, get_app_dirs
from book_manager import (get_all_books, get_words_from_book, 
                        add_word_to_book, add_words_to_book, 
                        create_book, book_exists, mark_word_as_done, get_done_words)
from web_extractor import extract_words_from_webpage, save_webpage_words
from epub_processor import parse_epub_file, save_epub_file, save_epub_words
from vocab_assessment import VocabularyAssessment, generate_adaptive_test, get_next_adaptive_question
from vocab_count_test import get_test_words, calculate_vocab_size

# Get directory paths
DIRS = get_app_dirs()
VOCAB_DIR = DIRS['VOCAB_DIR']
ATTACHMENT_DIR = DIRS['ATTACHMENT_DIR']
EPUB_DIR = DIRS['EPUB_DIR']

# Create a Blueprint for API routes
bp = Blueprint('vocabulary', __name__)

# Web routes
@bp.route('/')
def index():
    """Render the main application page"""
    books = get_all_books()
    return render_template('index.html', books=books)

@bp.route('/assessment')
def assessment():
    """Render the vocabulary assessment page"""
    return render_template('assessment.html')

@bp.route('/vocab_test')
def vocab_test():
    """Render the vocabulary count test page"""
    return render_template('vocab_test.html')

# API endpoints for vocabulary book management
@bp.route('/api/books', methods=['GET'])
def get_books():
    """API endpoint to get all vocabulary books"""
    books = get_all_books()
    return jsonify({
        'status': 'success',
        'books': books
    })

@bp.route('/api/books', methods=['POST'])
def create_new_book():
    """API endpoint to create a new vocabulary book"""
    data = request.get_json()
    if not data or 'book_name' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Book name is required'
        }), 400
    
    book_name = data['book_name']
    if create_book(book_name):
        return jsonify({
            'status': 'success',
            'message': f'Book "{book_name}" created successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Book "{book_name}" already exists'
        }), 400

@bp.route('/api/books/<book_name>', methods=['GET'])
def get_book(book_name):
    """API endpoint to get words from a vocabulary book"""
    words = get_words_from_book(book_name)
    return jsonify({
        'status': 'success',
        'book_name': book_name,
        'word_count': len(words),
        'words': words
    })

@bp.route('/api/books/<book_name>/words', methods=['POST'])
def add_word(book_name):
    """API endpoint to add a word to a vocabulary book"""
    data = request.get_json()
    if not data or 'word' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Word is required'
        }), 400
    
    word = data['word']
    if not book_exists(book_name):
        return jsonify({
            'status': 'error',
            'message': f'Book "{book_name}" does not exist'
        }), 404
    
    if add_word_to_book(book_name, word):
        return jsonify({
            'status': 'success',
            'message': f'Word "{word}" added to "{book_name}" successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Word "{word}" already exists in "{book_name}"'
        }), 400

@bp.route('/api/books/<book_name>/words/batch', methods=['POST'])
def add_words_batch(book_name):
    """API endpoint to add multiple words to a vocabulary book"""
    data = request.get_json()
    if not data or 'words' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Words are required'
        }), 400
    
    words = data['words']
    if not book_exists(book_name):
        return jsonify({
            'status': 'error',
            'message': f'Book "{book_name}" does not exist'
        }), 404
    
    word_count = add_words_to_book(book_name, words)
    return jsonify({
        'status': 'success',
        'message': f'{word_count} new words added to "{book_name}" successfully'
    })

# API endpoints for web content extraction
@bp.route('/api/extract-webpage', methods=['POST'])
def extract_webpage():
    """API endpoint to extract words from a webpage"""
    print("extract_webpage called")
    data = request.form
    print(f"Request form data: {data}")
    if not data or 'url' not in data:
        print("URL is missing in the request")
        return jsonify({
            'status': 'error',
            'message': 'URL is required'
        }), 400
    
    url = data['url']
    print(f"Extracting words from URL: {url}")
    words = extract_words_from_webpage(url)
    print(f"Extracted {len(words)} words")
    
    if not words:
        return jsonify({
            'status': 'error',
            'message': 'No words could be extracted from the webpage'
        }), 400
    
    # Save words to a file
    filename = save_webpage_words(url, words)
    
    if filename is None:
        return jsonify({
            'status': 'error',
            'message': 'Error saving extracted words to file'
        }), 500
    
    return jsonify({
        'status': 'success',
        'message': f'{len(words)} words extracted and saved to "{filename}"',
        'filename': filename,
        'word_count': len(words),
        'words': words[:20] if len(words) > 20 else words  # Send only the first 20 words
    })

@bp.route('/api/extract-to-book', methods=['POST'])
def extract_to_book():
    """API endpoint to extract words from a webpage and add them to a vocabulary book"""
    data = request.form
    if not data or 'url' not in data or 'book_name' not in data:
        return jsonify({
            'status': 'error',
            'message': 'URL and book name are required'
        }), 400
    
    url = data['url']
    book_name = data['book_name']
    
    if not book_exists(book_name):
        return jsonify({
            'status': 'error',
            'message': f'Book "{book_name}" does not exist'
        }), 404
    
    words = extract_words_from_webpage(url)
    
    if not words:
        return jsonify({
            'status': 'error',
            'message': 'No words could be extracted from the webpage'
        }), 400
    
    # Save words to a file
    filename = save_webpage_words(url, words)
    
    if filename is None:
        return jsonify({
            'status': 'error',
            'message': 'Error saving extracted words to file'
        }), 500
    
    # Add words to the vocabulary book
    word_count = add_words_to_book(book_name, words)
    
    return jsonify({
        'status': 'success',
        'message': f'{len(words)} words extracted, {word_count} new words added to "{book_name}"',
        'filename': filename,
        'word_count': len(words),
        'new_word_count': word_count,
        'words': words[:20] if len(words) > 20 else words  # Send only the first 20 words
    })

# API endpoints for EPUB processing
@bp.route('/api/upload-epub', methods=['POST'])
def upload_epub():
    """API endpoint to upload and process an EPUB file"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part'
        }), 400
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file'
        }), 400
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        epub_path, epub_filename = save_epub_file(file)
        
        if not epub_path or not epub_filename:
            return jsonify({
                'status': 'error',
                'message': 'Error saving the uploaded file'
            }), 500
        
        # Parse the EPUB file to extract words
        words = parse_epub_file(epub_path)
        
        if not words:
            return jsonify({
                'status': 'error',
                'message': 'No words could be extracted from the EPUB file'
            }), 400
        
        # Save the extracted words to a file
        filename = save_epub_words(epub_filename, words)
        
        if filename is None:
            return jsonify({
                'status': 'error',
                'message': 'Error saving extracted words to file'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': f'{len(words)} words extracted and saved to "{filename}"',
            'filename': filename,
            'word_count': len(words),
            'words': words[:20] if len(words) > 20 else words  # Send only the first 20 words
        })
    
    return jsonify({
        'status': 'error',
        'message': 'File type not allowed. Please upload an EPUB file.'
    }), 400

@bp.route('/api/epub-to-book', methods=['POST'])
def epub_to_book():
    """API endpoint to extract words from an EPUB file and add them to a vocabulary book"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part'
        }), 400
    
    if 'book_name' not in request.form:
        return jsonify({
            'status': 'error',
            'message': 'Book name is required'
        }), 400
    
    book_name = request.form['book_name']
    
    if not book_exists(book_name):
        return jsonify({
            'status': 'error',
            'message': f'Book "{book_name}" does not exist'
        }), 404
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file'
        }), 400
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        epub_path, epub_filename = save_epub_file(file)
        
        if not epub_path or not epub_filename:
            return jsonify({
                'status': 'error',
                'message': 'Error saving the uploaded file'
            }), 500
        
        # Parse the EPUB file to extract words
        words = parse_epub_file(epub_path)
        
        if not words:
            return jsonify({
                'status': 'error',
                'message': 'No words could be extracted from the EPUB file'
            }), 400
        
        # Save the extracted words to a file
        filename = save_epub_words(epub_filename, words)
        
        if filename is None:
            return jsonify({
                'status': 'error',
                'message': 'Error saving extracted words to file'
            }), 500
        
        # Add words to the vocabulary book
        word_count = add_words_to_book(book_name, words)
        
        return jsonify({
            'status': 'success',
            'message': f'{len(words)} words extracted, {word_count} new words added to "{book_name}"',
            'filename': filename,
            'word_count': len(words),
            'new_word_count': word_count,
            'words': words[:20] if len(words) > 20 else words  # Send only the first 20 words
        })
    
    return jsonify({
        'status': 'error',
        'message': 'File type not allowed. Please upload an EPUB file.'
    }), 400

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the uploaded files"""
    return send_from_directory(EPUB_DIR, filename)


# API endpoints for vocabulary assessment

# API endpoints for vocabulary count test
@bp.route('/api/vocab_test/words', methods=['GET'])
def get_vocab_test_words():
    """API endpoint to get words for vocabulary count test"""
    session_num = request.args.get('session', '1')
    
    try:
        session_num = int(session_num)
        if session_num < 1 or session_num > 3:
            return jsonify({
                'status': 'error',
                'message': 'Session number must be between 1 and 3'
            }), 400
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid session number'
        }), 400
    
    # Get test words for this session
    test_words = get_test_words(session_num)
    
    return jsonify({
        'status': 'success',
        'words': test_words,
        'session': session_num
    })

@bp.route('/api/vocab_test/calculate', methods=['POST'])
def calculate_vocab_test_results():
    """API endpoint to calculate vocabulary size estimate"""
    data = request.get_json()
    
    if not data or 'answers' not in data:
        return jsonify({
            'status': 'error',
            'message': 'No answers provided'
        }), 400
    
    # Calculate vocabulary size estimate
    results = calculate_vocab_size(data['answers'])
    
    return jsonify({
        'status': 'success',
        'results': results
    })

# API endpoints for managing done words
@bp.route('/api/words/done', methods=['POST'])
def mark_done():
    """API endpoint to mark a word as done (recognized)"""
    data = request.get_json()
    if not data or 'word' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Word is required'
        }), 400
    
    word = data['word']
    
    # Get list of books that contain this word (for response info)
    books_containing_word = []
    all_books = get_all_books()
    for book in all_books:
        if book != 'done' and word in get_words_from_book(book):
            books_containing_word.append(book)
    
    if mark_word_as_done(word):
        return jsonify({
            'status': 'success',
            'message': f'Word "{word}" marked as done successfully',
            'removed_from_books': books_containing_word
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Word "{word}" is already marked as done'
        }), 400

@bp.route('/api/words/done', methods=['GET'])
def get_done():
    """API endpoint to get all words marked as done"""
    words = get_done_words()
    return jsonify({
        'status': 'success',
        'word_count': len(words),
        'words': words
    })

# Initialize vocabulary assessment
vocab_assessment = VocabularyAssessment()

@bp.route('/api/assessment/generate_test', methods=['POST'])
def generate_vocabulary_test():
    """Generate a vocabulary assessment test"""
    data = request.json or {}
    
    # Generate a user ID if not provided
    user_id = data.get('user_id') or str(uuid.uuid4())
    test_type = data.get('test_type', 'quick')
    
    if test_type == 'quick':
        # Generate a quick test
        num_words = int(data.get('num_words', 50))
        test_data = vocab_assessment.generate_quick_test(num_words)
    elif test_type == 'adaptive':
        # Generate an adaptive test
        initial_level = data.get('initial_level', 'B1')
        max_questions = int(data.get('max_questions', 25))
        test_data = generate_adaptive_test(vocab_assessment, initial_level, max_questions)
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid test type'
        }), 400
    
    # Store test data in session
    session[f'test_{test_data["test_id"]}'] = test_data
    
    return jsonify({
        'status': 'success',
        'test_id': test_data['test_id'],
        'user_id': user_id,
        'words': [item['word'] for item in test_data['words']] if test_type == 'quick' else 
                [test_data['words'][0]['word']] if test_data['words'] else []
    })

@bp.route('/api/assessment/submit_test', methods=['POST'])
def submit_vocabulary_test():
    """Submit answers for a vocabulary assessment test"""
    data = request.json or {}
    
    test_id = data.get('test_id')
    user_id = data.get('user_id')
    answers = data.get('answers', {})
    
    if not test_id or not user_id or not answers:
        return jsonify({
            'status': 'error',
            'message': 'Missing required data'
        }), 400
    
    # Get test data from session
    test_data = session.get(f'test_{test_id}')
    if not test_data:
        return jsonify({
            'status': 'error',
            'message': 'Test not found'
        }), 404
    
    # Calculate score
    result = vocab_assessment.calculate_score(test_data, answers)
    
    # Save result
    vocab_assessment.save_result(user_id, result)
    
    # Clean up session
    session.pop(f'test_{test_id}', None)
    
    return jsonify({
        'status': 'success',
        'result': result
    })

@bp.route('/api/assessment/adaptive/next_question', methods=['POST'])
def get_adaptive_question():
    """Get the next question for an adaptive test"""
    data = request.json or {}
    
    test_id = data.get('test_id')
    knew_previous = data.get('knew_previous')
    
    if not test_id or knew_previous is None:
        return jsonify({
            'status': 'error',
            'message': 'Missing required data'
        }), 400
    
    # Get test data from session
    test_state = session.get(f'test_{test_id}')
    if not test_state:
        return jsonify({
            'status': 'error',
            'message': 'Test not found'
        }), 404
    
    # Get next question
    updated_state = get_next_adaptive_question(vocab_assessment, test_state, knew_previous)
    
    # Store updated state
    session[f'test_{test_id}'] = updated_state
    
    # Check if test is complete
    if updated_state.get('complete', False):
        return jsonify({
            'status': 'success',
            'complete': True
        })
    
    # Return next question
    next_idx = updated_state['next_question_index']
    next_word = updated_state['words'][next_idx]['word']
    
    return jsonify({
        'status': 'success',
        'word': next_word,
        'question_number': next_idx + 1,
        'total_questions': updated_state['max_questions']
    })

@bp.route('/api/assessment/history/<user_id>', methods=['GET'])
def get_assessment_history(user_id):
    """Get assessment history for a user"""
    if not user_id:
        return jsonify({
            'status': 'error',
            'message': 'User ID is required'
        }), 400
    
    history = vocab_assessment.get_user_history(user_id)
    
    return jsonify({
        'status': 'success',
        'history': history
    })
