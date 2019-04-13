
`timescale 1ns/1ns
module iopad_tb();

parameter Period = 20;

reg     [DW-1:0]    din        ;
reg     [DW-1:0]    dout    = 0;
`ifdef aa
reg     [DW-1:0]    dout_en = 0;
`endif
reg                 clk     = 0;
reg                 rst_n   = 0;


iopad  u_iopad(
    .din         (din         ),
    .dout        (dout        ),
`ifdef aa
    .dout_en     (dout_en     ),
`endif
    .clk         (clk         ),
    .rst_n       (rst_n       ));

initial begin
    clk = 0;
    forever #Period clk = ~clk;
end


initial begin
    #1000; $finish;
end

initial begin
`ifdef DUMP_FSDB
   $fsdbDumpfile("wave.fsdb");
   $fsdbDumpvars();
`elsif DUMP_SHM
   $shm_open("wave.shm);
   $shm_probe(iopad_tb,"AS");
`elsif DUMP_VCD
   $dumpfile("wave.vcd");
   $dumpvars()
`else
    $display("No dump andy waves")
`endif
end

`include "testcase.v"

endmodule
