# 22 + 4 - 11 * 4 - 18 - 11 - 1 = 30
# N E E N W S E E W N N E
grid = (('*',  '8', '-',  '1'),
        ('4',  '*', '11', '*'),
        ('+',  '4', '-',  '18'),
        ('22', '-', '9',  '*'))

dirs = ((-1, 0), (0, 1), (1, 0), (0, -1))


def search(path, path2, r1, c1, hist, depth):
    if depth == 0 or (r1, c1) == (0, 3):
        if (r1, c1) == (0, 3) and eval(path) == 30:
            print(path2, '=', eval(path))
            return True
        return False
    for dr, dc in dirs:
        r2 = r1 + dr
        c2 = c1 + dc
        if r2 < 0 or r2 > 3 or c2 < 0 or c2 > 3 or (r2, c2) == (3, 0):
            continue
        if depth % 2 == 0:
            newpath = f'({path}){grid[r2][c2]}'
            newpath2 = path2 + ' ' + grid[r2][c2]
        else:
            newpath = f'{path}{grid[r2][c2]}'
            newpath2 = path2 + ' ' + grid[r2][c2]
        res = search(newpath, newpath2, r2, c2, hist + [(r2, c2)], depth-1)
        if res:
            return True
    return False


solved = False
depth = 2
while not solved:
    solved = search('22', '22', 3, 0, [(3, 0)], depth)
    depth += 2
