// allocator.sv
//
// Allocates an input phit to an output port based on the routing header.
// Once assigned, holds a port for the duration of a packet
// (as long as payload phits are on input).
//
// Uses round-robin arbitration for fairness among requesters.
//

module allocator(
    input  logic       clk,
    input  logic [1:0] thisPort,
    input  logic [3:0] r0, r1, r2, r3,
    output logic [3:0] select,
    output logic       shift
);

  logic [3:0] grant, head, payload, match, request, hold;
  logic       avail;
  logic [3:0] last;
  logic [1:0] rr_ptr;   // round-robin pointer

  // Decode whether inputs are head or payload flits
  assign head    = {r3[3:2]==3, r2[3:2]==3, r1[3:2]==3, r0[3:2]==3};
  assign payload = {r3[3:2]==2, r2[3:2]==2, r1[3:2]==2, r0[3:2]==2};

  // Check if the flit matches this output port
  assign match   = {r3[1:0]==thisPort, r2[1:0]==thisPort,
                    r1[1:0]==thisPort, r0[1:0]==thisPort};
  assign request = head & match;

  // Availability: no ongoing payload
  assign avail   = ~(|hold);

  // Round-robin arbitration:
  // Rotate the request vector so rr_ptr is treated as "highest priority"
  logic [7:0] doubled_req;
  logic [3:0] rotated_req, rotated_grant;

  assign doubled_req   = {request, request};  // duplicate for wrap-around
  assign rotated_req   = doubled_req >> rr_ptr;

  // Fixed-priority grant on rotated request
  always_comb begin
    rotated_grant = 4'b0000;
    if      (rotated_req[0]) rotated_grant = 4'b0001;
    else if (rotated_req[1]) rotated_grant = 4'b0010;
    else if (rotated_req[2]) rotated_grant = 4'b0100;
    else if (rotated_req[3]) rotated_grant = 4'b1000;
  end

  // Rotate grant back to original positions
  assign grant = (rotated_grant << rr_ptr) |
                 (rotated_grant >> (4-rr_ptr));

  // Hold payload flits from last granted port
  assign hold   = last & payload;

  // Final selected port
  assign select = grant | hold;

  // Shift = a new head was granted
  assign shift  = |grant;

  // Update state
  always_ff @(posedge clk) begin
    last <= select;
    if (shift) begin
      // Advance round-robin pointer after a head grant
      rr_ptr <= rr_ptr + 2'd1;
    end
  end

  initial begin
    rr_ptr = 2'd0;
    $dumpfile("allocator.vcd");
    $dumpvars(0, allocator);
    #1;
  end

endmodule
