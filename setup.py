import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simfin-creei", # Replace with your own username
    version="0.0.8",
    author="Équipe CREEi",
    author_email="julien.navaux@hec.ca",
    description="Modèle de microsimulation des finances publiques SimFin",
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
