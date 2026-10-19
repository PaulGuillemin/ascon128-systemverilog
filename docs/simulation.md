# Simulation and validation

## Reproduce the checks

Install Python 3 and Icarus Verilog, then run from the repository root:

```sh
python3 scripts/run_sim.py
```

The script reads `sim/vectors.json`, generates `build/portfolio_tb.sv`, compiles the sources in `sim/rtl.f` and runs the simulation. It checks every full ciphertext block, the meaningful bytes of the partial final block, and the complete 128-bit tag. Handshake waits and the overall simulation are bounded to report a failure rather than hang.

A mismatch or timeout exits unsuccessfully. A waveform is written to `build/portfolio.vcd`, which can be opened in a VCD viewer. The runner has no Python package dependencies and does not modify the RTL.

## Reference data

The expected values are selected from the public [Ascon-128 v1.2 known-answer file at ascon-c v1.2.8](https://github.com/ascon/ascon-c/blob/v1.2.8/crypto_aead/ascon128v12/LWC_AEAD_KAT_128_128.txt). The exact raw source URL and original vector counts are recorded in `sim/vectors.json`. These keys and nonces are public test data, not operational credentials.

Associated-data lengths: **1, 7, 8, 15 bytes**. Plaintext lengths: **8, 16, 23 bytes**. The cross-product gives **12 vectors**, covering full and partial blocks as well as an extra associated-data block.

The tests exercise initialization, associated-data absorption, the transition into encryption, intermediate six-round permutations, finalization and tag generation. They do not provide exhaustive coverage of the controller or all possible lengths.

## Validation record â€” 19 October 2026

| Check | Result |
| --- | --- |
| RTL compilation | Passed with Icarus Verilog 12.0, SystemVerilog 2012 mode |
| Selected known-answer tests | 12/12 passed, ciphertext and tag |
| RTL comparison with the school source | Identical file contents; no functional edits |
| Test environment | Ubuntu under Windows Subsystem for Linux |
| Original testbench | Compiled and ran to completion; preserved as an archive |

The simulation harness and its checks were created during portfolio preparation. They are new verification evidence, not a reconstruction of the original development process.

## Original testbench

`sim/archive/ascon_tb.sv` preserves the original scenario. It drives initialization, associated data and plaintext, then waits for completion. It does not compare ciphertext or tags against expected values and should not be treated as an independent correctness check.

With Icarus installed, it can be compiled and run separately:

```sh
mkdir -p build
iverilog -g2012 -s ascon_tb -o build/archive.vvp -f sim/rtl.f sim/archive/ascon_tb.sv
vvp -n build/archive.vvp
```

`-n` makes the archived `$stop` finish a batch run instead of entering an interactive prompt.

## Not verified

No synthesis, place-and-route, FPGA programming, resource use, timing closure, power measurement, decryption or side-channel assessment was performed. The suite does not claim NIST SP 800-232 conformance; it uses the legacy Ascon-128 v1.2 variant.
