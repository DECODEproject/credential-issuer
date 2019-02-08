from setuptools import setup, find_packages

setup(
    name="dddc-credential-issuer",
    version="0.0.1",
    author="Puria Nafisi Azizi",
    author_email="puria@dyne.org",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pytest_runner"
    ],
    tests_require=[
        "pytest",
        "codecov",
        "requests",
        "pytest-cov",
    ],
)
