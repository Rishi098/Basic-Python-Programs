def fibonacci(n):
    """
    Returns the nth term in the Fibonacci sequence.

    Done by adding the two previous terms to get the next term.

    :arg n: int - The term to find in the Fibonacci sequence.
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
