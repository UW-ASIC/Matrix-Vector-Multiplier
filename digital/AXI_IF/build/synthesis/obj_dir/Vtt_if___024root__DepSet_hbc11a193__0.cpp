// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtt_if.h for the primary calling header

#include "Vtt_if__pch.h"
#include "Vtt_if___024root.h"

void Vtt_if___024root___eval_act(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_act\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtt_if___024root___nba_sequent__TOP__0(Vtt_if___024root* vlSelf);

void Vtt_if___024root___eval_nba(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_nba\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((3ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        Vtt_if___024root___nba_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtt_if___024root___nba_sequent__TOP__0(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___nba_sequent__TOP__0\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.i_rst_n) {
        if (vlSelfRef.i_ena) {
            vlSelfRef.tt_if__DOT__count = (0xfU & ((IData)(1U) 
                                                   + (IData)(vlSelfRef.tt_if__DOT__count)));
        }
    } else {
        vlSelfRef.tt_if__DOT__count = 0U;
    }
    vlSelfRef.uo_out = vlSelfRef.tt_if__DOT__count;
}

void Vtt_if___024root___eval_triggers__act(Vtt_if___024root* vlSelf);

bool Vtt_if___024root___eval_phase__act(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_phase__act\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<2> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtt_if___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtt_if___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtt_if___024root___eval_phase__nba(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_phase__nba\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtt_if___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__nba(Vtt_if___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtt_if___024root___dump_triggers__act(Vtt_if___024root* vlSelf);
#endif  // VL_DEBUG

void Vtt_if___024root___eval(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtt_if___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("/home/omare/Documents/UWASIC/Matrix-Vector-Analog/digital/AXI_IF/build/../src/tt_if.sv", 1, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtt_if___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("/home/omare/Documents/UWASIC/Matrix-Vector-Analog/digital/AXI_IF/build/../src/tt_if.sv", 1, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtt_if___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtt_if___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtt_if___024root___eval_debug_assertions(Vtt_if___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtt_if___024root___eval_debug_assertions\n"); );
    Vtt_if__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.i_clk & 0xfeU)))) {
        Verilated::overWidthError("i_clk");}
    if (VL_UNLIKELY(((vlSelfRef.i_rst_n & 0xfeU)))) {
        Verilated::overWidthError("i_rst_n");}
    if (VL_UNLIKELY(((vlSelfRef.i_ena & 0xfeU)))) {
        Verilated::overWidthError("i_ena");}
}
#endif  // VL_DEBUG
