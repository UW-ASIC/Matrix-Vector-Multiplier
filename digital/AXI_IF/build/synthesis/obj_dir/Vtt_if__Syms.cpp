// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtt_if__pch.h"
#include "Vtt_if.h"
#include "Vtt_if___024root.h"

// FUNCTIONS
Vtt_if__Syms::~Vtt_if__Syms()
{
}

Vtt_if__Syms::Vtt_if__Syms(VerilatedContext* contextp, const char* namep, Vtt_if* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(18);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-12);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
}
