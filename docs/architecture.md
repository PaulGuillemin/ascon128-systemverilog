# Architecture and interface

## Datapath

`ascon.sv` connects the controller, round counter and `Permutation` module. The state type in `ascon_pack.sv` is a packed array of five 64-bit words. The initialization value is `80400c0600000000`, followed by the key and nonce halves.

The permutation datapath contains:

1. A mux selecting initialization data or the saved state.
2. XOR logic for input blocks, key injection and domain separation.
3. Ciphertext capture from the first state word.
4. `Pc`: round-constant addition to the low byte of the third state word.
5. `Ps`: 64 parallel S-boxes, each operating on one bit from each state word.
6. `Pl`: rotation/XOR diffusion within each 64-bit word.
7. Final key XOR, state storage and tag capture.

One combinational permutation round sits between state-register updates. The counter selects a 12-round sequence for initialization/finalization and a six-round sequence for intermediate processing. Overall phase latency also includes control states; no maximum operating frequency was measured.

## Controller

`fsm_moore.sv` controls data selection, register enables, round-counter initialization and output flags. The top-level reset is active high; the internal registers use the inverted active-low reset.

| Operation | Caller action | Completion |
| --- | --- | --- |
| Initialize | Hold key/nonce stable and pulse `init_i` | Wait for `end_initialisation_o` |
| Absorb associated data | Present a padded block with `associate_data_i = 1`, pulse `data_valid_i` | Wait for `end_associate_o` |
| Encrypt a full block | Set `associate_data_i = 0`, `finalisation_i = 0`, pulse `data_valid_i` | Capture `cipher_o` at `end_cipher_o` |
| Finalize | Present the final padded block with `finalisation_i = 1`, pulse `data_valid_i` | Capture `tag_o` and final `cipher_o` at `end_tag_o` |

Keep each input block stable through completion. The core can use it after the cycle in which `data_valid_i` was asserted. Keep the key and nonce stable for the whole operation.

## Byte order and padding

The verification runner maps reference bytes into words most-significant byte first. Padding appends byte `80`, followed by zero bytes up to a multiple of eight bytes. A message or associated-data length that is already a multiple of eight still needs an additional padding block.

For example, seven bytes `00 01 02 03 04 05 06` become input word `0001020304050680`. An eight-byte message uses one regular block followed by final input `8000000000000000`.

For a partial final plaintext block, only the most significant bytes corresponding to the original plaintext length belong to the ciphertext. The core exposes a full 64-bit word; the caller discards the padding-related bytes.

## Supported verification sequence

The retained controller enters finalization from its ciphertext waiting state. The automated checks therefore use non-empty associated data and at least one full plaintext block before the final padded block. Empty associated data, plaintext shorter than eight bytes and restart without reset are not validated by this suite. Each vector starts with a reset.

No AXI wrapper, processor driver or board constraint file is part of this archive. This repository presents the RTL core and its simulation.
