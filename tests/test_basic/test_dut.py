from random import randint
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import Apb4Bus
from cocotbext.apb import ApbMonitor


def returned_val(read_op):
    return int.from_bytes(read_op, byteorder="little")


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.regwidth = int(dut.REGWIDTH)
        self.n_regs = int(dut.N_REGS)
        self.mask = (2**self.regwidth) - 1
        self.incr = int(self.regwidth / 8)
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        apb_prefix = "s_apb"
        self.bus = Apb4Bus.from_prefix(dut, apb_prefix)
        clk_name = "clk"
        self.intf = ApbMaster(self.bus, getattr(dut, clk_name))
        self.apb_mon = ApbMonitor(self.bus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


#         self.intf = ApbDriver(dut)


@test()
async def test_dut_basic(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(200)

    read_op = await tb.intf.read(0x0000)
    ret = returned_val(read_op)
    assert 0x1 == ret

    x = 0x12345678
    bytesdata = x.to_bytes(len(tb.bus.pwdata), "little")
    await tb.intf.write(0x0000, bytesdata)

    read_op = await tb.intf.read(0x0000)
    ret = returned_val(read_op)
    assert x == ret

    await tb.intf.read(0x0000, bytesdata)
    await tb.intf.read(0x0000, x)

    x = 0x12345679
    bytesdata = x.to_bytes(len(tb.bus.pwdata), "little")
    await tb.intf.write(0x0000, x)

    await tb.intf.read(0x0000, x)
    await tb.intf.read(0x0000, 0x12345679)

    await tb.intf.write(0x0000, 0x12)
    await tb.intf.read(0x0000, 0x12)

    await tb.intf.write(0x0000, 0x0)
    await tb.intf.write(0x0000, 0x87654321, 0x8)
    await tb.intf.read(0x0000, 0x87000000)
    await tb.intf.write(0x0000, 0x56346456, 0x4)
    await tb.intf.read(0x0000, 0x87340000)
    await tb.intf.write(0x0000, 0x69754233, 0x2)
    await tb.intf.read(0x0000, 0x87344200)
    await tb.intf.write(0x0000, 0x21454568, 0x1)
    await tb.intf.read(0x0000, 0x87344268)
    await tb.intf.write(0x0000, 0x0)
    await tb.intf.read(0x0000, 0x0)

    await tb.intf.write(0x0002, 0x87654321)
    await tb.intf.read(0x0000, 0x87654321)

    await tb.intf.write(0x0004, 0x97654321)
    await tb.cr.wait_clkn(2)
    await tb.intf.read(0x0006, 0x97654321)

    await tb.intf.write(0x0014, 0x77654321)
    await tb.intf.read(0x0016, 0x77654321)

    x = []
    for i in range(tb.n_regs):
        x.append(randint(0, (2**32) - 1))

    for i in range(tb.n_regs):
        bytesdata = x[i].to_bytes(len(tb.bus.pwdata), "little")
        await tb.intf.write(0x0000 + (i * tb.incr), bytesdata)

    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs - 1)
        y = x[z] & tb.mask
        read_op = await tb.intf.read(0x0000 + (z * tb.incr))
        ret = returned_val(read_op)
        assert y == ret
    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs - 1)
        y = x[z] & tb.mask
        read_op = await tb.intf.read(
            0x0000 + (z * tb.incr), y.to_bytes(len(tb.bus.prdata), "little")
        )
    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs - 1)
        y = x[z] & tb.mask
        tb.intf.read_nowait(
            0x0000 + (z * tb.incr), y.to_bytes(len(tb.bus.prdata), "little")
        )

    #     print('break')
    #     await tb.cr.wait_clkn(20)
    for i in range(tb.n_regs):
        #         print(i)
        y = x[i] & tb.mask
        read_op = await tb.intf.read(0x0000 + (i * tb.incr))
        ret = returned_val(read_op)
        assert y == ret

    await tb.cr.end_test(200)
