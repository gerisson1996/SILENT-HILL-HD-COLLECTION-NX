// sh3-nx (2026-10-29): the game-side hooks at the addresses Renut's renderer shares with a native renderer
// (renut_engine/gpu/banjo_shared_hooks.h). Renut defines only renut_native_sub_X there (BANJO_RENUT_HOOK_SHARED); in
// sa2-nx it is SA2's own renderer (src/me, src/cpu) that hooks these addresses and yields to Renut. Silent Hill 3 has
// no renderer of its own, so these hooks only yield: Renut's side when it is chosen, the game's original otherwise.
// Without them the draws, the inline data and the blocker never reach Renut ("0 draws" with the device running).
#include <rex/hook.h>
#include <rex/ppc.h>

#include "renut_engine/gpu/banjo_renut_select.h"
#include "renut_engine/gpu/banjo_shared_hooks.h"

#define SH3_RENUT_SHARED(subroutine)                                                   \
  REX_EXTERN(__imp__##subroutine);                                                     \
  extern "C" REX_FUNC(subroutine) {                                                    \
    BANJO_RENUT_YIELD_SHARED(subroutine)                                               \
    __imp__##subroutine(ctx, base);                                                    \
  }

SH3_RENUT_SHARED(sub_82275700)  // CDevice::AllocateInlineData
SH3_RENUT_SHARED(sub_82277530)  // CBlocker::Check
SH3_RENUT_SHARED(sub_82289610)  // D3DDevice_BeginVertices
SH3_RENUT_SHARED(sub_82289AD0)  // D3DDevice_DrawVerticesUP
SH3_RENUT_SHARED(sub_8228A0F8)  // D3DDevice_DrawVertices
SH3_RENUT_SHARED(sub_8228A510)  // D3DDevice_DrawIndexedVertices
