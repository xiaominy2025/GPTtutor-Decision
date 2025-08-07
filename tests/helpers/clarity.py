#!/usr/bin/env python3
"""
Clarity scoring helper functions for V1.6.5.1 test suite
"""

import re
from typing import Dict, List, Any

def calculate_clarity_score(answer_text: str) -> float:
    """
    Calculate clarity score based on sentence length distribution.
    
    Args:
        answer_text: The text to analyze
        
    Returns:
        Float between 0 and 1, where higher scores indicate better clarity
        (more sentences with <= 20 words)
    """
    if not answer_text or not answer_text.strip():
        return 0.0
    
    # Split text into sentences using regex
    # Handle various sentence endings: . ! ? and account for abbreviations
    sentences = re.split(r'(?<=[.!?])\s+', answer_text.strip())
    
    if not sentences:
        return 0.0
    
    # Filter out empty sentences and count sentences with <= 20 words
    valid_sentences = []
    short_sentences = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Count words in sentence
        words = re.findall(r'\b\w+\b', sentence)
        word_count = len(words)
        
        valid_sentences.append(sentence)
        
        # Consider sentences with <= 20 words as "clear"
        if word_count <= 20:
            short_sentences += 1
    
    # Calculate clarity score as ratio of short sentences
    if not valid_sentences:
        return 0.0
    
    clarity_score = short_sentences / len(valid_sentences)
    return clarity_score

def analyze_text_clarity(text: str) -> Dict[str, Any]:
    """
    Comprehensive text clarity analysis.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with clarity metrics
    """
    if not text or not text.strip():
        return {
            'clarity_score': 0.0,
            'total_sentences': 0,
            'short_sentences': 0,
            'long_sentences': 0,
            'average_sentence_length': 0.0,
            'sentence_lengths': []
        }
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    valid_sentences = []
    short_sentences = 0
    long_sentences = 0
    sentence_lengths = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Count words
        words = re.findall(r'\b\w+\b', sentence)
        word_count = len(words)
        
        valid_sentences.append(sentence)
        sentence_lengths.append(word_count)
        
        if word_count <= 20:
            short_sentences += 1
        else:
            long_sentences += 1
    
    if not valid_sentences:
        return {
            'clarity_score': 0.0,
            'total_sentences': 0,
            'short_sentences': 0,
            'long_sentences': 0,
            'average_sentence_length': 0.0,
            'sentence_lengths': []
        }
    
    clarity_score = short_sentences / len(valid_sentences)
    average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
    
    return {
        'clarity_score': clarity_score,
        'total_sentences': len(valid_sentences),
        'short_sentences': short_sentences,
        'long_sentences': long_sentences,
        'average_sentence_length': average_sentence_length,
        'sentence_lengths': sentence_lengths
    }

def validate_clarity_threshold(text: str, threshold: float = 0.6) -> Dict[str, Any]:
    """
    Validate if text meets clarity threshold.
    
    Args:
        text: The text to validate
        threshold: Minimum clarity score required (default 0.6)
        
    Returns:
        Dictionary with validation results
    """
    clarity_analysis = analyze_text_clarity(text)
    meets_threshold = clarity_analysis['clarity_score'] >= threshold
    
    return {
        'meets_threshold': meets_threshold,
        'threshold': threshold,
        'actual_score': clarity_analysis['clarity_score'],
        'analysis': clarity_analysis
    }

def get_clarity_recommendations(text: str) -> List[str]:
    """
    Get recommendations for improving text clarity.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of recommendations for improving clarity
    """
    analysis = analyze_text_clarity(text)
    recommendations = []
    
    if analysis['clarity_score'] < 0.6:
        recommendations.append("Consider breaking long sentences into shorter ones")
    
    if analysis['average_sentence_length'] > 25:
        recommendations.append("Average sentence length is quite high - aim for shorter sentences")
    
    if analysis['long_sentences'] > analysis['short_sentences']:
        recommendations.append("More than half of sentences are long - consider simplifying")
    
    if analysis['total_sentences'] < 3:
        recommendations.append("Very few sentences - consider adding more structure")
    
    return recommendations 