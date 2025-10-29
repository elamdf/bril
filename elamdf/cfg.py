import json
import sys

terms = "jmp", "br", "ret"


# worry about merging over functions l8r
def get_blocks(instrs):
    cur_block = []
    for inst in instrs:
        if 'op' in inst:
            cur_block.append(inst)
            if inst['op'] in terms:
                yield cur_block
                cur_block = []
        else:  # label
            yield cur_block
            cur_block = [inst]

    yield cur_block


def get_block_list(function):

    block_map = []
    for block in get_blocks(function['instrs']):
        if not block:
            continue

        if "label" in block[0]:
            block_map.append((block[0]['label'], block[1:]))
        else:  # if we aren't in a labeled block, we're in the top block of the function
            if len(block_map) == 0:
                block_map.append((function['name'], block))
            else:
                block_map.append((f"b{len(block_map)}", block))
    return block_map


def get_functions_called(insts):
    funcs = []
    for inst in insts:
        if 'op' in inst and inst['op'] == 'call':
            funcs.extend(inst['funcs'])
    return funcs


def get_local_cfg(block_list):

    cfg = {}
    for idx, (label, insts) in enumerate(block_list):

        term = insts[-1]

        if term['op'] in ["jmp", 'br']:
            succs = term['labels']
        elif term['op'] == "ret":
            succs = []
        else:  # another label
            if idx == len(block_list) - 1:
                # this should only be at the end of the main function ('implicit return')
                succs = []
            else:  # just fall in to the next label
                succs = [block_list[idx + 1][0]]

        succs += get_functions_called(insts)
        cfg[label] = succs
    return cfg


# assume labels are globally unique because I am lazy
def cfg():
    prog = json.load(sys.stdin)
    cfg = {}  # label : edges

    for f in prog['functions']:
        bmap = get_block_list(f)
        c = get_local_cfg(bmap)
        cfg.update(c)

    print(cfg)


if __name__ == "__main__":
    cfg()
