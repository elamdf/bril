import json
import sys


def insert_springboard():
    prog = json.load(sys.stdin)
    springboard = {
        "instrs": [
            {'dest': 'c', 'op': 'const', 'type': 'int', 'value': 3735928559},
            {"args": ["c"], "op": "print"},
            {"op": "ret"},
        ],
        "name": "springboard",
    }

    springboard_call = {"funcs": ["springboard"], "op": "call"}

    assert not any([i['name'] == 'springboard' for i in prog['functions']])
    prog['functions'].append(springboard)

    for f in prog['functions']:
        new_instrs = []
        for idx, inst in enumerate(f['instrs'].copy()):
            if "op" in inst and inst['op'] == 'call':
                new_instrs.append(springboard_call)
            new_instrs.append(inst)
        f["instrs"] = new_instrs
    print(json.dumps(prog))


if __name__ == "__main__":
    insert_springboard()
