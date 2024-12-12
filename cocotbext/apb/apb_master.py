import math
import logging

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from collections import deque
from cocotb.triggers import Event
from typing import Deque
from typing import Tuple

from .version import __version__
from .constants import ApbProt
from .utils import resolve_x_int

class ApbBase:
    def __init__(self, bus, clock, name="monitor", **kwargs) -> None:
        self.name = name
        self.bus = bus
        self.clock = clock
        if bus._name:
            self.log = logging.getLogger(f"cocotb.apb_{name}.{bus._name}")
        else:
            self.log = logging.getLogger(f"cocotb.apb_{name}")
        self.log.setLevel(logging.INFO)
        self.log.info(f"APB {self.name}")
        self.log.info(f"cocotbext-apb version {__version__}")
        self.log.info("Copyright (c) 2024 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-apb")

        self.address_width = len(self.bus.paddr)
        self.wwidth = len(self.bus.pwdata)
        self.rwidth = len(self.bus.prdata)
        self.rbytes = int(self.rwidth / 4)
        self.wbytes = int(self.wwidth / 4)
        self.byte_size = 8
        self.byte_lanes = self.wwidth // self.byte_size
        self.rdata_mask = 2**self.rwidth - 1
        self.wdata_mask = 2**self.wwidth - 1
        self.strb_mask = 2**self.byte_lanes - 1

        self.penable_present = hasattr(self.bus, "penable")
        self.pstrb_present = hasattr(self.bus, "pstrb")
        self.pprot_present = hasattr(self.bus, "pprot")
        self.pslverr_present = hasattr(self.bus, "pslverr")
        if self.pstrb_present:
            assert self.byte_lanes == len(self.bus.pstrb)
        assert self.byte_lanes * self.byte_size == self.wwidth

        self.log.info(f"APB {self.name} configuration:")
        self.log.info(f"  Address width: {self.address_width} bits")
        self.log.info(f"  Byte size: {self.byte_size} bits")
        self.log.info(f"  Data width: {self.wwidth} bits ({self.byte_lanes} bytes)")

        self.log.info("APB monitor signals:")
        for sig in sorted(
            list(set().union(self.bus._signals, self.bus._optional_signals))
        ):
            if hasattr(self.bus, sig):
                self.log.info(f"  {sig} width: {len(getattr(self.bus, sig))} bits")
            else:
                self.log.info(f"  {sig}: not present")

    def enable_logging(self):
        self.log.setLevel(logging.DEBUG)

    def disable_logging(self):
        self.log.setLevel(logging.INFO)


class ApbMonitor(ApbBase):
    def __init__(self, bus, clock, **kwargs) -> None:
        super().__init__(bus, clock, name="monitor", **kwargs)
        self.disable_logging()
        self.timeout_max = 1000
        self.timeout = 0

        for i, j in self.bus._signals.items():
            setattr(self, i, 0)

        self._run_coroutine_obj = None
        self._resolve_coroutine_obj = None
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        if self._resolve_coroutine_obj is not None:
            self._resolve_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())
        self._resolve_coroutine_obj = start_soon(self._resolve_signals())

    async def _resolve_signals(self):
        while True:
            for i, j in self.bus._signals.items():
                setattr(self, i, resolve_x_int(getattr(self.bus, i)))
            await RisingEdge(self.clock)

    async def _run(self):
        while True:
            self.timeout = 0

            if not 0 == self.psel:
                index = int(math.log2(self.psel))
                if not self.psel == 2**index:
                    self.log.critical(f"incorrect formatted psel {self.psel}")

                if self.paddr < 0 or self.paddr >= 2**self.address_width:
                    raise ValueError("Address out of range")

                if not self.pprot_present and self.pprot != ApbProt.NONSECURE:
                    raise ValueError(
                        "pprot sideband signal value specified, but signal is not connected"
                    )
                if 1 == self.penable:
                    self.log.critical(
                        "penable is asserted in the same first cycle with psel"
                    )

                pwrite = self.pwrite
                paddr = self.paddr
                pprot = self.pprot
                wdata = self.pwdata
                await RisingEdge(self.clock)
                if 0 == self.penable:
                    self.log.critical(
                        f"penable is not asserted in the second cycle after psel {self.penable}"
                    )
                while 0 == (self.pready and self.psel):
                    await RisingEdge(self.clock)
                    self.timeout += 1
                    if self.timeout >= self.timeout_max:
                        raise Exception(
                            f"pready wait has exceed timout {self.timeout_max}"
                        )
                apb = ""
                if not 0 == len(self.bus.psel) - 1:
                    apb = f"({index}) "
                if pwrite:
                    self.log.debug(
                        f"Write {apb}0x{paddr:08x}: 0x{wdata:08x} prot: {pprot}"
                    )
                else:
                    rdata = (self.prdata >> 32 * index) & self.wdata_mask
                    self.log.debug(
                        f"Read  {apb}0x{paddr:08x}: 0x{rdata:08x} prot: {pprot}"
                    )
            await RisingEdge(self.clock)


class ApbMaster(ApbBase):
    def __init__(self, bus, clock, **kwargs) -> None:
        super().__init__(bus, clock, name="master", **kwargs)

        self.queue_tx: Deque[Tuple[bool, int, bytes, int, ApbProt, int]] = deque()
        self.queue_rx: Deque[Tuple[bytes, int]] = deque()
        self.tx_id = 0

        self.sync = Event()

        self._idle = Event()
        self._idle.set()

        if self.penable_present:
            self.bus.penable.value = 0
        self.bus.psel.value = 0
        self.bus.paddr.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0
        if self.pprot_present:
            self.bus.pprot.value = 0
        self.bus.pwrite.value = 0
        self.bus.pwdata.value = 0

        #         self._init_reset(reset, reset_active_level)

        self._run_coroutine_obj = None
        self._restart()

    async def write(
        self,
        addr: int,
        data: int | bytes,
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
    ) -> None:
        self.write_nowait(addr, data, strb, prot)
        await self._idle.wait()

    def write_nowait(
        self,
        addr: int,
        data: int | bytes,
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
    ) -> None:
        """ """
        self.tx_id += 1
        if isinstance(data, int):
            datab = data.to_bytes(self.wbytes, "little")
        else:
            datab = data
        self.queue_tx.append((True, addr, datab, strb, prot, self.tx_id))
        self.sync.set()
        self._idle.clear()

    async def read(
        self,
        addr: int,
        data: int | bytes = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
    ) -> bytes:
        rx_id = self.read_nowait(addr, data, prot)
        found = False
        while not found:
            while self.queue_rx:
                ret, tx_id = self.queue_rx.popleft()
                if rx_id == tx_id:
                    found = True
                    break
            await RisingEdge(self.clock)
        await self._idle.wait()
        return ret

    def read_nowait(
        self,
        addr: int,
        data: int | bytes = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
    ) -> int:
        if isinstance(data, int):
            if data > self.rdata_mask:
                self.log.warning(
                    f"Read data 0x{data:08x} exceeds width expected 0x{self.rdata_mask:08x}"
                )
            datab = data.to_bytes(self.rbytes, "little")
        else:
            datab = data
        self.tx_id += 1
        self.queue_tx.append((False, addr, datab, -1, prot, self.tx_id))
        self.sync.set()
        self._idle.clear()
        return self.tx_id

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())

    def count_tx(self) -> int:
        return len(self.queue_tx)

    def empty_tx(self) -> bool:
        return not self.queue_tx

    def count_rx(self) -> int:
        return len(self.queue_rx)

    def empty_rx(self) -> bool:
        return not self.queue_rx

    def idle(self) -> bool:
        return self.empty_tx() and self.empty_rx()

    def clear(self) -> None:
        """Clears the RX and TX queues"""
        self.queue_tx.clear()
        self.queue_rx.clear()

    async def wait(self) -> None:
        """Wait for idle"""
        await self._idle.wait()

    async def _run(self):
        while True:
            while not self.queue_tx:
                self._idle.set()
                self.sync.clear()
                await self.sync.wait()

            write, addr, data, strb, prot, tx_id = self.queue_tx.popleft()

            if addr < 0 or addr >= 2**self.address_width:
                raise ValueError("Address out of range")

            if not self.pprot_present and prot != ApbProt.NONSECURE:
                raise ValueError(
                    "pprot sideband signal value specified, but signal is not connected"
                )

            self.bus.psel.value = 1
            self.bus.paddr.value = addr
            self.bus.pprot.value = prot
            #             if self.penable_present:
            #                 self.bus.penable.value = 1
            if write:
                data = int.from_bytes(data, byteorder="little")
                self.log.info(
                    f"Write addr: 0x{addr:08x} data: 0x{data:08x} prot: {prot}"
                )
                self.bus.pwdata.value = data & self.wdata_mask
                self.bus.pwrite.value = 1
                if self.pstrb_present:
                    if -1 == strb:
                        self.bus.pstrb.value = self.strb_mask
                    else:
                        self.bus.pstrb.value = strb
            else:
                self.log.info(f"Read addr: 0x{addr:08x} prot: {prot}")
            await RisingEdge(self.clock)
            if self.penable_present:
                self.bus.penable.value = 1
                await RisingEdge(self.clock)

            while not self.bus.pready.value:
                await RisingEdge(self.clock)
            if not write:
                ret = int(self.bus.prdata.value)
                self.log.info(f"Value read: 0x{ret:08x}")
                if not data == bytes():
                    data_int = int.from_bytes(data, byteorder="little")
                    if not data_int == ret:
                        raise Exception(
                            f"Expected 0x{data_int:08x} doesn't match returned 0x{ret:08x}"
                        )
                self.queue_rx.append(
                    (ret.to_bytes(len(self.bus.prdata), "little"), tx_id)
                )

            if self.penable_present:
                self.bus.penable.value = 0
            self.bus.psel.value = 0
            self.bus.paddr.value = 0
            self.bus.pprot.value = 0
            self.bus.pwrite.value = 0
            self.bus.pwdata.value = 0
            if self.pstrb_present:
                self.bus.pstrb.value = 0
            #             await RisingEdge(self.clock)

            self.sync.set()
