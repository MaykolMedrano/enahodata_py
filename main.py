import requests
import os
import zipfile
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

# Diccionario que mapea el año de ENAHO al código correspondiente y la variable year.
YEAR_MAP = {
    "2023": {"codigo": 906, "year": 2023},
    "2022": {"codigo": 784, "year": 2022},
    "2021": {"codigo": 759, "year": 2021},
    "2020": {"codigo": 737, "year": 2020},
    "2019": {"codigo": 687, "year": 2019},
    "2018": {"codigo": 634, "year": 2018},
    "2017": {"codigo": 603, "year": 2017},
    "2016": {"codigo": 546, "year": 2016},
    "2015": {"codigo": 498, "year": 2015},
    "2014": {"codigo": 440, "year": 2014},
    "2013": {"codigo": 404, "year": 2013},
    "2012": {"codigo": 324, "year": 2012},
    "2011": {"codigo": 291, "year": 2011},
    "2010": {"codigo": 279, "year": 2010},
    "2009": {"codigo": 285, "year": 2009},
    "2008": {"codigo": 284, "year": 2008},
    "2007": {"codigo": 283, "year": 2007},
    "2006": {"codigo": 282, "year": 2006},
    "2005": {"codigo": 281, "year": 2005},
    "2004": {"codigo": 280, "year": 2004},
}



def enahodata(
    modulos: list[str],
    anios: list[str],
    place: str = "",
    preserve: bool = False,
    condition: str = "",
    descomprimir: bool = False,
    output_dir: str = ".",
    overwrite: bool = False,
    chunk_size: int = 1024,
    verbose: bool = True,
    parallel_downloads: bool = False,
    max_workers: int = 4,
    only_dta: bool = False
) -> None:
    """
    Función principal para descargar los módulos de la ENAHO.
    
    Parámetros adicionales
    ----------------------
    only_dta : bool
        Si True, crea una carpeta con solo los archivos .dta 
        (además de la carpeta normal con todos los archivos extraídos).
    """
    if preserve and verbose:
        logging.warning("Opción 'preserve' no aplicada en Python (solo demostración).")
    if condition and verbose:
        logging.info(f"Se recibió la condición: {condition} (no implementada).")

    # Crear lista de tareas
    tasks = [(anio, modulo) for anio in anios for modulo in modulos]
    if verbose:
        logging.info(f"Se procesarán {len(tasks)} descargas en total.")

    if parallel_downloads:
        if verbose:
            logging.info(f"Descarga en paralelo habilitada. Máximo de hilos: {max_workers}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for anio, modulo in tasks:
                fut = executor.submit(
                    _download_and_extract_one,
                    anio=anio,
                    modulo=modulo,
                    output_dir=output_dir,
                    chunk_size=chunk_size,
                    overwrite=overwrite,
                    descomprimir=descomprimir,
                    verbose=verbose,
                    only_dta=only_dta
                )
                futures.append(fut)
            # Esperar a que terminen todas
            for future in as_completed(futures):
                exc = future.exception()
                if exc:
                    logging.error(f"Ocurrió un error en la descarga: {exc}")
    else:
        # Descarga secuencial
        for anio, modulo in tasks:
            _download_and_extract_one(
                anio=anio,
                modulo=modulo,
                output_dir=output_dir,
                chunk_size=chunk_size,
                overwrite=overwrite,
                descomprimir=descomprimir,
                verbose=verbose,
                only_dta=only_dta
            )


