import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pystrike",
    version="0.5.3",
    author="Joseph Schilz",
    author_email="joseph@schilz.org",
    description="Python library for interacting with Acinq's Strike lightning network payment web service.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/JASchilz/pystrike",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)
