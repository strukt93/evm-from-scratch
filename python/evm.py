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
            a = stack.pop()
            b = stack.pop()
            result = add_impl(a, b)
            stack.append(result)
        elif op == "02": #MUL
            a = stack.pop()
            b = stack.pop()
            result = mul_impl(a, b, MAX_UINT256)
            stack.append(result)
        elif op == "03": #SUB
            a = stack.pop()
            b = stack.pop()
            result = sub_impl(a, b)
            stack.append(result)
        elif op == "04": #DIV
            a = stack.pop()
            b = stack.pop()
            result = div_impl(a, b)
            stack.append(result)
        elif op == "06": #MOD
            a = stack.pop()
            b = stack.pop()
            result = mod_impl(a, b)
            stack.append(result)
        elif op == "08": #ADDMOD
            a = stack.pop()
            b = stack.pop()
            mod = stack.pop()
            result = add_impl(a, b)
            result = mod_impl(result, mod)
            stack.append(result)
        elif op == "09": #MULMOD
            a = stack.pop()
            b = stack.pop()
            mod = stack.pop()
            result = mul_impl(a, b, mod)
            result = mod_impl(result, MAX_UINT256)
            stack.append(result)
        elif op == "0a": #EXP
            a = stack.pop()
            b = stack.pop()
            result = exp_impl(a, b)
            stack.append(result)
        elif op == "0b": #SIGNEXTEND
            stack.pop() #Get rid of "b"
            x = stack.pop()
            bin_x = bin(x)[2:]
            bin_x = bin_x if len(bin_x) == 8 else ("0" * (8 - len(bin_x))) + bin_x # Fill with zeros if not 8 bits
            if bin_x[0] == "0":
                stack.append(x) #Push the operand if positive
            else:
                result = ("ff" * 31) + hex(x)[2:] #Else, append with "FF"s (to signal it is a negative number)
                stack.append(int(result, 16)) #Then push the int version to the stack
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