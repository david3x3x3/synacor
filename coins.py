from itertools import permutations

# 9 + 2 * 5**2 + 7**3 - 3 == 399

for p in permutations((2, 3, 5, 7, 9)):
    expression = f'{p[0]} + {p[1]} * {p[2]}**2 + {p[3]}**3 - {p[4]} == 399'
    if eval(expression):
        print(expression)
        break
