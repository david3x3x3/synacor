import sys

# list of opcodes. includes name, number of args and position of
# args that do write operations.

opcodes = [
    ['halt', 0, -1], ['set',  2,  0], ['push', 1, -1], ['pop',  1,  0],
    ['eq',   3,  0], ['gt',   3, -1], ['jmp',  1, -1], ['jt',   2, -1],
    ['jf',   2, -1], ['add',  3,  0], ['mult', 3,  0], ['mod',  3,  0],
    ['and',  3,  0], ['or',   3,  0], ['not',  2,  0], ['rmem', 2,  0],
    ['wmem', 2, -1], ['call', 1, -1], ['ret',  0, -1], ['out',  1, -1],
    ['in',   1, -1], ['noop', 0, -1]]


def mem_write(addr, val):
    if addr < 2**15:
        mem[addr] = val
    else:
        reg[addr - 2**15] = val


def disasm(addr, last_op='ret'):
    op = 'xyzzy'
    while addr < len(mem) and op != last_op:
        if mem[addr] < len(opcodes):
            op, oplen, outarg = opcodes[mem[addr]]
            addr2 = addr
            if op == 'out':
                args2 = []
                while mem[addr] == 19:
                    ch = mem[addr+1]
                    if ch >= 2**15:
                        ch = f'[reg{ch-2**15}]'
                    elif ch >= 128:
                        ch = f'[{ch}]'
                    else:
                        ch = chr(ch)
                        if ch == '\n':
                            ch = '\\n'
                    args2 += [ch]
                    addr += 2
                addr -= 2
            else:
                args = [mem[addr+1+i] for i in range(oplen)]
                args2 = ['%04x ' % a for a in args]
            print(f'0x{addr2:04x}: {op} {"".join(args2)}')
            addr += oplen+1
        else:
            ch = mem[addr]
            if ch < 128:
                ch = chr(ch)
            else:
                ch = '[%04x]' % ch
            print(f'0x{addr:04x}: data {ch}')
            addr += 1


reg = [0]*8
stack = []
in_buf = ''
out_buf = ''
cache_17a1 = {}
args_17a1 = []
tp_list = []
mem = []
maxb = 0
data = open('challenge.bin', mode='rb').read()
for i in range(0, len(data), 2):
    num = data[i] + data[i+1]*256
    maxb = max(maxb, num)
    # print(f'addr {i:x} = {num:x}')
    mem += [num]


# disasm(0x0863)
if len(sys.argv) > 1:
    disasm(0, "don't stop")
    sys.exit(0)

pc = 0
tracing = False
age = 0

while True:
    # run computer
    while True:
        age += 1
        # if pc == 0x1589:
        #     tracing = True
        if mem[pc] >= len(opcodes):
            print(f'unknown op {mem[pc]:d}')
            break
        op = opcodes[mem[pc]][0]
        # print(f'op = {op}')
        args = []
        preargs = []
        opcode = opcodes[mem[pc]]
        for i in range(opcode[1]):
            arg = mem[pc+1+i]
            preargs += [arg]
            # print(f'arg {i} = {arg}')
            if arg >= 2**15:
                arg = arg - 2**15
                if opcode[2] != i:
                    arg = reg[arg]
            args += [arg]
            # print(f'args = {args}')
        if tracing and op != 'out':
            print(f'{age} {pc:04x}: TRACE {op} {["%04x" % x for x in args]} '
                  f'({["%04x" % x for x in preargs]})')
        if op == 'add':
            mem_write(preargs[0], (args[1] + args[2]) % 2**15)
            pc += len(args)+1
        elif op == 'and':
            mem_write(preargs[0], args[1] & args[2])
            pc += len(args)+1
        elif op == 'call':
            if args[0] == 0x17a1 and (reg[0], reg[1], reg[7]) in cache_17a1:
                # check cached results of teleporter calls
                res_17a1 = cache_17a1[(reg[0], reg[1], reg[7])]
                reg[0], reg[1] = res_17a1
                pc += len(args)+1
            else:
                if args[0] == 0x17a1:
                    args_17a1.append((reg[0], reg[1], reg[7]))
                stack.append(pc+2)
                pc = args[0]
        elif op == 'eq':
            mem_write(preargs[0], 1 if args[1] == args[2] else 0)
            pc += len(args)+1
        elif op == 'gt':
            mem_write(preargs[0], 1 if args[1] > args[2] else 0)
            pc += len(args)+1
        elif op == 'halt':
            break
        elif op == 'in':
            if in_buf == '':
                # useful to see the address of the current game location:
                # print(f'location = 0x{mem[0x0ac3]:04x}')
                if len(tp_list) > 0:
                    # we've got a list of teleporter codes to check
                    # so call the system command for that
                    in_buf = '!tp2'
                else:
                    # read a game or system command from the user
                    in_buf = input() + '\n'
            if in_buf[0] == '!':
                # system commands start with a '!'
                cmd_buf = in_buf[1:]
                in_buf = ''
                # run system command
                break
            mem_write(preargs[0], ord(in_buf[0]))
            in_buf = in_buf[1:]
            # tracing = True
            pc += len(args)+1
        elif op == 'jmp':
            pc = args[0]
        elif op == 'jt':
            if args[0] != 0:
                pc = args[1]
            else:
                pc += len(args)+1
        elif op == 'jf':
            if args[0] == 0:
                pc = args[1]
            else:
                pc += len(args)+1
        elif op == 'mod':
            mem_write(preargs[0], args[1] % args[2])
            pc += len(args)+1
        elif op == 'mult':
            mem_write(preargs[0], (args[1] * args[2]) % 2**15)
            pc += len(args)+1
        elif op == 'noop':
            pc += len(args)+1
        elif op == 'not':
            mem_write(preargs[0], args[1] ^ (2**15-1))
            pc += len(args)+1
        elif op == 'or':
            mem_write(preargs[0], args[1] | args[2])
            pc += len(args)+1
        elif op == 'out':
            ch = chr(args[0])
            if ch != '\n':
                out_buf = out_buf + ch
            else:
                print(out_buf, end='\n')
                out_buf = ''
            pc += len(args)+1
        elif op == 'pop':
            mem_write(preargs[0], stack.pop())
            pc += len(args)+1
        elif op == 'push':
            stack.append(args[0])
            pc += len(args)+1
        elif op == 'ret':
            # check return codes from teleporter code
            if pc in (0x17a8, 0x17b5, 0x17c9):
                arg_17a1 = args_17a1.pop()
                cache_17a1[arg_17a1] = (reg[0], reg[1])
                if len(args_17a1) == 0:
                    # this wasn't recursive, so display final answer
                    print(f'cache_17a1[{arg_17a1}] = ({reg[0]}, {reg[1]})')
                    if len(tp_list) > 0 and reg[0] == 6:
                        # final answer was correct, and we're searching,
                        # not actually running the teleporter,
                        # so tell the !tp command to stop searching
                        tp_list = [0]
                    cache_17a1 = {}
            # otherwise handle 'ret' operator as normal
            addr = stack.pop()
            pc = addr
        elif op == 'rmem':
            mem_write(preargs[0], mem[args[1]])
            pc += len(args)+1
        elif op == 'set':
            mem_write(preargs[0], args[1])
            pc += len(args)+1
        elif op == 'wmem':
            mem_write(args[0], args[1])
            pc += len(args)+1
        else:
            print(f'unknown op {op}')
            break

    # handle system commands
    words = cmd_buf.split()
    if words[0] == 'help':
        print('system commands:')
        print('')
        print('!st\n  print program counter and stack')
        print('!tp\n  search for the right number to use in the teleporter')
        print('!dis\n  disassemble the program in memory')
        print('!reg\n  show the register values')
        print('!reg <reg num> <value>\n  set register <reg num> to <value>')
        print('!save\n  save the vm state to a file')
        print('!load\n  restore the vm state from a file')
    elif words[0] == 'st':
        # print stack
        print(f'stack len = {len(stack)}, pc = {pc:04x}')
        print([f'0x{n:04x}' for n in stack])
    elif words[0] == 'dis':
        disasm(0x0, "don't stop")
    elif words[0] == 'tp':
        for i in range(1, 32768):
            # add numbers to a list of reg[7] values to try
            tp_list.append(i)
        save_reg = list(reg)
    elif words[0] == 'tp2':
        reg[0] = 4
        reg[1] = 1
        reg[7] = tp_list.pop(0)
        if reg[7] == 0:
            # restore registers to value before !tp
            reg = list(save_reg)
        else:
            # set return point to 'in' op code we were called from
            stack.append(pc)
            args_17a1.append((reg[0], reg[1], reg[7]))
            # call the teleporter code
            pc = 0x17a1
    elif words[0] == 'reg':
        # registers
        if len(words) == 1:
            print([f'0x{n:04x}' for n in reg])
        else:
            reg[int(words[1])-1] = int(words[2])
            print('updated register')
    elif words[0] == 'save':
        # save game state
        with open('save.bin', 'wb') as fp:
            # write save file:
            # 8 registers
            for x in reg:
                fp.write(bytearray([x % 256, x // 256]))
            # size of memory
            x = len(mem)
            fp.write(bytearray([x % 256, x // 256]))
            # memory contents
            for x in mem:
                fp.write(bytearray([x % 256, x // 256]))
            # size of stack
            x = len(stack)
            fp.write(bytearray([x % 256, x // 256]))
            # stack contents
            for x in stack:
                fp.write(bytearray([x % 256, x // 256]))
            # program counter
            x = pc
            fp.write(bytearray([x % 256, x // 256]))
    elif words[0] == 'load':
        # load game state
        with open('save.bin', 'rb') as fp:
            # write save file:
            # 8 registers
            x = fp.read(16)
            reg = [x[i] + x[i+1]*256 for i in range(0, 16, 2)]
            # size of memory
            x2 = fp.read(2)
            x = x2[i] + x2[i+1]*256
            # memory contents
            mem = fp.read(x*2)
            mem = [mem[i] + mem[i+1]*256 for i in range(0, x*2, 2)]
            # size of stack
            x2 = fp.read(2)
            x = x2[i] + x2[i+1]*256
            # stack contents
            stack = fp.read(x*2)
            stack = [stack[i] + stack[i+1]*256 for i in range(0, x*2, 2)]
            # program counter
            x2 = fp.read(2)
            pc = x2[i] + x2[i+1]*256
        print('loaded save file')
    else:
        print('unknown emulator command')
