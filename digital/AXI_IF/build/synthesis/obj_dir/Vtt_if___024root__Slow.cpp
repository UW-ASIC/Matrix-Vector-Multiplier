// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtt_if.h for the primary calling header

#include "Vtt_if__pch.h"
#include "Vtt_if__Syms.h"
#include "Vtt_if___024root.h"

void Vtt_if___024root___ctor_var_reset(Vtt_if___024root* vlSelf);

Vtt_if___024root::Vtt_if___024root(Vtt_if__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vtt_if___024root___ctor_var_reset(this);
}

void Vtt_if___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtt_if___024root::~Vtt_if___024root() {
}
