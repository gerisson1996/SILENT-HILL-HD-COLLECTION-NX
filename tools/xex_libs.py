#!/usr/bin/env python3
"""
Lists the XDK libraries a XEX was linked with (the XEX2 optional header 0x000103FF, import libraries, plus the
static library versions in 0x000200FF), to know which Direct3D a game carries.

Usage:
    python tools/xex_libs.py assets/game_root/sh3_360.xex
"""
import struct
import sys


def main():
    data = open(sys.argv[1], "rb").read()
    count = struct.unpack_from(">I", data, 0x14)[0]
    for i in range(count):
        key, value = struct.unpack_from(">II", data, 0x18 + i * 8)
        if key == 0x000200FF:  # static libraries: 8-byte name + 4 x u16 version + u16 flags
            size = struct.unpack_from(">I", data, value)[0]
            off = value + 4
            print("static libraries:")
            while off + 16 <= value + size:
                name = data[off:off + 8].rstrip(b"\0").decode("ascii", "replace")
                major, minor, build, qfe = struct.unpack_from(">HHHH", data, off + 8)
                print("  %-8s %d.%d.%d.%d" % (name, major, minor, build, qfe & 0x7FFF))
                off += 16
        elif key == 0x000103FF:  # import libraries
            size = struct.unpack_from(">I", data, value)[0]
            strings_size, nlibs = struct.unpack_from(">II", data, value + 4)
            table = data[value + 12:value + 12 + strings_size]
            names = [s.decode("ascii", "replace") for s in table.split(b"\0") if s]
            off = value + 12 + strings_size
            print("import libraries:")
            for _ in range(nlibs):
                lib_size = struct.unpack_from(">I", data, off)[0]
                version, min_version, name_index = struct.unpack_from(">IIH", data, off + 0x24 - 4 + 4)[0:3] \
                    if False else struct.unpack_from(">II", data, off + 0x20) + (struct.unpack_from(">H", data, off + 0x28)[0],)
                def v(x):
                    return "%d.%d.%d.%d" % (x >> 28, (x >> 24) & 0xF, (x >> 8) & 0xFFFF, x & 0xFF)
                name = names[name_index & 0xFF] if (name_index & 0xFF) < len(names) else "?"
                print("  %-10s %s (min %s)" % (name, v(version), v(min_version)))
                off += lib_size


if __name__ == "__main__":
    main()
