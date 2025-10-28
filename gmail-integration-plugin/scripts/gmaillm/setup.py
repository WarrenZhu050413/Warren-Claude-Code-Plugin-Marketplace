"""Setup script for gmaillm package."""

from setuptools import setup, find_packages

setup(
    name="gmaillm",
    version="0.1.0",
    description="LLM-friendly Gmail API wrapper with CLI",
    author="Warren Zhu",
    author_email="wzhu@college.harvard.edu",
    packages=find_packages(),
    install_requires=[
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "pydantic>=2.0.0",
        "python-dateutil",
        "packaging",
    ],
    entry_points={
        'console_scripts': [
            'gmail=gmaillm.cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
