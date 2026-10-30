# SILENT HILL HD COLLECTION NX

🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 **Español**

**Silent Hill 3** (Silent Hill HD Collection, Xbox 360) en **Nintendo Switch**, como homebrew (`.nro`), mediante
**recompilación estática**. El código PowerPC de `sh3_360.xex` se traduce a C++ con
[ReXGlue](https://github.com/rexglue/rexglue-sdk) y se compila para ARM64. No es emulación: el juego corre nativo,
con el Direct3D 9 de Xbox 360 reescrito sobre deko3d, la API gráfica nativa de Switch.

| | |
|---|---|
| **Versión** | V1.0 |
| **Estado** | Jugable: intro, menús, gameplay y audio, a **30 fps** con el reloj original de la consola |
| **Descarga** | `sh3.nro` y `SH3-NX-V1.0.zip` en [Releases](https://github.com/gerisson1996/SILENT-HILL-HD-COLLECTION-NX/releases/latest) |
| **Próximo** | Android e iOS; después Silent Hill 2 de la misma colección |

### ☕ Apoya el proyecto

**¡Necesitamos tu ayuda!** Las herramientas que uso para hacer estos ports son **de pago**, y cada donación ayuda a
mantenerlas y a seguir con el proyecto. ¿Quieres ver otro juego portado o una mejora? **Haz tu pedido junto con tu
donación** (escríbelo en el mensaje de Ko-fi, PayPal o Pix).

Si el port te resultó útil, considera apoyar:

- **Ko-fi:** [ko-fi.com/gerissoncassiano](https://ko-fi.com/gerissoncassiano)
- **PayPal:** [Donar con PayPal](https://www.paypal.com/donate/?hosted_button_id=B3YTKT29F5ZLG)
- **Pix:** `pocketneogames@gmail.com`

> [!IMPORTANT]
> Este repositorio **no contiene ningún archivo del juego** ni el código generado a partir de él. Necesitas tu propia
> copia original de Silent Hill HD Collection para Xbox 360.

---

## Qué funciona

- El juego corre nativo en Switch: intro, menús, gameplay, audio y la pantalla de guardado.
- **30 fps** en el gameplay con el reloj original de la CPU (1020 MHz), probado en modo portátil.
- Renderizador nativo en deko3d: los shaders del juego se traducen y se compilan en la propia consola y se guardan en
  `deko3d_shaders.bin`, así que cada variante se compila una sola vez.
- **720p** en portátil y **1080p** en el dock.
- Menú del port (**L + R + Plus**) con el brillo de la imagen.
- Probado con la colección en PT-BR.

## Qué falta

- Precompilar la caché de shaders, para que la consola no compile variantes durante el juego en las áreas nuevas.
- Probar el juego entero de principio a fin (hasta ahora se probaron las primeras áreas).
- Android e iOS.
- Silent Hill 2 (`sh2_360.xex`) y el lanzador de la colección (`default.xex`).

---

## Instalar en Switch

```
sdmc:/switch/sh3-nx/sh3.nro
sdmc:/switch/sh3-nx/game_root/sh3_360.xex   <- de tu disco
sdmc:/switch/sh3-nx/game_root/sh3_360/      <- la carpeta de SH3 de tu disco (con data/)
```

- Necesita Atmosphère y hbmenu.
- Ábrelo en **modo título**: mantén **R** al abrir un juego instalado y elige Silent Hill 3 en el hbmenu.
- La primera vez en cada área compila sus shaders (unos segundos); después salen de la caché.
- Los logs quedan en `sdmc:/switch/sh3-nx/logs/`.

---

## Cómo funciona

| Carpeta | Qué es |
|---|---|
| `app/` | El port: configuración del generador de código (`overrides.toml`, `thunks.toml`, `huecos.toml`), la aplicación (`src/sh3_app.h`) y el renderizador Renut (`src/renut_engine`), que reemplaza el Direct3D 9 de Xbox 360 por deko3d. |
| `sdk/` | El SDK de recompilación [ReXGlue](https://github.com/rexglue/rexglue-sdk) v0.10.0, con la capa de Switch (memoria, archivos en la SD, hilos, audio). |
| `app/thirdparty/` | plume (abstracción gráfica), XenosRecomp (shaders de Xenos a HLSL/GLSL), uam (compilador de shaders de deko3d) y Dear ImGui. |
| `tools/` | Scripts de compilación y de análisis del `.xex` (thunks, huecos de código, shaders de deko3d). |
| `docs/` | Notas técnicas: [la traducción del `.xex`](docs/notas-traducao.md) y [el renderizador](docs/plano-renut.md). |

---

## Compilar

### Requisitos

- **Windows** con **Visual Studio 2022 Build Tools** ("Desarrollo para el escritorio con C++" y "Herramientas de
  Clang para C++") y **LLVM clang 18+**.
- **devkitPro** con `switch-dev`, libnx y deko3d.
- **Python 3.10+** y **Git**.
- El repositorio en una ruta **sin acentos ni espacios** (p. ej. `C:\dev\sh3-nx`).

### Pasos

1. Compilar el generador de código:

   ```bat
   tools\build_host.bat
   ```

2. Poner los archivos de tu disco en `assets\game_root` (`sh3_360.xex` y la carpeta `sh3_360\`) y traducir el juego,
   lo que genera `app/generated/sh3`:

   ```sh
   REXGLUE=sdk/out/win-amd64/rexglue.exe tools/codegen.sh app
   ```

3. Compilar el `.nro` (deko3d):

   ```bat
   tools\build_switch.bat C:\ruta\al\nvk_sdk nonvk
   ```

   El resultado queda en `out\switch-deko\sh3.nro`.

---

## Créditos

- **ReXGlue SDK**: Tom Clay, con partes de [Xenia](https://xenia.jp) (BSD-3-Clause)
- **Renderizador Renut**: de los ports sa2-nx y banjo-nx
- **XenosRecomp**: hedge-dev (MIT)
- **deko3d y uam**: fincs (devkitPro)
- **Port para Switch**: RECOMP-GUTO (gerisson1996)
- **Bibliotecas**: libnx/devkitPro, plume, glslang, SPIRV-Tools, FFmpeg, Dear ImGui, toml++, fmt, spdlog; ver
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

Licencia GPL-3.0 para el código principal; el SDK y las bibliotecas mantienen sus propias licencias.

Silent Hill es una marca de Konami Digital Entertainment. Este proyecto no tiene relación con ella.
