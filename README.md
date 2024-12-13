# JTAG interface modules for Cocotb

[![Build Status](https://github.com/daxzio/cocotbext-apb/workflows/Regression%20Tests/badge.svg?branch=main)](https://github.com/daxzio/cocotbext-apb/actions/)
[![codecov](https://codecov.io/gh/daxzio/cocotbext-apb/branch/main/graph/badge.svg)](https://codecov.io/gh/daxzio/cocotbext-apb)
[![PyPI version](https://badge.fury.io/py/cocotbext-apb.svg)](https://pypi.org/project/cocotbext-apb)
[![Downloads](https://pepy.tech/badge/cocotbext-apb)](https://pepy.tech/project/cocotbext-apb)

GitHub repository: https://github.com/daxzio/cocotbext-apb

## Introduction

APB simulation models for [cocotb](https://github.com/cocotb/cocotb).

## Installation

Installation from git (latest development version, potentially unstable):

    $ pip install https://github.com/daxzio/cocotbext-apb/archive/main.zip

Installation for active development:

    $ git clone https://github.com/daxzio/cocotbext-apb
    $ pip install -e cocotbext-apb

## Documentation and usage examples

See the `tests` directory for complete testbenches using these modules.

### APB Bus

The `APBBus` is used to map to a JTAG interface on the `dut`.  These hold instances of bus objects for the individual channels, which are currently extensions of `cocotb_bus.bus.Bus`.  Class methods `from_entity` and `from_prefix` are provided to facilitate signal default name matching. 

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






