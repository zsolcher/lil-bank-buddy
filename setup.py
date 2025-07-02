from setuptools import setup, find_packages

setup(
    name="buddy",
    version="0.1.0",
    description="lil' bank buddy: Your friendly CLI for bank account analysis and reporting.",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "openpyxl",
        "matplotlib",
        "plotly",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "buddy=report_generator:cli"
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
)
