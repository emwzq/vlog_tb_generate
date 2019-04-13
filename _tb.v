
`timescale 1ns/1ns
module _tb();




  u_);


initial begin
    $finish;
end

initial begin
`ifdef DUMP_FSDB
   $fsdbDumpfile("wave.fsdb");
   $fsdbDumpvars();
`elsif DUMP_SHM
   $shm_open("wave.shm);
   $shm_probe(_tb,"AS");
`elsif DUMP_VCD
   $dumpfile("wave.vcd");
   $dumpvars()
`else
    $display("No dump andy waves")
`endif
end

`include "testcase.v"

endmodule
