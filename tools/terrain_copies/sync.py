"""Give every per-unit `hills`/`desert` block, and every `terrain = { type = "hills"/"desert" ... }` weather entry,
a `desert_hills`/`deep_desert` twin with the same body.

    python tools/terrain_copies/sync.py          # insert missing twins
    python tools/terrain_copies/sync.py --check  # report missing twins and twins whose body differs
"""
import glob
import os
import re
import sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAIRS = {"hills": "desert_hills", "desert": "deep_desert"}
SKIP = {os.path.join("common", "terrain")}
TERRAIN_KEYS = {"attack", "defence", "movement"}


def tokenize(text):
    toks = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n":
            i += 1
        elif c == "#":
            while i < n and text[i] != "\n":
                i += 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            toks.append(("str", i, j + 1))
            i = j + 1
        elif c in "{}=<>":
            toks.append((c, i, i + 1))
            i += 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n#{}=<>\"":
                j += 1
            toks.append(("word", i, j))
            i = j
    return toks


def parse(text):
    """Return list of nodes: (key, key_start, block_start, block_end_exclusive, children) for `key = { ... }` blocks."""
    toks = tokenize(text)
    root = []
    stack = [root]
    open_nodes = []
    k = 0
    while k < len(toks):
        t = toks[k]
        if t[0] == "word" and k + 2 < len(toks) and toks[k + 1][0] == "=" and toks[k + 2][0] == "{":
            node = [text[t[1]:t[2]], t[1], toks[k + 2][1], None, []]
            stack[-1].append(node)
            stack.append(node[4])
            open_nodes.append(node)
            k += 3
            continue
        if t[0] == "{":
            node = [None, t[1], t[1], None, []]
            stack[-1].append(node)
            stack.append(node[4])
            open_nodes.append(node)
        elif t[0] == "}":
            if not open_nodes:
                raise ValueError(f"unbalanced '}}' at offset {t[1]}")
            node = open_nodes.pop()
            node[3] = t[2]
            stack.pop()
        k += 1
    if open_nodes:
        raise ValueError(f"unclosed '{{' at offset {open_nodes[-1][1]}")
    return root


def walk(nodes, parent=None):
    for node in nodes:
        yield node, nodes
        yield from walk(node[4], node)


def body(text, node):
    inner = text[node[2] + 1: node[3] - 1]
    return " ".join(inner[a:b] for _, a, b in tokenize(inner))


TYPE_RE = re.compile(r'(\btype\s*=\s*")(%s)(")' % "|".join(PAIRS))


def terrain_type(text, node):
    """For `terrain = { type = "hills" ... }` entries (common/weather.txt): the quoted type, else None."""
    if node[0] != "terrain":
        return None
    m = TYPE_RE.search(text, node[2], node[3])
    if m and m.group(2) in PAIRS:
        return m
    return None


def typed_body(text, node):
    return re.sub(r'type = "\w+"', "type", body(text, node))


def line_end_after(text, pos, default):
    m = re.compile(r"[ \t]*(#[^\r\n]*)?(\r?\n)").match(text, pos)
    return m.group(2) if m else default


def process(path, check):
    raw = open(path, "rb").read()
    text = raw.decode("latin-1")
    nl = "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"
    if not re.search(r"(?<![\w.])(%s)\s*=\s*\{" % "|".join(PAIRS), text) and not TYPE_RE.search(text):
        return 0, []
    try:
        tree = parse(text)
    except ValueError as e:
        return 0, [f"cannot parse ({e}); skipped"]
    inserts = []
    problems = []
    for node, siblings in walk(tree):
        key = node[0]
        line = text.count("\n", 0, node[1]) + 1
        typed = terrain_type(text, node)
        if typed:
            src, dst = typed.group(2), PAIRS[typed.group(2)]
            twins = [s for s in siblings if s[0] == "terrain" and (terrain_type(text, s) is None)
                     and re.search(r'\btype\s*=\s*"%s"' % dst, text[s[2]:s[3]])]
            if twins:
                if typed_body(text, twins[0]) != typed_body(text, node):
                    problems.append(f'type "{dst}" differs from type "{src}" at line {line}')
                continue
            copy = text[node[1]:typed.start(2)] + dst + text[typed.end(2):node[3]]
        elif key in PAIRS:
            keys = set(re.findall(r"[A-Za-z_]+(?=\s*=)", text[node[2] + 1: node[3] - 1]))
            if not keys <= TERRAIN_KEYS:
                problems.append(f"{key} block at line {line} has non-terrain keys {sorted(keys - TERRAIN_KEYS)}; skipped")
                continue
            twins = [s for s in siblings if s[0] == PAIRS[key]]
            if twins:
                if body(text, twins[0]) != body(text, node):
                    problems.append(f"{PAIRS[key]} differs from {key} at line {line}")
                continue
            copy = PAIRS[key] + text[node[1] + len(key): node[3]]
        else:
            continue
        line_start = text.rfind("\n", 0, node[1]) + 1
        indent = text[line_start:node[1]]
        sep = line_end_after(text, node[3], nl) + indent if indent.strip() == "" else " "
        inserts.append((node[3], sep + copy))
    if not check and inserts:
        for pos, s in sorted(inserts, reverse=True):
            text = text[:pos] + s + text[pos:]
        parse(text)
        open(path, "wb").write(text.encode("latin-1"))
    return len(inserts), problems


def main():
    check = "--check" in sys.argv
    total = 0
    bad = 0
    for path in sorted(glob.glob(os.path.join(MOD, "common", "**", "*.txt"), recursive=True)):
        rel = os.path.relpath(path, MOD)
        if any(rel.startswith(s + os.sep) for s in SKIP):
            continue
        n, problems = process(path, check)
        total += n
        if n:
            print(f"{'missing' if check else 'added'} {n:3d}  {rel}")
        for p in problems:
            bad += 1
            print(f"  ! {rel}: {p}")
    print(f"{'missing' if check else 'added'} {total} twin blocks, {bad} problems")
    return 1 if check and (total or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
