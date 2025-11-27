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
from typing import Any, Deque, Tuple
from collections import deque

from cocotb import start_soon
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.utils import get_sim_time

from .constants import ApbProt
from .utils import resolve_x_int
from .apb_base import ApbBase


class ApbMonitor(ApbBase):
    def __init__(self, bus, clock, **kwargs) -> None:
        super().__init__(bus, clock, name="monitor", **kwargs)
        self.disable_logging()
        self.timeout_max = 1000
        self.timeout = 0

        for i, j in self.bus._signals.items():
            setattr(self, i, 0)

        self.queue_txn: Deque[Tuple[bool, int, bytes, int, ApbProt, int]] = deque()
        self.txn_id = 0

        self._run_coroutine_obj: Any = None
        self._resolve_coroutine_obj: Any = None
        self._check_sync_coroutines: Any = []
        # self.enable_check_sync()
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        if self._resolve_coroutine_obj is not None:
            self._resolve_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())
        self._resolve_coroutine_obj = start_soon(self._resolve_signals())

    def enable_check_sync(self) -> None:
        """Enable check for synchronous signal changes"""
        self.disable_check_sync()
        self._last_clk_time = get_sim_time()
        self._check_sync_coroutines.append(start_soon(self._check_sync_clock()))
        for name in self.bus._signals:
            if hasattr(self.bus, name):
                self._check_sync_coroutines.append(
                    start_soon(self._check_sync_signal(name, getattr(self.bus, name)))
                )

    def disable_check_sync(self) -> None:
        """Disable check for synchronous signal changes"""
        for coro in self._check_sync_coroutines:
            coro.kill()
        self._check_sync_coroutines.clear()

    async def _check_sync_clock(self) -> None:
        while True:
            await RisingEdge(self.clock)
            self._last_clk_time = get_sim_time()

    async def _check_sync_signal(self, name: str, signal: Any) -> None:
        while True:
            await signal.value_change
            if get_sim_time() != self._last_clk_time:
                await ReadOnly()
                if get_sim_time() != self._last_clk_time:
                    self.log.error(
                        f"Signal {name} changed at {get_sim_time()}, "
                        f"which is not aligned with the last clock edge at {self._last_clk_time}"
                    )

    async def _resolve_signals(self):
        while True:
            for i, j in self.bus._signals.items():
                setattr(self, i, resolve_x_int(getattr(self.bus, i)))
            await RisingEdge(self.clock)

    @property
    def empty_txn(self) -> bool:
        return not self.queue_txn

    async def _run(self):
        while True:
            await RisingEdge(self.clock)
            self.timeout = 0

            if not 0 == self.psel:
                device = int(math.log2(self.psel))
                if not self.psel == 2**device:
                    self.log.critical(f"incorrect formatted psel {self.psel}")

                if self.paddr < 0 or self.paddr >= 2**self.address_width:
                    raise ValueError("Address out of range")

                if self.penable_present and 1 == self.penable:
                    self.log.critical(
                        "penable is asserted in the same first cycle with psel"
                    )

                pwrite = self.pwrite
                paddr = self.paddr
                pstrb = self.strb_mask
                if self.pstrb_present:
                    pstrb = self.pstrb
                extra_text = ""
                if self.pprot_present:
                    pprot = self.pprot
                    extra_text += f" prot: {pprot}"
                else:
                    pprot = ApbProt.NONSECURE
                apb = ""
                if self.multi_device:
                    apb = f"({device}) "

                wdata = self.pwdata
                await RisingEdge(self.clock)
                if self.penable_present and 0 == self.penable:
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

                if pwrite:
                    data = wdata
                    self.log.debug(
                        f"Write {apb}0x{paddr:08x}: 0x{data:08x}{extra_text}"
                    )
                else:
                    data = (self.prdata >> 32 * device) & self.rdata_mask[device]
                    self.log.debug(
                        f"Read  {apb}0x{paddr:08x}: 0x{data:08x}{extra_text}"
                    )
                self.queue_txn.append((pwrite, paddr, data, pstrb, pprot, self.txn_id))
                self.txn_id += 1


#             await RisingEdge(self.clock)
