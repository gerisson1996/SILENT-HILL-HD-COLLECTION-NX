# SILENT HILL HD COLLECTION NX

🇧🇷 [Português](README.md) · 🇺🇸 **English** · 🇪🇸 [Español](README.es.md)

**Silent Hill 3** (Silent Hill HD Collection, Xbox 360) on the **Nintendo Switch**, as homebrew (`.nro`), through
**static recompilation**. The PowerPC code of `sh3_360.xex` is translated to C++ with
[ReXGlue](https://github.com/rexglue/rexglue-sdk) and compiled for ARM64. It is not emulation: the game runs
natively, with the Xbox 360's Direct3D 9 rewritten on top of deko3d, the Switch's native graphics API.

| | |
|---|---|
| **Version** | V1.0 |
| **State** | Playable: intro, menus, gameplay and audio, at **30 fps** at the console's stock clock |
| **Download** | `sh3.nro` and `SH3-NX-V1.0.zip` in [Releases](https://github.com/gerisson1996/SILENT-HILL-HD-COLLECTION-NX/releases/latest) |
| **Next** | Android and iOS; then Silent Hill 2 from the same collection |

### ☕ Support the project

**We need your help!** The tools I use to make these ports are **paid**, and every donation helps keep them and
keep the project going. Want another game ported or an improvement? **Send your request with your donation**
(write it in the Ko-fi, PayPal or Pix message).

If the port was useful to you, please consider supporting:

- **Ko-fi:** [ko-fi.com/gerissoncassiano](https://ko-fi.com/gerissoncassiano)
- **PayPal:** [Donate with PayPal](https://www.paypal.com/donate/?hosted_button_id=B3YTKT29F5ZLG)
- **Pix:** `pocketneogames@gmail.com`

> [!IMPORTANT]
> This repository **contains no game files** and no code generated from them. You need your own original copy of
> Silent Hill HD Collection for Xbox 360.

---

## What works

- The game runs natively on the Switch: intro, menus, gameplay, audio and the save screen.
- **30 fps** in gameplay at the stock CPU clock (1020 MHz), tested in handheld mode.
- Native deko3d renderer: the game's shaders are translated and compiled on the console itself and kept in
  `deko3d_shaders.bin`, so each variant is compiled only once.
- **720p** handheld and **1080p** docked.
- Port menu (**L + R + Plus**) with image brightness.
- Tested with the PT-BR collection.

## What is missing

- Prebuilding the shader cache, so the console does not compile variants while playing in new areas.
- Testing the whole game from start to finish (only the first areas have been tested so far).
- Android and iOS.
- Silent Hill 2 (`sh2_360.xex`) and the collection's launcher (`default.xex`).

---

## Installing on the Switch

```
sdmc:/switch/sh3-nx/sh3.nro
sdmc:/switch/sh3-nx/game_root/sh3_360.xex   <- from your disc
sdmc:/switch/sh3-nx/game_root/sh3_360/      <- SH3's folder from your disc (with data/)
```

- Needs Atmosphère and hbmenu.
- Open it in **title mode**: hold **R** while launching an installed game, then pick Silent Hill 3 in hbmenu.
- The first visit to each area compiles its shaders (a few seconds); after that they come from the cache.
- Logs go to `sdmc:/switch/sh3-nx/logs/`.

---

## How it works

| Folder | What it is |
|---|---|
| `app/` | The port: code generator configuration (`overrides.toml`, `thunks.toml`, `huecos.toml`), the application (`src/sh3_app.h`) and the Renut renderer (`src/renut_engine`), which replaces the Xbox 360's Direct3D 9 with deko3d. |
| `sdk/` | The [ReXGlue](https://github.com/rexglue/rexglue-sdk) v0.10.0 recompilation SDK, with the Switch layer (memory, files on the SD, threads, audio). |
| `app/thirdparty/` | plume (graphics abstraction), XenosRecomp (Xenos shaders to HLSL/GLSL), uam (deko3d shader compiler) and Dear ImGui. |
| `tools/` | Build scripts and `.xex` analysis (thunks, code gaps, deko3d shaders). |
| `docs/` | Technical notes: [the `.xex` translation](docs/notas-traducao.md) and [the renderer](docs/plano-renut.md). |

---

## Building

### Requirements

- **Windows** with **Visual Studio 2022 Build Tools** ("Desktop development with C++" and "C++ Clang tools") and
  **LLVM clang 18+**.
- **devkitPro** with `switch-dev`, libnx and deko3d.
- **Python 3.10+** and **Git**.
- The repository in a path **without accents or spaces** (e.g. `C:\dev\sh3-nx`).

### Steps

1. Build the code generator:

   ```bat
   tools\build_host.bat
   ```

2. Put your disc's files in `assets\game_root` (`sh3_360.xex` and the `sh3_360\` folder) and translate the game,
   which writes `app/generated/sh3`:

   ```sh
   REXGLUE=sdk/out/win-amd64/rexglue.exe tools/codegen.sh app
   ```

3. Build the `.nro` (deko3d):

   ```bat
   tools\build_switch.bat C:\path\to\nvk_sdk nonvk
   ```

   The result is `out\switch-deko\sh3.nro`.

---

## Credits

- **ReXGlue SDK**: Tom Clay, with parts from [Xenia](https://xenia.jp) (BSD-3-Clause)
- **Renut renderer**: from the sa2-nx and banjo-nx ports
- **XenosRecomp**: hedge-dev (MIT)
- **deko3d and uam**: fincs (devkitPro)
- **Switch port**: RECOMP-GUTO (gerisson1996)
- **Libraries**: libnx/devkitPro, plume, glslang, SPIRV-Tools, FFmpeg, Dear ImGui, toml++, fmt, spdlog; see
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

GPL-3.0 for the main source; the SDK and the libraries keep their own licenses.

Silent Hill is a trademark of Konami Digital Entertainment. This project is not affiliated with it.
