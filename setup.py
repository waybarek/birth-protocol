from setuptools import setup, find_packages

setup(
    name="tif",
    version="0.1.0",
    description="Token-Centered Information Framework – defensive semantic layer for Birth Protocol",
    author="@waybarek",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "transformers",
        "sentence-transformers",
        "scipy",
        "numpy"
    ],
    python_requires=">=3.9",
)
