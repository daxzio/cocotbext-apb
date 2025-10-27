from random import randint
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import ApbBus
from cocotbext.apb import ApbMonitor


def returned_val(read_op):
    return int.from_bytes(read_op, byteorder="little")


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        apb_prefix = "s_apb"
        self.bus = ApbBus.from_prefix(dut, apb_prefix)
        clk_name = "clk"
        self.intf = ApbMaster(self.bus, getattr(dut, clk_name))
        self.apb_mon = ApbMonitor(self.bus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


#         self.intf = ApbDriver(dut)


@test()
async def test_dut_proper_err(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(200)

    # Read initial value
    await tb.intf.read(0x0, 40)

    # Write and read back
    await tb.intf.write(0x0, 61)
    await tb.intf.read(0x0, 61)

    # Read constant value
    await tb.intf.read(0x4, 80)

    # Try to write (should error)
    await tb.intf.write(0x4, 81, error_expected=True)

    # Verify value unchanged
    await tb.intf.read(0x4, 80)

    # --------------------------------------------------------------------------
    # r_w - sw=w; hw=r; // Storage element
    # --------------------------------------------------------------------------

    # Try to read (should error, returns 0)
    await tb.intf.read(0x8, 0, error_expected=True)

    # Verify hardware sees initial value
    assert int(tb.dut.hwif_out_r_w_f.value) == 100, "Initial HW value mismatch"

    # Write new value
    await tb.intf.write(0x8, 101)

    # Try to read again (still errors)
    await tb.intf.read(0x8, 0, error_expected=True)

    # Verify hardware sees new value
    assert int(tb.dut.hwif_out_r_w_f.value) == 101, "Updated HW value mismatch"

    await tb.cr.end_test(200)


@test()
async def test_dut_incorrect_write_err(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(200)

    # Read constant value
    await tb.intf.read(0x4, 80)

    tb.intf.exception_enabled = False
    assert (
        tb.intf.exception_occurred == False
    ), "Exception occurred when it should not have"
    # Try to write (should error)
    await tb.intf.write(0x4, 81, error_expected=False)
    assert (
        tb.intf.exception_occurred == True
    ), "Exception did not occur when it should have"

    await tb.cr.end_test(200)


@test()
async def test_dut_incorrect_read_err(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(200)

    # Read constant value
    await tb.intf.write(0x8, 101)

    tb.intf.exception_enabled = False
    assert (
        tb.intf.exception_occurred == False
    ), "Exception occurred when it should not have"
    # Try to write (should error)
    await tb.intf.read(0x8, 0, error_expected=False)
    assert (
        tb.intf.exception_occurred == True
    ), "Exception did not occur when it should have"

    await tb.cr.end_test(200)
