import cmath

def solve_quadratic(a, b, c):
    d = b**2 - 4*a*c
    root1 = (-b + cmath.sqrt(d)) / (2*a)
    root2 = (-b - cmath.sqrt(d)) / (2*a)
    
    return root1, root2
a = float(input("Enter coefficient a: "))
b = float(input("Enter coefficient b: "))
c = float(input("Enter coefficient c: "))
if a == 0:
    print("Coefficient 'a' cannot be zero for a quadratic equation.")
else:
    roots = solve_quadratic(a, b, c)
    print(f"The roots are: {roots[0]} and {roots[1]}")
