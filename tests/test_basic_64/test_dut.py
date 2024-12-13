from random import randint     
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import Apb4Bus
from cocotbext.apb import ApbMonitor

def returned_val(read_op):
    return int.from_bytes(read_op, byteorder='little')


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.regwidth = int(dut.REGWIDTH)
        self.n_regs   = int(dut.N_REGS)
        self.mask = (2 ** self.regwidth) - 1
        self.incr = int(self.regwidth/8)
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut
        
        apb_prefix="s_apb"
        self.bus = Apb4Bus.from_prefix(dut, apb_prefix)
        clk_name="clk"
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
    bytesdata = x.to_bytes(len(tb.bus.pwdata), 'little')
    await tb.intf.write(0x0000, bytesdata)

    read_op = await tb.intf.read(0x0000)
    ret = returned_val(read_op)
    assert x == ret
    
    await tb.intf.read(0x0000, bytesdata)
    await tb.intf.read(0x0000, x)

    x = 0x12345679
    bytesdata = x.to_bytes(len(tb.bus.pwdata), 'little')
    await tb.intf.write(0x0000, x)

    await tb.intf.read(0x0000, x)
    await tb.intf.read(0x0000, 0x12345679)

    await tb.intf.write(0x0000, 0x12)
    await tb.intf.read(0x0000, 0x12)
    
    await tb.intf.write(0x0000, 0x0)
    await tb.intf.write(0x0000, 0x8765432163ea4ff4, 0x80)
    await tb.intf.read(0x0000, 0x8700000000000000)
    await tb.intf.write(0x0000, 0x563464569912da3a, 0x40)
    await tb.intf.read(0x0000, 0x8734000000000000)
    await tb.intf.write(0x0000, 0x6975423312d8d48a, 0x20)
    await tb.intf.read(0x0000, 0x8734420000000000)
    await tb.intf.write(0x0000, 0x21454568695769b6, 0x10)
    await tb.intf.read(0x0000, 0x8734426800000000)
    await tb.intf.write(0x0000, 0xeb9c904fd9c9cb7b, 0x8)
    await tb.intf.read(0x0000,  0x87344268d9000000)
    await tb.intf.write(0x0000, 0x273f242004d6157d, 0x4)
    await tb.intf.read(0x0000,  0x87344268d9d60000)
    await tb.intf.write(0x0000, 0xc00a466d695769b6, 0x2)
    await tb.intf.read(0x0000,  0x87344268d9d66900)
    await tb.intf.write(0x0000, 0xa65122c00aa87356, 0x1)
    await tb.intf.read(0x0000,  0x87344268d9d66956)
    await tb.intf.write(0x0000, 0x0)
    await tb.intf.read(0x0000, 0x0)

    await tb.intf.write(0x0004, 0x87654321)
    await tb.intf.read(0x0000, 0x87654321)

    await tb.intf.write(0x0004, 0x97654321)
    await tb.cr.wait_clkn(2)
    await tb.intf.read(0x0006, 0x97654321)

    await tb.intf.write(0x0014, 0x77654321)
    await tb.intf.read(0x0016, 0x77654321)
    
    await tb.intf.write(0x0000, 0x7765432121454568)
    await tb.intf.read(0x0000, 0x7765432121454568)

    x = []
    for i in range(tb.n_regs):
        x.append(randint(0, (2**tb.regwidth)-1))
    
    for i in range(tb.n_regs):
        bytesdata = x[i].to_bytes(len(tb.bus.pwdata), 'little')
        await tb.intf.write(0x0000 + (i*tb.incr), bytesdata)
    
    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs-1)
        y = x[z] & tb.mask
        read_op = await tb.intf.read(0x0000 + (z*tb.incr))
        ret = returned_val(read_op)
        assert y == ret
    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs-1)
        y = x[z] & tb.mask
        read_op = await tb.intf.read(0x0000 + (z*tb.incr), y.to_bytes(len(tb.bus.prdata), "little"))
    for i in range(tb.n_regs):
        z = randint(0, tb.n_regs-1)
        y = x[z] & tb.mask
        tb.intf.read_nowait(0x0000 + (z*tb.incr), y.to_bytes(len(tb.bus.prdata), "little"))

    for i in range(tb.n_regs):
        y = x[i] & tb.mask
        read_op = await tb.intf.read(0x0000 + (i*tb.incr))
        ret = returned_val(read_op)
        assert y == ret


    await tb.cr.end_test(200)
