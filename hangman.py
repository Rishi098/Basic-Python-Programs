import random

words = ['python', 'javascript', 'computer', 'programming', 'algorithm', 'keyboard', 
         'monitor', 'software', 'hardware', 'internet', 'database', 'network']

def display_hangman(tries):
    stages = [
        '''
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / \\
           -
        ''',
        '''
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / 
           -
        ''',
        '''
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |      
           -
        ''',
        '''
           --------
           |      |
           |      O
           |     \\|
           |      |
           |     
           -
        ''',
        '''
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        ''',
        '''
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        ''',
        '''
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        '''
    ]
    return stages[tries]

def play_game():
    word = random.choice(words)
    word_letters = set(word)
    guessed_letters = set()
    tries = 6

    print("Let's play Hangman!")
    print(display_hangman(tries))

    while tries > 0 and word_letters:
        print(f"\nYou have {tries} tries left")
        print("Letters guessed: ", ' '.join(sorted(guessed_letters)) if guessed_letters else "None yet")

        word_display = ''.join([letter if letter in guessed_letters else '_' for letter in word])
        print("Word: ", ' '.join(word_display))

        guess = input("\nGuess a letter: ").lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter!")
            continue

        if guess in guessed_letters:
            print("You already guessed that letter. Try again!")
            continue

        guessed_letters.add(guess)

        if guess in word_letters:
            word_letters.remove(guess)
            print(f"Nice! '{guess}' is in the word!")
        else:
            tries -= 1
            print(f"Sorry, '{guess}' is not in the word.")
            print(display_hangman(tries))

    if tries == 0:
        print(f"\nGame over! The word was '{word}'")
    else:
        print(f"\nCongrats! You guessed the word '{word}'!")

def main():
    while True:
        play_game()
        response = input("\nWanna play again? (yes/no): ").lower()
        if response != 'yes' and response != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
