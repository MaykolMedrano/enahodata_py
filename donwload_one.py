import requests
import os
import zipfile
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

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
