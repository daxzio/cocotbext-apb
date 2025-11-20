"""

Copyright (c) 2024-2025 Daxzio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import math
import logging

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from collections import deque
from cocotb.triggers import Event
from typing import Deque
from typing import Tuple
from typing import Any
from typing import Union

from .apb_base import ApbBase
from .constants import ApbProt
from .utils import resolve_x_int


class ApbMaster(ApbBase):
    def __init__(self, bus, clock, timeout_max=1000, **kwargs) -> None:
        super().__init__(bus, clock, name="master", **kwargs)

        self.timeout_max = timeout_max
        self.exception_enabled = True
        self.exception_occurred = False

        self.queue_tx: Deque[
            Tuple[bool, int, bytes, int, ApbProt, bool, int, int]
        ] = deque()
        self.queue_rx: Deque[Tuple[bytes, int]] = deque()
        self.tx_id = 0
        self.return_int = False
        self.ret: Union[bytes, None] = None

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
        self.multi_device = False
        if not 0 == len(self.bus.psel):
            self.multi_device = True

        #         self._init_reset(reset, reset_active_level)

        self._run_coroutine_obj: Any = None
        self._restart()

    def calc_length(self, length, data):
        if -1 == length:
            length = self.wbytes
        if not 0 == length % self.wbytes:
            raise Exception(
                f"Length needs to be a multiple of the byte width: {length}%{self.wbytes}"
            )
        if isinstance(data, int):
            min_length = math.ceil(data.bit_length() / self.wwidth)
        else:
            min_length = math.ceil(len(data) / self.wwidth)
        length = max(int(length / self.wbytes), min_length)
        return length

    async def write(
        self,
        addr: int,
        data: Union[int, bytes],
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        device: int = 0,
        length: int = -1,
    ) -> None:
        self.write_nowait(addr, data, strb, prot, error_expected, device, length)
        await self._idle.wait()

    def write_nowait(
        self,
        addr: int,
        data: Union[int, bytes],
        strb: int = -1,
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        device: int = 0,
        length: int = -1,
    ) -> None:
        """ """
        self.loop = self.calc_length(length, data)

        self._idle.clear()
        for i in range(self.loop):
            addrb = addr + i * self.wbytes
            if isinstance(data, int):
                subdata = (data >> self.wwidth * i) & self.wdata_mask
                datab = subdata.to_bytes(self.wbytes, "little")
            else:
                datab = data[i * self.wbytes : (i + 1) * self.wbytes]
            self.tx_id += 1
            self.queue_tx.append(
                (True, addrb, datab, strb, prot, error_expected, device, self.tx_id)
            )
        self.sync.set()

    async def poll(
        self,
        addr: int,
        data: Union[int, bytes] = bytes(),
        device: int = 0,
    ) -> None:
        self.log.info(f"Poll addr:  0x{addr:08x}")
        level_num = self.log.getEffectiveLevel()
        self.log.setLevel(logging.WARNING)
        if isinstance(data, int):
            datab = data.to_bytes(self.rbytes, "little")
        else:
            datab = data
        self.ret = None
        while not self.ret == datab:
            await self.read(addr, device=device)
        self.log.setLevel(level_num)

    async def read(
        self,
        addr: int,
        data: Union[int, bytes] = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        device: int = 0,
        length: int = -1,
    ) -> Union[bytes, int]:
        rx_id = self.read_nowait(addr, data, prot, error_expected, device)
        found = False
        while not found:
            while self.queue_rx:
                ret, tx_id = self.queue_rx.popleft()
                if rx_id == tx_id:
                    found = True
                    break
            await RisingEdge(self.clock)
        await self._idle.wait()
        self.ret = ret
        if self.return_int:
            return int.from_bytes(ret, byteorder="little")
        else:
            return ret

    def read_nowait(
        self,
        addr: int,
        data: Union[int, bytes] = bytes(),
        prot: ApbProt = ApbProt.NONSECURE,
        error_expected: bool = False,
        device: int = 0,
        length: int = -1,
    ) -> int:
        self.loop = self.calc_length(length, data)
        self.sync.set()
        for i in range(self.loop):
            addrb = addr + i * self.rbytes
            if isinstance(data, int):
                subdata = (data >> self.rwidth * i) & self.rdata_mask
                datab = subdata.to_bytes(self.rbytes, "little")
            else:
                datab = data
            self.tx_id += 1
            self.queue_tx.append(
                (False, addrb, datab, -1, prot, error_expected, device, self.tx_id)
            )
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
        while True:
            await RisingEdge(self.clock)
            while not self.queue_tx:
                self._idle.set()
                self.sync.clear()
                await self.sync.wait()

            (
                write,
                addr,
                data,
                strb,
                prot,
                error_expected,
                device,
                tx_id,
            ) = self.queue_tx.popleft()

            if addr < 0 or addr >= 2**self.address_width:
                raise ValueError("Address out of range")

            if device > len(self.bus.psel) - 1:
                raise ValueError(
                    f"Trying to access a device, {device}, that is not available on the bus {len(self.bus.psel)-1}"
                )

            self.bus.psel.value = 1 << device
            self.bus.paddr.value = addr
            extra_text = ""
            if self.pprot_present:
                self.bus.pprot.value = prot
                extra_text += f" prot: {prot}"
            if self.multi_device:
                extra_text += f" device: {device}"
            if self.penable_present:
                self.bus.penable.value = 0
            if write:
                data = int.from_bytes(data, byteorder="little")
                self.log.info(
                    f"Write addr: 0x{addr:08x} data: 0x{data:08x}{extra_text}"
                )
                self.bus.pwdata.value = data & self.wdata_mask
                self.bus.pwrite.value = 1
                if self.pstrb_present:
                    if -1 == strb:
                        self.bus.pstrb.value = self.strb_mask
                    else:
                        self.bus.pstrb.value = strb
            #             else:
            #                 self.log.info(f"Read addr:  0x{addr:08x}{extra_text}")
            await RisingEdge(self.clock)
            if self.penable_present:
                self.bus.penable.value = 1
                await RisingEdge(self.clock)

            timeout = 0
            while not self.bus.pready.value:
                await RisingEdge(self.clock)
                if self.timeout_max != -1:
                    timeout += 1
                    if timeout >= self.timeout_max:
                        self.log.info(f"Read addr:  0x{addr:08x}{extra_text}")
                        raise TimeoutError(
                            f"APB transaction timeout: pready not asserted within {self.timeout_max} clock cycles (addr: 0x{addr:08x})"
                        )

            if self.pslverr_present:
                if not bool(self.bus.pslverr.value) == error_expected:
                    if bool(self.bus.pslverr.value):
                        msg = "PSLVERR detected not expected!"
                    else:
                        msg = "PSLVERR expected not detected!"
                    if self.pprot_present:
                        msg += f" PPROT - {ApbProt(self.bus.pprot.value).name}"
                    self.exception_occurred = True
                    if self.exception_enabled:
                        self.log.critical(msg)
                        raise Exception(msg)
                    else:
                        self.log.warning(msg)

            extra_text = ""
            if self.multi_device:
                extra_text += f" device: {device}"
            if not write:
                ret = resolve_x_int(self.bus.prdata)
                # Need something that can handle dynamic read widths per device,
                # Using the write width as a proxy for now, FIXME
                ret_slice = (ret >> (device * self.wwidth)) & self.wdata_mask
                self.log.info(
                    f"Read  addr: 0x{addr:08x} data: 0x{ret_slice:08x}{extra_text}"
                )
                if not data == bytes():
                    data_int = int.from_bytes(data, byteorder="little")
                    if not data_int == ret_slice:
                        self.bus.psel.value = 0
                        await RisingEdge(self.clock)
                        await RisingEdge(self.clock)
                        await RisingEdge(self.clock)
                        raise Exception(
                            f"Expected 0x{data_int:08x} doesn't match returned 0x{ret_slice:08x}"
                        )
                self.queue_rx.append((ret.to_bytes(self.rbytes, "little"), tx_id))

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
