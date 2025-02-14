from setuptools import setup, find_packages

setup(
    name="market-trading-dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance==0.2.51",
        "pandas==2.2.3",
        "numpy==2.2.3",
        "rich==13.9.4",
        "talib-binary==0.6.0",
    ],
    entry_points={
        "console_scripts": [
            "market-dashboard=market_dashboard.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A real-time forex trading dashboard with market analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/market-trading-dashboard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8s",
)
