// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VTT_IF__SYMS_H_
#define VERILATED_VTT_IF__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vtt_if.h"

// INCLUDE MODULE CLASSES
#include "Vtt_if___024root.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES)Vtt_if__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vtt_if* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vtt_if___024root               TOP;

    // CONSTRUCTORS
    Vtt_if__Syms(VerilatedContext* contextp, const char* namep, Vtt_if* modelp);
    ~Vtt_if__Syms();

    // METHODS
    const char* name() { return TOP.name(); }
};

#endif  // guard
