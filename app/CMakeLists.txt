# sh3 - Silent Hill 3 (HD Collection), ReXGlue recompiled project
#
# SDK boilerplate lives in generated/rexglue.cmake (written by the codegen).

cmake_minimum_required(VERSION 3.25)
project(sh3 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# As in shh-nx (from sa2-nx): -mearly-ra=none for everything compiled for the console. devkitA64 GCC 16.1's AArch64
# early register allocation pass miscompiled the XDK's streaming copy in other ports. Here, before the SDK is added,
# so its libraries and the LTO link get it too.
option(SH3_SWITCH_EARLY_RA "Leave GCC's AArch64 early register allocation pass on (Switch; miscompiles)" OFF)
if(REXGLUE_PLATFORM_SWITCH AND NOT SH3_SWITCH_EARLY_RA)
    add_compile_options(-mearly-ra=none)
    add_link_options(-mearly-ra=none)
endif()

if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/generated/rexglue.cmake")
    message(FATAL_ERROR "Run the codegen first: REXGLUE=sdk/out/win-amd64/rexglue.exe tools/codegen.sh app")
endif()
include(generated/rexglue.cmake)

set(SH3_SOURCES
    src/main.cpp
)

if(WIN32)
    add_executable(sh3 WIN32 ${SH3_SOURCES})
else()
    add_executable(sh3 ${SH3_SOURCES})
endif()

# GPU_PLUGINS puts the graphics backend DLL (rexgpu-xenos) next to the .exe; src/sh3_app.h
# sets gpu_plugin=xenos by default so it is loaded.
rexglue_setup_target(sh3 GPU_PLUGINS xenos)

# Renut's Direct3D-level renderer (docs/plano-renut.md), sa2-nx's, moved to Silent Hill 3's Direct3D (same XDK
# generation as SA2): no PM4 ring, no EDRAM; the game's Direct3D draws natively through plume. Chosen at boot with
# sh3_renderer = "renut"; the emulated GPU stays the default and the reference.
option(SH3_RENUT_RENDERER "Link Renut's Direct3D-level renderer (sh3_renderer = renut)" ON)
if(SH3_RENUT_RENDERER)
    include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/sh3_renut_gpu.cmake")
endif()

# sh3_register.cpp is one huge function that registers every game function; GCC at -O3 spends many minutes on it.
# It only runs once at startup, so -O1 costs nothing. The precompiled header is built at the target's optimization
# level, and clang refuses it at another one, so this file goes without it.
set_source_files_properties("${CMAKE_CURRENT_SOURCE_DIR}/generated/sh3/sh3_register.cpp"
    PROPERTIES COMPILE_OPTIONS "-O1" SKIP_PRECOMPILE_HEADERS ON)

# Nintendo Switch: sh3.nro next to the ELF. On the SD card it goes in sdmc:/switch/sh3-nx/ with the
# game_root/ folder beside it.
if(REXGLUE_PLATFORM_SWITCH)
    # Homebrew menu icon: a 256x256 JPEG, as elf2nro expects, cut from the dashboard art on the user's own disc
    # (nxeart). Not distributed; without it the NRO gets the default libnx icon.
    set(SH3_ICON "${CMAKE_CURRENT_SOURCE_DIR}/../tools/switch/icon/sh3_icon.jpg")
    set(SH3_ICON_ARG)
    if(EXISTS "${SH3_ICON}")
        set(SH3_ICON_ARG ICON "${SH3_ICON}")
    endif()
    rexglue_switch_add_nro(sh3
        NAME "Silent Hill 3"
        AUTHOR "RECOMP-GUTO"
        VERSION "1.0"
        ${SH3_ICON_ARG})
endif()
