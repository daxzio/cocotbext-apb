from random import randint     
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import Apb4Bus

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

    bytesdata = 0x12345679.to_bytes(len(tb.bus.pwdata), 'little')
    await tb.intf.read(0x0000, bytesdata)
    try:
        await tb.intf.read(0x0000, bytesdata)
#         raise
    except Exception:
        pass

#     x = []
#     for i in range(tb.n_regs):
#         x.append(randint(0, (2**32)-1))
#     
#     for i in range(tb.n_regs):
#         bytesdata = x[i].to_bytes(len(tb.bus.pwdata), 'little')
#         await tb.intf.write(0x0000 + (i*tb.incr), bytesdata)
#     
#     for i in range(tb.n_regs):
#         z = randint(0, tb.n_regs-1)
#         y = x[z] & tb.mask
#         read_op = await tb.intf.read(0x0000 + (z*tb.incr))
#         ret = returned_val(read_op)
#         assert y == ret
#     for i in range(tb.n_regs):
#         z = randint(0, tb.n_regs-1)
#         y = x[z] & tb.mask
#         read_op = await tb.intf.read(0x0000 + (z*tb.incr), y.to_bytes(len(tb.bus.prdata), "little"))
#     for i in range(tb.n_regs):
#         z = randint(0, tb.n_regs-1)
#         y = x[z] & tb.mask
#         tb.intf.read_nowait(0x0000 + (z*tb.incr), y.to_bytes(len(tb.bus.prdata), "little"))
# 
# #     print('break')
# #     await tb.cr.wait_clkn(20)
#     for i in range(tb.n_regs):
# #         print(i)
#         y = x[i] & tb.mask
#         read_op = await tb.intf.read(0x0000 + (i*tb.incr))
#         ret = returned_val(read_op)
#         assert y == ret


    await tb.cr.end_test(200)
