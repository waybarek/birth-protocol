“””
Birth Protocol - Token-Centered Information Framework (TIF)
Setup configuration for pip installation
“””

from setuptools import setup, find_packages

with open(“README.md”, “r”, encoding=“utf-8”) as fh:
long_description = fh.read()

setup(
name=“tif”,
version=“0.1.0”,
author=”@waybarek”,
description=“Token-Centered Information Framework for AI agent validation”,
long_description=long_description,
long_description_content_type=“text/markdown”,
url=“https://github.com/waybarek/birth-protocol”,
packages=find_packages(),
classifiers=[
“Development Status :: 3 - Alpha”,
“Intended Audience :: Developers”,
“Topic :: Scientific/Engineering :: Artificial Intelligence”,
“License :: OSI Approved :: MIT License”,
“Programming Language :: Python :: 3.8”,
“Programming Language :: Python :: 3.9”,
“Programming Language :: Python :: 3.10”,
“Programming Language :: Python :: 3.11”,
],
python_requires=”>=3.8”,
install_requires=[
“torch>=2.0.0”,
“transformers>=4.30.0”,
“sentence-transformers>=2.2.0”,
“numpy>=1.24.0”,
“scipy>=1.10.0”,
“pyyaml>=6.0”,
“tqdm>=4.65.0”,
],
extras_require={
“dev”: [
“pytest>=7.3.0”,
“pytest-cov>=4.1.0”,
“black>=23.3.0”,
“flake8>=6.0.0”,
“mypy>=1.3.0”,
],
“bitcoin”: [
“python-bitcoinlib>=0.12.0”,
“hashlib>=20081119”,
],
},
)
