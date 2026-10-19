`timescale 1 ns / 1 ps

module state_register_w_en
  import ascon_pack::*;
(
    input  logic      clock_i,
    input  logic      resetb_i,
    input  logic      en_i,
    input  type_state data_i,
    output type_state data_o
);

  type_state data_s;

  always_ff @(posedge clock_i or negedge resetb_i) begin
    if (resetb_i == 1'b0) begin
      data_s <= {64'h0, 64'h0, 64'h0, 64'h0, 64'h0};
    end else begin
      if (en_i == 1'b1) begin
        data_s <= data_i;
      end else data_s <= data_s;
    end
  end

  assign data_o = data_s;

endmodule : state_register_w_en


