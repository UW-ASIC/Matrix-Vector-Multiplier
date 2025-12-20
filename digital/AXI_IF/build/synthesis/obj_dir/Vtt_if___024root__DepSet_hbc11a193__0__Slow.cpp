// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtt_if.h for the primary calling header

#include "Vtt_if__pch.h"
#include "Vtt_if___024root.h"

VL_ATTR_COLD void Vtt_if___024root___eval_static(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_static\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__i_clk__0 = vlSelfRef.i_clk;
    vlSelfRef.__Vtrigprevexpr___TOP__i_rst_n__0 = vlSelfRef.i_rst_n;
}

VL_ATTR_COLD void Vtt_if___024root___eval_initial__TOP(Vtt_if___024root* vlSelf);

VL_ATTR_COLD void Vtt_if___024root___eval_initial(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_initial\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtt_if___024root___eval_initial__TOP(vlSelf);
}

VL_ATTR_COLD void Vtt_if___024root___eval_initial__TOP(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_initial__TOP\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.uio_out = 0U;
    vlSelfRef.uio_oe = 0U;
}

VL_ATTR_COLD void Vtt_if___024root___eval_final(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_final\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__stl(Vtt_if___024root* vlSelf);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtt_if___024root___eval_phase__stl(Vtt_if___024root* vlSelf);

VL_ATTR_COLD void Vtt_if___024root___eval_settle(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_settle\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VstlIterCount;
    CData/*0:0*/ __VstlContinue;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    __VstlContinue = 1U;
    while (__VstlContinue) {
        if (VL_UNLIKELY(((0x64U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtt_if___024root___dump_triggers__stl(vlSelf);
#endif
            VL_FATAL_MT("/home/omare/Documents/UWASIC/Matrix-Vector-Analog/digital/AXI_IF/build/../src/tt_if.sv", 1, "", "Settle region did not converge.");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        __VstlContinue = 0U;
        if (Vtt_if___024root___eval_phase__stl(vlSelf)) {
            __VstlContinue = 1U;
        }
        vlSelfRef.__VstlFirstIteration = 0U;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__stl(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___dump_triggers__stl\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VstlTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        VL_DBG_MSGF("         'stl' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtt_if___024root___stl_sequent__TOP__0(Vtt_if___024root* vlSelf);

VL_ATTR_COLD void Vtt_if___024root___eval_stl(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_stl\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        Vtt_if___024root___stl_sequent__TOP__0(vlSelf);
    }
}

VL_ATTR_COLD void Vtt_if___024root___stl_sequent__TOP__0(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___stl_sequent__TOP__0\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.uo_out = vlSelfRef.tt_if__DOT__count;
}

VL_ATTR_COLD void Vtt_if___024root___eval_triggers__stl(Vtt_if___024root* vlSelf);

VL_ATTR_COLD bool Vtt_if___024root___eval_phase__stl(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_phase__stl\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VstlExecute;
    // Body
    Vtt_if___024root___eval_triggers__stl(vlSelf);
    __VstlExecute = vlSelfRef.__VstlTriggered.any();
    if (__VstlExecute) {
        Vtt_if___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__act(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___dump_triggers__act\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VactTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge i_clk)\n");
    }
    if ((2ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 1 is active: @(negedge i_rst_n)\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__nba(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___dump_triggers__nba\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VnbaTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge i_clk)\n");
    }
    if ((2ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 1 is active: @(negedge i_rst_n)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtt_if___024root___ctor_var_reset(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___ctor_var_reset\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->name());
    vlSelf->i_clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 15925868812496733354ull);
    vlSelf->i_rst_n = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 4084054307081237675ull);
    vlSelf->i_ena = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14579764417200185297ull);
    vlSelf->ui_in = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 9967284984545053805ull);
    vlSelf->uo_out = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 4898547878985855477ull);
    vlSelf->uio_in = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 1424820951596298123ull);
    vlSelf->uio_out = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 16185529977779244833ull);
    vlSelf->uio_oe = VL_SCOPED_RAND_RESET_I(8, __VscopeHash, 3840965624738958755ull);
    vlSelf->tt_if__DOT__count = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 10041471433456987894ull);
    vlSelf->__Vtrigprevexpr___TOP__i_clk__0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 14745602394763455243ull);
    vlSelf->__Vtrigprevexpr___TOP__i_rst_n__0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17733911451503446258ull);
}
