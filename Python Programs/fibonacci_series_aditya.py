"""
Prints the first n terms of the Fibonacci sequence.
"""

n = int(input("Enter number of terms: "))

a, b = 0, 1
count = 0

if n <= 0:
    print("Please enter a positive integer")
elif n == 1:
    print(a)
else:
    while count < n:
        print(a, end=" ")
        a, b = b, a + b
        count += 1
