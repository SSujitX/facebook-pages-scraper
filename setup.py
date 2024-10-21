from setuptools import setup, find_packages

setup(
    name="facebook-page-scraper",
    version="0.1.0",
    description="A Python package to scrape and extract comprehensive information from Facebook pages.",
    long_description=open("README.md").read(),
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
