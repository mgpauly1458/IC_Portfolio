# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_my_design.py (simple)

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock
import random
random.seed(0)  # For reproducibility in tests

HEADER_PHIT_TYPE = 0b11
PAYLOAD_PHIT_TYPE = 0b10
NULL_PHIT_TYPE = 0b00

class Phit:
    def __init__(self, type, address=0, data=0):
        self.type = type
        self.address = address
        self.data = data
        if self.type is HEADER_PHIT_TYPE:
            self.phit = (self.type << 16) | (self.address << 10)
            self.data = 0

        elif self.type is PAYLOAD_PHIT_TYPE:
            # only includes data, no address
            self.phit = (self.type << 16) | (self.data)
            self.address = 0

        elif self.type is NULL_PHIT_TYPE:
            # null phit has no data or address
            self.phit = (self.type << 16)
            self.address = 0
            self.data = 0

    def get_address(self):
        # returns the address of the phit, if it is a header phit
        if self.type == HEADER_PHIT_TYPE:
            return self.address
        else:
            raise ValueError(f"Phit of type {self.type} does not have an address")

    def get_data(self):
        # returns the data of the phit, if it is a payload phit
        if self.type == PAYLOAD_PHIT_TYPE:
            return self.data
        else:
            raise ValueError(f"Phit of type {self.type} does not have data")

    def get_type(self):
        # returns the type of the phit
        return self.type

    def allocator_input(self):
        # returns 4 most significant bits as a 4 bit return number
        return (self.type << 16 | self.address << 10 | self.data) >> 14 & 0b1111

    def __str__(self):
        return bin(self.phit)

    def __call__(self):
        return self.phit
    
class Packet:
    # Creates a packet with a random total size from 32 to 512 bits of data.
    # A packet is broken up into phits, each of 18 bits.
    # the first 2 bits are the type, 11 for header, 10 for payload, 00 for null
    # the next 6 bits are used for the destination address
    # the last 10 bits are unused for headers
    # payload packets have 2 bits for the type, and 16 bits for the data.
    
    # This class creates a packet with a random total size from 32 to 512 bits of data.
    # it will include a header phit with a random destination address, and then 0 or more payload phits.
    def __init__(self):
        self.phits = []
        self.total_data_size = random.randint(32, 512) // 16 * 16  # Total data size must be a multiple of 16 bits
        self.number_of_data_phits = self.total_data_size // 16
        self.total_size_bits = self.total_data_size + (self.total_data_size / 16)*2 + 18  # Total size includes header and payload phits
        self.destination = random.randint(0, 63)  # Destination address is 6 bits
        self.create_phits()


    def create_header_phit(self):
        # give header phit type 11, destination address, and 10 unused bits
        return Phit(
            type=HEADER_PHIT_TYPE,
            address=self.destination,
        )
    
    def create_payload_phit(self, data):
        # give payload phit type 10, data, and 0 unused bits
        return Phit(
            type=PAYLOAD_PHIT_TYPE,
            data=data,
        )
    
    def create_phits(self):
        # Create the header phit
        self.phits.append(self.create_header_phit())
        
        # Calculate the number of payload phits needed
        num_payload_phits = (self.total_data_size // 16)
        
        # Create payload phits with random data
        for _ in range(num_payload_phits):
            # data = random.randint(0, 0xFFFF)
            # make data fixed value for testing
            data = 0x1234  # Example fixed value for testing
            self.phits.append(self.create_payload_phit(data))

    def pop_phit(self):
        if self.phits:
            return self.phits.pop(0)
        return None

class Allocator_Handler:
    def __init__(self, log=True):
        self.number_of_dropped_packets = 0
        self.log = log

    def initialize_allocator(self, dut):
        # Initialize the allocator
        dut.clk.value = 0
        dut.thisPort.value = 0b00  # Set thisPort to 0b00, first port
        dut.r0.value = 0b0000
        dut.r1.value = 0b0000
        dut.r2.value = 0b0000
        dut.r3.value = 0b0000

    def handle_inputs(self, dut, phit0, phit1, phit2, phit3):
        # Handle the inputs to the allocator
        dut.r0.value = phit0.allocator_input()
        dut.r1.value = phit1.allocator_input()
        dut.r2.value = phit2.allocator_input()
        dut.r3.value = phit3.allocator_input()

    def process_interaction(self, dut, phit: Phit):
        if phit.type != HEADER_PHIT_TYPE or (phit.get_address() >> 4) != dut.thisPort.value:
            return
        
        if self.log:
            dut._log.info("Allocator interaction with phit: %s", phit)
            dut._log.info("Allocator input value: %s", bin(phit.allocator_input()))

        # log output
        if self.log:
            dut._log.info("select: %s", bin(dut.select.value))
            dut._log.info("shift: %s", bin(dut.shift.value))
            dut._log.info("hold: %s", bin(dut.hold.value))

        if dut.hold.value == 0b1:
            # Header packet showed up and hold is set, so packet is dropped
            self.number_of_dropped_packets += 1
            if self.log:
                self.packet_dropped_log(dut)


    def packet_dropped_log(self, dut):
        dut._log.info("\n############################\n")
        dut._log.info("Packet dropped due to hold signal being set.")
        dut._log.info("############################\n")

class Traffic_Generator:
    # Generates random traffic for the allocator.
    # at random time intervals, a packet will be created and
    # the phits will be popped and sent to the allocator input.

    def __init__(self, dut, number_of_cycles=100, packet_generation_frequency=0.1, log=True):
        self.dut = dut
        self.allocator_handler = Allocator_Handler(log=log)
        self.allocator_handler.initialize_allocator(dut)
        self.packet_generation_frequency = packet_generation_frequency
        self.number_of_cycles = number_of_cycles
        self.debug_cycle_counter = 0
        self.log = log

        self.packet0 = None
        self.packet1 = None
        self.packet2 = None
        self.packet3 = None

    def _packet_generated_log(self, packet_number):
        print(f"\nPacket {packet_number} generated. Current cycle: {self.debug_cycle_counter}")
        print(f"Packet destination: {bin(self.destination)} and total number of payload phits: {self.number_of_data_phits}")

    def generate_traffic(self):
        # Randomly decide if a packet should be created or not.
        # If a packet is already being processed, do not create a new one.
        if not self.packet0 and random.random() < self.packet_generation_frequency:
            self.packet0 = Packet()
            if self.log:
                self._packet_generated_log(0)
        if not self.packet1 and random.random() < self.packet_generation_frequency:
            self.packet1 = Packet()
            if self.log:
                self._packet_generated_log(1)
        if not self.packet2 and random.random() < self.packet_generation_frequency:
            self.packet2 = Packet()
            if self.log:
                self._packet_generated_log(2)
        if not self.packet3 and random.random() < self.packet_generation_frequency:
            self.packet3 = Packet()
            if self.log:
                self._packet_generated_log(3)

    async def process_traffic(self):
        for _ in range(self.number_of_cycles):
            self.generate_traffic()
            # initialize phits to null
            phit0 = Phit(NULL_PHIT_TYPE)
            phit1 = Phit(NULL_PHIT_TYPE)
            phit2 = Phit(NULL_PHIT_TYPE)
            phit3 = Phit(NULL_PHIT_TYPE)
            if self.packet0:
                phit0 = self.packet0.pop_phit()
                if not self.packet0.phits:
                    self.packet0 = None
            if self.packet1:
                phit1 = self.packet1.pop_phit()
                if not self.packet1.phits:
                    self.packet1 = None
            if self.packet2:
                phit2 = self.packet2.pop_phit()
                if not self.packet2.phits:
                    self.packet2 = None
            if self.packet3:
                phit3 = self.packet3.pop_phit()
                if not self.packet3.phits:
                    self.packet3 = None
            self.allocator_handler.handle_inputs(
                self.dut,
                phit0,
                phit1,
                phit2,
                phit3
            )

            await RisingEdge(self.dut.clk)

            # Only log if packet is for this port
            self.allocator_handler.process_interaction(self.dut, phit0)
            self.allocator_handler.process_interaction(self.dut, phit1)
            self.allocator_handler.process_interaction(self.dut, phit2)
            self.allocator_handler.process_interaction(self.dut, phit3)

            self.debug_cycle_counter += 1

@cocotb.test()
async def test_random_traffic(dut):
    # Initialize inputs

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await Timer(5, units="ns")  # Wait for clock to start
    await FallingEdge(dut.clk)  # Wait for a falling edge to start

    dut._log.info("\n\nStarting random traffic test\n")

    total_packets_dropped = 0
    total_iterations = 10
    number_of_cycles = 100000  # Number of cycles for each iteration
    packet_generation_frequency = 0.1  # Frequency of packet generation

    for iteration in range(total_iterations):
        traffic_generator = Traffic_Generator(
            dut,
            number_of_cycles=number_of_cycles,
            packet_generation_frequency=packet_generation_frequency,
            log=False,
        )
        await traffic_generator.process_traffic()

        total_packets_dropped += traffic_generator.allocator_handler.number_of_dropped_packets

        dut._log.info(f"\n\nRandom traffic test completed for iteration {iteration}\n")
        dut._log.info("Number of dropped packets: %d", traffic_generator.allocator_handler.number_of_dropped_packets)

    dut._log.info(f"\n\nAverage number of dropped packets per iteration: {total_packets_dropped / total_iterations}\n")