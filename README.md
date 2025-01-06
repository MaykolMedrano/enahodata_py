# ENAHODATA
Esta libreria consta de un comando para extraer datos de la Encuesta Nacional de Hogares (ENAHO) del Instituto Nacional de Estadística e Informática (INEI) de Perú que se realiza cada año desde el 2004. Esta encuesta esta organizado por modulos.

[Ficha técnica](https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/FichaTecnica/498-Ficha.pdf)

### Modulos de la Encuesta Nacional de Hogares (ENAHO)

Los modulos son los siguientes:

Nro|Código Módulo|Modulo|Preguntas
:-------|:-------|:---------|:------
1|`01`|Características de la Vivienda y del Hogar|`Preguntas`
2|`02`|Características de los Miembros del Hogar|`Preguntas`
3|`03`|Educación|`Preguntas`
4|`04`|Salud|`Preguntas`
5|`05`|Empleo e Ingresos|`Preguntas`
6|`07`|	Gastos en Alimentos y Bebidas (Módulo 601)|`Preguntas`
7|`08`|Instituciones Beneficas|`Preguntas`
8|`09`|Mantenimiento de la Vivienda|`Preguntas`
9|`10`|Transportes y Comunicaciones|`Preguntas`
10|`11`|Servicios a la Vivienda|`Preguntas`
11|`12`|Esparcimiento , Diversion y Servicios de Cultura|`Preguntas`
12|`13`|Vestido y Calzado|`Preguntas`
13|`15`|Gastos de Transferencias|`Preguntas`
14|`16`|Muebles y Enseres|`Preguntas`
15|`17`|Otros Bienes y Servicios|`Preguntas`
16|`18`|Equipamiento del Hogar|`Preguntas`
17|`22`|Producción Agrícola|`Preguntas`
18|`23`|Subproductos Agricolas|`Preguntas`
19|`24`|Producción Forestal|`Preguntas`
20|`25`|Gastos en Actividades Agricolas y/o Forestales|`Preguntas`
21|`26`|Producción Pecuaria|`Preguntas`
22|`27`|Subproductos Pecuarios|`Preguntas`
23|`28`|Gastos en Actividades Pecuarias|`Preguntas`
24|`34`|Sumarias ( Variables Calculadas )|`Preguntas`
25|`37`|Programas Sociales (Miembros del Hogar)|`Preguntas`
26|`77`|Ingresos del Trabajador Independiente|`Preguntas`
27|`78`|Bienes y Servicios de Cuidados Personales|`Preguntas`
28|`84`|Participación Ciudadana|`Preguntas`
29|`85`|Gobernabilidad, Democracia y Transparencia|`Preguntas`

## I. Instalacion

#### Requerimientos
Para el correcto funcionamiento del paquete y sus respectivos modulos, es necesario tener instalado los siguientes paquetes adicionales:

- requests
- tqdm

#### Iniciamos la instalacion
```python
pip install enahodata
```

## II. Descripción de la libreria 

#### 1.- Importamos la libreria

```python
from enahodata import enahodata2 
import os
```

- En esta etapa importamos las librerias que se usaran, **enahodata** para extraer el comando **enahodata2**.
- También importamos **os** para manejar las carpetas.

#### 2.- Definimos el directorio de trabajo
```python
os.chdir("/path/to/your/directory")
```
- Usamos este código para definir el directorio de trabajo donde se trabajará.

#### 3.- Definimos los paramétros del comando **_enahodata2_**
El comando es enahodata2, y tiene los siguientes parametros:
```python
enahodata2(
    modulos: list[str]=["", "", "", ...],
    anios: list[str]=["", "", "", ...],
    descomprimir: bool = False,
    only_dta: bool = False
    overwrite: bool = False,
    output_dir: str = "NOMBRE_CARPETA",   
)
```
- **modulos:** en este parámetro ponemos la lista de modulos que se quiere descargar. Se puede extraer el codigo de la columna _Código Módulo_.
```python
enahodata2(
    modulos = ["01", "02", "03",...],
    ... 
)
```

- **anios:** en este parámetro se pone la lista de años.
```python
enahodata2(
    ...
    anios = ["2020", "2021", "2022",...]
    ...
)
```
- **descomprimir:** con esta opción se selecciona _True_ o _False_ para que se descomprima o no, respectivamente.
```python
enahodata2(
    ...
    descomprimir:bool = ...,
    ...
)
```
- **only_data:** con este parametro del comando seleccionamos si se enfocara solo en los archivos _.dta_ o no. Tiene dos valores _True_ o _False_.
```python
enahodata2(
    ...
    only_dta: bool = ...,
    ...
)
```
- **overwrite:** con esta opción se indica si se reemplaza los archivos ya existentes o no. Tiene dos valores _True_ o _False_.
```python
enahodata2(
    ...
    overwrite: bool = ...,
    ...
)
```
- **output_dir:** con este parámetro se indica el nombre que tendra la carpeta donde se almacenaran los archivos de los modulos descargados de la ENAHO. 
```python
enahodata2(
    ...
    output_dir: str = "NOMBRE_CARPETA",   
)
```


#### 4.- Plantilla completa

```python
from enahodata import enahodata2 
import os

os.chdir("/path/to/your/directory")

enahodata2(
    modulos = ["01", "02", "03",...],,
    anios = list[str],
    descomprimir = ...,
    only_dta = ...,
    overwrite = ...,
    output_dir = "NOMBRE_CARPETA",   
)

```

## III. Ejemplo práctico

Se necesita descargar de los años 2022 y 2023, los siguientes módulos de la Encuesta Nacional de Hogares de Perú:
- Características de la Vivienda y del Hogar
- Educación 
- Salud

Entonces, con la información anterior revisamos el codigo de cada modulo. En este caso los codigos son los siguientes:
- `01` : Características de la vivienda y del hogar
- `03` : Educación
- `04` : Salud

Luego, realizamos lo siguiente:
```python
pip install enahodata
```
En otro archivo `ejemplo.py`, por ejemplo escribimos el siguiente código:
```python
from enahodata import enahodata2
import os

os.chdir("C:\Users\Usuario\Desktop\ejemplo")

enahodata2(
  modulos=["01","03","04"],
  anios=["2022", "2023"],
  descomprimir=True,
  only_dta=True,
  overwrite=True, 
  output_dir="datos_ENAHO"
)

```
Ejecutamos el codigo:
```python
python ejemplo.py
```
![enahodata](https://raw.githubusercontent.com/JelsinPalomino/documentosCorreciones/refs/heads/main/img/resultados.PNG?token=GHSAT0AAAAAAC4F2OLINXKJJAG24YAUHBXWZ33L42Q)

Y se creara la siguiente estructura de carpetas, como resultado:

<img src="https://raw.githubusercontent.com/JelsinPalomino/documentosCorreciones/refs/heads/main/img/tree.PNG?token=GHSAT0AAAAAAC4F2OLJ24QPX6Q53NSYCRJCZ33L4OQ" width="210" height="">

Donde:
- **/modulo_01_2022_dta_only** 
- **/modulo_01_2023_dta_only** 
- **/modulo_03_2022_dta_only** 
- **/modulo_03_2023_dta_only** 
- **/modulo_04_2022_dta_only** 
- **/modulo_04_2023_dta_only** 
>Son las carpetas donde se encuentran los dataset en formato `.dta`

- **/modulo_01_2022_extract** 
- **/modulo_01_2023_extract** 
- **/modulo_03_2022_extract** 
- **/modulo_03_2023_extract** 
- **/modulo_04_2022_extract** 
- **/modulo_04_2023_extract** 

>En estas carpetas se encuentran, la información descomprimida de la ENAHO, con toda la información que viene desde el portal de microdatos del INEI.

## Licencia

Este repositorio esta autorizado bajo la licencia MIT. Ver LICENCIA para mas detalles.