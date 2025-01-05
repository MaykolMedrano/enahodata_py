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

# enapresdata(
#   modulos=["1727","1728","1729"],
#   anios=["2022"],
#   descomprimir=True,
#   only_dta=True,
#   overwrite=True, 
#   output_dir="datos_ENAPRES"
# )


# endesdata(
#   modulos=["01","02","03"],
#   anios=["2006"],
#   descomprimir=True,
#   only_dta=True,
#   overwrite=True, 
#   output_dir="datos_ENAHO"
# )

# enahodata(
#   modulos=["01","02","03"],
#   anios=["2004", "2005"],
#   descomprimir=True,
#   only_dta=True,
#   overwrite=True, 
#   output_dir="datos_ENAHO"
# )

  ### Descargas en paralelo
# enahodata(
#   modulos=["01","02"],
#   anios=["2021","2022","2023"],
#   parallel_downloads=True,
#   max_workers=4
# )
