# APB interface modules for Cocotb

[![Build Status](https://github.com/daxzio/cocotbext-apb/actions/workflows/test_checkin.yml/badge.svg?branch=main)](https://github.com/daxzio/cocotbext-apb/actions/)
[![PyPI version](https://badge.fury.io/py/cocotbext-apb.svg)](https://pypi.org/project/cocotbext-apb)
[![Downloads](https://pepy.tech/badge/cocotbext-apb)](https://pepy.tech/project/cocotbext-apb)

GitHub repository: https://github.com/daxzio/cocotbext-apb

## Introduction

APB simulation models for [cocotb](https://github.com/cocotb/cocotb).

The APB protocol is cover in these documents [APB Protocol Specification](https://github.com/daxzio/cocotbext-apb/blob/main/assets/IHI0024D_amba_apb_protocol_spec.pdf) and [APB Architecture Specification](https://github.com/daxzio/cocotbext-apb/blob/main/assets/IHI0024E_amba_apb_architecture_spec.pdf)

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

### APB Write

![APB Write](https://github.com/daxzio/cocotbext-apb/raw/main/assets/apb_write.png)

### APB Read

![APB Read](https://github.com/daxzio/cocotbext-apb/raw/main/assets/apb_read.png)

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

The master automatically handles data wider than the bus width by splitting transactions into multiple sequential APB accesses at consecutive addresses. This allows seamless transfers of wide data values across narrower APB interfaces.

To use these modules, import the one you need and connect it to the DUT:

    from cocotbext.apb import ApbMaster, ApbBus

    bus = ApbBus.from_prefix(dut, "s_apb")
    apb_driver = ApbMaster(bus, dut.clk)

The first argument to the constructor accepts an `ApbBus` object.  These objects are containers for the interface signals and include class methods to automate connections.

Once the module is instantiated, read and write operations can be initiated in a couple of different ways.

#### `ApbMaster`constructor parameters
* _bus_: `ApbBus` object containing APB interface signals
* _clock_: clock signal
* _timeout_max_: Maximum clock cycles to wait for `pready` signal before timing out (optional, default `1000`). Set to `-1` to disable timeout.
* _reset_: reset signal (optional)
* _reset_active_level_: reset active level (optional, default `True`)


#### Additional optional arguments for `ApbMaster`
* _seednum_: For random testing a seed can be supplied, default `None`, random seed.

#### Address Mapping

The `ApbMaster` supports address mapping through the `addrmap` attribute, which allows using string names instead of numeric addresses in read and write operations. This makes testbenches more readable and maintainable by using register names instead of hardcoded addresses.

The `addrmap` attribute is a dictionary that maps register names (strings) to their corresponding addresses (integers). When a string is passed as the `addr` parameter to `read()`, `write()`, `read_nowait()`, `write_nowait()`, or `poll()` methods, the master will automatically look up the address in the `addrmap` dictionary.

**Indexed Register Access:**

For registers that are arrays or need indexed access, you can use either:
1. String format with bracket notation: `"STATUS[0]"`, `"STATUS[1]"`, etc.
2. The `index` parameter: `read("STATUS", data, index=0)`, `write("STATUS", data, index=1)`, etc.

Both methods add an offset to the base register address equal to `index * wbytes` (where `wbytes` is the bus width in bytes). The `index` parameter is particularly useful when using a variable index in loops.

Example:

```python
from cocotbext.apb import ApbMaster, ApbBus

bus = ApbBus.from_prefix(dut, "s_apb")
apb_driver = ApbMaster(bus, dut.clk)

apb_driver.addrmap = {
    'STATUS'    : 0x00,
    'BUSY'      : 0x04,
    'CONFIG'    : 0x08,
    'INTERRUPT' : 0x0c,
}

# Use string names instead of numeric addresses
await apb_driver.write('STATUS', 0x12)
await apb_driver.read('CONFIG')

# Indexed access using string format
await apb_driver.read('STATUS[0]', 0x12)
await apb_driver.read('STATUS[1]', 0x34)

# Indexed access using index parameter (useful with variables)
for i in range(4):
    await apb_driver.write('STATUS', data[i], index=i)
    await apb_driver.read('STATUS', expected[i], index=i)
```

#### Methods
* `enable_logging()`: Enable debug logging
* `disable_logging()`: Disable debug logging
* `enable_backpressure(seednum=None)`: Enable random delays on the interface
* `disable_backpressure()`: Disable random delays on the interface
* `wait()`: blocking wait until all outstanding operations complete
* `write(addr, data, strb=-1, prot=ApbProt.NONSECURE, error_expected=False, device=0, length=-1, index=-1)`: write _data_ (bytes or int), to _addr_ (int or string when `addrmap` is configured), wait for result.  If an slverr is experienced a critical warning will be issued by default, but will reduced this to an info warning if `error_expected=True`. If _data_ is wider than the bus width, it will automatically be split into multiple sequential APB write accesses at consecutive addresses. The optional _length_ parameter can override the automatic length calculation, should be a multiple of the number of bytes in the wdata bus. The optional _device_ parameter specifies the slave index to target. The optional _index_ parameter adds an offset to the address equal to `index * wbytes`, useful for accessing indexed registers (alternative to using string format like `"STATUS[0]"`).
* `write_nowait(addr, data, strb=-1, prot=ApbProt.NONSECURE, error_expected=False, device=0, length=-1, index=-1)`: write _data_ (bytes or int), to _addr_ (int or string when `addrmap` is configured), submit to queue. If an slverr is experienced a critical warning will be issued by default, but will reduced this to an info warning if `error_expected=True`. If _data_ is wider than the bus width, it will automatically be split into multiple sequential APB write accesses at consecutive addresses. The optional _length_ parameter can override the automatic length calculation, should be a multiple of the number of bytes in the wdata bus. The optional _device_ parameter specifies the slave index to target. The optional _index_ parameter adds an offset to the address equal to `index * wbytes`, useful for accessing indexed registers (alternative to using string format like `"STATUS[0]"`).
* `read(addr, data=bytes(), prot=ApbProt.NONSECURE, error_expected=False, device=0, index=-1, length=-1)`: read bytes, at _addr_ (int or string when `addrmap` is configured), if _data_ supplied check for match, wait for result. If an slverr is experienced a critical warning will be issued by default, but will reduced this to an info warning if `error_expected=True`. If _data_ is wider than the bus width, it will automatically be split into multiple sequential APB read accesses at consecutive addresses. The optional _length_ parameter can override the automatic length calculation, should be a multiple of the number of bytes in the wdata bus. The optional _device_ parameter specifies the slave index to target. The optional _index_ parameter adds an offset to the address equal to `index * wbytes`, useful for accessing indexed registers (alternative to using string format like `"STATUS[0]"`).
* `read_nowait(addr, data=bytes(), prot=ApbProt.NONSECURE, error_expected=False, device=0, index=-1, length=-1)`: read bytes, at _addr_ (int or string when `addrmap` is configured), if _data_ supplied check for match, submit to queue. If an slverr is experienced a critical warning will be issued by default, but will reduced this to an info warning if `error_expected=True`. If _data_ is wider than the bus width, it will automatically be split into multiple sequential APB read accesses at consecutive addresses. The optional _length_ parameter can override the automatic length calculation, should be a multiple of the number of bytes in the wdata bus. The optional _device_ parameter specifies the slave index to target. The optional _index_ parameter adds an offset to the address equal to `index * wbytes`, useful for accessing indexed registers (alternative to using string format like `"STATUS[0]"`).
* `poll(addr, data=bytes(), device=0)`: poll address, at _addr_ (int or string when `addrmap` is configured), until data at address matches _data_. The optional _device_ parameter specifies the slave index to target.


Example:

```python
# Write to slave 0
await tb.intf.write(0x100, 0xDEADBEEF, device=0)

# Read from slave 1
val = await tb.intf.read(0x200, device=1)
```

### APB Monitor

The `ApbMonitor` class tracks APB bus transactions and verifies signal synchronization.

#### Usage

    from cocotbext.apb import ApbMonitor
    monitor = ApbMonitor(bus, dut.clk)

#### Methods

* `enable_check_sync()`: Enable checking that signal changes are aligned with the clock edge, default.
* `disable_check_sync()`: Disable the synchronous signal check.

### Multi-Device Support

The `ApbMaster` supports multiple slave devices on the same bus instance. To use this feature:

1.  **Signal Connection**:
    *   `psel` must be a vector (e.g., `[1:0]` for 2 slaves).
    *   `prdata` must be a concatenated vector of all slave read data outputs (e.g., `[63:0]` for 2 slaves with 32-bit data width).

2.  **Access**:
    *   Use the `device` parameter in `read`, `write`, `read_nowait`, and `write_nowait` methods to specify the target slave index (integer).
    *   The `ApbMaster` will assert the corresponding bit in `psel` (`1 << device`) and slice the `prdata` appropriately.

Example:

```python
# Write to slave 0
await tb.intf.write(0x100, 0xDEADBEEF, device=0)

# Read from slave 1
val = await tb.intf.read(0x200, device=1)
```

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

#### `ApbSlave` editable attibutes

It is possible to set area of addressable memory to be treated a priviledged address space or instruction address space.  If an APB master tries to access these regions, but has not set the correct `prot` value, `NONSECURE` for example, the `ApbSlave` will issue a `slverr` duting the `pready` phase of it response.

The `ApbSlave` has two attributes that can be edited by the user to allocate addresses and/or address ranges to the priviledged or instruction space.

* _privileged_addrs_
* _instruction_addrs_

Both attributes are arrays, and each element can be a single address, or a two element list, with a low address to a high address:

    tb.ram.privileged_addrs =  [[0x1000, 0x1fff], 0x3000]
    tb.ram.instruction_addrs = [[0x2000, 0x2fff], 0x4000]

If there is a read or a write with an address in this space, and the prot from the master does not match, it will report the type of error, as a warning, and assert `slverr`. The access will also be unsuccessful, the write will not occur and a read will result in all zeros being returned.

![APB Write Error](https://github.com/daxzio/cocotbext-apb/raw/main/assets/apb_write_error.png)

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
