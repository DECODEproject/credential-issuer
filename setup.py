from setuptools import setup, find_packages

setup(
    name="dddc-credential-issuer",
    version="0.1.0",
    author="Puria Nafisi Azizi",
    author_email="puria@dyne.org",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.3.0",
        "pytest_runner==4.2",
        "zenroom==0.0.5",
        "pre-commit==1.14.3",
        "python-multipart==0.0.5",
        "pyjwt==1.7.1",
        "sqlalchemy==1.2.18",
    ],
    tests_require=["pytest", "codecov", "requests", "pytest-cov"],
)
