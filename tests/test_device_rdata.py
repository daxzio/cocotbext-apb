"""Unit tests for multi-device prdata slicing (including non-32-bit widths)."""

from cocotbext.apb.apb_base import ApbBase


class _Bits:
    def __init__(self, width: int):
        self._width = width

    def __len__(self) -> int:
        return self._width


class _MultiDeviceBus:
    """Stub bus with concatenated prdata across N devices of equal data width."""

    def __init__(self, n_devices: int, data_width: int):
        self.psel = _Bits(n_devices)
        self.paddr = _Bits(16)
        self.pwdata = _Bits(data_width)
        self.prdata = _Bits(n_devices * data_width)
        self.pwrite = _Bits(1)
        self.pready = _Bits(n_devices)
        self._name = "stub"
        self._signals = ["psel", "paddr", "pwdata", "prdata", "pwrite", "pready"]
        self._optional_signals = ["penable", "pstrb", "pprot", "pslverr"]


class _StubClock:
    pass


def _base(n_devices: int, data_width: int) -> ApbBase:
    return ApbBase(_MultiDeviceBus(n_devices, data_width), _StubClock(), name="test")


def test_device_rdata_32bit_multi_device():
    base = _base(n_devices=2, data_width=32)
    assert base.rwidth == [32, 32]
    # device0=0xA5A5A5A5, device1=0x5A5A5A5A
    prdata = 0x5A5A5A5A_A5A5A5A5
    assert base.device_rdata(prdata, 0) == 0xA5A5A5A5
    assert base.device_rdata(prdata, 1) == 0x5A5A5A5A


def test_device_rdata_64bit_multi_device():
    """Regression: monitor previously hard-coded ``>> 32 * device``."""
    base = _base(n_devices=2, data_width=64)
    assert base.rwidth == [64, 64]
    # Distinct per-device patterns spanning the full 64-bit lane
    d0 = 0x0123456789ABCDEF
    d1 = 0xFEDCBA9876543210
    prdata = (d1 << 64) | d0
    assert base.device_rdata(prdata, 0) == d0
    assert base.device_rdata(prdata, 1) == d1
    # Old hard-coded 32-bit shift would return the wrong upper half of device 0
    wrong = (prdata >> 32 * 1) & ((1 << 64) - 1)
    assert wrong != d1
    assert wrong == ((d0 >> 32) | ((d1 & 0xFFFFFFFF) << 32))


def test_device_rdata_16bit_four_devices():
    base = _base(n_devices=4, data_width=16)
    assert base.rwidth == [16, 16, 16, 16]
    lanes = [0x1111, 0x2222, 0x3333, 0x4444]
    prdata = 0
    for i, lane in enumerate(lanes):
        prdata |= lane << (16 * i)
    for i, lane in enumerate(lanes):
        assert base.device_rdata(prdata, i) == lane
