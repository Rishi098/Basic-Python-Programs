"""
Program: Pangram Checker
    A pangram is a sentence that contains every letter of the English alphabet at least once.
    This program checks whether a given sentence is a pangram or not.

Example:
    Input:  "The quick brown fox jumps over the lazy dog"
    Output: "✅ The sentence is a pangram."
"""

import string 

def is_pangram(sentence):
    """
    Function to check whether a given sentence is a pangram.

    Args:
        sentence (str): The sentence to check.
    
    Returns:
        bool: True if the sentence is a pangram, False otherwise.
    """
    # Get a set of all lowercase alphabets (a-z)
    alphabet = set(string.ascii_lowercase)

    # Convert the sentence to lowercase and make a set of characters present
    sentence_letters = set(sentence.lower())

    # Check if all alphabets are present in the sentence
    return alphabet <= sentence_letters


# --- Main Program ---
if __name__ == "__main__":
    sentence = input("Enter a sentence: ")  # Take input from user
    
    # Check and display result
    if is_pangram(sentence):
        print("✅ The sentence is a pangram.")
    else:
        print("❌ The sentence is not a pangram.")
