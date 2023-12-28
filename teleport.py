from multiprocessing import Pool
import tqdm


def call(r1, r2, a):
    if (r1, r2) in cache:
        # return result from cache instead of calling
        r1, r2 = cache[(r1, r2)]
    else:
        # actually make the call
        cache_res.append((r1, r2))
        stack.append(a)
        a = 0x17a1
    return r1, r2, a


def ret(r1, r2):
    # put the result of the call in the cache
    cache[cache_res.pop()] = (r1, r2)
    # then return the next address
    return stack.pop()


def ack(reg1, reg2, reg8):
    addr = 0x17a1
    while True:
        if addr == 0x17a1:
            if reg1 != 0:
                addr = 0x17a9
                continue
            reg1 = (reg2 + 1) % 32768
            addr = ret(reg1, reg2)
            continue
        elif addr == 0x17a9:
            if reg2 != 0:
                addr = 0x17b6
                continue
            reg1 = (reg1+32767) % 32768
            reg2 = reg8
            reg1, reg2, addr = call(reg1, reg2, 0x17b5)
            continue
        elif addr == 0x17b5:
            addr = ret(reg1, reg2)
            continue
        elif addr == 0x17b6:
            stack.append(reg1)
            reg2 = (reg2+32767) % 32768
            reg1, reg2, addr = call(reg1, reg2, 0x17be)
            continue
        elif addr == 0x17be:
            reg2 = reg1
            reg1 = stack.pop()
            reg1 = (reg1 + 32767) % 32768
            reg1, reg2, addr = call(reg1, reg2, 0x17c9)
            continue
        elif addr == 0x17c9:
            if len(stack) == 0:
                return reg1
            addr = ret(reg1, reg2)
            continue


def call_ack(reg8):
    global cache, cache_res, stack
    cache = {}
    cache_res = []
    stack = []
    res = ack(4, 1, reg8)
    # print(reg8, res)
    return (reg8, res)
    

if __name__ == '__main__':
    with Pool() as p:
        # tasks = list(range(0, 32768))
        tasks = range(0, 32768)
        solutions = []
        for res in tqdm.tqdm(p.imap_unordered(call_ack, tasks),
                             total=len(tasks), ascii=True):
            if res[1] == 6:
                solutions.append(res[0])
    print(solutions)
    
