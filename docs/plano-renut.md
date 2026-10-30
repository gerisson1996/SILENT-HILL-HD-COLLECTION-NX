# Plan: Renut on plume/deko3d for Silent Hill 3 (HD Collection)

Why: the first console run (NRO 7B76378E, 2026-10-29) works with the emulated Xenos GPU on NVK, at about 3 fps.
Every working ReXGlue Switch port of a 3D game draws through Renut's Direct3D-level renderer on deko3d instead
(sa2-nx, mk9-nx, usf4-nx, mgr-nx-deko, naruto-nx, and shh-nx for Homecoming).

## What Silent Hill 3 has in its favour: SA2's XDK

`tools/xex_libs.py out/sh3_360.xex` (the XEX header's static libraries):

| Game | D3D9 / XDK |
|---|---|
| Silent Hill 3 HD (2012) | 2.0.20871 |
| Sonic Adventure 2 (sa2-nx, where Renut is maintained) | 2.0.21076 |
| Banjo N&B (where Renut was written) | 2.0.7645 |
| Silent Hill: Homecoming (shh-nx) | 2.0.6690 |

The device offsets in SH3's own code are SA2's, not N&B's (the ones shh-nx had to put back):

| Field | SH3 | SA2 (sa2-nx `d3d.h`) | N&B / Homecoming |
|---|---|---|---|
| current fence tag | 11036 | 11036 | 10908 |
| completed-fence pointer | 11024 | - | 10896 |
| KickOff flags | 11068 | - | 10940 |
| in-KickOff word | 13600 | - | 13232 |
| swap count | 16968 | 16968 | 16560 |

(IsFencePending, KickOff and Swap in `app/generated/sh3`, against shh-nx's.) So the base is sa2-nx's
`renut_engine` with its own values, not shh-nx's retargeted copy. shh-nx is still the reference for what had to be
added for a game other than SA2 (the game-side hooks, the shader package build, deko3d fixes), copied by hand.

## Where SH3's Direct3D is

The library sits at about 0x82274000-0x822A0000. `tools/d3d_match.py` (from sa2-nx), with Homecoming's image and
hooks as the reference (`tools/renut_hook_names.py` lists them; there is no SA2 or N&B image here), places the core:

| Function | Homecoming | SH3 | score |
|---|---|---|---|
| Direct3D_CreateDevice | 82910928 | 82277C68 | 0.96 |
| CDevice::KickOff | 8290FBB8 | 822768C8 | 0.95 |
| CDevice::KickOffSegment | 8290FA30 | 82276588 | 0.90 |
| ring segment allocator | 8290F8A0 | 822757E8 | 0.97 |
| CDevice::AllocateInlineData | 8290EE48 | 82275700 | 0.98 |
| CDevice::BlockOnFence | 8290F4A0 | 82275488 | 0.87 |
| CBlocker::Check (?) | 82910448 | 82277530 | 0.85 |
| D3DDevice_IsFencePending | 8290FCF0 | 82276A08 | 0.88 |
| SynchronizeToPresentationInterval | 82911880 | 82280388 | 0.88 |
| D3DDevice_Clear(F) | 8290E528 | 82295B10 | 0.97 |
| D3DDevice_SetIndices | 82907640 | 8227A558 | 0.94 |
| D3DDevice_DrawVertices | 82908408 | 8228A0F8 | 0.91 |
| D3DDevice_DrawIndexedVertices | 829087F8 | 8228A510 | 0.90 |
| 82909990 / 82909D60 | | 82288AA8 / 82288690 | 0.94 / 0.88 |
| 82911000 | | 822850F8 | 0.93 |
| D3DDevice_Swap | 82911D68 | 82280848 | 0.64, check |
| BeginRingBig | 8290FDD8 | 82276B00 | 0.71, check |
| Resolve | 82914EA8 | 82293828 | 0.61, check |

Full output: `out/d3d_match_shh.txt`. Hypotheses until a hook on them works.

Homecoming's other hooks are on its *game* functions (its XDK inlines the setters), so they do not carry over. SA2's
286 hooks (255 in `state.cpp`) are the list to place in SH3: the setters are real functions in this XDK.

## What SA2's setup needs, and what it does not

- SA2 hooks no state setter (`state.cpp` is not built): its own setters write the device the draws read, and so do
  Silent Hill 3's (same layout). Only 24 hooks: device 14, draw 6, resource 1, shader 3.
- `BANJO_RENUT_HOOK_SHARED` defines only `renut_native_sub_X`; in sa2-nx SA2's own renderer hooks those addresses and
  yields. Silent Hill 3 has none, so `app/src/sh3_renut_shared.cpp` hooks the six and yields. Without it: the device
  ran at 30 fps with "0 draws".
- SH3 draws with DrawIndexedVerticesUP too (sub_8228A058, its renderer's vtable method sub_822E40E0): N&B's hook is
  wired there.
- The rest of the SA2 addresses in the sources (resource.cpp, d3d_native_state.cpp, the caps and Fusion constants,
  BeginTiling / EndTiling) are in N&B paths SA2 does not build or does not wire: dead here too. The one data address
  that is live is VdGlobalDevice's import slot: 0x82000760.
- SA2's app pieces the hooks include are stubbed: `sa2_capture.h` (lockstep capture, off), `g_sa2_game_frames` and the
  relaxed-vsync switch (off) in `sh3_compat`.
- Pending: D3DResource_Destroy (sub_8254A200 in SA2) is not placed, so the hook is off and host objects of destroyed
  resources leak. BeginTiling / EndTiling (Homecoming hooks them) if SH3 tiles.
- `[sh3 diag]` in `draw.cpp`: the first calls of each draw, clear and resolve hook. Temporary.

## State (2026-10-29)

PC, `sh3.exe --sh3_renderer=renut`: device created by Renut, 30.00 fps paced by sa2-nx's pacing, the intro movie
drawn (about 60 draws a second, ClearF and Resolve every frame), GPU 0.76 ms a frame. The shader cache is built from
the shaders Renut captures at run time (`out/pc/shader_capture` -> `app/shaders`): 70 after the intro; every new
area adds more, and the next build translates them.

## Stages (each verified before the next)

1. **Vendor sa2-nx's Renut** into `app/` (renut_engine, plume, reblue-XenosRecomp, imgui, uam, app/cmake), a boot key
   `sh3_renderer` (`xenos` / `renut`), the emulated GPU kept as the reference. Gate: builds and links on the PC.
2. **Device hooks** on the addresses above (CreateDevice, KickOff, fences, Swap, Clear, Resolve). Gate: device
   created, fences, Swap presenting the clear colour.
3. **Shaders, resources, draws and setters** (SA2's list placed one by one in SH3). Gate: the intro and the title
   render through Renut on the PC.
4. **Switch build on deko3d** with the shader package from the PC. Gate: 30 fps target on the console.

## Switch (2026-10-30)

- NRO 43691495: first deko3d run. Intro 30 fps; gameplay 20 fps, CPU-bound (Main XThread ~35 ms a frame at
  1020 MHz, GPU 8-11 ms). The user's test: CPU at 1326 MHz holds 30 fps.
- Crash entering the first area (NRO 6678A419): `Unresolved call from 0x82251E74 to 0x82251DE0`. `tools/thunks.py`
  had taken 8 loop tails (`addi; b` a few bytes away) for this-adjust thunks; commented out in `app/thunks.toml`,
  with the function splits made after them. The generated code has no `REX_FATAL` left (count it, not only the
  codegen's warnings).
- Brightness `sh3_output_gamma` (0.6 on the Switch) and the menu (F5 / L+R+Plus), from shh-nx.
- Resolution `sh3_resolution` (handheld, 720p) and `sh3_resolution_docked` (1080p), from shh-nx's. SH3's shaders
  read no texture scale code and no `resolution_scale`: the passes scale1 / fragscale change nothing (package
  compared with and without them), so `PackageScales()` accepts a package without either.
