## Características
- Descarga múltiples módulos y años en una sola llamada.
- Descomprime automáticamente los archivos ZIP.
- Extrae únicamente los archivos `.dta` (formato Stata) si así se desea.
- Soporta barra de progreso en descargas.
- Manejo de descargas en paralelo.

# Establecer ruta de directorio
os.chdir('C:/Users/User/Desktop/prueba_01/prueba_python')
### Múltiples módulos y años
enahodata(
  # modulos=["01","02","03"],
  #anios=["2022","2023"],
  descomprimir=True,
  only_dta=True,
  overwrite=True, 
  output_dir="datos_ENAHO"
)

  ### Descargas en paralelo
enahodata(
  modulos=["01","02"],
  anios=["2021","2022","2023"],
  parallel_downloads=True,
  max_workers=4
)
