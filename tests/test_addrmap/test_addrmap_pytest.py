"""
Example pytest-based test for test_addrmap with parameterization.

This demonstrates how to migrate from Makefile-based cocotb tests to pytest
with cocotb-test, including parameterization for different elaboration-time values.
"""
import pytest
from cocotb_test.simulator import run
import os


# Define the test parameters - this will run the test 3 times with different REGWIDTH values
@pytest.mark.parametrize("regwidth", [8, 16, 32])
def test_addrmap(regwidth):
    """Test addrmap functionality with different register widths."""

    # Get the test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Determine which regblock file to use based on regwidth
    # This assumes the RDL files have been pre-generated
    regblock_file = f"{test_dir}/regblock_{regwidth}.sv"

    # If the file doesn't exist, fall back to generating it or using the base file
    if not os.path.exists(regblock_file):
        # You might want to generate it here or use a different approach
        regblock_file = f"{test_dir}/regblock.sv"

    # Run the simulation with cocotb-test
    run(
        # Verilog sources - list all required files
        verilog_sources=[
            regblock_file,
            # Add other required source files here
        ],
        # Top-level module name
        toplevel="regblock",
        # Python test module (your actual test code)
        module="test_dut",
        # Parameters to pass to the DUT at elaboration time
        parameters={"REGWIDTH": regwidth},
        # Simulator to use (can also be set via environment variable)
        sim_build=f"{test_dir}/sim_build_{regwidth}",
        # Additional compile/simulation arguments if needed
        # extra_args=["-Wno-WIDTHEXPAND"]  # Example for Verilator
    )
