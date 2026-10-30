# Silent Hill 3 (HD Collection), Nintendo Switch port (sh3-nx)

Unofficial fan project, not affiliated with Konami. A native Switch port of Silent Hill 3 from the Xbox 360
Silent Hill HD Collection: the PowerPC code of `sh3_360.xex` is statically recompiled to C++ with
[ReXGlue](https://github.com/rexglue/rexglue-sdk) and built for the Switch with devkitA64 and libnx. It is not an
emulator. Android and iOS are planned next.

Nothing from the game is in this repository. You need your own Xbox 360 copy of the game.

`sdk/` and `tools/` started as a copy of shh-nx's (Silent Hill: Homecoming). They are this project's own from then
on: fixes here do not go back there, and the other way round.

## Status (V1.0, 2026-10-30)

| Platform | State |
|---|---|
| Nintendo Switch | V1.0: intro, menus and gameplay at 30 fps at the stock clock (CPU 1020 MHz) |
| Android | planned |
| iOS | planned |

### O que já funciona

- Silent Hill 3 roda nativo no Switch (NRO), sem emulador: intro, menus, gameplay, áudio e a tela de save.
- 30 fps no gameplay com o clock original da CPU (1020 MHz), testado no modo portátil.
- Renderer nativo em deko3d (Renut): shaders do jogo traduzidos e compilados no próprio console, com cache em
  `deko3d_shaders.bin` no cartão.
- Resolução 720p no portátil e 1080p no dock (`sh3_resolution`, `sh3_resolution_docked`).
- Brilho ajustável (`sh3_output_gamma`) e menu do port (L+R+Plus).
- Otimizações de CPU no gerador de código (registradores como variáveis locais, `skip_msr`, divisões e conversões
  inline), que levaram o gameplay de 20 para 30 fps.
- Corrigido: crash ao entrar na primeira área (falsos thunks em `app/thunks.toml`) e crash na tela de save (o leitor
  JPEG do D3DX usa `setjmp`/`longjmp`, agora declarados em `app/overrides.toml`).

### O que falta

- Pré-compilar o cache de shaders (`tools/deko3d_variant_cache.py`), para o console não compilar variantes durante o
  jogo nas áreas novas.
- Testar o jogo inteiro do começo ao fim; até agora foram testadas as primeiras áreas.
- Android e iOS.
- Silent Hill 2 (`sh2_360.xex`) e o launcher da coleção (`default.xex`): ainda não traduzidos.

### Notes from the translation

- Game: Title ID `4B4E0845`, Media ID `625FCB0C`, version 0.0.0.5, XEX file time 2012-02-22. Code 820A0000-823E70FC.
- The first codegen failed on two branch targets with no function; they are declared in `app/overrides.toml`.
  It then writes 59 C++ files (about 60 MB) in a few seconds.
- The first run died on `Call to invalid or unregistered function at guest address 0x8237FF20`: a run of
  "this" adjusting thunks (`addi r3,r3,-4; b method`) folded together with the function after it. `tools/thunks.py`
  lists them all (45 thunks, 11 glued functions) in `app/thunks.toml`. `tools/huecos.py --min 8` plus
  `tools/huecos_conflictos.py` leave 79 gaps in `app/huecos.toml`; the codegen then gives no warnings.
- `NtQueryInformationFile(XFileXctdCompressionInformation)` is unimplemented; the game asks at every file open and
  goes on without it (logged once).

## The disc

| File | What |
|---|---|
| `default.xex` + `data\` | The collection's launcher (choose SH2 or SH3). Not translated: this port starts SH3 directly |
| `sh2_360.xex` + `sh2_360\` | Silent Hill 2. Not part of this project yet |
| `sh3_360.xex` + `sh3_360\data\` | Silent Hill 3, about 3.7 GB in 7,142 files |

The whole disc folder is the game root (`game:\`), as on the console; `app/src/sh3_app.h` loads
`game:\sh3_360.xex` instead of `default.xex`.

## Building

The build runs on Windows: Visual Studio 2022 Build Tools, LLVM clang 18+, Python 3.10+, Git and devkitPro
(devkitA64, libnx, deko3d).

Code generator:

```bat
tools\build_host.bat
```

Put the disc files in `assets\game_root`, then translate the game:

```sh
REXGLUE=sdk/out/win-amd64/rexglue.exe tools/codegen.sh app
```

The C++ goes to `app/generated/sh3` and the log to `app/codegen.log`. Then the Switch NRO (Renut on deko3d):

```bat
tools\build_switch.bat C:\path\to\nvk_sdk nonvk
```

It writes `out\switch-deko\sh3.nro`; copy it to `sdmc:/switch/sh3-nx/` with the shader package.

## License

GPL-3.0 for the main source, inherited from shh-nx and nfsmw-nx. The SDK and third-party parts keep their own
licenses; see `THIRD_PARTY_NOTICES.md`.
