#!/usr/bin/env python3
"""
Lists the Direct3D functions a Renut tree hooks, as the names file tools/d3d_match.py reads:

    0x82911D68 = { name = "D3DDevice_Swap_hook" }

Each BANJO_RENUT_HOOK*(sub_ADDR[, function]) line gives the address; the name is the hook function, or the trailing
comment for RAW hooks (or sub_ADDR when there is neither). An address hooked twice keeps its first name.

Usage:
    python tools/renut_hook_names.py C:/dev/shh-nx/app/src/renut_engine > out/shh_hooks.toml
"""
import os
import re
import sys

HOOK = re.compile(r'BANJO_RENUT_HOOK\w*\(sub_([0-9A-Fa-f]{8})(?:\s*,\s*(\w+))?\)[^\n]*?(?://\s*(.*))?$', re.M)


def main():
    seen = {}
    for root, _, files in os.walk(sys.argv[1]):
        for f in sorted(files):
            if not f.endswith(('.cpp', '.h')):
                continue
            text = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
            for m in HOOK.finditer(text):
                addr = int(m.group(1), 16)
                name = m.group(2) or (m.group(3) or '').strip() or 'sub_%08X' % addr
                name = re.sub(r'[^\w:]+', '_', name).strip('_')
                seen.setdefault(addr, (name, f))
    for addr, (name, f) in sorted(seen.items()):
        print('0x%08X = { name = "%s" }   # %s' % (addr, name, f))


if __name__ == '__main__':
    main()
