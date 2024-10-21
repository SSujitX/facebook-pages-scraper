from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="facebook-page-scraper",
    version="0.1.0",
    description="Facebook page scraper is a python package that helps you scrape data from facebook page.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SSujitX/facebook-page-scraper",
    author="Sujit Biswas",
    author_email="ssujitxx@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "curl-cffi",
        "selectolax",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="facebook page scraper, scrape facebook page info, facebook data scraper, facebook page info extractor, python facebook scraper",
    project_urls={
        "Bug Tracker": "https://github.com/SSujitX/facebook-page-scraper/issues",
        "Documentation": "https://github.com/SSujitX/facebook-page-scraper#readme",
        "Source Code": "https://github.com/SSujitX/facebook-page-scraper",
    },
    python_requires=">=3.9",
)
