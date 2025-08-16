module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/allocator.fst");
    $dumpvars(0, allocator);
end
endmodule
