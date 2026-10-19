"""Run the archived RTL against selected public Ascon-128 v1.2 vectors."""

import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def padded_blocks(data):
    padded = data + b"\x80"
    padded += bytes((-len(padded)) % 8)
    return [padded[i:i + 8].hex() for i in range(0, len(padded), 8)]


def generate_bench(vectors):
    body = []
    for vector in vectors:
        message = bytes.fromhex(vector["PT"])
        ad = bytes.fromhex(vector["AD"])
        ciphertext = bytes.fromhex(vector["CT"])
        # The retained FSM requires associated data and a full message block
        # before its finalization state. Other lengths are outside this test.
        if not ad or len(message) < 8:
            raise ValueError("Vector is outside the retained interface's tested scope")
        body += ["reset_core();", f"key_i = 128'h{vector['Key']};",
                 f"nonce_i = 128'h{vector['Nonce']};", "start_core();"]
        for word in padded_blocks(ad):
            body += [f"send_word(64'h{word}, 1'b1, 1'b0);", "wait_done(1);"]
        full = len(message) // 8
        for i in range(full):
            word = message[i * 8:(i + 1) * 8].hex()
            expected = ciphertext[i * 8:(i + 1) * 8].hex()
            body += [f"send_word(64'h{word}, 1'b0, 1'b0);", "wait_done(2);",
                     f"if (cipher_o !== 64'h{expected}) $fatal(1, \"KAT {vector['Count']}: ciphertext block {i} mismatch\");"]
        tail = message[full * 8:]
        body += [f"send_word(64'h{padded_blocks(tail)[0]}, 1'b0, 1'b1);", "wait_done(3);"]
        if tail:
            width = 8 * len(tail)
            expected = ciphertext[full * 8:len(message)].hex()
            body += [f"if (cipher_o[63 -: {width}] !== {width}'h{expected}) $fatal(1, \"KAT {vector['Count']}: final ciphertext mismatch\");"]
        body += [f"if (tag_o !== 128'h{ciphertext[-16:].hex()}) $fatal(1, \"KAT {vector['Count']}: tag mismatch\");",
                 f"$display(\"PASS KAT {vector['Count']} (AD={len(ad)}, PT={len(message)} bytes)\");"]
    return """`timescale 1ns/1ps
module portfolio_tb;
  logic clock_i = 0;
  always #5 clock_i = ~clock_i;
  logic reset_i, init_i, associate_data_i, finalisation_i, data_valid_i;
  logic [63:0] data_i;
  logic [127:0] key_i, nonce_i;
  wire end_associate_o, cipher_valid_o, end_tag_o;
  wire end_initialisation_o, end_cipher_o;
  wire [63:0] cipher_o;
  wire [127:0] tag_o;
  ascon dut (.*);

  task automatic reset_core;
    reset_i = 1; init_i = 0; data_valid_i = 0;
    associate_data_i = 0; finalisation_i = 0;
    data_i = 0; key_i = 0; nonce_i = 0;
    repeat (3) @(negedge clock_i);
    reset_i = 0;
    @(negedge clock_i);
  endtask

  task automatic wait_done(input integer phase);
    integer cycles;
    logic done;
    begin
      cycles = 0;
      done = 0;
      while (!done && cycles < 100) begin
        @(negedge clock_i);
        case (phase)
          0: done = end_initialisation_o;
          1: done = end_associate_o;
          2: done = end_cipher_o;
          3: done = end_tag_o;
        endcase
        cycles = cycles + 1;
      end
      if (!done) $fatal(1, "Handshake timeout, phase %0d", phase);
    end
  endtask

  task automatic start_core;
    init_i = 1;
    @(negedge clock_i);
    init_i = 0;
    wait_done(0);
  endtask

  task automatic send_word(input logic [63:0] word_value,
                            input logic is_ad, input logic is_final);
    data_i = word_value;
    associate_data_i = is_ad;
    finalisation_i = is_final;
    data_valid_i = 1;
    @(negedge clock_i);
    data_valid_i = 0;
  endtask

  initial begin
    $dumpfile("build/portfolio.vcd");
    $dumpvars(0, portfolio_tb);
""" + "\n".join("    " + line for line in body) + f"""
    $display("PASS: {len(vectors)} known-answer vectors");
    $finish;
  end
  initial begin
    #100000;
    $fatal(1, "Global simulation timeout");
  end
endmodule
"""


def main():
    for tool in ("iverilog", "vvp"):
        if not shutil.which(tool):
            raise SystemExit(f"Missing {tool}: install Icarus Verilog and add it to PATH.")
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    vectors = json.loads((ROOT / "sim/vectors.json").read_text())["vectors"]
    (build / "portfolio_tb.sv").write_text(generate_bench(vectors))
    subprocess.run(["iverilog", "-g2012", "-s", "portfolio_tb", "-o",
                    "build/portfolio.vvp", "-f", "sim/rtl.f",
                    "build/portfolio_tb.sv"], cwd=ROOT, check=True, timeout=60)
    subprocess.run(["vvp", "build/portfolio.vvp"], cwd=ROOT, check=True, timeout=30)


if __name__ == "__main__":
    main()
