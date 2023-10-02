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

def evm(code):
    pc = 0
    success = True
    stack = []

    while pc < len(code):
        op = code[pc] + code[pc + 1]
        pc += 2
        if op == "00":
            return (True, stack)
        elif op == "5f":
            stack.append(0)
        elif op == "60":
            op = code[pc] + code[pc + 1]
            pc += 2
            stack.append(int(op, 16))
        elif op.startswith("6") or op.startswith("7"):
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
