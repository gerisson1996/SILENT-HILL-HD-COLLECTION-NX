# SILENT HILL HD COLLECTION NX

🇧🇷 **Português** · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)

**Silent Hill 3** (Silent Hill HD Collection, Xbox 360) no **Nintendo Switch**, como homebrew (`.nro`), por
**recompilação estática**. O código PowerPC do `sh3_360.xex` é traduzido para C++ com
[ReXGlue](https://github.com/rexglue/rexglue-sdk) e compilado para ARM64. Não é emulação: o jogo roda nativo, com o
Direct3D 9 do Xbox 360 reescrito sobre o deko3d, a API gráfica nativa do Switch.

| | |
|---|---|
| **Versão** | V1.0 |
| **Estado** | Jogável: intro, menus, gameplay e áudio, a **30 fps** no clock original do console |
| **Download** | `sh3.nro` e `SH3-NX-V1.0.zip` em [Releases](https://github.com/gerisson1996/SILENT-HILL-HD-COLLECTION-NX/releases/latest) |
| **Próximo** | Android e iOS; depois o Silent Hill 2 da mesma coleção |

### ☕ Apoie o projeto

**Precisamos da sua ajuda!** As ferramentas que uso para fazer estes ports são **pagas**, e cada doação ajuda a
mantê-las e a continuar o projeto. Quer ver outro jogo portado ou uma melhoria? **Faça seu pedido junto com a sua
doação** (escreva na mensagem do Ko-fi, do PayPal ou do Pix).

Se o port foi útil para você, considere apoiar:

- **Ko-fi:** [ko-fi.com/gerissoncassiano](https://ko-fi.com/gerissoncassiano)
- **PayPal:** [Doar pelo PayPal](https://www.paypal.com/donate/?hosted_button_id=B3YTKT29F5ZLG)
- **Pix:** `pocketneogames@gmail.com`

> [!IMPORTANT]
> Este repositório **não contém nenhum arquivo do jogo** nem o código gerado a partir dele. Você precisa da sua
> própria cópia original do Silent Hill HD Collection de Xbox 360.

---

## O que já funciona

- O jogo inteiro roda nativo no Switch: intro, menus, gameplay, áudio e a tela de save.
- **30 fps** no gameplay com o clock original da CPU (1020 MHz), testado no modo portátil.
- Renderizador nativo em deko3d: os shaders do jogo são traduzidos e compilados no próprio console e guardados em
  `deko3d_shaders.bin`, então cada variante só é compilada uma vez.
- **720p** no portátil e **1080p** no dock.
- Menu do port (**L + R + Plus**) com o brilho da imagem.
- Testado com a coleção em PT-BR.

## O que falta

- Pré-compilar o cache de shaders, para o console não compilar variantes durante o jogo nas áreas novas.
- Testar o jogo inteiro do começo ao fim (até agora foram testadas as primeiras áreas).
- Android e iOS.
- Silent Hill 2 (`sh2_360.xex`) e o launcher da coleção (`default.xex`).

---

## Instalar no Switch

```
sdmc:/switch/sh3-nx/sh3.nro
sdmc:/switch/sh3-nx/game_root/sh3_360.xex   <- do seu disco
sdmc:/switch/sh3-nx/game_root/sh3_360/      <- a pasta do SH3 do seu disco (com data/)
```

- Precisa de Atmosphère e hbmenu.
- Abra em **modo título**: segure **R** ao abrir um jogo instalado e escolha o Silent Hill 3 no hbmenu.
- A primeira vez em cada área compila os shaders dela (alguns segundos); da segunda em diante já sai do cache.
- Os logs ficam em `sdmc:/switch/sh3-nx/logs/`.

---

## Como funciona

| Pasta | O que é |
|---|---|
| `app/` | O port: configuração do gerador de código (`overrides.toml`, `thunks.toml`, `huecos.toml`), o aplicativo (`src/sh3_app.h`) e o renderizador Renut (`src/renut_engine`), que troca o Direct3D 9 do Xbox 360 por deko3d. |
| `sdk/` | O SDK de recompilação [ReXGlue](https://github.com/rexglue/rexglue-sdk) v0.10.0, com a camada do Switch (memória, arquivos no SD, threads, áudio). |
| `app/thirdparty/` | plume (abstração gráfica), XenosRecomp (shaders do Xenos para HLSL/GLSL), uam (compilador de shaders do deko3d) e Dear ImGui. |
| `tools/` | Scripts de build e de análise do `.xex` (thunks, lacunas de código, shaders do deko3d). |
| `docs/` | Notas técnicas: [tradução do `.xex`](docs/notas-traducao.md) e [renderizador](docs/plano-renut.md). |

---

## Compilar

### Requisitos

- **Windows** com **Visual Studio 2022 Build Tools** ("Desenvolvimento para desktop com C++" e "Ferramentas do C++
  Clang") e **LLVM clang 18+**.
- **devkitPro** com `switch-dev`, libnx e deko3d.
- **Python 3.10+** e **Git**.
- O repositório num caminho **sem acento e sem espaço** (ex.: `C:\dev\sh3-nx`).

### Passos

1. Compilar o gerador de código:

   ```bat
   tools\build_host.bat
   ```

2. Colocar os arquivos do seu disco em `assets\game_root` (o `sh3_360.xex` e a pasta `sh3_360\`) e traduzir o jogo,
   o que gera `app/generated/sh3`:

   ```sh
   REXGLUE=sdk/out/win-amd64/rexglue.exe tools/codegen.sh app
   ```

3. Compilar o `.nro` (deko3d):

   ```bat
   tools\build_switch.bat C:\caminho\para\nvk_sdk nonvk
   ```

   O resultado fica em `out\switch-deko\sh3.nro`.

---

## Créditos

- **ReXGlue SDK**: Tom Clay, com partes do [Xenia](https://xenia.jp) (BSD-3-Clause)
- **Renderizador Renut**: dos ports sa2-nx e banjo-nx
- **XenosRecomp**: hedge-dev (MIT)
- **deko3d e uam**: fincs (devkitPro)
- **Port para Switch**: RECOMP-GUTO (gerisson1996)
- **Bibliotecas**: libnx/devkitPro, plume, glslang, SPIRV-Tools, FFmpeg, Dear ImGui, toml++, fmt, spdlog; veja
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

Licença GPL-3.0 para o código principal; o SDK e as bibliotecas mantêm as suas próprias licenças.

Silent Hill é marca da Konami Digital Entertainment. Este projeto não tem relação com ela.
