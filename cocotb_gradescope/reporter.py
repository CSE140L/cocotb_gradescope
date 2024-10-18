import json
import inspect
from pathlib import Path
from enum import Enum
from functools import wraps
from cocotb.result import TestFailure, TestError
from cocotb.handle import HierarchyObject

if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec


class Visibility(Enum):
    HIDDEN = "hidden"
    AFTER_DUE_DATE = "after_due_date"
    AFTER_PUBLISHED = "after_published"
    VISIBLE = "visible"
    DEFAULT = "visible"


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


class GradescopeReporter:
    def __init__(self, results_path: Path = Path("results.json")) -> None:
        self.test_results = {"tests": []}
        self.results_path = results_path

    def __del__(self):
        self._write_results_to_file(self.results_path)

    def report_test(self, visibility: Visibility, max_score: int, visibility_on_success: Visibility = None, visibility_on_failure: Visibility = None):
        """Decorator to capture and store test results with support for partial scores."""

        def decorator(func):
            @wraps(func)
            async def wrapper(dut: HierarchyObject, *args, **kwargs):
                test_name = func.__name__
                test_result = {
                    "name": test_name,
                    "status": TestStatus.FAILED.value,
                    "output": "",
                    "score": 0,
                    "max_score": max_score,
                    "visibility": visibility.value,
                }

                def set_score(score: int):
                    """Set or update the score within the allowed range."""
                    test_result["score"] = min(max(score, 0), max_score)

                # Pass the set_score function to the test as a keyword argument
                if 'set_score' in inspect.getargspec(func).args:
                    kwargs['set_score'] = set_score

                try:
                    # Run the actual test
                    await func(dut, *args, **kwargs)
                    test_result["status"] = TestStatus.PASSED.value
                    # Give full credit if the test passes and the score wasn't already set
                    if test_result["score"] == 0:
                        test_result["score"] = max_score
                    if visibility_on_success is not None:
                        test_result["visibility"] = visibility_on_success.value
                except (TestFailure, TestError, AssertionError) as e:
                    test_result["output"] = str(e).split("\n")[0]
                    if visibility_on_failure is not None:
                        test_result["visibility"] = visibility_on_failure.value
                    dut._log.error(e)
                except Exception as e:
                    dut._log.warning(f"Gradescope Export Error: {e}")
                finally:
                    # Store the result in the global dictionary
                    self.test_results["tests"].append(test_result)

                    self._write_results_to_file(self.results_path)

                if test_result["status"] == TestStatus.PASSED.value:
                    return True
                else:
                    raise AssertionError

            return wrapper

        return decorator

    def _write_results_to_file(self, filename: Path = Path("results.json")):
        """Write the collected test results to a JSON file."""
        with open(filename.absolute(), "w") as f:
            json.dump(self.test_results, f, indent=4)
