"""
Vocabulary Assessment Module

This module provides functionality to assess a user's English vocabulary level
through different testing methodologies:

1. Word Recognition Test - User is shown words of varying difficulty and indicates
   if they know the meaning
2. Frequency Band Test - Tests knowledge of words from different frequency bands
3. Adaptive Testing - Dynamically adjusts word difficulty based on user responses

The assessment can be completed quickly (5-10 minutes) and taken multiple times
to improve accuracy through averaging results.
"""

import random
import json
import os
import math
from utils import get_app_dirs

# Get directory paths
DIRS = get_app_dirs()

# Define the path for assessment data
ASSESSMENT_DIR = os.path.join(DIRS.get('APP_DIR', ''), 'assessment_data')
os.makedirs(ASSESSMENT_DIR, exist_ok=True)

# Dictionary of CEFR levels with approximate vocabulary sizes
VOCAB_LEVELS = {
    'A1': 500,     # Beginner
    'A2': 1000,    # Elementary
    'B1': 2000,    # Intermediate
    'B2': 4000,    # Upper Intermediate
    'C1': 8000,    # Advanced
    'C2': 16000    # Proficient
}

# Path to word frequency lists
WORD_LISTS_PATH = os.path.join(ASSESSMENT_DIR, 'frequency_lists')
os.makedirs(WORD_LISTS_PATH, exist_ok=True)

class VocabularyAssessment:
    """Class for managing vocabulary assessment tests"""
    
    def __init__(self):
        """Initialize the vocabulary assessment module"""
        self.word_frequency_data = {}
        self.load_word_frequency_data()
        
    def load_word_frequency_data(self):
        """Load word frequency data from files or download if not available"""
        # Check if word frequency data exists
        frequency_file = os.path.join(ASSESSMENT_DIR, 'word_frequency.json')
        
        if os.path.exists(frequency_file):
            with open(frequency_file, 'r') as f:
                self.word_frequency_data = json.load(f)
        else:
            # For demonstration, create a sample word frequency dataset
            # In production, you would download from a reliable source
            self.create_sample_frequency_data()
            
            # Save the data
            with open(frequency_file, 'w') as f:
                json.dump(self.word_frequency_data, f)
    
    def create_sample_frequency_data(self):
        """Create sample frequency data for demonstration purposes"""
        # In a real implementation, you would use actual frequency data
        # This is just a small sample for testing
        cefr_samples = {
            'A1': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I'],
            'A2': ['book', 'school', 'friend', 'family', 'house', 'work', 'day', 'time', 'year', 'food'],
            'B1': ['consider', 'expect', 'determine', 'receive', 'provide', 'explain', 'contain', 'maintain', 'establish', 'occur'],
            'B2': ['acquire', 'analyze', 'comprehensive', 'interpret', 'implement', 'policy', 'concept', 'perspective', 'framework', 'conclude'],
            'C1': ['endeavor', 'rationalize', 'methodology', 'facilitate', 'fundamental', 'contingent', 'constitute', 'subsequent', 'albeit', 'intrinsic'],
            'C2': ['ubiquitous', 'amalgamate', 'esoteric', 'superfluous', 'paradigm', 'juxtapose', 'paradoxical', 'quintessential', 'antithetical', 'idiosyncrasy']
        }
        
        # Generate a larger dataset for each level
        for level, samples in cefr_samples.items():
            # Expand sample set with randomized fake words for testing
            expanded_samples = samples.copy()
            
            # Generate 20 more fake words per level
            base_words = ['examin', 'struct', 'complic', 'migrat', 'configur']
            suffixes = ['ation', 'ify', 'ology', 'istic', 'isation']
            
            for i in range(20):
                if i < 5:
                    fake_word = f"{base_words[i % len(base_words)]}{suffixes[i % len(suffixes)]}"
                else:
                    fake_word = f"{base_words[i % len(base_words)]}{i}{suffixes[i % len(suffixes)]}"
                expanded_samples.append(fake_word)
            
            self.word_frequency_data[level] = expanded_samples
    
    def generate_quick_test(self, num_words=50):
        """
        Generate a quick vocabulary assessment test
        
        Args:
            num_words (int): Number of words to include in the test
            
        Returns:
            dict: Test data with words categorized by CEFR level
        """
        test_data = {
            'words': [],
            'distribution': {},
            'test_id': random.randint(1000, 9999)
        }
        
        # Determine number of words from each level
        words_per_level = max(3, num_words // len(VOCAB_LEVELS))
        remaining = num_words - (words_per_level * len(VOCAB_LEVELS))
        
        # Distribute remaining words to higher levels
        level_distribution = {level: words_per_level for level in VOCAB_LEVELS}
        for level in list(VOCAB_LEVELS.keys())[-remaining:]:
            level_distribution[level] += 1
        
        test_data['distribution'] = level_distribution
        
        # Select words for each level
        for level, count in level_distribution.items():
            if level in self.word_frequency_data:
                level_words = self.word_frequency_data[level]
                selected = random.sample(level_words, min(count, len(level_words)))
                for word in selected:
                    test_data['words'].append({
                        'word': word,
                        'level': level
                    })
        
        # Shuffle the words to randomize the test
        random.shuffle(test_data['words'])
        
        return test_data
    
    def calculate_score(self, test_data, answers):
        """
        Calculate vocabulary size and CEFR level based on test answers
        
        Args:
            test_data (dict): The test data including words and their levels
            answers (dict): Dictionary mapping words to True (known) or False (unknown)
            
        Returns:
            dict: Assessment results including estimated vocabulary size and CEFR level
        """
        # Count known words per level
        level_counts = {level: {'total': 0, 'known': 0} for level in VOCAB_LEVELS}
        
        for word_data in test_data['words']:
            word = word_data['word']
            level = word_data['level']
            
            level_counts[level]['total'] += 1
            if word in answers and answers[word]:
                level_counts[level]['known'] += 1
        
        # Calculate proportion known at each level
        level_proportions = {}
        for level, counts in level_counts.items():
            if counts['total'] > 0:
                level_proportions[level] = counts['known'] / counts['total']
            else:
                level_proportions[level] = 0
        
        # Estimate vocabulary size based on proportion known at each level
        vocabulary_size = 0
        for level, proportion in level_proportions.items():
            level_size = VOCAB_LEVELS[level]
            vocabulary_size += level_size * proportion
        
        # Round to nearest 100
        vocabulary_size = round(vocabulary_size / 100) * 100
        
        # Determine CEFR level
        cefr_level = 'A1'
        for level, size in VOCAB_LEVELS.items():
            if vocabulary_size >= size * 0.8:  # 80% of level vocabulary known
                cefr_level = level
        
        # Calculate confidence level (higher with more consistent results across levels)
        variance = sum((proportion - sum(level_proportions.values()) / len(level_proportions)) ** 2 
                    for proportion in level_proportions.values()) / len(level_proportions)
        confidence = max(0, min(100, 100 - (variance * 100)))
        
        return {
            'vocabulary_size': vocabulary_size,
            'cefr_level': cefr_level,
            'level_proportions': level_proportions,
            'confidence': round(confidence),
            'test_id': test_data['test_id']
        }
    
    def save_result(self, user_id, result):
        """
        Save assessment result for a user
        
        Args:
            user_id (str): Identifier for the user
            result (dict): Assessment result to save
            
        Returns:
            bool: Success status
        """
        user_results_dir = os.path.join(ASSESSMENT_DIR, 'user_results')
        os.makedirs(user_results_dir, exist_ok=True)
        
        user_file = os.path.join(user_results_dir, f'{user_id}.json')
        
        # Load existing results or create new
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
        else:
            user_data = {'results': []}
        
        # Add timestamp to result
        result['timestamp'] = os.path.getmtime(user_file) if os.path.exists(user_file) else 0
        
        # Add new result
        user_data['results'].append(result)
        
        # Calculate average score from last 3 tests
        recent_results = user_data['results'][-3:]
        
        if len(recent_results) > 0:
            avg_vocab_size = sum(r['vocabulary_size'] for r in recent_results) / len(recent_results)
            user_data['average_vocabulary_size'] = round(avg_vocab_size / 100) * 100
            
            # Determine average CEFR level
            avg_level_idx = 0
            levels = list(VOCAB_LEVELS.keys())
            for r in recent_results:
                avg_level_idx += levels.index(r['cefr_level'])
            avg_level_idx = round(avg_level_idx / len(recent_results))
            user_data['average_cefr_level'] = levels[min(avg_level_idx, len(levels) - 1)]
        
        # Save updated data
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        
        return True
    
    def get_user_history(self, user_id):
        """
        Get assessment history for a user
        
        Args:
            user_id (str): Identifier for the user
            
        Returns:
            dict: User's assessment history
        """
        user_results_dir = os.path.join(ASSESSMENT_DIR, 'user_results')
        user_file = os.path.join(user_results_dir, f'{user_id}.json')
        
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                return json.load(f)
        else:
            return {'results': []}

# Function to generate an adaptive test that adjusts difficulty based on responses
def generate_adaptive_test(assessment, initial_level='B1', max_questions=25):
    """
    Generate an adaptive test that adjusts difficulty based on responses
    
    Args:
        assessment (VocabularyAssessment): Assessment instance
        initial_level (str): Initial CEFR level to start with
        max_questions (int): Maximum number of questions
        
    Returns:
        dict: Adaptive test configuration
    """
    levels = list(VOCAB_LEVELS.keys())
    current_level_idx = levels.index(initial_level)
    
    # Start with 5 words from the initial level
    words = []
    if initial_level in assessment.word_frequency_data:
        initial_words = random.sample(
            assessment.word_frequency_data[initial_level],
            min(5, len(assessment.word_frequency_data[initial_level]))
        )
        for word in initial_words:
            words.append({
                'word': word,
                'level': initial_level
            })
    
    return {
        'words': words,
        'current_level_idx': current_level_idx,
        'levels': levels,
        'max_questions': max_questions,
        'adaptive': True,
        'test_id': random.randint(1000, 9999),
        'next_question_index': len(words)
    }

def get_next_adaptive_question(assessment, test_state, previous_result):
    """
    Get the next question for an adaptive test based on previous answer
    
    Args:
        assessment (VocabularyAssessment): Assessment instance
        test_state (dict): Current state of the adaptive test
        previous_result (bool): Whether the user knew the previous word
        
    Returns:
        dict: Updated test state with new question
    """
    levels = test_state['levels']
    current_level_idx = test_state['current_level_idx']
    
    # Adjust level based on previous response
    if previous_result:
        # If correct, make it harder (move up a level)
        current_level_idx = min(current_level_idx + 1, len(levels) - 1)
    else:
        # If incorrect, make it easier (move down a level)
        current_level_idx = max(current_level_idx - 1, 0)
    
    # Get the current level
    current_level = levels[current_level_idx]
    
    # Get words already used in this test
    used_words = [item['word'] for item in test_state['words']]
    
    # Get available words for the current level
    available_words = [
        word for word in assessment.word_frequency_data.get(current_level, [])
        if word not in used_words
    ]
    
    # Add a new word if available
    if available_words and len(test_state['words']) < test_state['max_questions']:
        new_word = random.choice(available_words)
        test_state['words'].append({
            'word': new_word,
            'level': current_level
        })
        test_state['next_question_index'] = len(test_state['words']) - 1
    else:
        # Test is complete or no more words available
        test_state['complete'] = True
    
    # Update the current level index
    test_state['current_level_idx'] = current_level_idx
    
    return test_state
