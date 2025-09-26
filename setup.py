# Copyright Sierra

from setuptools import find_packages, setup

setup(
    name="tau_bench",
    version="0.1.0",
    description="The Tau-Bench package with API service",
    long_description=open("README.md").read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.13.3",
        "mistralai>=0.4.0",
        "anthropic>=0.26.1",
        "google-generativeai>=0.5.4",
        "tenacity>=8.3.0",
        "termcolor>=2.4.0",
        "numpy>=1.26.4",
        "litellm>=1.41.0",
        # API service dependencies
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "requests>=2.31.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "tau-bench-server=tau_bench.api.server:main",
        ],
    },
)
