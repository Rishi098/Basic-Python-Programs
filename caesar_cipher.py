# filename: caesar_cipher.py
# Run: python caesar_cipher.py encrypt "hello" 3

import sys

def caesar(text, shift, mode="encrypt"):
    result = ""
    if mode == "decrypt":
        shift = -shift
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python caesar_cipher.py <encrypt|decrypt> <text> <shift>")
        sys.exit(1)
    mode, text, shift = sys.argv[1], sys.argv[2], int(sys.argv[3])
    print(caesar(text, shift, mode))
