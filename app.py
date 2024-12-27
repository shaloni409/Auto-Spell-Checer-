import string
import re
import numpy as np
from collections import Counter
import streamlit as st


# Function to read and process corpus
def read_corpus(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        words = []
        for line in lines:
            words += re.findall(r'\w+', line.lower())
        return words


# Load the corpus
corpus = read_corpus(r'big.txt')

# Generate vocabulary and probabilities
vocab = set(corpus)
words_count = Counter(corpus)
total_words_count = float(sum(words_count.values()))
word_probabs = {word: words_count[word] / total_words_count for word in words_count.keys()}


# Functions for spelling corrections
def split(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]


def delete(word):
    return [left + right[1:] for left, right in split(word) if right]


def swap(word):
    return [left + right[1] + right[0] + right[2:] for left, right in split(word) if len(right) > 1]


def replace(word):
    return [left + c + right[1:] for left, right in split(word) if right for c in string.ascii_lowercase]


def insert(word):
    return [left + c + right for left, right in split(word) for c in string.ascii_lowercase]


def level_one_edits(word):
    return set(delete(word) + swap(word) + replace(word) + insert(word))


def level_two_edits(word):
    return set(e2 for e1 in level_one_edits(word) for e2 in level_one_edits(e1))


def correct_spelling(word, vocab, word_probabs):
    if word in vocab:
        return f"'{word}' is already correctly spelled."

    # Generate spelling suggestions
    suggestions = level_one_edits(word) or level_two_edits(word) or [word]
    best_guesses = [w for w in suggestions if w in vocab]

    if not best_guesses:
        return f"Sorry, no suggestions found for '{word}'."

    # Rank suggestions by probability
    suggestions_with_probabs = [(w, word_probabs[w]) for w in best_guesses]
    suggestions_with_probabs.sort(key=lambda x: x[1], reverse=True)

    return f"Suggestions for '{word}': " + ', '.join([f"{w} ({prob:.2%})" for w, prob in suggestions_with_probabs[:10]])


# Streamlit GUI
st.title("AutoCorrect Misspelled Word Search Engine System")
word = st.text_input('Search Here')

if st.button('Check'):
    if word.strip():  # Handle empty input
        result = correct_spelling(word.strip(), vocab, word_probabs)
        st.write(result)
    else:
        st.write("Please enter a word to check.")
