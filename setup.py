from setuptools import setup, find_packages

setup(
    name="lil-bank-buddy",
    version="0.1.0",
    description="lil' bank buddy: Your friendly CLI for bank account analysis and reporting.",
    author="Your Name",
    packages=["src"],
    package_dir={"src": "src"},
    py_modules=["src.cli"],
    install_requires=[
        "pandas",
        "openpyxl", 
        "matplotlib",
        "plotly",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "buddy=src.cli:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
)
