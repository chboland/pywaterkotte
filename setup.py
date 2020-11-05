import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywaterkotte", 
    version="0.0.1",
    author="Christian Boland",
    author_email="pywaterkotte@chbol.de",
    description="python library for waterkotte heatpumps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chboland/pywaterkotte",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
