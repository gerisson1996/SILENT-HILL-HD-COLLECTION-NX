// sh3 - Silent Hill 3 (HD Collection), ReXGlue recompiled project
//
// Customize the app by overriding virtual hooks from rex::ReXApp.

#pragma once

#include <rex/cvar.h>
#include <rex/filesystem.h>
#include <rex/logging.h>
#include <rex/input/read_hook.h>
#include <rex/rex_app.h>
#include <rex/ui/keybinds.h>
#include <rex/ui/overlay/quick_settings.h>

#include <filesystem>
#include <system_error>
#include <thread>
#include <vector>

#if REX_PLATFORM_SWITCH
#include <rex/ui/switch_apm.h>
#endif

// Included once (main.cpp), so the key is defined here.
REXCVAR_DEFINE_BOOL(sh3_official_clocks, true, "SH3",
                    "Switch: ask for Nintendo's official clock profiles (docked GPU 768 MHz, handheld GPU 460.8 MHz); "
                    "an overclock tool such as sys-clk still wins over them")
    .lifecycle(rex::cvar::Lifecycle::kInitOnly);

#if SH3_RENUT_RENDERER
#include "renut_engine/gpu/banjo_renut_select.h"
#include "renut_engine/gpu/overlay/app_integration.h"
#endif

class Sh3App : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<Sh3App>(new Sh3App(ctx, "sh3", PPCImageConfig));
  }

  // Settings the game needs, so that a plain "sh3.exe" starts like the long command line.
  // Only the ones nobody set are touched: the command line still wins.
  void OnPostInitLogging() override {
    // Without a GPU plugin the game runs but the runtime discards its graphics calls and the window stays black.
    // It has to be set here: SetupPresentation reads it right after.
    //
    // Not with Renut's renderer (sh3_renderer = renut), as in shh-nx: its hooks take the game's Direct3D, and the
    // emulated Xenos GPU must not take its share of the guest's physical window (both would be drawing).
    bool renut = false;
#if SH3_RENUT_RENDERER
    renut = banjo::renut_gpu::Active();
    if (renut) {
      // As in shh-nx (its perfil-shh.md): the code generation marks no store cards, so the exact streams would hash
      // every vertex and index copy on the render thread (1.5 GB in 10 s in Homecoming); the background verifier
      // proves them instead.
      SetIfNotRequested("banjo_renut_exact_streams", "false");
    }
#endif
    if (!renut)
      SetIfNotRequested("gpu_plugin", "xenos");
    // No asset pack, as in shh-nx: on the console's first boot the SDK spent 1 min 45 s listing the 7,142 files
    // before it started copying 3.7 GB into a second copy on the SD card. The folder is read as it is.
    SetIfNotRequested("asset_pack_build", "false");
#if !REX_PLATFORM_SWITCH
    // Keyboard and mouse in addition to the gamepad.
    SetIfNotRequested("mnk_mode", "true");
#else
    // As in shh-nx (SHH-05): Silent Hill is dark by design and a handheld screen shows it darker still; 0.6 is what the
    // user settled on for Homecoming's console. The menu (L+R+Plus) changes it.
    SetIfNotRequested("sh3_output_gamma", "0.6");
    // As in shh-nx: Nintendo's official clock profiles, docked GPU 768 MHz and handheld GPU 460.8 MHz (switch_apm.h);
    // Horizon changes between them on docking. Its own thread: it waits to log the clocks it got. Not detached:
    // libnx has no pthread_detach, and std::thread::detach throws ENOSYS there (std::terminate at boot, NRO
    // C737FC3A); the thread object is left alive instead, never joined or destroyed.
    if (REXCVAR_GET(sh3_official_clocks))
      new std::thread([] { RexSwitchApmOfficialClocks([](const char* line) { REXLOG_INFO("{}", line); }); });
#endif
  }

  // The disc root is game:\, as on the console; the launcher (default.xex) is skipped and SH3's own XEX is loaded.
  void OnLoadXexImage(std::string& xex_image) override { xex_image = "game:\\sh3_360.xex"; }

  // Without --game_data_root (a double click on sh3.exe), look for the game files ourselves:
  // a "game_root" folder next to the exe (the layout of a package), then the project's
  // assets/game_root (the exe built in out/pc). The first one with sh3_360.xex wins.
  void OnConfigurePaths(rex::PathConfig& paths) override {
    if (!paths.game_data_root.empty()) {
      return;
    }
    const auto exe_dir = rex::filesystem::GetExecutableFolder();
    for (const auto& candidate : {exe_dir / "game_root", exe_dir / ".." / ".." / "assets" / "game_root"}) {
      std::error_code ec;
      if (std::filesystem::is_regular_file(candidate / "sh3_360.xex", ec)) {
        paths.game_data_root = std::filesystem::weakly_canonical(candidate, ec);
        if (ec) {
          paths.game_data_root = candidate;
        }
        REXLOG_INFO("Game files found at {}", paths.game_data_root.string());
        return;
      }
    }
  }

#if SH3_RENUT_RENDERER
  // As in shh-nx and sa2-nx: Renut's renderer starts once the paths are final (the window and its drawer exist by
  // then) and follows every window resize; the SDK's menus are drawn by its present.
  std::unique_ptr<rex::ui::ImmediateDrawer> OnCreateImmediateDrawer() override {
    if (banjo::renut_gpu::Active())
      return renut::gpu::CreateOverlayDrawer();
    return rex::ReXApp::OnCreateImmediateDrawer();
  }

  void OnWindowPixelSizeChanged(uint32_t pixel_width, uint32_t pixel_height) override {
    rex::ReXApp::OnWindowPixelSizeChanged(pixel_width, pixel_height);
    if (banjo::renut_gpu::Active())
      renut::gpu::OnWindowResized();
  }

  std::optional<rex::PathConfig> OnFinalizePaths(const rex::PathConfig& defaults,
                                                 std::function<void(rex::PathConfig)> resume) override {
    if (banjo::renut_gpu::Active())
      renut::gpu::StartRenderer(app_context(), [this] { return imgui_drawer(); });
    return rex::ReXApp::OnFinalizePaths(defaults, std::move(resume));
  }
#endif

  // As in shh-nx (SHH-10): the game's menu (F5; L+R+Plus on the Switch, where the Plus does not reach the game with
  // L+R held): brightness and the button layout, applied at once and saved to the configuration file.
  void OnCreateDialogs(rex::ui::ImGuiDrawer* drawer) override {
    rex::ReXApp::OnCreateDialogs(drawer);
    rex::ui::RegisterBind("bind_sh3_menu", "F5", "Silent Hill 3 menu", [this] { ToggleMenu(); });
    // LB+RB+Start, read where every controller's input passes (input_system.cpp): from the thread that reads input,
    // so the menu opens on the UI thread.
    menu_app_ = this;
    rex::input::SetMenuComboCallback([] {
      if (Sh3App* app = menu_app_)
        app->app_context().CallInUIThread([app] { app->ToggleMenu(); });
    });
  }

 private:
  void ToggleMenu() {
    REXLOG_INFO("[menu] toggled");
    rex::ui::ToggleQuickSettings(imgui_drawer(), "Silent Hill 3", MenuSettings(), config_path());
  }
  static inline Sh3App* menu_app_ = nullptr;

  static std::vector<rex::ui::QuickSetting> MenuSettings() {
    std::vector<rex::ui::QuickSetting> settings;
#if SH3_RENUT_RENDERER
    rex::ui::QuickSetting resolution;
    resolution.cvar = "sh3_resolution";
#if REX_PLATFORM_SWITCH
    // As in shh-nx: one resolution per mode; docked defaults to 1080p (sh3_resolution_docked).
    resolution.label = "Resolucao no portatil";
    resolution.choices = {{"480p", "480p"}, {"600p", "600p"}, {"720p", "720p"}};
    settings.push_back(std::move(resolution));

    rex::ui::QuickSetting docked;
    docked.cvar = "sh3_resolution_docked";
    docked.label = "Resolucao na dock";
    docked.choices = {{"600p", "600p"}, {"720p", "720p"}, {"1080p", "1080p"}};
    docked.note = "muda sozinha ao encaixar ou tirar da dock";
    settings.push_back(std::move(docked));
#else
    resolution.label = "Resolucao";
    resolution.choices = {{"480p", "480p"}, {"600p", "600p"}, {"720p", "720p"}, {"1080p", "1080p"}};
    settings.push_back(std::move(resolution));
#endif

    rex::ui::QuickSetting gamma;
    gamma.cvar = "sh3_output_gamma";
    gamma.label = "Gama da tela (menor = mais claro)";
    gamma.min = 0.3f;
    gamma.max = 1.2f;
    gamma.note = "0.6 no Switch, 1.0 e a imagem original";
    settings.push_back(std::move(gamma));
#endif
#if REX_PLATFORM_SWITCH
    rex::ui::QuickSetting buttons;
    buttons.cvar = "input_xbox_layout";
    buttons.label = "Botoes A/B/X/Y";
    buttons.choices = {{"false", "Pela letra (Switch)"}, {"true", "Pela posicao (Xbox)"}};
    buttons.note = "pela letra: o A do Switch e o A do jogo";
    settings.push_back(std::move(buttons));
#endif
    return settings;
  }

  static void SetIfNotRequested(const char* name, const char* value) {
    if (rex::cvar::GetFlagInfo(name) == nullptr) {
      REXLOG_DEBUG("Setting '{}' not registered yet; left alone.", name);
      return;
    }
    if (rex::cvar::HasNonDefaultValue(name) || rex::cvar::GetFlagSource(name) != rex::cvar::Source::kDefault) {
      return;  // set explicitly (the default itself, too, from the menu's Save): do not override it.
    }
    if (rex::cvar::SetFlagByName(name, value)) {
      REXLOG_DEBUG("Default setting: {} = {}", name, value);
    }
  }
};
