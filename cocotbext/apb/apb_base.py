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

import logging
import datetime

from .version import __version__


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
        self.log.info(f"Copyright (c) 2024-{datetime.datetime.now().year} Daxzio")
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
