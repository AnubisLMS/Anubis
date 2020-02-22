import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Anubis",
    version='0.0.1',
    author="John McCann Cunniff Jr",
    author_email="john@osiris.cyber.nyu.edu",
    description="Interface for managing jobs on the Anubis cluster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    entry_points={
        "console_scripts": {
            'anubis=acli:main'
        }
    }
)
