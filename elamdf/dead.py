from collections import OrderedDict
import json
import sys
from cfg import get_blocks


# stupid version
def unused_var_elim(fun):
    blocks = list(get_blocks(fun['instrs']))
    used = set()
    for block in blocks:
        for inst in block:
            if 'args' in inst:
                for a in inst['args']:
                    used.add(a)

    changed = False

    for block in blocks:
        new_block = [i for i in block if "dest" not in i or i['dest'] in used]
        changed |= len(block) != len(new_block)
        block[:] = new_block

    fun['instrs'] = [inst for inst in block for block in blocks]

    return changed


def clobbered_var_elim(fun):
    changed = False
    blocks = list(get_blocks(fun['instrs']))

    for block in blocks:
        unused = {}  # var : inst that last overwrote it

        to_remove = []
        for inst in block:

            if 'args' in inst:
                for a in inst['args']:
                    if a in unused:
                        del unused[a]
            if 'dest' in inst:
                dest = inst['dest']
                if dest in unused:
                    to_remove.append(unused[dest])

                unused[dest] = inst

        changed |= len(to_remove) > 0
        block[:] = [i for i in block if i not in to_remove]

    fun['instrs'] = [inst for inst in block for block in blocks]

    return changed


def dce():

    prog = json.load(sys.stdin)

    cfg = {}  # label : edges

    for f in prog['functions']:
        while unused_var_elim(f) or clobbered_var_elim(f):
            pass

    print(json.dumps(prog, indent=1))


if __name__ == "__main__":
    dce()
