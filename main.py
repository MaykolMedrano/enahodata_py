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


def _download_and_extract_one(
    anio: str,
    modulo: str,
    output_dir: str,
    chunk_size: int,
    overwrite: bool,
    descomprimir: bool,
    verbose: bool,
    only_dta: bool
) -> None:
    """Descarga un solo archivo (para un año y un módulo) y opcionalmente lo descomprime."""

    # Validar año
    if anio not in YEAR_MAP:
        raise ValueError(f"Año {anio} no está en la lista de ENAHO soportados.")

    codigo_enaho = YEAR_MAP[anio]["codigo"]
    year_enaho = YEAR_MAP[anio]["year"]

    # Construir URL
    url = f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo_enaho}-Modulo{modulo}.zip"
    
    # Rutas y nombres
    os.makedirs(output_dir, exist_ok=True)
    zip_filename = f"modulo_{modulo}_{year_enaho}.zip"
    zip_path = os.path.join(output_dir, zip_filename)

    # Logging informativo
    if verbose:
        logging.info(f"Descargando módulo '{modulo}' para el año '{anio}'. URL: {url}")

    # Verificar sobreescritura
    if os.path.isfile(zip_path) and not overwrite:
        if verbose:
            logging.info(f"Archivo '{zip_path}' ya existe y overwrite=False. No se descargará de nuevo.")
        return

    # Descargar con barra de progreso
    try:
        with requests.get(url, stream=True) as r:
            if r.status_code == 200:
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                desc_tqdm = f"Descargando {os.path.basename(zip_path)}"
                with open(zip_path, 'wb') as f, tqdm(
                    total=total_size_in_bytes,
                    unit='iB',
                    unit_scale=True,
                    desc=desc_tqdm,
                    disable=not verbose
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

                if verbose:
                    logging.info(f"Descarga exitosa: {zip_path}")

                # Descomprimir si se solicita
                if descomprimir:
                    extract_dir = os.path.join(output_dir, f"modulo_{modulo}_{year_enaho}_extract")
                    os.makedirs(extract_dir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(zip_path, "r") as zip_ref:
                            zip_ref.extractall(extract_dir)
                        if verbose:
                            logging.info(f"Archivo descomprimido en: {extract_dir}")

                        # Si se desea solo .dta
                        if only_dta:
                            # Crear una carpeta para los .dta
                            dta_dir = os.path.join(output_dir, f"modulo_{modulo}_{year_enaho}_dta_only")
                            os.makedirs(dta_dir, exist_ok=True)
                            
                            # Recorrer la carpeta extraída para buscar .dta
                            for root, dirs, files in os.walk(extract_dir):
                                for file in files:
                                    if file.lower().endswith(".dta"):
                                        source_file = os.path.join(root, file)
                                        shutil.copy2(source_file, dta_dir)
                            
                            if verbose:
                                logging.info(f"Archivos .dta copiados a: {dta_dir}")

                    except zipfile.BadZipFile:
                        logging.error(f"Error: el archivo '{zip_path}' no parece ser un ZIP válido.")
            else:
                logging.error(f"Error al descargar {url}. Código de estado HTTP: {r.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error durante la conexión o la descarga: {e}")


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


