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

from .address_map import AddressMap
from .address_space import (
    AddressSpace,
    MemoryInterface,
    MemoryRegion,
    PeripheralRegion,
    Pool,
    Region,
    SparseMemoryRegion,
    Window,
    WindowPool,
)
from .apb_bus import Apb3Bus, Apb4Bus, Apb5Bus, ApbBus

# from .apb_interface import Apb4Interface
from .apb_master import ApbMaster
from .apb_monitor import ApbMonitor
from .apb_ram import ApbRam
from .apb_slave import ApbSlave
from .constants import APBInstructionErr, APBPrivilegedErr, ApbProt, APBSlvErr
from .version import __version__

__all__ = [
    "APBInstructionErr",
    "APBPrivilegedErr",
    "APBSlvErr",
    "AddressMap",
    "AddressSpace",
    "Apb3Bus",
    "Apb4Bus",
    # "Apb4Interface",
    "Apb5Bus",
    "ApbBus",
    "ApbMaster",
    "ApbMonitor",
    "ApbProt",
    "ApbRam",
    "ApbSlave",
    "MemoryInterface",
    "MemoryRegion",
    "PeripheralRegion",
    "Pool",
    "Region",
    "SparseMemoryRegion",
    "Window",
    "WindowPool",
    "__version__",
]
