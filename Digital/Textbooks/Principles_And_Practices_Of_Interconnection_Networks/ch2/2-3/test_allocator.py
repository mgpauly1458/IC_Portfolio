# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_my_design.py (simple)

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock
import random
import pandas as pd
import math

random.seed(0)  # Forreproducibility in tests

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
    def __init__(self, log=False):
        self.phits = []
        self.total_data_size = random.randint(32, 512) // 16 * 16  # Total data size must be a multiple of 16 bits
        self.number_of_data_phits = self.total_data_size // 16
        self.total_size_bits = self.total_data_size + (self.total_data_size / 16)*2 + 18  # Total size includes header and payload phits
        self.destination = random.randint(0, 63)  # Destination address is 6 bits
        self.create_phits()

        if log:
            print(f"Packet created with destination: {bin(self.destination)[2:].zfill(6)}, number of payload phits: {self.number_of_data_phits}")

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

    def _packet_was_dropped(self, dut,port_number):
        # Assumed always working with header phits
        hold = dut.hold.value
        if port_number == 0 and hold != 0b0001 and hold != 0b0000:
            return True
        elif port_number == 1 and hold != 0b0010 and hold != 0b0000:
            return True
        elif port_number == 2 and hold != 0b0100 and hold != 0b0000:
            return True
        elif port_number == 3 and hold != 0b1000 and hold != 0b0000:
            return True
        return False

    def process_interaction(self, dut, phit: Phit, port_number, callback):
        if phit.type != HEADER_PHIT_TYPE or (phit.get_address() >> 4) != dut.thisPort.value:
            return
        
        if self.log:
            dut._log.info("Allocator interaction with phit: %s", phit)
            dut._log.info("Allocator input value: %s", bin(phit.allocator_input()))

        # log output
        if self.log:
            dut._log.info("select: %s", bin(dut.select.value)[2:].zfill(4))
            dut._log.info("shift: %s", bin(dut.shift.value)[2:].zfill(4))
            dut._log.info("hold: %s", bin(dut.hold.value)[2:].zfill(4))

        if self._packet_was_dropped(dut, port_number):
            # Header packet showed up and hold is set, so packet is dropped
            self.number_of_dropped_packets += 1
            callback(port_number)

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
        self.total_packets_generated = 0

        self.packet0 = None
        self.packet1 = None
        self.packet2 = None
        self.packet3 = None
        
        self.number_of_0_packets_dropped = 0
        self.number_of_1_packets_dropped = 0
        self.number_of_2_packets_dropped = 0
        self.number_of_3_packets_dropped = 0

    def add_dropped_packet_to_port_callback(self, port_number):
        if port_number == 0:
            self.number_of_0_packets_dropped += 1
        elif port_number == 1:
            self.number_of_1_packets_dropped += 1
        elif port_number == 2:
            self.number_of_2_packets_dropped += 1
        elif port_number == 3:
            self.number_of_3_packets_dropped += 1
        else:
            raise ValueError(f"Invalid port number: {port_number}")

    def _packet_generated_log(self, packet_number):
        print(f"\nPacket {packet_number} generated. Current cycle: {self.debug_cycle_counter}")

    def generate_traffic(self):
        # Randomly decide if a packet should be created or not.
        # If a packet is already being processed, do not create a new one.
        if not self.packet0 and random.random() < self.packet_generation_frequency:
            self.packet0 = Packet(self.log)
            self.total_packets_generated += 1
            if self.log:
                self._packet_generated_log(0)
        if not self.packet1 and random.random() < self.packet_generation_frequency:
            self.packet1 = Packet(self.log)
            self.total_packets_generated += 1
            if self.log:
                self._packet_generated_log(1)
        if not self.packet2 and random.random() < self.packet_generation_frequency:
            self.packet2 = Packet(self.log)
            self.total_packets_generated += 1
            if self.log:
                self._packet_generated_log(2)
        if not self.packet3 and random.random() < self.packet_generation_frequency:
            self.packet3 = Packet(self.log)
            self.total_packets_generated += 1
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
            self.allocator_handler.process_interaction(self.dut, phit0, 0, self.add_dropped_packet_to_port_callback)
            self.allocator_handler.process_interaction(self.dut, phit1, 1, self.add_dropped_packet_to_port_callback)
            self.allocator_handler.process_interaction(self.dut, phit2, 2, self.add_dropped_packet_to_port_callback)
            self.allocator_handler.process_interaction(self.dut, phit3, 3, self.add_dropped_packet_to_port_callback)

            self.debug_cycle_counter += 1

@cocotb.test()
async def test_random_traffic(dut):
    # Initialize inputs
    df = pd.DataFrame(columns=["Number of Cycles", "Average Dropped Packets", "Ratio of Dropped Packets"])

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await Timer(5, units="ns")  # Wait for clock to start
    await FallingEdge(dut.clk)  # Wait for a falling edge to start

    dut._log.info("\n\nStarting random traffic test\n")

    total_iterations = 10
    
    start_number_of_cycles = 1000
    end_number_of_cycles = 10000  # Number of cycles for each iteration
    number_of_cycle_step_size = 1000

    start_packet_generation_frequency = 0.1  # Probability of generating a packet each cycle
    end_packet_generation_frequency = 1  # Probability of generating a packet each cycle
    packet_generation_frequency_step_size = 0.05
    
    current_number_of_cycles = start_number_of_cycles
    current_packet_generation_frequency = start_packet_generation_frequency

    data_file_name = "data/random_traffic_results_constant_number_of_cycles.csv"
    # data_file_name = "data/random_traffic_results_constant_packet_gen_frequency.csv"

    while current_packet_generation_frequency <= end_packet_generation_frequency:
    # while current_number_of_cycles <= end_number_of_cycles:
        total_packets_dropped = 0
        total_0_packets_dropped = 0
        total_1_packets_dropped = 0
        total_2_packets_dropped = 0
        total_3_packets_dropped = 0
        for iteration in range(total_iterations):
            traffic_generator = Traffic_Generator(
                dut,
                number_of_cycles=5000,
                # number_of_cycles=current_number_of_cycles,
                packet_generation_frequency=current_packet_generation_frequency,
                # packet_generation_frequency=0.1,
            log=False,
        )
            await traffic_generator.process_traffic()

            total_packets_dropped += traffic_generator.allocator_handler.number_of_dropped_packets
            total_0_packets_dropped += traffic_generator.number_of_0_packets_dropped
            total_1_packets_dropped += traffic_generator.number_of_1_packets_dropped
            total_2_packets_dropped += traffic_generator.number_of_2_packets_dropped
            total_3_packets_dropped += traffic_generator.number_of_3_packets_dropped

            dut._log.info(f"\n\nRandom traffic test completed for iteration {iteration}\n")
            dut._log.info("Number of dropped packets: %d", traffic_generator.allocator_handler.number_of_dropped_packets)

        average_dropped_packets = total_packets_dropped / total_iterations
        average_0_packets_dropped = total_0_packets_dropped / total_iterations
        average_1_packets_dropped = total_1_packets_dropped / total_iterations
        average_2_packets_dropped = total_2_packets_dropped / total_iterations
        average_3_packets_dropped = total_3_packets_dropped / total_iterations
        standard_deviation_dropped_packets = math.sqrt(
            (average_0_packets_dropped ** 2 + average_1_packets_dropped ** 2 + average_2_packets_dropped ** 2 + average_3_packets_dropped ** 2) / 4
        )

        dut._log.info(f"\n\nCompleted {total_iterations} iterations with {current_number_of_cycles} cycles each.\n")
        dut._log.info(f"\n\nAverage number of dropped packets per iteration: {average_dropped_packets}\n")
        dut._log.info(f"Ratio of dropped packets to total cycles: {average_dropped_packets / current_number_of_cycles}\n")

        # Add results to df
        new_row = {
            "Number of Cycles": current_number_of_cycles,
            "Packet Generation Frequency": current_packet_generation_frequency,
            "Average Dropped Packets": average_dropped_packets,
            "Ratio of Dropped Packets to Total Cycles": average_dropped_packets / current_number_of_cycles,
            "Ratio of Dropped Packets to Packet Generation Frequency": average_dropped_packets / current_packet_generation_frequency,
            "Total Packets Generated": traffic_generator.total_packets_generated,
            "Average 0 Packets Dropped": average_0_packets_dropped,
            "Average 1 Packets Dropped": average_1_packets_dropped,
            "Average 2 Packets Dropped": average_2_packets_dropped,
            "Average 3 Packets Dropped": average_3_packets_dropped,
            "Standard Deviation Dropped Packets": standard_deviation_dropped_packets
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # reset for next iteration
        current_number_of_cycles += number_of_cycle_step_size
        current_packet_generation_frequency += packet_generation_frequency_step_size
        total_packets_dropped = 0

    # Save results to CSV
    df.to_csv(data_file_name, index=False)