import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enahodata",
    version="0.0.1",  # This will be replaced with the commit tag
    author="Maykol Medrano Cahuana & Jelsin Stalin Palomino Huaytapuma",
    author_email="maykolmedrano35@gmail.com & jstpalomino@hotmail.com",
    description="Library that automates the download of the modules of the National Household Survey (ENAHO in spanish) conducted by the National Institute of Statistics and Informatics of Peru each year.",
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
    install_requires=["requests", "tqdm"],
    keywords=['Perú', 'Peru', 'inei', 'enaho'], 
    python_requires=">3.11",    
)