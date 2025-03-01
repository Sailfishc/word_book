# Vocabulary Book Manager

A simple web application for managing vocabulary books. Built with Python and Flask.

## Features

- Create new vocabulary books
- Add words to vocabulary books (single and batch additions)
- View all words in a vocabulary book
- Extract English words from webpages
- Parse EPUB files and extract English words
- Save extracted words to text files
- Add extracted words to vocabulary books
- RESTful API for programmatic access

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip3 install -r requirements.txt
```

## Usage

1. Start the application:

```bash
python3 app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## API Documentation

### Get all vocabulary books

```
GET /api/books
```

Response:
```json
{
  "books": ["book1", "book2", "book3"]
}
```

### Create a new vocabulary book

```
POST /api/books
```

Request body:
```json
{
  "name": "new_book_name"
}
```

Response:
```json
{
  "message": "Book 'new_book_name' created successfully"
}
```

### Get words from a vocabulary book

```
GET /api/books/{book_name}
```

Response:
```json
{
  "book": "book_name",
  "words": ["word1", "word2", "word3"]
}
```

### Add a word to a vocabulary book

```
POST /api/books/{book_name}/words
```

Request body:
```json
{
  "word": "new_word"
}
```

Response:
```json
{
  "message": "Word 'new_word' added to 'book_name' successfully"
}
```

### Add multiple words to a vocabulary book

```
POST /api/books/{book_name}/words/batch
```

Request body:
```json
{
  "words": ["word1", "word2", "word3"]
}
```

Response:
```json
{
  "message": "Added 3 new words to 'book_name'",
  "added_count": 3
}
```

### Extract words from a webpage

```
POST /api/extract-webpage
```

Request body:
```json
{
  "url": "https://example.com"
}
```

Response:
```json
{
  "message": "Successfully extracted 150 unique words from the webpage",
  "file": "example_com_1709257123.txt",
  "word_count": 150,
  "words": ["word1", "word2", "word3", ...]
}
```

### Extract words from a webpage and add to a vocabulary book

```
POST /api/extract-to-book
```

Request body:
```json
{
  "url": "https://example.com",
  "book_name": "my_book"
}
```

Response:
```json
{
  "message": "Successfully extracted 150 unique words and added 120 new words to 'my_book'",
  "file": "example_com_1709257123.txt",
  "total_words": 150,
  "added_count": 120
}
```

### Upload and parse an EPUB file

```
POST /api/upload-epub
```

Request body: FormData containing the EPUB file with key 'file'

Response:
```json
{
  "message": "Successfully extracted 500 unique words from the EPUB file",
  "file": "book_1709257123.txt",
  "word_count": 500,
  "filename": "book.epub"
}
```

### Upload an EPUB file and add words to a vocabulary book

```
POST /api/epub-to-book
```

Request body: FormData containing:
- EPUB file with key 'file'
- book_name parameter

Response:
```json
{
  "message": "Successfully extracted 500 unique words and added 450 new words to 'my_book'",
  "file": "book_1709257123.txt",
  "total_words": 500,
  "added_count": 450,
  "filename": "book.epub"
}
```

## File Structure

- Vocabulary books are stored as text files in the `vocabulary_books` directory
- Each vocabulary book is a separate text file
- Each word is stored on a separate line in the text file
- Uploaded EPUB files are stored in the `epub` directory
- Extracted words from webpages and EPUB files are stored in the `attachment` directory
- Extracted webpage files are named based on the domain (e.g., `example_com_1709257123.txt`)
- Extracted EPUB files are named based on the EPUB filename (e.g., `book_1709257123.txt`)
