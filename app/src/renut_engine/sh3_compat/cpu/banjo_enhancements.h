// shh-nx (2026-10-28): banjo-nx's enhancement switches, as Renut's renderer (through banjo-nx) asks for them, answered
// by SHH's own two masters (src/cpu/sh3_enhancements.h): a banjo_* key is active when it is on and its group's master
// is on (sh3_cpu_enhancements / sh3_noncpu_enhancements).
#pragma once

#include "cpu/sh3_enhancements.h"

namespace banjo {

enum class EnhancementGroup { kCpu, kNonCpu };

inline bool EnhancementActive(EnhancementGroup group, bool own_key) {
  return own_key && (group == EnhancementGroup::kCpu ? sh3::enh::CpuMaster() : sh3::enh::NonCpuMaster());
}

// The generated code's self-checks: SHH has no enhancement report yet, so nothing to collect.
inline void CodegenChecksReport(int) {}

}  // namespace banjo
