from setuptools import find_packages, setup


setup(
    name="power-outage-mlops",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
)
