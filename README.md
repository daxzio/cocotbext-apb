# APB interface modules for Cocotb

[![Build Status](https://github.com/daxzio/cocotbext-apb/workflows/Regression%20Tests/badge.svg?branch=main)](https://github.com/daxzio/cocotbext-apb/actions/)
[![codecov](https://codecov.io/gh/daxzio/cocotbext-apb/branch/main/graph/badge.svg)](https://codecov.io/gh/daxzio/cocotbext-apb)
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

The `APBBus` is used to map to a JTAG interface on the `dut`.  Class methods `from_entity` and `from_prefix` are provided to facilitate signal default name matching. 

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

The `ApbMaster` class implement a APB driver and is capable of generating read and write operations against JTAG devices, either singularly or in a chain.  

To use these modules, import the one you need and connect it to the DUT:

    from cocotbext.apb import ApbMaster, ApbBus

    bus = ApbBus.from_prefix(dut, "s_apb")
    apb_driver = ApbMaster(bus, dut.clk)

The first argument to the constructor accepts an `ApbBus` object.  These objects are containers for the interface signals and include class methods to automate connections.

Once the module is instantiated, read and write operations can be initiated in a couple of different ways.


