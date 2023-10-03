#!/usr/bin/env python3

# EVM From Scratch
# Python template
#
# To work on EVM From Scratch in Python:
#
# - Install Python3: https://www.python.org/downloads/
# - Go to the `python` directory: `cd python`
# - Edit `evm.py` (this file!), see TODO below
# - Run `python3 evm.py` to run the tests

import json
import os

MAX_UINT256 = 2**256
BITS_IN_32 = 256

def push_impl(op, code, stack, pc):
    push1 = "60"
    size = (int(op, 16) - int(push1, 16)) + 1
    pc += (size * 2)
    result_str = ""
    i = 0
    while i < size * 2:
        result_str += code[i] + code[i + 1]
        i += 2
    stack.append(int(result_str, 16))
    return (stack, pc)

def dup_impl(op, stack, pc):
    dup1 = "80"
    size = (int(op, 16) - int(dup1, 16)) + 1
    pc += (size * 2) - 2
    old_vals = []
    i = 0
    while i < size:
        old_vals.append(stack.pop())
        i += 1
    a = old_vals[-1]
    stack.append(a)
    for x in old_vals:
        stack.append(x)
    return (stack, pc)

def swap_impl(op, stack, pc):
    swap = "90"
    size = (int(op, 16) - int(swap, 16)) + 1
    pc += (size * 2) - 2
    old_vals = []
    i = 0
    a = stack.pop()
    while i < size - 1:
        old_vals.append(stack.pop())
        i += 1
    old_vals.reverse()
    stack.append(a)
    for x in old_vals:
        stack.append(x)
    return (stack, pc)

def add_impl(a, b):
    return (a + b) % MAX_UINT256

def mul_impl(a, b, mod):
    return (a * b) % mod

def sub_impl(a, b):
    result = a - b
    return result if result >= 0 else (MAX_UINT256 + result)

def div_impl(a, b):
    return 0 if b == 0 else int(a / b)

def mod_impl(a, b):
    return 0 if b == 0 else int(a % b)

def exp_impl(a, b):
    return (a ** b) % MAX_UINT256

def sigextend_impl(x):
    bin_x = bin(x)[2:]
    bin_x = bin_x if len(bin_x) == 8 else ("0" * (8 - len(bin_x))) + bin_x
    if bin_x[0] == "0":
        return x, False
    else:
        result = ("ff" * 31) + hex(x)[2:]
        return int(result, 16), True

def to_signed(x):
    result = -(x & 0x80000000) | (x & 0x7fffffff)
    return result

def to_32b_hex(x):
    hex_x = hex(x)[2:]
    if len(hex_x) < 64:
        hex_x = "0" * (64 - len(hex_x)) + hex_x
    return hex_x
    
def evm(code):
    pc = 0
    success = True
    stack = []

    while pc < len(code):
        op = code[pc] + code[pc + 1]
        pc += 2
        if op == "00": #STOP
            return (True, stack)
        elif op == "01": #ADD
            a, b = stack.pop(), stack.pop()
            result = add_impl(a, b)
            stack.append(result)
        elif op == "02": #MUL
            a, b = stack.pop(), stack.pop()
            result = mul_impl(a, b, MAX_UINT256)
            stack.append(result)
        elif op == "03": #SUB
            a, b = stack.pop(), stack.pop()
            result = sub_impl(a, b)
            stack.append(result)
        elif op == "04": #DIV
            a, b = stack.pop(), stack.pop()
            result = div_impl(a, b)
            stack.append(result)
        elif op == "05": #SDIV
            a, b = stack.pop(), stack.pop()
            sig_a, sig_b = to_signed(a), to_signed(b)
            result = div_impl(sig_a, sig_b)
            if result < 0:
                result = MAX_UINT256 + result
            stack.append(result)
        elif op == "06": #MOD
            a, b = stack.pop(), stack.pop()
            result = mod_impl(a, b)
            stack.append(result)
        elif op == "07": #SMOD
            a, b = stack.pop(), stack.pop()
            sig_a, sig_b = to_signed(a), to_signed(b)
            result = mod_impl(sig_a, sig_b)
            if result < 0:
                result = MAX_UINT256 + result
            stack.append(result)
        elif op == "08": #ADDMOD
            a, b = stack.pop(), stack.pop()
            mod = stack.pop()
            result = add_impl(a, b)
            result = mod_impl(result, mod)
            stack.append(result)
        elif op == "09": #MULMOD
            a, b = stack.pop(), stack.pop()
            mod = stack.pop()
            result = mul_impl(a, b, mod)
            result = mod_impl(result, MAX_UINT256)
            stack.append(result)
        elif op == "0a": #EXP
            a, b = stack.pop(), stack.pop()
            result = exp_impl(a, b)
            stack.append(result)
        elif op == "0b": #SIGNEXTEND
            stack.pop() #Get rid of "b"
            x = stack.pop()
            (result, _) = sigextend_impl(x)
            stack.append(result)
        elif op == "10": #LT
            a, b = stack.pop(), stack.pop()
            result = 1 if a < b else 0
            stack.append(result)
        elif op == "11": #GT
            a, b = stack.pop(), stack.pop()
            result = 1 if a > b else 0
            stack.append(result)
        elif op == "12": #SLT
            a, b = stack.pop(), stack.pop()
            sig_a, sig_b = to_signed(a), to_signed(b)
            result = 1 if sig_a < sig_b else 0
            stack.append(result)
        elif op == "13": #SGT
            a, b = stack.pop(), stack.pop()
            sig_a, sig_b = to_signed(a), to_signed(b)
            result = 1 if sig_a > sig_b else 0
            stack.append(result)
        elif op == "14": #EQ
            a, b = stack.pop(), stack.pop()
            result = 1 if a == b else 0
            stack.append(result)
        elif op == "15": #ISZERO
            a = stack.pop()
            result = 1 if a == 0 else 0
            stack.append(result)
        elif op == "16": #AND
            a, b = stack.pop(), stack.pop()
            stack.append(a & b)
        elif op == "17": #OR
            a, b = stack.pop(), stack.pop()
            stack.append(a | b)
        elif op == "18": #XOR
            a, b = stack.pop(), stack.pop()
            stack.append(a ^ b)
        elif op == "19": #NOT
            a = stack.pop()
            stack.append(MAX_UINT256 + ~a)
        elif op == "1a": #BYTE
            a, b = stack.pop(), stack.pop()
            if a > 31:
                stack.append(0)
            else:
                b_32 = to_32b_hex(b)
                offset = a * 2
                stack.append(int(b_32[offset] + b_32[offset + 1], 16))
        elif op == "1b": #SHL
            a, b = stack.pop(), stack.pop()
            result = hex(b << a)[2:]
            if len(result) > 64:
                result = result[-64:]
            stack.append(int(result, 16))
        elif op == "1c": #SHR
            a, b = stack.pop(), stack.pop()
            result = b >> a
            stack.append(result)
        elif op == "1d": #SAR
            a, b = stack.pop(), stack.pop()
            if a >= BITS_IN_32 and to_32b_hex(b)[0] == "0":
                stack.append(0)
            else:
                b_sig = to_signed(b)
                result = b_sig >> a
                if result < 0:
                    result = MAX_UINT256 + result
                stack.append(result)
        elif op == "50": #POP
            stack.pop()
        elif op == "5f": #PUSH0
            stack.append(0)
        elif op == "60": #PUSH1
            op = code[pc] + code[pc + 1]
            pc += 2
            stack.append(int(op, 16))
        elif op.startswith("6") or op.startswith("7"): #PUSH2 - PUSH32
            (stack, pc) = push_impl(op, code[pc:], stack, pc)
        elif op.startswith("8"): #DUP1 - DUP16
            (stack, pc) = dup_impl(op, stack, pc)
        elif op.startswith("9"): #DUP1 - DUP16
            (stack, pc) = swap_impl(op, stack, pc)
    return (success, stack)

def test():
    script_dirname = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dirname, "..", "evm.json")
    with open(json_file) as f:
        data = json.load(f)
        total = len(data)

        for i, test in enumerate(data):
            # Note: as the test cases get more complex, you'll need to modify this
            # to pass down more arguments to the evm function
            # code = bytes.fromhex(test['code']['bin'])
            code = test['code']['bin']
            (success, stack) = evm(code)

            expected_stack = [int(x, 16) for x in test['expect']['stack']]
            
            if stack != expected_stack or success != test['expect']['success']:
                print(f"❌ Test #{i + 1}/{total} {test['name']}")
                if stack != expected_stack:
                    print("Stack doesn't match")
                    print(" expected:", expected_stack)
                    print("   actual:", stack)
                else:
                    print("Success doesn't match")
                    print(" expected:", test['expect']['success'])
                    print("   actual:", success)
                print("")
                print("Test code:")
                print(test['code']['asm'])
                print("")
                print("Hint:", test['hint'])
                print("")
                print(f"Progress: {i}/{len(data)}")
                print("")
                break
            else:
                print(f"✓  Test #{i + 1}/{total} {test['name']}")

if __name__ == '__main__':
    test()