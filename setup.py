from setuptools import setup, find_packages

setup(
    name="dddc-credential-issuer",
    version="0.1.0",
    author="Puria Nafisi Azizi",
    author_email="puria@dyne.org",
    packages=find_packages(),
    install_requires=[
        "bunch==1.0.1",
        "fastapi==0.44.0",
        "pytest_runner==5.1",
        "zenroom==1.0.7rc0",
        "pre-commit==2.0.0",
        "python-multipart==0.0.5",
        "pyjwt==1.7.1",
        "sqlalchemy==1.3.10",
    ],
    tests_require=["pytest", "pytest-env","codecov", "requests", "pytest-cov"],
)
