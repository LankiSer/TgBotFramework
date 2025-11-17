"""
Setup файл для TgFramework
"""

from setuptools import setup, find_packages
from pathlib import Path


def get_version():
    version_file = Path(__file__).parent / "tgframework" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "2.0.0"


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="tgframework-bot",
    version=get_version(),
    author="Илья Кострицын",
    author_email="kostricyn50@mail.ru", 
    description="Полнофункциональный фреймворк для разработки Telegram ботов с встроенной БД, FSM, фильтрами и квизами",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LankiSer/TgBotFramework", 
    project_urls={
        "Bug Reports": "https://github.com/LankiSer/TgBotFramework/issues",
        "Source": "https://github.com/LankiSer/TgBotFramework",
        "Documentation": "https://github.com/LankiSer/TgBotFramework#readme",
    },
    packages=find_packages(exclude=["examples*", "tests*", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="telegram bot api framework sqlite fsm filters quiz pagination",
    zip_safe=False,
    include_package_data=True,
)

