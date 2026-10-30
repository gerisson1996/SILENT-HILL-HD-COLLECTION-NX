#!/usr/bin/env python3
"""
Predicts where SA2's hooked Direct3D functions sit in Silent Hill 3 from the functions already placed.

Both games link XDK 2.0.2xxxx's Direct3D with its object files in the same order, so a function keeps about the same
distance from its neighbours. For each SA2 hook not placed yet, this takes the nearest placed anchor (by SA2 address),
moves by the same distance in SH3 (scaled by the anchors' spacing when there are two around it), and lists SH3's
function starts around that point with their sizes.

Usage:
    python tools/d3d_neighbours.py [--gen app/generated/sh3]
"""
import argparse
import glob
import os
import re

# SA2 address -> SH3 address, from tools/d3d_match.py against Homecoming (docs/plano-renut.md).
ANCHORS = {
    0x8254FC10: 0x82277C68,  # Direct3D_CreateDevice
    0x825589D8: 0x82280388,  # SynchronizeToPresentationInterval
    0x8254EBB8: 0x822768C8,  # KickOff
    0x8254E830: 0x82276588,  # KickOffSegment
    0x8254D9A8: 0x82275700,  # AllocateInlineData
    0x8254DA90: 0x822757E8,  # ring segment allocator
    0x8254D6E8: 0x82275488,  # BlockOnFence
    0x8254F400: 0x82277530,  # CBlocker::Check
    0x8254ECF8: 0x82276A08,  # IsFencePending
    0x82565C60: 0x8228A0F8,  # DrawVertices
    0x82566078: 0x8228A510,  # DrawIndexedVertices
}

WANTED = {
    0x8254EEE8: "D3DDevice_InsertCallback",
    0x8254EDF8: "BeginRingBig (match 82276B00, 0.71)",
    0x8254D4B8: "RingBufferDeviceAllocate",
    0x8254EF40: "D3DDevice_SetRingBufferParameters",
    0x82558E98: "D3DDevice_Swap (match 82280848, 0.64)",
    0x82565C18: "D3DDevice_DrawVerticesUP",
    0x82565758: "D3DDevice_BeginVertices",
    0x82563978: "draw.cpp RAW 82563978",
    0x825656F8: "draw.cpp RAW 825656F8",
    0x8254A200: "resource.cpp RAW 8254A200",
    0x8255E658: "shader.cpp RAW 8255E658",
    0x8255DBF8: "shader.cpp RAW 8255DBF8",
    0x8255E198: "shader.cpp RAW 8255E198",
}


def starts(gen):
    out = set()
    for path in glob.glob(os.path.join(gen, '*_recomp.*.cpp')):
        for m in re.finditer(r'^DEFINE_REX_FUNC\(sub_([0-9A-F]+)\)', open(path, errors='replace').read(), re.M):
            out.add(int(m.group(1), 16))
    return sorted(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--gen', default='app/generated/sh3')
    p.add_argument('--window', type=lambda s: int(s, 0), default=0x180)
    a = p.parse_args()
    fs = starts(a.gen)
    anchors = sorted(ANCHORS.items())
    for sa2, name in sorted(WANTED.items()):
        lower = [t for t in anchors if t[0] <= sa2]
        upper = [t for t in anchors if t[0] > sa2]
        if lower and upper and upper[0][0] - lower[-1][0] < 0x20000:
            (s0, h0), (s1, h1) = lower[-1], upper[0]
            guess = h0 + int((sa2 - s0) * (h1 - h0) / (s1 - s0))
            how = "between %08X and %08X" % (s0, s1)
        else:
            s0, h0 = min(anchors, key=lambda t: abs(t[0] - sa2))
            guess = h0 + (sa2 - s0)
            how = "from %08X" % s0
        near = [f for f in fs if abs(f - guess) <= a.window]
        cells = []
        for f in near:
            i = fs.index(f)
            size = fs[i + 1] - f if i + 1 < len(fs) else 0
            cells.append("%08X(%d)" % (f, size // 4))
        print("%-42s SA2 %08X -> ~%08X (%s)\n    %s" % (name, sa2, guess, how, " ".join(cells)))


if __name__ == '__main__':
    main()
