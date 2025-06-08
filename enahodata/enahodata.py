import requests
import os
import zipfile
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import time
#import pandas as pd  # <-- para la opción de cargar los .dta

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

# DICCIONARIO DE AÑOS Y CÓDIGOS DE LA ENAHO (Corte Transversal)
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

# DICCIONARIO DE AÑOS Y CÓDIGOS DE LA ENAHO (Datos de panel)
YEAR_MAP_PANEL = {
    "2023": {"codigo": 912, "year": 2023},
    "2022": {"codigo": 845, "year": 2022},
    "2021": {"codigo": 763, "year": 2021},
    "2020": {"codigo": 743, "year": 2020},
    "2019": {"codigo": 699, "year": 2019},
    "2018": {"codigo": 651, "year": 2018},
    "2017": {"codigo": 612, "year": 2017},
    "2016": {"codigo": 614, "year": 2016},
    "2015": {"codigo": 529, "year": 2015},
    "2011": {"codigo": 302, "year": 2011},
}


def _download_and_extract_one(
    anio: str,
    modulo: str,
    output_dir: str,
    chunk_size: int,
    overwrite: bool,
    descomprimir: bool,
    verbose: bool,
    only_dta: bool,
    panel_code: int,
    load_dta: bool = False,
):
    """
    Descarga un solo archivo (para un año y un módulo)
    usando el código dado (sea panel o corte transversal),
    y opcionalmente lo descomprime, elimina el .zip,
    aplana la carpeta al extraer, y permite cargar los .dta.
    
    Retorna:
    --------
    - Si load_dta=True, retorna un diccionario { nombre_archivo: DataFrame, ... }
    - De lo contrario, retorna None.
    """

    url = f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{panel_code}-Modulo{modulo}.zip"
    zip_filename = f"modulo_{modulo}_{anio}.zip"
    zip_path = os.path.join(output_dir, zip_filename)
 
    if verbose:
        logging.info(f"Descargando módulo '{modulo}' para el año '{anio}'. URL: {url}")

    if os.path.isfile(zip_path) and not overwrite:
        if verbose:
            logging.info(f"Archivo '{zip_path}' ya existe y overwrite=False. No se descargará de nuevo.")
        return None

    # -- Descargar con barra de progreso --
    #start_request = time.time()
    try:
        with requests.get(url, stream=True, timeout=4) as r:
            if r.status_code == 200:
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                #end_request = time.time()
                #logging.info(f"El request demoró {(end_request - start_request):.4f}s")
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

                # -- Descomprimir si se solicita --
                if descomprimir:
                    # Directorio de extracción (uno por cada módulo+año, sin subcarpetas anidadas)
                    extract_dir = os.path.join(output_dir, f"modulo_{modulo}_{anio}")
                    os.makedirs(extract_dir, exist_ok=True)

                    try:
                        with zipfile.ZipFile(zip_path, "r") as zip_ref:
                            # Extraer "aplanando" la estructura (sin subcarpetas).
                            for zinfo in zip_ref.infolist():
                                if zinfo.is_dir():
                                    # Omitir directorios
                                    continue
                                # Obtener sólo el nombre del archivo (sin ruta interna)
                                filename = os.path.basename(zinfo.filename)
                                if not filename:
                                    # Si es carpeta vacía o ruta rara, ignorar
                                    continue

                                # Si se desea sólo .dta, omitimos otros archivos
                                if only_dta and not filename.lower().endswith(".dta"):
                                    continue

                                # Ruta final (en la carpeta de extracción) sin subcarpetas
                                final_path = os.path.join(extract_dir, filename)
                                # Extraer el archivo manualmente
                                with zip_ref.open(zinfo) as source, open(final_path, 'wb') as target:
                                    shutil.copyfileobj(source, target)

                        if verbose:
                            logging.info(f"Archivo descomprimido (aplanado) en: {extract_dir}")

                        # -- Eliminar el .zip una vez descomprimido --
                        os.remove(zip_path)
                        if verbose:
                            logging.info(f"Archivo .zip eliminado: {zip_path}")

                        # -- Cargar los .dta si se pide --
                        if load_dta:
                            import pandas as pd
                            
                            dta_dfs = {}
                            for f in os.listdir(extract_dir):
                                if f.lower().endswith(".dta"):
                                    dta_path = os.path.join(extract_dir, f)
                                    try:
                                        df = pd.read_stata(dta_path)
                                        dta_dfs[f] = df
                                    except Exception as e:
                                        logging.error(f"Error al cargar {dta_path}: {e}")
                            return dta_dfs

                    except zipfile.BadZipFile:
                        logging.error(f"Error: el archivo '{zip_path}' no parece ser un ZIP válido.")
                else:
                    # Si no se descomprime, no cargamos nada
                    return None
            else:
                logging.error(f"Error al descargar {url}. Código de estado HTTP: {r.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error durante la conexión o la descarga: {e}")

    return None


def enahodata(
    modulos: list[str],
    anios: list[str],
    descomprimir: bool = False,
    output_dir: str = ".",
    overwrite: bool = False,
    chunk_size: int = 1024,
    verbose: bool = True,
    parallel_downloads: bool = False,
    max_workers: int = 5,
    only_dta: bool = False,
    panel: bool = False,
    preserve: bool = False,
    load_dta: bool = False,   # <-- nueva opción para cargar automáticamente los .dta
):
    """
    Función principal para descargar módulos de la ENAHO 
    (corte transversal o panel, según 'panel=True').

    Parameters
    ----------
    modulos : list[str]
        Lista de módulos a descargar. Ejemplo: ["01", "02"] (ENAHO regular)
        o ["1474", "1475"] (panel). ¡No puede estar vacía!
    anios : list[str]
        Lista de años. Ejemplo: ["2023", "2022"].
    panel : bool, optional
        Si True, usa datos de panel (YEAR_MAP_PANEL). Si False, corte transversal (YEAR_MAP).
        Por defecto: False.
    descomprimir : bool, optional
        Si True, descomprime el ZIP y lo elimina después.
        Por defecto: True.
    only_dta : bool, optional
        Si True, solo extrae/copia archivos .dta (ignora otros formatos).
        Por defecto: False.
    load_dta : bool, optional
        Si True, carga los archivos .dta en memoria (DataFrames de pandas) y retorna un diccionario.
        Por defecto: False.
    **kwargs
        Parámetros adicionales:
        - output_dir : str, optional
            Directorio personalizado para guardar archivos.
        - overwrite : bool, optional
            Sobrescribir archivos existentes. Por defecto: False.
        - chunk_size : int, optional
            Tamaño de chunks para descargas (bytes). Por defecto: 8192.
        - parallel_downloads : bool, optional
            Descargas en paralelo. Por defecto: False.
        - max_workers : int, optional
            Número de hilos para descargas paralelas. Por defecto: 5.

    Retorna
    -------
    dict | None
        - Si `load_dta=True`: Retorna un diccionario anidado con la estructura:
            ```python
            {
                ("2023", "01"): {
                    "enaho_2023_01.dta": pd.DataFrame,
                    ...
                },
                ...
            }
            ```
        - Si `load_dta=False`: Retorna None.

    Ejemplos
    --------
    >>> datos = descargar_modulos(
    ...     modulos=["01", "02"],
    ...     anios=["2023"],
    ...     load_dta=True
    ... )
    >>> datos[("2023", "01")].keys()  # Si load_dta = True, retorna diccionario de diccionarios
    """

    if preserve and verbose:
        logging.warning("Opción 'preserve' no aplicada en Python (solo demostración).")

    # Elegir diccionario según panel
    if panel:
        map_dict = YEAR_MAP_PANEL
        if verbose:
            logging.info("Descargando ENAHO Panel.")
    else:
        map_dict = YEAR_MAP
        if verbose:
            logging.info("Descargando ENAHO corte transversal.")

    # Validar que el usuario haya pasado 'modulos'
    if not modulos:
        logging.error("Debes especificar al menos un módulo en 'modulos'.")
        return None

    # Crear la carpeta de salida
    os.makedirs(output_dir, exist_ok=True)

    # Construir lista de tareas (año, módulo)
    tasks = []

    if not all(isinstance(anio, str) for anio in anios):
        anios = [str(anio) for anio in anios]

    for anio in anios:
        if anio not in map_dict:
            logging.error(f"El año {anio} no está en la tabla {'panel' if panel else 'corte transversal'}.")
            continue

        code_inei = map_dict[anio]["codigo"]
        for m in modulos:
            tasks.append((anio, m, code_inei))

    if verbose:
        logging.info(f"Se procesarán {len(tasks)} descargas en total.")

    # Si vamos a cargar .dta, almacenaremos los resultados aquí
    all_dta_results = {} if load_dta else None

    # Descarga paralela
    if parallel_downloads:
        if verbose:
            logging.info(f"Descarga en paralelo habilitada. Máximo de hilos: {max_workers}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for (anio, modulo, code) in tasks:
                fut = executor.submit(
                    _download_and_extract_one,
                    anio=anio,
                    modulo=modulo,
                    output_dir=output_dir,
                    chunk_size=chunk_size,
                    overwrite=overwrite,
                    descomprimir=descomprimir,
                    verbose=verbose,
                    only_dta=only_dta,
                    panel_code=code,
                    load_dta=load_dta
                )
                futures.append((anio, modulo, fut))

            # Recoger resultados
            for (anio, modulo, fut) in futures:
                try:
                    result = fut.result()
                    if load_dta and result:
                        # result es un dict { filename: DataFrame }
                        all_dta_results[(anio, modulo)] = result
                except Exception as e:
                    logging.error(f"Ocurrió un error en la descarga del (año={anio}, módulo={modulo}): {e}")

    else:
        # Descarga secuencial
        for (anio, modulo, code) in tasks:
            try:
                result = _download_and_extract_one(
                    anio=anio,
                    modulo=modulo,
                    output_dir=output_dir,
                    chunk_size=chunk_size,
                    overwrite=overwrite,
                    descomprimir=descomprimir,
                    verbose=verbose,
                    only_dta=only_dta,
                    panel_code=code,
                    load_dta=load_dta
                )
                if load_dta and result:
                    all_dta_results[(anio, modulo)] = result
            except Exception as e:
                logging.error(f"Ocurrió un error en la descarga del (año={anio}, módulo={modulo}): {e}")

    # Si no se pidió cargar dta, no retornamos nada
    if load_dta:
        return all_dta_results
    else:
        return None
