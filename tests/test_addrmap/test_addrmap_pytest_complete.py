"""
Complete pytest-based test for test_addrmap with parameterization.

This example shows:
1. Parameterization for different REGWIDTH values
2. RDL file generation before running tests
3. Proper file path handling
4. Error handling
"""

import pytest
from cocotb_test.simulator import run
import os
import subprocess
import sys


def generate_rdl_file(test_dir, regwidth, cpuif="apb4-flat"):
    """
    Generate RDL file for the given register width.

    This replaces the Makefile-based RDL generation.
    """
    rdl_file = f"{test_dir}/regblock.rdl"
    output_file = f"{test_dir}/regblock_{regwidth}.sv"

    # Check if file already exists and is newer than RDL file
    if os.path.exists(output_file):
        rdl_mtime = os.path.getmtime(rdl_file)
        output_mtime = os.path.getmtime(output_file)
        if output_mtime > rdl_mtime:
            # File is up to date, skip generation
            return output_file

    # Generate the RDL file using peakrdl
    cmd = [
        "peakrdl",
        "regblock",
        rdl_file,
        "-o",
        test_dir,
        "--cpuif",
        cpuif,
        "-P",
        f"REGWIDTH={regwidth}",
        "--rename",
        "regblock",
    ]

    try:
        result = subprocess.run(
            cmd, cwd=test_dir, check=True, capture_output=True, text=True
        )
        # Rename the output file if needed
        generated_file = f"{test_dir}/regblock.sv"
        if os.path.exists(generated_file) and generated_file != output_file:
            os.rename(generated_file, output_file)
        return output_file
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Failed to generate RDL file: {e.stderr}")
    except FileNotFoundError:
        pytest.skip("peakrdl not found. Install with: pip install peakrdl-regblock")


@pytest.fixture(scope="session")
def ensure_rdl_generated():
    """Fixture to ensure RDL files are generated before tests run."""
    # This runs once per test session
    # You could generate all required files here
    pass


# Define the test parameters - this will run the test 3 times with different REGWIDTH values
@pytest.mark.parametrize("regwidth", [8, 16, 32])
def test_addrmap(regwidth, ensure_rdl_generated):
    """
    Test addrmap functionality with different register widths.

    This test will be run 3 times:
    - test_addrmap[8]
    - test_addrmap[16]
    - test_addrmap[32]
    """

    # Get the test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate the RDL file for this regwidth
    regblock_file = generate_rdl_file(test_dir, regwidth)

    if not os.path.exists(regblock_file):
        pytest.skip(f"RDL file not generated: {regblock_file}")

    # Run the simulation with cocotb-test
    run(
        # Verilog sources - list all required files
        verilog_sources=[
            regblock_file,
            # Add other required source files here if needed
            # f"{test_dir}/../common/common.sv",
        ],
        # Top-level module name
        toplevel="regblock",
        # Python test module (your actual test code - unchanged!)
        module="test_dut",
        # Parameters to pass to the DUT at elaboration time
        # For Verilog, these become -P parameters
        # For VHDL, these become -g generics
        parameters={"REGWIDTH": regwidth},
        # Simulator build directory - use unique directory per parameter
        sim_build=f"{test_dir}/sim_build_{regwidth}",
        # Simulator selection (can also use environment variable SIM)
        # simulator="icarus",  # Options: icarus, verilator, vcs, etc.
        # Additional compile/simulation arguments if needed
        # extra_args=["-Wno-WIDTHEXPAND"],  # Example for Verilator
    )


# Example: Test with multiple parameters
@pytest.mark.parametrize("regwidth,expected_incr", [(8, 1), (16, 2), (32, 4)])
def test_addrmap_with_expected_values(regwidth, expected_incr):
    """
    Example showing how to test with multiple related parameters.

    This demonstrates testing with both input parameters and expected values.
    """
    test_dir = os.path.dirname(os.path.abspath(__file__))
    regblock_file = generate_rdl_file(test_dir, regwidth)

    if not os.path.exists(regblock_file):
        pytest.skip(f"RDL file not generated: {regblock_file}")

    # You can access expected_incr in your test_dut.py via environment variable
    # or pass it as a parameter if your DUT supports it
    os.environ["EXPECTED_INCR"] = str(expected_incr)

    try:
        run(
            verilog_sources=[regblock_file],
            toplevel="regblock",
            module="test_dut",
            parameters={"REGWIDTH": regwidth},
            sim_build=f"{test_dir}/sim_build_{regwidth}_{expected_incr}",
        )
    finally:
        # Clean up environment variable
        os.environ.pop("EXPECTED_INCR", None)
