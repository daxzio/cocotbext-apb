"""
Apb4Interface against a DUT whose APB bus has no penable signal.

Companion to test_interface (which uses a fully-populated APB4 DUT).  This
suite pins the optional-signal behaviour: cocotbext-interface declares
optional signals with a ``= None`` class default, so an absent signal must
still report ``hasattr(bus, name) is False`` for the VIPs' guards to work.
"""

from cocotb import test

from interfaces.clkrst import ClkReset

from cocotbext.apb import (
    HAVE_COCOTBEXT_INTERFACE,
    Apb4Interface,
    ApbDevice,
    ApbHost,
    ApbMonitor,
    MemoryRegion,
)

# cocotbext-interface is an optional dependency: skip rather than fail when
# it is not installed.
SKIP = not HAVE_COCOTBEXT_INTERFACE


class testbench:
    def __init__(self, dut, reset_sense=1, period=10):
        self.cr = ClkReset(dut, period, reset_sense=reset_sense, resetname="rst")
        self.dut = dut

        self.sbus = Apb4Interface.from_prefix(dut, "s_apb")
        self.mbus = Apb4Interface.from_prefix(dut, "m_apb")
        self.m = ApbHost(self.sbus, dut.clk)

        self.apb_mon = ApbMonitor(self.sbus, dut.clk)
        self.apb_mon.enable_logging()


@test(skip=SKIP)
async def test_absent_optional_signals(dut):
    """The DUT has no penable: it must look genuinely missing on the bus."""
    bus = Apb4Interface.from_prefix(dut, "s_apb")

    assert not hasattr(bus, "penable"), "absent penable must not be visible"
    assert getattr(bus, "penable", None) is None

    # Present optional and required signals stay reachable.
    for name in ("pstrb", "pprot", "pslverr"):
        assert hasattr(bus, name), f"{name} is present on this DUT"
    for name in ("psel", "pwrite", "paddr", "pwdata", "pready", "prdata"):
        assert hasattr(bus, name), f"required signal {name} missing"

    # The bus-compat view must exclude the absent signal but still advertise
    # it as optional, mirroring Apb4Bus.
    assert "penable" not in bus._signals
    assert "penable" in bus._optional_signals
    assert bus._name == "s_apb"


@test(skip=SKIP)
async def test_traffic_without_penable(dut):
    """ApbHost/ApbMonitor drive a penable-less bus built from Apb4Interface."""
    tb = testbench(dut, reset_sense=1)
    tb.s = ApbDevice(tb.mbus, dut.clk)
    tb.s.target = MemoryRegion(2**tb.s.address_width)

    assert not tb.m.penable_present, "ApbHost must detect penable as absent"
    assert not tb.apb_mon.penable_present, "ApbMonitor must detect penable absent"

    await tb.cr.wait_clkn(20)

    await tb.m.write(0x0010, 0x87654321)
    await tb.m.read(0x0010, 0x87654321)

    await tb.m.write(0x0020, 0xDEADBEEF)
    await tb.m.read(0x0020, 0xDEADBEEF)

    # Byte strobes still work through the interface-backed bus.
    await tb.m.write(0x0030, 0x00000000)
    await tb.m.write(0x0030, 0x11223344, 0x2)
    await tb.m.read(0x0030, 0x00003300)

    await tb.cr.end_test(20)
