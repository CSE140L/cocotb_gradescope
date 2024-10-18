from setuptools import setup, find_packages

setup(
    name="cocotb_gradescope",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
