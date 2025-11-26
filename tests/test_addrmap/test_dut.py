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

        self.regwidth = len(dut.s_apb_pwdata)
        self.mask = (2**self.regwidth) - 1
        self.incr = int(self.regwidth / 8)
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        apb_prefix = "s_apb"
        self.bus = ApbBus.from_prefix(dut, apb_prefix)
        clk_name = "clk"
        self.intf = ApbMaster(self.bus, getattr(dut, clk_name))
        self.intf.addrmap = {
            "STATUS": 0x0000 + self.incr * 0,
            "BUSY": 0x0000 + self.incr * 1,
            "CONFIG": 0x0000 + self.incr * 2,
            "INTERRUPT": 0x0000 + self.incr * 3,
        }

        self.apb_mon = ApbMonitor(self.bus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


#         self.intf = ApbDriver(dut)


@test()
async def test_dut_basic(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(200)

    await tb.intf.read(0x0000 + tb.incr * 0, 0x12)
    await tb.intf.read(0x0000 + tb.incr * 1, 0x34)
    await tb.intf.read(0x0000 + tb.incr * 2, 0x56)
    await tb.intf.read(0x0000 + tb.incr * 3, 0x78)

    await tb.intf.read("STATUS", 0x12)
    await tb.intf.read("BUSY", 0x34)
    await tb.intf.read("CONFIG", 0x56)
    await tb.intf.read("INTERRUPT", 0x78)

    x = []
    for i in range(4):
        x.append(randint(0, 0xFF))

    await tb.intf.write("STATUS", x[0])
    await tb.intf.write("BUSY", x[1])
    await tb.intf.write("CONFIG", x[2])
    await tb.intf.write("INTERRUPT", x[3])

    await tb.intf.read("STATUS", x[0])
    await tb.intf.read("BUSY", x[1])
    await tb.intf.read("CONFIG", x[2])
    await tb.intf.read("INTERRUPT", x[3])

    await tb.cr.end_test(200)
