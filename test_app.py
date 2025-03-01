import os
import pytest
import tempfile
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200

def test_create_book(client):
    """Test creating a new vocabulary book"""
    response = client.post('/api/books', 
                          json={'name': 'test_book'},
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "created successfully" in data['message']

def test_get_books(client):
    """Test getting all vocabulary books"""
    # First create a book
    client.post('/api/books', 
               json={'name': 'test_book2'},
               content_type='application/json')
    
    response = client.get('/api/books')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'books' in data
    assert 'test_book2' in data['books']

def test_add_word(client):
    """Test adding a word to a vocabulary book"""
    # First create a book
    client.post('/api/books', 
               json={'name': 'test_book3'},
               content_type='application/json')
    
    response = client.post('/api/books/test_book3/words',
                          json={'word': 'example'},
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "added to 'test_book3' successfully" in data['message']
    
    # Check that the word was added
    response = client.get('/api/books/test_book3')
    data = json.loads(response.data)
    assert 'example' in data['words']

def test_add_batch_words(client):
    """Test adding multiple words to a vocabulary book"""
    # First create a book
    client.post('/api/books', 
               json={'name': 'test_book4'},
               content_type='application/json')
    
    response = client.post('/api/books/test_book4/words/batch',
                          json={'words': ['word1', 'word2', 'word3']},
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['added_count'] == 3
    
    # Check that the words were added
    response = client.get('/api/books/test_book4')
    data = json.loads(response.data)
    assert 'word1' in data['words']
    assert 'word2' in data['words']
    assert 'word3' in data['words']
