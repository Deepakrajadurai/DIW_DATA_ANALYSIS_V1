from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="german-economic-dashboard",
    version="1.0.0",
    author="Economic Analysis Team",
    author_email="contact@economic-dashboard.com",
    description="AI-powered German economic insights dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/german-economic-dashboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "production": [
            "gunicorn>=20.0.0",
            "uvicorn[standard]>=0.24.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "german-dashboard=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.env.example"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/german-economic-dashboard/issues",
        "Source": "https://github.com/yourusername/german-economic-dashboard",
        "Documentation": "https://github.com/yourusername/german-economic-dashboard#readme",
    },
)