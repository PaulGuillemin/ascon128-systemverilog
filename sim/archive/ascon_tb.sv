//                              -*- Mode: Verilog -*-
// Filename        : permutation_full_tb.sv
// Description     : package definition
// Author          : Jean-Baptiste RIGAUD
// Created On      : Sat Oct 14 15:30:30 2023
// Last Modified By: Jean-Baptiste RIGAUD
// Last Modified On: Sat Oct 14 15:30:30 2023
// Update Count    : 0
// Status          : Unknown, Use with caution!
`timescale 1 ns / 1 ps

module ascon_tb
  import ascon_pack::*;
(
    //vide
);

  logic clock_s;
  logic reset_s;
  logic init_s;
  logic [127:0] key_s;
  logic [127:0] nonce_s;
  logic [63:0] data_s;
  logic data_valid_s;
  logic cipher_valid_s;
  logic [63:0] cipher_s;
  logic end_s;
  logic end_initialisation_s;
  logic end_associate_s;
  logic end_cipher_s;
  logic associate_data_s;
  logic start_finalisation_s;
  logic [127:0] tag_s;

  ascon DUT (
      .clock_i(clock_s),
      .reset_i(reset_s),
      .init_i(init_s),
      .associate_data_i(associate_data_s),
      .finalisation_i(start_finalisation_s),
      .data_i(data_s),
      .data_valid_i(data_valid_s),
      .key_i(key_s),
      .nonce_i(nonce_s),
      .end_associate_o(end_associate_s),
      .cipher_o(cipher_s),
      .cipher_valid_o(cipher_valid_s),
      .tag_o(tag_s),
      .end_tag_o(end_s),
      .end_initialisation_o(end_initialisation_s),
      .end_cipher_o(end_cipher_s)
  );

  //horloge
  initial begin
    clock_s = 0;
    forever #10 clock_s = ~clock_s;
  end
  //stimuli
  initial begin
    reset_s = 1;
    key_s = 128'h8A55114D1CB6A9A2BE263D4D7AECAAFF;
    nonce_s = 128'h4ED0EC0B98C529B7C8CDDF37BCD0284A;
    init_s = 0;
    data_s = '0;
    data_valid_s = 0;
    associate_data_s = 0;
    start_finalisation_s = 0;
    #40;
    $display("reset du circuit");
    reset_s = 0;
    #100;
    $display("début du chiffrement");
    init_s = 1;
    #20;
    init_s = 0;
    do begin
      #20;
    end while (end_initialisation_s != 1'b1);
    $display("fin de la phase d'initialisation");

	// wait a little
	#150;
    
    associate_data_s = 1;
    data_s = 64'h6F74206563696C41;
    data_valid_s = 1;
    #20;
    data_valid_s = 0;
    do begin
      #20;
    end while (end_associate_s != 1'b1);
    $display("fin de la phase de traitement des données associées");

 	// wait a little
	#70;

    associate_data_s = 0;
    data_s = 64'h7475657620657551;
    data_valid_s = 1;
    #20;
    data_valid_s = 0;
    do begin
      #20;
    end while (end_cipher_s != 1'b1);
    $display("fin de la phase de traitement du premier bloc de données");
 
	// wait a little
	#195;
   
    associate_data_s = 0;
    data_s = 64'h74614E2061747265;
    data_valid_s = 1;
    #20;
    data_valid_s = 0;
    do begin
      #20;
    end while (end_cipher_s != 1'b1);
    $display("fin de la phase de traitement du deuxieme bloc de données");
    
 	// wait a little
	#120;

    associate_data_s = 0;
    start_finalisation_s = 1;
    data_s = 64'hD20746E75696E65;
    data_valid_s = 1;
    #20;
    data_valid_s = 0;
    do begin
      #20;
    end while (end_s != 1'b1);
    $display("fin du chiffrement");
    
	// wait a little
	#110;

    #20;
    $stop();

  end

endmodule : ascon_tb
