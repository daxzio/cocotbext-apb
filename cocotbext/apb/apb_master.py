from cocotb import start_soon
from cocotb.triggers import RisingEdge

from collections import deque
from cocotb.triggers import Event
from typing import Deque
from typing import Tuple
from typing import Any
from typing import Union

from .utils import resolve_x_int
from .constants import ApbProt
from .apb_base import ApbBase


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

        self._run_coroutine_obj: Any = None
        self._restart()

    async def write(
        self,
        addr: int,
        data: Union[int, bytes],
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
    ) -> None:
        self.write_nowait(addr, data, strb, prot)
        await self._idle.wait()

    def write_nowait(
        self,
        addr: int,
        data: Union[int, bytes],
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
        data: Union[int, bytes] = bytes(),
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
        data: Union[int, bytes] = bytes(),
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

    @property
    def count_tx(self) -> int:
        return len(self.queue_tx)

    @property
    def empty_tx(self) -> bool:
        return not self.queue_tx

    @property
    def count_rx(self) -> int:
        return len(self.queue_rx)

    @property
    def empty_rx(self) -> bool:
        return not self.queue_rx

    @property
    def idle(self) -> bool:
        return self.empty_tx and self.empty_rx

    def clear(self) -> None:
        """Clears the RX and TX queues"""
        self.queue_tx.clear()
        self.queue_rx.clear()

    async def wait(self) -> None:
        """Wait for idle"""
        await self._idle.wait()

    async def _run(self):
        await RisingEdge(self.clock)
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
            if self.pprot_present:
                self.bus.pprot.value = prot
            if self.penable_present:
                self.bus.penable.value = 0
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
                #                 ret = int(self.bus.prdata.value)
                ret = resolve_x_int(self.bus.prdata)
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
            if self.pprot_present:
                self.bus.pprot.value = 0
            self.bus.pwrite.value = 0
            self.bus.pwdata.value = 0
            if self.pstrb_present:
                self.bus.pstrb.value = 0

            self.sync.set()
