from random import randint
from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import ApbMaster
from cocotbext.apb import Apb4Bus
from cocotbext.apb import ApbMonitor
from cocotbext.apb import ApbRam
from cocotbext.apb import ApbSlave
from cocotbext.apb import MemoryRegion
from cocotbext.apb import ApbProt
from cocotbext.apb import APBSlvErr, APBPrivilegedErr, APBInstructionErr

# def returned_val(read_op):
#     return int.from_bytes(read_op, byteorder='little')


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):

        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        self.sbus = Apb4Bus.from_prefix(dut, "s_apb")
        self.mbus = Apb4Bus.from_prefix(dut, "m_apb")
        clk_name = "clk"
        self.m = ApbMaster(self.sbus, getattr(dut, clk_name))

        self.apb_mon = ApbMonitor(self.sbus, getattr(dut, "clk"))
        self.apb_mon.enable_logging()


@test()
async def test_apb_pprot(dut):
    tb = testbench(dut, reset_sense=1)
    tb.s = ApbSlave(tb.mbus, getattr(dut, "clk"))
    region = MemoryRegion(2**tb.s.address_width)
    tb.s.target = region
    tb.s.privileged_addrs = [[0x1000, 0x1FFF], 0x3000]
    tb.s.instruction_addrs = [[0x2000, 0x2FFF], 0x4000]

    await tb.cr.wait_clkn(20)

    await tb.m.write(0x0010, 0x87654321)
    await tb.m.read(0x0010, 0x87654321)

    await tb.m.write(0x0010, 0x63456347, prot=ApbProt.NONSECURE)
    await tb.m.read(0x0010, 0x63456347, prot=ApbProt.NONSECURE)

    await tb.m.write(0x1000, 0x74568562, prot=ApbProt.PRIVILEGED)
    await tb.m.read(0x1000, 0x74568562, prot=ApbProt.PRIVILEGED)
    await tb.m.read(0x1000, 0x74568562, prot=ApbProt.NONSECURE)

    await tb.m.write(0x1000, 0x52346325, prot=ApbProt.NONSECURE)
    await tb.m.read(0x1000, 0x52346325, prot=ApbProt.PRIVILEGED)

    await tb.m.read(0x1000, 0x52346325, prot=ApbProt.NONSECURE, error_expected=False)

    await tb.m.write(0x2000, 0xA356B3E1, prot=ApbProt.INSTRUCTION)
    await tb.m.read(0x2000, 0xA356B3E1, prot=ApbProt.INSTRUCTION)
    await tb.m.read(0x2000, 0xA356B3E1, prot=ApbProt.NONSECURE, error_expected=False)

    await tb.m.write(0x2000, 0x45325533, prot=ApbProt.NONSECURE)
    await tb.m.read(0x2000, 0x45325533, prot=ApbProt.INSTRUCTION)

    await tb.m.write(0x2000, 0x45325533, prot=ApbProt.NONSECURE, error_expected=False)
    await tb.m.read(0x2000, 0x45325533, prot=ApbProt.INSTRUCTION)

    await tb.cr.end_test(20)


@test()
async def test_apb_memdump(dut):
    tb = testbench(dut, reset_sense=1)
    tb.s = ApbSlave(tb.mbus, getattr(dut, "clk"))
    region = MemoryRegion(2**tb.s.address_width)
    tb.s.target = region

    await tb.cr.wait_clkn(20)

    await tb.m.write(0x0010, 0x87654321)
    await tb.m.read(0x0010, 0x87654321)

    x = []
    for i in range(32):
        x.append(randint(0, 0xFFFFFFFF))

    for i in range(32):
        await tb.m.write(0x0000 + i * 0x4, x[i])

    index = randint(0, 30)
    z = await tb.s.target.read(index * 4, 1)
    y = int.from_bytes(z, byteorder="little")
    assert y == (x[index] & 0xFF)

    z = await tb.s.target.read((index * 4) + 1, 1)
    y = int.from_bytes(z, byteorder="little")
    assert y == ((x[index] >> 8) & 0xFF)

    z = await tb.s.target.read_byte(index * 4)
    y = int.from_bytes(z, byteorder="little")
    assert y == (x[index] & 0xFF)

    z = await tb.s.target.read_byte((index * 4) + 1)
    y = int.from_bytes(z, byteorder="little")
    assert y == ((x[index] >> 8) & 0xFF)

    z = await tb.s.target.read_word(index * 4)
    assert z == (x[index] & 0xFFFF)

    z = await tb.s.target.read_dword(index * 4)
    assert z == x[index]

    z = await tb.s.target.read_qword(index * 4)
    assert z == x[index] | (x[index + 1] << 32)

    await tb.cr.end_test(20)


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
    await tb.m.write(0x0020, 0xA356B3E1, 0x1)
    await tb.m.read(0x0020, 0x523285E1)

    x = []
    for i in range(32):
        x.append(randint(0, 0xFFFFFFFF))

    for i in range(32):
        await tb.m.write(0x0000 + i * 0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i * 0x4, x[i])

    tb.s.enable_backpressure()
    x = []
    for i in range(32):
        x.append(randint(0, 0xFFFFFFFF))

    for i in range(32):
        await tb.m.write(0x0000 + i * 0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i * 0x4, x[i])

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
    await tb.m.write(0x0020, 0xA356B3E1, 0x1)
    await tb.m.read(0x0020, 0x523285E1)
    x = []
    for i in range(32):
        x.append(randint(0, 0xFFFFFFFF))

    for i in range(32):
        await tb.m.write(0x0000 + i * 0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i * 0x4, x[i])

    tb.s.enable_backpressure()
    x = []
    for i in range(32):
        x.append(randint(0, 0xFFFFFFFF))

    for i in range(32):
        await tb.m.write(0x0000 + i * 0x4, x[i])

    for i in range(32):
        await tb.m.read(0x0000 + i * 0x4, x[i])

    await tb.cr.end_test(20)
