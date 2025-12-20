// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vtt_if__pch.h"

//============================================================
// Constructors

Vtt_if::Vtt_if(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vtt_if__Syms(contextp(), _vcname__, this)}
    , i_clk{vlSymsp->TOP.i_clk}
    , i_rst_n{vlSymsp->TOP.i_rst_n}
    , i_ena{vlSymsp->TOP.i_ena}
    , ui_in{vlSymsp->TOP.ui_in}
    , uo_out{vlSymsp->TOP.uo_out}
    , uio_in{vlSymsp->TOP.uio_in}
    , uio_out{vlSymsp->TOP.uio_out}
    , uio_oe{vlSymsp->TOP.uio_oe}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vtt_if::Vtt_if(const char* _vcname__)
    : Vtt_if(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vtt_if::~Vtt_if() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vtt_if___024root___eval_debug_assertions(Vtt_if___024root* vlSelf);
#endif  // VL_DEBUG
void Vtt_if___024root___eval_static(Vtt_if___024root* vlSelf);
void Vtt_if___024root___eval_initial(Vtt_if___024root* vlSelf);
void Vtt_if___024root___eval_settle(Vtt_if___024root* vlSelf);
void Vtt_if___024root___eval(Vtt_if___024root* vlSelf);

void Vtt_if::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vtt_if::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vtt_if___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        vlSymsp->__Vm_didInit = true;
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vtt_if___024root___eval_static(&(vlSymsp->TOP));
        Vtt_if___024root___eval_initial(&(vlSymsp->TOP));
        Vtt_if___024root___eval_settle(&(vlSymsp->TOP));
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vtt_if___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vtt_if::eventsPending() { return false; }

uint64_t Vtt_if::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vtt_if::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vtt_if___024root___eval_final(Vtt_if___024root* vlSelf);

VL_ATTR_COLD void Vtt_if::final() {
    Vtt_if___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vtt_if::hierName() const { return vlSymsp->name(); }
const char* Vtt_if::modelName() const { return "Vtt_if"; }
unsigned Vtt_if::threads() const { return 1; }
void Vtt_if::prepareClone() const { contextp()->prepareClone(); }
void Vtt_if::atClone() const {
    contextp()->threadPoolpOnClone();
}
