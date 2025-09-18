### Regulated Cascode Transimpedance Amplifier

This component was originally authored by: Mathew Hanson (mthanson1)

Complete documentation for this component can be found here: [RCG-TIA Datasheet](https://docs.uwasic.com/doc/current-sensor-SS7PohUOm0)

## Testbenches

Testbenches are currently split accross multiple files. Future development could include simplifying the testbench to 1 file.

*BASE:* Simulates gain of TIA and input impedance/range

*BODE:* Simulates bode plot for frequency response of the component

*FREQUENCY:* Simulates a constant small AC input (iirc \-MH) 

*NOISE:* Simulates thermal Johnston-Nyquist noise for the component
