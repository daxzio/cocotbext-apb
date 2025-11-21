from random import randint
from cocotb import test
from cocotb.triggers import Timer

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import ApbBus
from cocotbext.apb import ApbMonitor


def returned_val(read_op):
    return int.from_bytes(read_op, byteorder="little")


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.regwidth = len(dut.s_apb_pwdata)
        self.n_regs = 2 ** (len(dut.s_apb_paddr) - 2)
        # self.n_regs = 32
        self.mask = (2**self.regwidth) - 1
        self.incr = int(self.regwidth / 8)
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        apb_prefix = "s_apb"
        self.bus = ApbBus.from_prefix(dut, apb_prefix)
        clk_name = "clk"
        self.intf = ApbMaster(self.bus, getattr(dut, clk_name))
        self.apb_mon = ApbMonitor(self.bus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


@test()
async def test_dut_basic(dut):
    tb = testbench(dut)

    await tb.cr.wait_clkn(200)

    await Timer(1, "ns")
    await tb.intf.write(0x000C, 0x87654321)
    await tb.intf.write(0x0004, 0x21454568)
    await tb.intf.write(0x0008, 0x73462364)
    await Timer(5.1, "ns")
    await tb.intf.write(0x000C, 0x87654321)
    await tb.intf.write(0x0004, 0x21454568)
    await tb.cr.wait_clkn(4)

    await Timer(9, "ns")
    await tb.intf.read(0x0004, 0x21454568)
    await tb.intf.read(0x000C, 0x87654321)
    await Timer(6, "ns")
    await tb.intf.read(0x0004, 0x21454568)
    await tb.intf.read(0x000C, 0x87654321)

    await tb.intf.write(0x000C, 0x87654321)
    await tb.intf.write(0x0004, 0x21454568)
    await tb.intf.read(0x0004, 0x21454568)
    await tb.intf.write(0x0008, 0x73462364)
    await tb.intf.read(0x000C, 0x87654321)
    await tb.cr.wait_clkn(20)

    x = randint(0, 0xFFFFFFFFFFFFFFFF)
    await tb.intf.write(0x0000, x, length=8)
    await tb.intf.read(0x0000, x & 0xFFFFFFFF)
    await tb.intf.read(0x0004, (x >> 32) & 0xFFFFFFFF)

    await tb.cr.end_test(200)
