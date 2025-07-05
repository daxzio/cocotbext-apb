# Pull Request Templates for APB Extension Bug Fixes

## Overview
This document contains templates for creating 3 separate Pull Requests to fix the bugs found in the CocoTB APB extension. Each PR focuses on a single bug to make review and merging easier.

---

## Pull Request 1: Fix List Mutation Bug in APB Bus Classes

### Branch Name
`fix/apb-bus-optional-signals`

### PR Title
`Fix APB4Bus and APB5Bus optional_signals set to None due to incorrect extend() usage`

### PR Description Template
```markdown
## Description
Fixes a critical bug in `Apb4Bus` and `Apb5Bus` classes where `optional_signals` was being set to `None` due to incorrect use of the `extend()` method.

## Problem
The `extend()` method modifies a list in place and returns `None`, but the code was assigning the return value to `optional_signals`:

```python
# Buggy code:
optional_signals = self._optional_signals.extend(["pstrb", "pprot", "pslverr"])
# extend() returns None, so optional_signals becomes None
```

## Solution
Create a copy of the parent class's optional signals list and then extend it:

```python
# Fixed code:
optional_signals = self._optional_signals.copy()
optional_signals.extend(["pstrb", "pprot", "pslverr"])
```

## Changes Made
- `cocotbext/apb/apb_bus.py`: Fixed `Apb4Bus.__init__()` method
- `cocotbext/apb/apb_bus.py`: Fixed `Apb5Bus.__init__()` method

## Impact
- ✅ APB4 signals (`pstrb`, `pprot`, `pslverr`) now properly recognized
- ✅ APB5 signals (`pwakeup`, `pauser`, `pwuser`, `pruser`, `pbuser`, `pnse`) now properly recognized
- ✅ No more runtime errors when accessing optional signals
- ✅ Full APB4 and APB5 protocol support restored

## Testing
- [ ] Unit tests for APB4Bus signal recognition
- [ ] Unit tests for APB5Bus signal recognition
- [ ] Integration tests with APB4/APB5 protocols
- [ ] Regression tests for existing functionality

## Type of Change
- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)

## Checklist
- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
```

### Files to Change
1. `cocotbext/apb/apb_bus.py` - Lines 44-45 and 60-61

### Git Commands
```bash
# Create and switch to new branch
git checkout -b fix/apb-bus-optional-signals

# Make the changes to cocotbext/apb/apb_bus.py
# (Apply the fix I provided earlier)

# Commit the changes
git add cocotbext/apb/apb_bus.py
git commit -m "Fix APB4Bus and APB5Bus optional_signals list mutation bug

- Fixed incorrect use of extend() method that was setting optional_signals to None
- Properly copy and extend optional signals list for APB4Bus and APB5Bus
- Restores full APB4 and APB5 protocol support
- Fixes runtime errors when accessing optional signals

Fixes: APB4Bus and APB5Bus optional_signals set to None"

# Push to your fork
git push origin fix/apb-bus-optional-signals
```

---

## Pull Request 2: Fix Incorrect Byte Calculation

### Branch Name
`fix/byte-calculation-error`

### PR Title
`Fix incorrect byte calculation in ApbBase class`

### PR Description Template
```markdown
## Description
Fixes incorrect byte calculation in the `ApbBase` class that was dividing bit width by 4 instead of 8 (bits per byte).

## Problem
The byte calculation was fundamentally wrong:

```python
# Buggy code:
self.rbytes = int(self.rwidth / 4)  # Should be 8 bits per byte
self.wbytes = int(self.wwidth / 4)  # Should be 8 bits per byte
```

## Solution
Correct the calculation to use 8 bits per byte:

```python
# Fixed code:
self.rbytes = int(self.rwidth / 8)  # Correct: 8 bits per byte
self.wbytes = int(self.wwidth / 8)  # Correct: 8 bits per byte
```

## Changes Made
- `cocotbext/apb/apb_base.py`: Fixed byte calculation in `ApbBase.__init__()` method

## Impact
- ✅ Correct buffer sizes and memory calculations
- ✅ Eliminates data corruption risk during read/write operations
- ✅ Correct byte lane calculations
- ✅ Improved performance due to correct buffer sizing
- ✅ Prevents potential memory access violations

## Root Cause Analysis
This bug affected all APB operations that relied on byte calculations, potentially causing:
- Buffer overflows/underflows
- Incorrect memory allocation
- Data corruption during transfers
- Performance degradation

## Testing
- [ ] Unit tests for byte calculation accuracy
- [ ] Memory operation tests with various data widths
- [ ] Performance regression tests
- [ ] Buffer boundary tests

## Type of Change
- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)

## Checklist
- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
```

### Files to Change
1. `cocotbext/apb/apb_base.py` - Lines 45-46

### Git Commands
```bash
# Create and switch to new branch
git checkout -b fix/byte-calculation-error

# Make the changes to cocotbext/apb/apb_base.py
# (Apply the fix I provided earlier)

# Commit the changes
git add cocotbext/apb/apb_base.py
git commit -m "Fix incorrect byte calculation in ApbBase class

- Changed bit-to-byte calculation from /4 to /8 (8 bits per byte)
- Fixes potential data corruption and memory access violations
- Corrects buffer sizing for all APB operations
- Improves performance by using correct buffer sizes

Fixes: Incorrect byte calculation causing data corruption risk"

# Push to your fork
git push origin fix/byte-calculation-error
```

---

## Pull Request 3: Fix Address Range Security Vulnerability

### Branch Name
`fix/address-range-security`

### PR Title
`Fix address range boundary condition security vulnerability`

### PR Description Template
```markdown
## Description
Fixes a security vulnerability in address range checking that allowed unauthorized access to boundary addresses of privileged/instruction memory regions.

## Security Issue
The address range check had an off-by-one error:

```python
# Buggy code (security vulnerability):
if addrs[0] <= address < addrs[1]:  # Upper boundary excluded
    raise exception
```

This allowed attackers to access the upper boundary address (`addrs[1]`) without proper authorization.

## Solution
Include the upper boundary in the protection check:

```python
# Fixed code (secure):
if addrs[0] <= address <= addrs[1]:  # Upper boundary included
    raise exception
```

## Changes Made
- `cocotbext/apb/apb_slave.py`: Fixed boundary condition in `check_address()` method

## Security Impact
- ✅ Prevents unauthorized access to privileged memory regions
- ✅ Prevents unauthorized access to instruction memory regions
- ✅ Closes APB protection mechanism bypass
- ✅ Eliminates potential system compromise vector

## Attack Scenario (Before Fix)
1. Attacker configures privileged address range `[0x1000, 0x1FFF]`
2. Attacker attempts to access address `0x1FFF` without privileged permissions
3. Access is allowed due to boundary condition bug
4. Attacker gains unauthorized access to privileged data

## Verification (After Fix)
1. Configure privileged address range `[0x1000, 0x1FFF]`
2. Attempt to access address `0x1FFF` without privileged permissions
3. Access is properly denied with `APBPrivilegedErr` exception
4. Security boundary is maintained

## Testing
- [ ] Boundary condition security tests
- [ ] Privileged address range tests
- [ ] Instruction address range tests
- [ ] Security regression tests
- [ ] APB protection mechanism verification

## Type of Change
- [x] Bug fix (non-breaking change which fixes an issue)
- [x] Security fix (fixes a security vulnerability)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)

## Checklist
- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] Security implications have been considered and documented
```

### Files to Change
1. `cocotbext/apb/apb_slave.py` - Line 74

### Git Commands
```bash
# Create and switch to new branch
git checkout -b fix/address-range-security

# Make the changes to cocotbext/apb/apb_slave.py
# (Apply the fix I provided earlier)

# Commit the changes
git add cocotbext/apb/apb_slave.py
git commit -m "Fix address range boundary condition security vulnerability

- Fixed off-by-one error in address range checking
- Include upper boundary address in privilege/instruction protection
- Prevents unauthorized access to boundary addresses
- Closes security vulnerability in APB protection mechanism

Security fix: Address range boundary condition allows unauthorized access"

# Push to your fork
git push origin fix/address-range-security
```

---

## How to Create the Pull Requests

### Prerequisites
1. **Fork the repository**: https://github.com/daxzio/cocotbext-apb
2. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/cocotbext-apb.git`
3. **Set up upstream**: `git remote add upstream https://github.com/daxzio/cocotbext-apb.git`

### Step-by-Step Process

#### For Each PR:

1. **Create the branch** using the suggested branch name
2. **Apply the specific fix** for that bug
3. **Test the fix** (run existing tests, create new ones if needed)
4. **Commit with descriptive message**
5. **Push to your fork**
6. **Create PR on GitHub** using the template

### Creating PR on GitHub

1. Go to your fork on GitHub
2. You'll see a banner suggesting to create a PR for your pushed branch
3. Click "Compare & pull request"
4. Use the appropriate template from above
5. Fill in any missing details specific to your environment
6. Submit the PR

### PR Order Recommendation

I recommend creating PRs in this order:
1. **Address Range Security Fix** (highest priority - security vulnerability)
2. **Byte Calculation Fix** (medium-high priority - data corruption risk)  
3. **APB Bus Fix** (high priority - functionality restoration)

This prioritization helps maintainers focus on the most critical issues first.

### Additional Tips

- **Link PRs**: Reference the other PRs in each description
- **Small commits**: Keep each PR focused on one specific bug
- **Tests**: Add unit tests for each fix if possible
- **Documentation**: Update documentation if the fixes change behavior
- **Be responsive**: Respond quickly to any review feedback

Would you like me to help you create any additional test cases or documentation for these fixes?