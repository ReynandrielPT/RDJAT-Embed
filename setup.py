"""Setup script for RDJAT-Embed package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="rdjat-embed",
    version="1.0.0",
    description="A GUI application for image steganography using the RDJAT average-bin method for embedding and extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RDJAT-Embed Project",
    author_email="",
    url="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rdjat-embed=rdjat:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Security :: Cryptography",
    ],
    keywords="steganography, image-processing, gui, embedding, extraction, RDJAT, RDJAT-Embed",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
    include_package_data=True,
    zip_safe=False,
)