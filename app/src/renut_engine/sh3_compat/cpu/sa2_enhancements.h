// sh3-nx (2026-10-29): what sa2-nx's frame pacing (gpu/sa2_renut_pacing.cpp) takes from SA2's enhancement list
// (sa2-nx's src/cpu/sa2_enhancements.h): one switch, g_vsync_relaxed, which there belongs to SA2's own vsync code
// (me_native_system.cpp). Silent Hill 3 has no such code, so the switch is defined off (sh3_compat.cpp) and only its
// shape is kept here.
#pragma once

#include <atomic>
#include <cstdint>

namespace sa2::enh {

enum Group : uint8_t { kCpu = 0, kNonCpu = 1 };

struct Enhancement {
  const char* key;
  Group group;
  const char* what;
  bool active = false;
  std::atomic<uint64_t> uses{0};

  void Use(uint64_t n = 1) { uses.fetch_add(n, std::memory_order_relaxed); }
};

}  // namespace sa2::enh
