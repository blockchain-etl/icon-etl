from setuptools import setup

setup(
    name="iconetl",
    version="0.0.1",
    packages=[""],
    url="",
    license="",
    author="Richard Mah",
    author_email="richard@richardmah.com",
    description="",
    python_requires=">=3.6.0,<=3.8.0",
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
)
