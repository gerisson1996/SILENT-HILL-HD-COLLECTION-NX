#!/usr/bin/env python3
"""
Moves sa2-nx's Renut from SA2's Direct3D addresses to Silent Hill 3's (docs/plano-renut.md).

Both games link XDK 2.0.2xxxx's Direct3D (SA2 21076, SH3 20871): same device layout, same functions. Each SA2
address below was placed in SH3 by tools/d3d_match.py (against Homecoming's image) or by its distance from placed
neighbours (tools/d3d_neighbours.py) with the size and body checked in tools/asm.py; the evidence is in the comment.

Every "sub_XXXXXXXX" (hooks, __imp__ calls, comments) of a mapped address is rewritten in the given files. Run it on
a fresh copy of sa2-nx's sources only: it is not idempotent against partly edited files (it only maps SA2 -> SH3).

Usage:
    python tools/retarget_sa2.py app/src/renut_engine
"""
import os
import re
import sys

SA2_TO_SH3 = {
    # device.cpp
    0x8254FC10: 0x82277C68,  # Direct3D_CreateDevice: match 0.96
    0x8254EEE8: 0x82276BF0,  # D3DDevice_InsertCallback: BeginRingBig + 0xF0 in both, 22 instructions in both
    0x825589D8: 0x82280388,  # D3D::SynchronizeToPresentationInterval: match 0.88
    0x8254EBB8: 0x822768C8,  # CDevice::KickOff: match 0.95
    0x8254E830: 0x82276588,  # CDevice::KickOffSegment: match 0.90
    0x8254EDF8: 0x82276B00,  # CDevice::BeginRingBig: match 0.71; IsFencePending + 0xF8 (SA2 + 0x100)
    0x8254D4B8: 0x82275258,  # D3D::RingBufferDeviceAllocate: BlockOnFence - 0x230 in both
    0x8254D9A8: 0x82275700,  # CDevice::AllocateInlineData: match 0.98
    0x8254DA90: 0x822757E8,  # the ring segment allocator: match 0.97
    0x8254EF40: 0x82276C48,  # D3DDevice_SetRingBufferParameters: after InsertCallback; Homecoming's ring init, 0.79
    0x82558E98: 0x82280848,  # D3DDevice_Swap: match 0.64; SynchronizeToPresentationInterval + 0x4C0 in both
    0x8254D6E8: 0x82275488,  # CDevice::BlockOnFence: match 0.87
    0x8254F400: 0x82277530,  # CBlocker::Check: match 0.85
    0x8254ECF8: 0x82276A08,  # D3DDevice_IsFencePending: match 0.88
    0x8255CB20: 0x82287078,  # D3D::InitializePresentationParameters: match 0.83; ApiState + 0x9D0 in both
    0x8255C150: 0x822866A8,  # D3D::InitializeApiState: match 0.97
    # draw.cpp
    0x82565C60: 0x8228A0F8,  # D3DDevice_DrawVertices: match 0.91
    0x82566078: 0x8228A510,  # D3DDevice_DrawIndexedVertices: match 0.90
    0x82565C18: 0x82289AD0,  # D3DDevice_DrawVerticesUP: 18 instructions in both, BeginVertices then memcpy
    0x82565758: 0x82289610,  # D3DDevice_BeginVertices: 303 instructions (SA2 304), UP's callee
    0x82563978: 0x82295B10,  # D3DDevice_ClearF: match 0.97 (Homecoming's hooked ClearF)
    0x825656F8: 0x82294980,  # D3DDevice_Resolve: reads ClearStencil and pParameters at +92/+100, calls the core
    0x825645A0: 0x82293828,  # the resolve core: match 0.61, the wrapper's only callee
    # shader.cpp
    0x8255E658: 0x82288AA8,  # XGRegisterVertexShader: match 0.94 (memset 872, type 6, physical part at +32)
    0x8255DBF8: 0x82288130,  # XGRegisterPixelShader: type 7, physical part at +24 (Homecoming's notes)
    0x8255E198: 0x82288690,  # D3DDevice_CreateVertexDeclaration: match 0.88; VS - 0x418 (SA2 - 0x4C0)
}


def main():
    pattern = re.compile(r'sub_(8[0-9A-F]{7})')
    changed = 0
    for root, _, files in os.walk(sys.argv[1]):
        for f in files:
            if not f.endswith(('.cpp', '.h', '.cmake')):
                continue
            path = os.path.join(root, f)
            text = open(path, encoding='utf-8', errors='surrogateescape').read()

            def repl(m):
                addr = int(m.group(1), 16)
                return 'sub_%08X' % SA2_TO_SH3[addr] if addr in SA2_TO_SH3 else m.group(0)

            new = pattern.sub(repl, text)
            if new != text:
                open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(new)
                changed += 1
                print('  ' + os.path.relpath(path, sys.argv[1]))
    print('%d files rewritten' % changed)


if __name__ == '__main__':
    main()
