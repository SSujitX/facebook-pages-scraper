import os
from setuptools import setup, find_packages

def get_version():
    version_file = os.path.join(
        os.path.dirname(__file__), "facebook_page_scraper", "__version__.py"
    )
    with open(version_file, "r") as f:
        version_vars = {}
        exec(f.read(), version_vars)
    return version_vars["__version__"]

setup(
    name="facebook-pages-scraper",
    version=get_version(),
    description="Facebook page scraper is a python package that helps you scrape data from facebook pages.",
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
