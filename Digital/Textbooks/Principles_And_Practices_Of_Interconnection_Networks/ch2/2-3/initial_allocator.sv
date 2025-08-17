// // allocator.sv
// //
// of input phit and current field of routing header
// //
// once assigned, holds a port for the duration of a packet
// //
// as long as payload phits are on input).
// //
// uses fixed priority arbitration (r0 is highest).

module allocator(input logic clk,
                 input logic [1:0] thisPort,
                 input logic [3:0] r0, r1, r2, r3,
                 output logic [3:0] select,
                 output logic shift);

  logic [3:0] grant, head, payload, match, request, hold;
  logic [2:0] pass;
  logic avail;
  logic [3:0] last;
  logic [3:0] drops_0, drops_1, drops_2, drops_3;

  assign head = {r3[3:2]==3, r2[3:2]==3, r1[3:2]==3, r0[3:2]==3};
  assign payload = {r3[3:2]==2, r2[3:2]==2, r1[3:2]==2, r0[3:2]==2};
  assign match = {r3[1:0]==thisPort, r2[1:0]==thisPort,
                  r1[1:0]==thisPort, r0[1:0]==thisPort};
  assign request = head & match;
  assign pass[0] = avail & ~request[0];
  assign pass[1] = pass[0] & ~request[1];
  assign pass[2] = pass[1] & ~request[2];
  assign grant = request & {pass, avail};
  assign hold = last & payload;
  assign select = grant | hold;
  assign avail = ~(|hold);
  assign shift = |grant;
    always @(posedge clk) begin
        last <= select;
    end

    initial begin
        $dumpfile("allocator.vcd"); // Specify filename
        $dumpvars(0, allocator); // Dump all signals within the scope of my_design
        #1; // Wait a small amount of time to ensure dump starts
    end
endmodule
