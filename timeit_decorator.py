# filename: timeit_decorator.py
# Run: python timeit_decorator.py

import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {(end-start):.6f}s")
        return result
    return wrapper

@timeit
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

if __name__ == "__main__":
    # Small n to avoid too long recursion
    print("fib(10) =", fib(10))
  
# Note: fib is recursive and intentionally slow — useful to show timing.
