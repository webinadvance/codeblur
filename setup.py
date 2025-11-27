from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codeblur",
    version="1.0.1",
    author="CodeBlur Team",
    author_email="",
    description="A powerful GUI tool for obfuscating and deobfuscating code strings with clipboard integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/codeblur/",
    packages=find_packages(),
    package_data={
        "codeblur": [
            "known_words.json",
            "brand_words.json",
            "package_words.json",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "codeblur=codeblur.codeblur:main",
        ],
    },
)
