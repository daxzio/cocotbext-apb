from random import randint, shuffle
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
        self.n_regs = 2 ** (len(dut.s_apb_paddr) - 2)
        self.num_slaves = len(dut.s_apb_psel)
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
async def test_dut_multi_device_random(dut):
    tb = testbench(dut, reset_sense=1)

    await tb.cr.wait_clkn(20)

    def build_block_accesses(start_addr: int, count: int, mask: int, device: int):
        block = []
        for idx in range(count):
            addr = start_addr + (idx * 4)
            value = randint(0, 0xFFFFFFFF)
            block.append((addr, mask, value, device))
        return block

    accesses = []

    # Generate accesses for each slave
    # RDL_ARGS in Makefile specifies N_REGS=32, so we can test 32 registers
    for i in range(tb.num_slaves):
        accesses += build_block_accesses(0x0000, 32, 0xFFFFFFFF, device=i)

    write_order = accesses[:]
    read_order = accesses[:]
    shuffle(write_order)
    shuffle(read_order)

    dut._log.info(f"Starting random writes ({len(write_order)} transactions)...")
    for addr, _mask, value, device in write_order:
        await tb.intf.write(addr, value, device=device)

    dut._log.info(f"Starting random reads ({len(read_order)} transactions)...")
    for addr, mask, value, device in read_order:
        # The read method verifies the expected data if provided
        await tb.intf.read(addr, value & mask, device=device)

    await tb.cr.end_test(20)
