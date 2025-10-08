import random

quotes = [
    "Keep pushing forward!",
    "You are capable of amazing things.",
    "Code is like humor. When you have to explain it, it’s bad.",
    "Stay hungry, stay foolish.",
    "Dream big, work hard."
]

def random_quote():
    print("Random Quote of the Day:")
    print(random.choice(quotes))

if __name__ == "__main__":
    random_quote()
