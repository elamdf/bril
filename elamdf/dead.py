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


def dce():

    prog = json.load(sys.stdin)

    cfg = {}  # label : edges

    for f in prog['functions']:
        while unused_var_elim(f):
            pass

    print(json.dumps(prog, indent=1))


if __name__ == "__main__":
    dce()
