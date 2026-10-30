// sh3-nx (2026-10-29): what sa2-nx's Swap hook (renut_engine/gpu/d3d/hooks/device.cpp) takes from SA2's frame
// capture (sa2-nx's src/sa2_capture.h): the lockstep capture, a diagnostic of SA2's app. Silent Hill 3 has none, so it
// is always off.
#pragma once

#include <cstdint>

namespace rex::ui {
struct RawImage;
}

namespace sa2::capture {

inline bool RenutLockstepOn() { return false; }
inline void RenutLockstepFrame(uint64_t /*game_frame*/, const rex::ui::RawImage* /*image*/) {}

}  // namespace sa2::capture
