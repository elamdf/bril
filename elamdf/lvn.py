from cfg import get_blocks, get_local_cfg, get_block_list
import uuid

from util import flatten
import sys
from collections import OrderedDict
import json


def lvn(fun):
    blocks = list(get_blocks(fun['instrs']))
    # cfg = get_local_cfg(get_block_list(fun))
    # print(cfg)
    changed = False
    for block in blocks:

        new_block, _, _ = lvn_block(block)
        changed |= new_block != block
        block[:] = new_block
    fun['instrs'] = flatten(blocks)
    return changed


def lvn_block(block):
    new_block = []

    table = OrderedDict()
    var2num = {}

    for instr in block:

        orig_instr = instr.copy()

        if 'op' in instr:

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
            elif len(args) == 2:
                value = (instr['op'], args[0], args[1])
            else:
                if 'value' in instr:
                    value = (instr['op'], instr['value'])
                else:
                    assert (
                        'dest' not in instr
                    ), "there are no args nor value but there is a dest"
                    value = (instr['op'], None)

            if value in table:  # direct subexp replacement
                idx = list(table.keys()).index(value)
                if idx == var2num[table[value]]:
                    instr['op'] = "id"
                    instr["args"] = [table[value]]
            else:  # look up args by number in
                if 'args' in instr:
                    new_args = []
                    for tbl_idx in args:
                        if isinstance(tbl_idx, int):
                            new_args.append(list(table.values())[tbl_idx])
                        else:  # blindly trust that this is in scope. eventually, we'll wabnt to keep a table/var2num along the cfg
                            new_args.append(tbl_idx)

                        instr['args'] = new_args

            if 'dest' in instr:

                if value in table:
                    idx = list(table.keys()).index(value)
                    var2num[instr['dest']] = idx
                else:
                    table[value] = instr['dest']
                    var2num[instr['dest']] = len(table) - 1

            new_block.append(instr)

        else:

            new_block.append(instr)

    return new_block, table, var2num
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
