# APB interface modules for Cocotb

[![Build Status](https://github.com/daxzio/cocotbext-apb/actions/workflows/test_checkin.yml/badge.svg?branch=main)](https://github.com/daxzio/cocotbext-apb/actions/)
[![PyPI version](https://badge.fury.io/py/cocotbext-apb.svg)](https://pypi.org/project/cocotbext-apb)
[![Downloads](https://pepy.tech/badge/cocotbext-apb)](https://pepy.tech/project/cocotbext-apb)

GitHub repository: https://github.com/daxzio/cocotbext-apb

## Introduction

APB simulation models for [cocotb](https://github.com/cocotb/cocotb).

## Installation

Installation from pip (release version, stable):

    $ pip install cocotbext-apb

Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/daxzio/cocotbext-apb/archive/main.zip

Installation for active development:

    $ git clone https://github.com/daxzio/cocotbext-apb
    $ pip install -e cocotbext-apb

## Documentation and usage examples

See the `tests` directory for complete testbenches using these modules.

### APB Bus

The `APBBus` is used to map to a APB interface on the `dut`.  Class methods `from_entity` and `from_prefix` are provided to facilitate signal default name matching. 

#### Required:
* _psel_
* _pwrite_
* _paddr_
* _pwdata_
* _pready_
* _prdata_

#### Optional:
* _pstrb_
* _pprot_
* _pslverr_

### APB Master

The `ApbMaster` class implement a APB driver and is capable of generating read and write operations against APB slaves.  

To use these modules, import the one you need and connect it to the DUT:

    from cocotbext.apb import ApbMaster, ApbBus

    bus = ApbBus.from_prefix(dut, "s_apb")
    apb_driver = ApbMaster(bus, dut.clk)

The first argument to the constructor accepts an `ApbBus` object.  These objects are containers for the interface signals and include class methods to automate connections.

Once the module is instantiated, read and write operations can be initiated in a couple of different ways.

#### `ApbMaster`constructor parameters
* _bus_: `ApbBus` object containing APB interface signals
* _clock_: clock signal
* _reset_: reset signal (optional)
* _reset_active_level_: reset active level (optional, default `True`)


#### Additional optional arguments for `ApbMaster`
* _seednum_: For random testing a seed can be supplied, default `None`, random seed.


#### Methods
* `enable_logging()`: Enable debug logging
* `disable_logging()`: Disable debug logging
* `enable_backpressure(seednum=None)`: Enable random delays on the interface
* `disable_backpressure()`: Disable random delays on the interface
* `wait()`: blocking wait until all outstanding operations complete
* `write(addr, data, strb=-1, prot=ApbProt.NONSECURE)`: write _data_ (bytes), to _addr_, wait for result
* `write_nowait(addr, data, strb=-1, prot=ApbProt.NONSECURE)`:write _data_ (bytes), to _addr_, submit to queue
* `read(addr, data=-1, prot=ApbProt.NONSECURE)`: read bytes, at _addr_, id _data_supplied check for match, wait for result
* `read_nowait(addr, data, prot=ApbProt.NONSECURE)`: read bytes, at _addr_, id _data_supplied check for match, submit to queue
 
### APB slave

The `ApbSlave` classe implement an APB slaves and is capable of completing read and write operations from upstream APB masters.  This modules can either be used to perform memory reads and writes on a `MemoryInterface` on behalf of the DUT, or they can be extended to implement customized functionality.

To use these modules, import the one you need and connect it to the DUT:

    from cocotbext.apb import ApbBus, ApbSlave, MemoryRegion

    apb_slave = ApbSlave(ApbBus.from_prefix(dut, "m_apb"), dut.clk, dut.rst)
    region = MemoryRegion(2**apb_slave.read_if.address_width)
    apb_slave.target = region

The first argument to the constructor accepts an `ApbBus` object.  These objects are containers for the interface signals and include class methods to automate connections.

It is also possible to extend these modules; operation can be customized by overriding the internal `_read()` and `_write()` methods.  See `ApbRam` for an example.

#### `ApbSlave` constructor parameters

* _bus_: `ApbBus` object containing APB interface signals
* _clock_: clock signal
* _reset_: reset signal (optional)
* _reset_active_level_: reset active level (optional, default `True`)
* _target_: target region (optional, default `None`)

### APB RAM

The `ApbRam` class implements APB RAMs and is capable of completing read and write operations from upstream APB masters.  These modules are extensions of the corresponding `ApbSlave` module.  Internally, `SparseMemory` is used to support emulating very large memories.

To use these modules, import and connect it to the DUT:

    from cocotbext.apb import ApbBus, ApbRam

    apb_ram = ApbRam(ApbBus.from_prefix(dut, "m_apb"), dut.clk, dut.rst, size=2**32)

The first argument to the constructor accepts an `ApbBus` object.  These objects are containers for the interface signals and include class methods to automate connections.

Once the module is instantiated, the memory contents can be accessed in a couple of different ways.  First, the `mmap` object can be accessed directly via the `mem` attribute.  Second, `read()`, `write()`, and various word-access wrappers are available.  Hex dump helper methods are also provided for debugging.  For example:

    apb_ram.write(0x0000, b'test')
    data = apb_ram.read(0x0000, 4)
    apb_ram.hexdump(0x0000, 4, prefix="RAM")

Multi-port memories can be constructed by passing the `mem` object of the first instance to the other instances.  For example, here is how to create a four-port RAM:

    apb_ram_p1 = ApbRam(ApbBus.from_prefix(dut, "m00_apb"), dut.clk, dut.rst, size=2**32)
    apb_ram_p2 = ApbRam(ApbBus.from_prefix(dut, "m01_apb"), dut.clk, dut.rst, mem=apb_ram_p1.mem)
    apb_ram_p3 = ApbRam(ApbBus.from_prefix(dut, "m02_apb"), dut.clk, dut.rst, mem=apb_ram_p1.mem)
    apb_ram_p4 = ApbRam(ApbBus.from_prefix(dut, "m03_apb"), dut.clk, dut.rst, mem=apb_ram_p1.mem)

#### `ApbRam` and `ApbLiteRam` constructor parameters

* _bus_: `ApbBus` object containing APB interface signals
* _clock_: clock signal
* _reset_: reset signal (optional)
* _reset_active_level_: reset active level (optional, default `True`)
* _size_: memory size in bytes (optional, default `2**32`)
* _mem_: `mmap` or `SparseMemory` backing object to use (optional, overrides _size_)

#### Attributes:

* _mem_: directly access shared `mmap` or `SparseMemory` backing object

#### Methods

* `read(address, length)`: read _length_ bytes, starting at _address_
* `read_words(address, count, byteorder='little', ws=2)`: read _count_ _ws_-byte words, starting at _address_
* `read_dwords(address, count, byteorder='little')`: read _count_ 4-byte dwords, starting at _address_
* `read_qwords(address, count, byteorder='little')`: read _count_ 8-byte qwords, starting at _address_
* `read_byte(address)`: read single byte at _address_
* `read_word(address, byteorder='little', ws=2)`: read single _ws_-byte word at _address_
* `read_dword(address, byteorder='little')`: read single 4-byte dword at _address_
* `read_qword(address, byteorder='little')`: read single 8-byte qword at _address_
* `write(address, data)`: write _data_ (bytes), starting at _address_
* `write_words(address, data, byteorder='little', ws=2)`: write _data_ (_ws_-byte words), starting at _address_
* `write_dwords(address, data, byteorder='little')`: write _data_ (4-byte dwords), starting at _address_
* `write_qwords(address, data, byteorder='little')`: write _data_ (8-byte qwords), starting at _address_
* `write_byte(address, data)`: write single byte at _address_
* `write_word(address, data, byteorder='little', ws=2)`: write single _ws_-byte word at _address_
* `write_dword(address, data, byteorder='little')`: write single 4-byte dword at _address_
* `write_qword(address, data, byteorder='little')`: write single 8-byte qword at _address_
* `hexdump(address, length, prefix='')`: print hex dump of _length_ bytes starting from _address_, prefix lines with optional _prefix_
* `hexdump_line(address, length, prefix='')`: return hex dump (list of str) of _length_ bytes starting from _address_, prefix lines with optional _prefix_
* `hexdump_str(address, length, prefix='')`: return hex dump (str) of _length_ bytes starting from _address_, prefix lines with optional _prefix_
