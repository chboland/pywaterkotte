""" Setup """
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywaterkotte2",
    version="0.0.5b",
    author="Michael Pattison",
    author_email="michael@pattison.de",
    description="python library for waterkotte heatpumps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pattisonmichael/pywaterkotte",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
