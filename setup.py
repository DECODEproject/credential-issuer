from setuptools import setup, find_packages

setup(
    name="dddc-credential-issuer",
    version="0.1.0",
    author="Puria Nafisi Azizi",
    author_email="puria@dyne.org",
    packages=find_packages(),
    install_requires=[
        "bunch==1.0.1",
        "fastapi==0.30.0",
        "pytest_runner==4.4",
        "zenroom==0.2.5",
        "pre-commit==1.17.0",
        "python-multipart==0.0.5",
        "pyjwt==1.7.1",
        "sqlalchemy==1.3.4",
    ],
    tests_require=["pytest", "codecov", "requests", "pytest-cov"],
)
