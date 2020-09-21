import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read("README.md") if os.path.isfile("README.md") else ""

setup(
    name="icon-etl",
    version="0.1.0",
    packages=find_packages(exclude=["schemas", "tests"]),
    url="https://github.com/insight-icon/icon-etl",
    author="Richard Mah",
    author_email="richard@richardmah.com",
    description="Tools for exporting ICON blockchain data to CSV or JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6.0,<3.8.0",
    install_requires=[
        "blockchain-etl-common==1.3.0",
        "requests==2.20.0",
        "python-dateutil==2.7.0",
        "click==7.0",
        "iconsdk >= 1.3.2",
        "web3 >= 5.5.0",
    ],
    extras_require={
        "streaming": ["timeout-decorator==0.4.1", "sqlalchemy==1.3.13",],
        "dev": ["pytest~=4.3.0"],
    },
    project_urls={
        "Bug Reports": "https://github.com/insight-icon/icon-etl/issues",
        "Source": "https://github.com/insight-icon/icon-etl",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["iconetl=iconetl.cli:cli",],},
)
