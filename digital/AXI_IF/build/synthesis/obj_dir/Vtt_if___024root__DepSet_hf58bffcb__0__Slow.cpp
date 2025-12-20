// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtt_if.h for the primary calling header

#include "Vtt_if__pch.h"
#include "Vtt_if__Syms.h"
#include "Vtt_if___024root.h"

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__stl(Vtt_if___024root* vlSelf);
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtt_if___024root___eval_triggers__stl(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_triggers__stl\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VstlTriggered.setBit(0U, (IData)(vlSelfRef.__VstlFirstIteration));
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtt_if___024root___dump_triggers__stl(vlSelf);
    }
#endif
}
