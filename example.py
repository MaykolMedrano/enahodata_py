from ineidata.endes.endes import endesdata
from ineidata.enapres.enapres import enapresdata
from ineidata.enaho.enaho import enahodata

import os

## Características
# - Descarga múltiples módulos y años en una sola llamada.
# - Descomprime automáticamente los archivos ZIP.
# - Extrae únicamente los archivos `.dta` (formato Stata) si así se desea.
# - Soporta barra de progreso en descargas.
# - Manejo de descargas en paralelo.

# Establecer ruta de directorio
os.chdir('E:\otrosTrabajosSTATA-practicas\proyectStataToGitHub\pruebas')
### Múltiples módulos y años

enahodata(
  modulos=["01","02","03"],
  anios=["2022","2023"],
  descomprimir=True,
  only_dta=True,
  overwrite=True, 
  output_dir="datos_ENAHO"
)

enapresdata(
  modulos=["1815","1816","1817"],
  anios=["2022","2023"],
  descomprimir=True,
  only_dta=True,
  overwrite=True, 
  output_dir="datos_ENAPRES"
)

endesdata(
  modulos=["1629","1630","1631"],
  anios=["2022","2023"],
  descomprimir=True,
  only_dta=True,
  overwrite=True, 
  output_dir="datos_ENDES"
)

  ### Descargas en paralelo
# enahodata(
#   modulos=["01","02"],
#   anios=["2021","2022","2023"],
#   parallel_downloads=True,
#   max_workers=4
# )
