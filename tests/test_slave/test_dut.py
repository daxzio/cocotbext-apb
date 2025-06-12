from random import randint     
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import Apb4Bus
from cocotbext.apb import ApbMonitor
from cocotbext.apb import ApbRam
from cocotbext.apb import ApbSlave
from cocotbext.apb import MemoryRegion

# def returned_val(read_op):
#     return int.from_bytes(read_op, byteorder='little')


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut
        
        self.sbus = Apb4Bus.from_prefix(dut, "s_apb")
        self.mbus = Apb4Bus.from_prefix(dut, "m_apb")
        clk_name="clk"
        self.m = ApbMaster(self.sbus, getattr(dut, clk_name))

        self.apb_mon = ApbMonitor(self.sbus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()



@test()
async def test_apb_slave(dut):
    tb = testbench(dut, reset_sense=1)
    tb.s = ApbSlave(tb.mbus, getattr(dut, "clk"))
    region = MemoryRegion(2**tb.s.address_width)
    tb.s.target = region

    await tb.cr.wait_clkn(20)
    
    await tb.m.write(0x0010, 0x87654321)
    await tb.m.read(0x0010, 0x87654321)
    
    await tb.m.read(0x0020, 0x00000000)
    await tb.m.write(0x0020, 0x52346325, 0x8)
    await tb.m.read(0x0020, 0x52000000)
    await tb.m.write(0x0020, 0x45325533, 0x4)
    await tb.m.read(0x0020, 0x52320000)
    await tb.m.write(0x0020, 0x74568562, 0x2)
    await tb.m.read(0x0020, 0x52328500)
    await tb.m.write(0x0020, 0xa356b3e1, 0x1)
    await tb.m.read(0x0020, 0x523285e1)

    x = []
    for i in range(32):
        x.append(randint(0, 0xffffffff))

    for i in range(32):
        await tb.m.write(0x0000 + i*0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i*0x4, x[i])
    
    tb.s.enable_backpressure()
    x = []
    for i in range(32):
        x.append(randint(0, 0xffffffff))

    for i in range(32):
        await tb.m.write(0x0000 + i*0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i*0x4, x[i])
    
    await tb.cr.end_test(20)

@test()
async def test_apb_ram(dut):
    tb = testbench(dut, reset_sense=1)
    tb.s = ApbRam(tb.mbus, getattr(dut, "clk"))

    await tb.cr.wait_clkn(20)
    
    await tb.m.write(0x0010, 0x87654321)
    await tb.m.read(0x0010, 0x87654321)

    await tb.m.read(0x0020, 0x00000000)
    await tb.m.write(0x0020, 0x52346325, 0x8)
    await tb.m.read(0x0020, 0x52000000)
    await tb.m.write(0x0020, 0x45325533, 0x4)
    await tb.m.read(0x0020, 0x52320000)
    await tb.m.write(0x0020, 0x74568562, 0x2)
    await tb.m.read(0x0020, 0x52328500)
    await tb.m.write(0x0020, 0xa356b3e1, 0x1)
    await tb.m.read(0x0020, 0x523285e1)
    x = []
    for i in range(32):
        x.append(randint(0, 0xffffffff))

    for i in range(32):
        await tb.m.write(0x0000 + i*0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i*0x4, x[i])
    
    tb.s.enable_backpressure()
    x = []
    for i in range(32):
        x.append(randint(0, 0xffffffff))

    for i in range(32):
        await tb.m.write(0x0000 + i*0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i*0x4, x[i])
    
    await tb.cr.end_test(20)
