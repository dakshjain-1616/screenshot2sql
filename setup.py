from setuptools import setup, find_packages

setup(
    name="screenshot2sql",
    version="0.3.0",
    description="Convert UI screenshots to database schemas using Claude vision",
    author="NEO",
    url="https://heyneo.so",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.40.0",
        "streamlit>=1.40.0",
        "Pillow>=10.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "screenshot2sql=screenshot2sql_conve.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
