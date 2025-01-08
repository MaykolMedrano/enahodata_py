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
):
    """
    Descarga un solo archivo (para un año y un módulo)
    usando el código dado (sea panel o corte transversal),
    y opcionalmente lo descomprime.
    """
    url = f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{panel_code}-Modulo{modulo}.zip"
    zip_filename = f"modulo_{modulo}_{anio}.zip"
    zip_path = os.path.join(output_dir, zip_filename)

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
                    extract_dir = os.path.join(output_dir, f"modulo_{modulo}_{anio}_extract")
                    os.makedirs(extract_dir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(zip_path, "r") as zip_ref:
                            zip_ref.extractall(extract_dir)
                        if verbose:
                            logging.info(f"Archivo descomprimido en: {extract_dir}")

                        # Si se desea solo .dta
                        if only_dta:
                            dta_dir = os.path.join(output_dir, f"modulo_{modulo}_{anio}_dta_only")
                            os.makedirs(dta_dir, exist_ok=True)
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
    descomprimir: bool = False,
    output_dir: str = ".",
    overwrite: bool = False,
    chunk_size: int = 1024,
    verbose: bool = True,
    parallel_downloads: bool = False,
    max_workers: int = 4,
    only_dta: bool = False,
    panel: bool = False
) -> None:
    """
    Función principal para descargar módulos de la ENAHO 
    (corte transversal o panel, según 'panel=True').
    
    NOTA: 
    - Se eliminó la opción 'condition'.
    - Para panel=True NO se toman módulos por defecto. 
      El usuario debe especificarlos en 'modulos'.

    Parámetros:
    -----------
    modulos : list[str]
        Lista de módulos (e.g. ["01","02"] para ENAHO regular, 
        ["1474","1475"] para ENAHO panel).
        - Se exige que NO esté vacío, tanto para panel=True como panel=False.
    anios : list[str]
        Lista de años (ej. ["2023","2022"]).
    panel : bool
        Si True, usa YEAR_MAP_PANEL (datos de panel).
        Si False, usa YEAR_MAP (corte transversal).
    ...
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
        logging.error("Debes especificar al menos un módulo en 'modulos' (tanto para panel como para corte transversal).")
        return

    # Crear la carpeta de salida
    os.makedirs(output_dir, exist_ok=True)

    # Construir lista de tareas (año, módulo)
    tasks = []
    for anio in anios:
        if anio not in map_dict:
            logging.error(f"El año {anio} no está en la tabla {'panel' if panel else 'corte transversal'}.")
            continue

        code_inei = map_dict[anio]["codigo"]
        # Agregar (anio, modulo, code) a la lista
        for m in modulos:
            tasks.append((anio, m, code_inei))

    if verbose:
        logging.info(f"Se procesarán {len(tasks)} descargas en total.")

    # Descarga en paralelo o secuencial
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
                    panel_code=code
                )
                futures.append(fut)
            # Esperar a que terminen
            for future in as_completed(futures):
                exc = future.exception()
                if exc:
                    logging.error(f"Ocurrió un error en la descarga: {exc}")
    else:
        # Descarga secuencial
        for (anio, modulo, code) in tasks:
            _download_and_extract_one(
                anio=anio,
                modulo=modulo,
                output_dir=output_dir,
                chunk_size=chunk_size,
                overwrite=overwrite,
                descomprimir=descomprimir,
                verbose=verbose,
                only_dta=only_dta,
                panel_code=code
            )
