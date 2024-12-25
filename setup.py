from setuptools import setup, find_packages

setup(
    name="mcp-ortools",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ortools>=9.4.1874",
        "asyncio>=3.4.3",
        "aiohttp>=3.8.1",
        "pydantic>=1.9.0",
        "mcp>=0.1.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "mcp-ortools=mcp_ortools.server:main",
        ],
    },
    author="Jacck",
    description="MCP Server with Google OR-Tools backend",
    long_description_content_type="text/markdown",
)