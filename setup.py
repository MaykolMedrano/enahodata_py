import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setuptools.setup(
    name="enahodata",
    version="0.0.2",  
    author="Maykol Medrano Cahuana & Jelsin Stalin Palomino Huaytapuma",
    author_email="maykolmedrano35@gmail.com & jstpalomino@hotmail.com",
    description="Library that automates the download of the modules of the National Household Survey (ENAHO in spanish) conducted by the National Institute of Statistics and Informatics of Peru each year.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/MaykolMedrano/enahodata2",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: Microsoft ",
        "Intended Audience :: Education",
    ],
    install_requires=["requests", "tqdm"],
    keywords=['Perú', 'Peru', 'inei', 'enaho', 'microdatos'], 
)