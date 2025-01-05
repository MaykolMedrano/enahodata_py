import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    install_requires = f.read().split("\n")[:-1]

# Set a development version for source installs 
__version__ = "0.0.1"

setuptools.setup(
    name="ineidata",
    version=__version__,  # This will be replaced with the commit tag
    author="Maykol Medrano Cahuana & Jelsin Stalin Palomino Huaytapuma",
    author_email="maykolmedrano35@gmail.com & jstpalomino@hotmail.com",
    description="Library that automates the download of survey datasets found at the National Institute of Statistics and Informatics of Peru.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MaykolMedrano/enahodata2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.11.0",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Intended Audience :: Education",
        "License :: MIT License",
    ],
    install_requires=install_requires,
    keywords=['Perú', 'Peru', 'inei', 'enaho', 'endes', 'epen', 'enapres'], 
    python_requires=">3.11",    
)