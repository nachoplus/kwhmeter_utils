from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="kwhmeter_utils",
    version_config=True,
    setup_requires=['setuptools-git-versioning'],
    author="nachomas",
    author_email="mas.ignacio@gmail.com",
    description="Simulador de facturas PVPC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nachoplus/kalpa_factura.git",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['data/*.yml']},    
    install_requires=[
        'kwhmeter@git+https://github.com/nachoplus/kwhmeter.git',
        'pandas'
    ],
    extras_require={

    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
