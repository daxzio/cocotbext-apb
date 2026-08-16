"""

Copyright (c) 2024-2026 Daxzio

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

import re


class AddressMap(dict):
    """Name-to-address resolution for memory-mapped register maps.

    Maps register names to byte addresses per device. Supports indexed
    register access (``NAME[idx]``) and reverse lookup for logging.

    This class is protocol-agnostic: it has no bus-specific dependencies and
    can be used standalone or embedded in any memory-mapped bus master.

    Data model
    ----------
    The object is keyed by device index (``int``). Each value is a ``dict``
    mapping register name (``str``) to byte address (``int``).

    Parameters
    ----------
    word_bytes:
        Bus data width in bytes. Used for ``NAME[N]`` index offsets and for
        reverse lookup alignment. Default ``4``.
    multi_device:
        When ``True``, reserve extra column width in ``format_col()`` output
        for multi-slave log prefixes. Default ``False``.

    Methods
    -------
    add(addrmap, device=0):
        Register a name→address dict for *device* and update label width.
    resolve(addr, device=0, index=-1):
        Forward lookup: register name or int → byte address.
    format(addr, device=0):
        Reverse lookup: byte address → register name (or ``0x........``).
    format_col(label, prefix=""):
        Pad *label* for aligned read/write log columns.

    Examples
    --------
    >>> am = AddressMap(word_bytes=4)
    >>> am.add({"STATUS": 0x00, "CONFIG": 0x08})
    >>> am.resolve("STATUS")
    0
    >>> am.resolve("STATUS[2]")
    8
    >>> am.format(0x08)
    'CONFIG'
    """

    def __init__(self, word_bytes=4, multi_device=False):
        super().__init__()
        self.word_bytes = word_bytes
        self.multi_device = multi_device
        self._label_width = 10

    def add(self, addrmap, device=0):
        self[device] = addrmap
        self._update_label_width()

    def resolve(self, addr, device=0, index=-1):
        """Resolve a register name or integer address to a byte address."""
        resolved = addr
        if len(self) != 0 and isinstance(addr, str):
            h = re.findall(r"\[(\d+)\]", addr)
            addr = re.sub(r"\[.+", "", addr)
            resolved = self[device][addr]
            for g in h:
                resolved += int(g) * self.word_bytes
        if index != -1:
            resolved += index * self.word_bytes
        return resolved

    def format(self, addr, device=0):
        """Resolve a byte address to a register name when addrmap is configured."""
        if device not in self or not self[device]:
            return f"0x{addr:08x}"

        best_name = None
        best_base = -1
        for name, base in self[device].items():
            if addr < base or (addr - base) % self.word_bytes:
                continue
            if base > best_base:
                idx = (addr - base) // self.word_bytes
                best_name = name if idx == 0 else f"{name}[{idx}]"
                best_base = base

        return best_name if best_name is not None else f"0x{addr:08x}"

    def format_col(self, label, apb=""):
        """Pad address/register label so read/write data columns align."""
        width = self._label_width + (4 if self.multi_device else 0)
        return f"{apb}{label}".ljust(width)

    def _update_label_width(self):
        width = 10
        for device_map in self.values():
            for name in device_map:
                width = max(width, len(name), len(name) + 4)
        self._label_width = width
