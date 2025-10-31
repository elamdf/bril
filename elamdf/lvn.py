from cfg import get_blocks
import sys
from collections import OrderedDict
import json


def lvn(fun):
    blocks = list(get_blocks(fun['instrs']))
    changed = False
    for block in blocks:
        new_block = lvn_block(block)
        changed |= new_block != block
        block[:] = new_block
    return changed


def lvn_block(block):
    new_block = []
    table = OrderedDict()  # value tuple -> canoncial variable
    var2num = {}  # each variable's current value number (index in table

    # build table
    for instr in block:
        orig_instr = instr.copy()

        if 'op' in instr and 'args' in instr:

            # find value used
            args = []
            if 'args' in instr:
                for a in instr['args']:
                    if a in var2num:
                        args.append(var2num[a])
                    else:
                        args.append(a)

            if len(args) == 1:
                value = (instr['op'], args[0])
            else:
                value = (instr['op'], args[0], args[1])

            if value in table and table[value]:
                idx = list(table.keys()).index(value)
                if idx == var2num[table[value]]:
                    instr['op'] = "id"
                    instr["args"] = [table[value]]

            if 'dest' in instr:
                table[value] = instr['dest']
                var2num[instr['dest']] = len(table) - 1

            new_block.append(instr)

        else:
            if 'dest' in instr:
                var2num[instr['dest']] = len(table) - 1
            new_block.append(instr)

    return new_block
    # create dest in table if there is one


def lvn_dce():

    prog = json.load(sys.stdin)

    cfg = {}  # label : edges

    for f in prog['functions']:
        while lvn(f):
            pass

    print(json.dumps(prog, indent=1))


if __name__ == "__main__":
    lvn_dce()
