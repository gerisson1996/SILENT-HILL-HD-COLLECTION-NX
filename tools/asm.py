#!/usr/bin/env python3
"""
Prints the PowerPC of generated functions, from the "// <asm>" comment the codegen writes per instruction.

Usage:
    python tools/asm.py 8228A058 [8228A0F8 ...] [--gen app/generated/sh3] [--max 80]
"""
import argparse
import glob
import os
import re


def main():
    p = argparse.ArgumentParser()
    p.add_argument('addrs', nargs='+')
    p.add_argument('--gen', default='app/generated/sh3')
    p.add_argument('--max', type=int, default=80)
    a = p.parse_args()
    wanted = {x.upper().replace('0X', '').replace('SUB_', '') for x in a.addrs}
    for path in sorted(glob.glob(os.path.join(a.gen, '*_recomp.*.cpp'))):
        text = open(path, errors='replace').read()
        for m in re.finditer(r'^DEFINE_REX_FUNC\(sub_([0-9A-F]+)\)', text, re.M):
            if m.group(1) not in wanted:
                continue
            end = text.find('\nDEFINE_REX_FUNC(', m.end())
            body = text[m.end(): end if end > 0 else len(text)]
            lines = re.findall(r'^\s*// (.+)$', body, re.M)
            addr = int(m.group(1), 16)
            print('== sub_%s (%d instructions)' % (m.group(1), len(lines)))
            for i, line in enumerate(lines[: a.max]):
                print('  %08X  %s' % (addr + 4 * i, line))
            if len(lines) > a.max:
                print('  ...')


if __name__ == '__main__':
    main()
