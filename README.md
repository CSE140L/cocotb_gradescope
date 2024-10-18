# Cocotb Gradescope

This library provides utilities to quickly deploy cocotb tests with Gradescope autograders.

## Installation

```bash
git clone https://github.com/CSE140L/cocotb_gradescope
cd cocotb_gradescope
pip install .
```

## Usage

To use the library, please refer to the following example which should outline everything.

```python
import cocotb
from pathlib import Path
from cocotb_gradescope.reporter import GradescopeReporter, Visibility

results_path = Path("results.json")
reporter = GradescopeReporter(results_path)

@cocotb.test()
@reporter.report_test(visibility=Visibility.HIDDEN, max_score=10)
async def test_part1(dut):
    # If set_score isn't provided then if the test passes then the final score will set it to max_score
    assert 1 == 1

@cocotb.test()
# If the test is a failure, we can make it available to students
@reporter.report_test(visibility=Visibility.HIDDEN, max_score=10, visibility_on_failure=Visibility.VISIBLE)
async def test_part1(dut, set_score):
    assert 1 == 1
    set_score(5)
    assert 1 == 2
    set_score(10)
```