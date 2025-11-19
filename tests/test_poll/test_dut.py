from random import randint, shuffle
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import ApbBus
from cocotbext.apb import ApbMonitor


# def returned_val(read_op):
#     return int.from_bytes(read_op, byteorder="little")


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        # self.n_regs = 32
        # self.mask = (2**self.regwidth) - 1
        # self.incr = int(self.regwidth / 8)
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        apb_prefix = "s_apb"
        self.bus = ApbBus.from_prefix(dut, apb_prefix)
        clk_name = "clk"
        self.intf = ApbMaster(self.bus, getattr(dut, clk_name))
        self.apb_mon = ApbMonitor(self.bus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


@test()
async def test_dut_poll(dut):
    tb = testbench(dut)

    await tb.cr.wait_clkn(20)

    await tb.intf.read(0x04, 0)
    await tb.intf.write(0x00, 1)
    await tb.intf.read(0x04, 1)
    await tb.intf.read(0x04, 1)

    await tb.intf.poll(0x04, 0)

    await tb.cr.end_test(20)


@test()
async def test_dut_poll2(dut):
    tb = testbench(dut)

    await tb.cr.wait_clkn(20)

    await tb.intf.read(0x04, 0)
    await tb.intf.write(0x00, 1)

    await tb.intf.poll(0x04, 0)

    await tb.cr.end_test(20)


@test()
async def test_dut_poll3(dut):
    tb = testbench(dut)

    await tb.cr.wait_clkn(20)

    await tb.intf.read(0x04, 0)
    await tb.intf.write(0x00, 1)

    # await tb.intf.poll(0x04, 0)
    await tb.intf.poll(0x04, b"\x00\x00\x00\x00")

    await tb.cr.end_test(20)
