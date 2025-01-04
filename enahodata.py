import requests
import os
import zipfile
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

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


