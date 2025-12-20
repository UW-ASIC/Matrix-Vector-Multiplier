// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtt_if.h for the primary calling header

#ifndef VERILATED_VTT_IF___024ROOT_H_
#define VERILATED_VTT_IF___024ROOT_H_  // guard

#include "verilated.h"


class Vtt_if__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtt_if___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(i_clk,0,0);
    VL_IN8(i_rst_n,0,0);
    VL_IN8(i_ena,0,0);
    VL_IN8(ui_in,7,0);
    VL_OUT8(uo_out,7,0);
    VL_IN8(uio_in,7,0);
    VL_OUT8(uio_out,7,0);
    VL_OUT8(uio_oe,7,0);
    CData/*3:0*/ tt_if__DOT__count;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__i_clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__i_rst_n__0;
    CData/*0:0*/ __VactContinue;
    IData/*31:0*/ __VactIterCount;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtt_if__Syms* const vlSymsp;

    // CONSTRUCTORS
    Vtt_if___024root(Vtt_if__Syms* symsp, const char* v__name);
    ~Vtt_if___024root();
    VL_UNCOPYABLE(Vtt_if___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
