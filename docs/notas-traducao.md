# Notes from the translation of `sh3_360.xex`

- Game: Title ID `4B4E0845`, Media ID `625FCB0C`, version 0.0.0.5, XEX file time 2012-02-22. Code 820A0000-823E70FC.
- The first codegen failed on two branch targets with no function; they are declared in `app/overrides.toml`.
  It then writes 59 C++ files (about 60 MB) in a few seconds.
- The first run died on `Call to invalid or unregistered function at guest address 0x8237FF20`: a run of
  "this" adjusting thunks (`addi r3,r3,-4; b method`) folded together with the function after it. `tools/thunks.py`
  lists them all (45 thunks, 11 glued functions) in `app/thunks.toml`. `tools/huecos.py --min 8` plus
  `tools/huecos_conflictos.py` leave 79 gaps in `app/huecos.toml`; the codegen then gives no warnings.
- Crash entering the first area: `tools/thunks.py` had taken 8 loop tails (`addi; b` a few bytes away) for
  this-adjust thunks; they are commented out in `app/thunks.toml`.
- Crash on the save screen: D3DX's image loader `longjmp`s out of its JPEG reader; `setjmp` (`0x823CC7C0`) and
  `longjmp` (`0x823CC380`) are declared in `app/overrides.toml`.
- Gameplay went from 20 to 30 fps at the stock CPU clock with the code generator's register-as-local options
  (`app/overrides.toml`, top).
- `NtQueryInformationFile(XFileXctdCompressionInformation)` is unimplemented; the game asks at every file open and
  goes on without it (logged once).

## The disc

| File | What |
|---|---|
| `default.xex` + `data\` | The collection's launcher (choose SH2 or SH3). Not translated: this port starts SH3 directly |
| `sh2_360.xex` + `sh2_360\` | Silent Hill 2. Not part of this project yet |
| `sh3_360.xex` + `sh3_360\data\` | Silent Hill 3, about 3.7 GB in 7,142 files |

The game root (`game:\`) is the folder with `sh3_360.xex`, as on the console; `app/src/sh3_app.h` loads
`game:\sh3_360.xex` instead of `default.xex`.
