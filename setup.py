import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simfin", # Replace with your own username
    version="0.0.1",
    author="Équipe CREEi",
    author_email="pierre-carl.michaud@hec.ca",
    description="Modele de microsimulation des finances publiques SimFin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://creei-models.github.io/simfin",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)