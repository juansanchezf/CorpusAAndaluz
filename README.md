# Repositorio de mi TFG sobre atribución de autoría

Este proyecto convierte el dataset del Parlamento Andaluz en un formato adecuado para su uso con el Benchmark **Valla** y también incluye un modelo para la atribución de iniciativas parlamentarias. A continuación se detallan los pasos necesarios para realizar la conversión y el uso de las funcionalidades del modelo de atribución.

## Requisitos Previos

- **Python 3.x**
- Las bibliotecas de Python necesarias: `pandas`, `regex`, `argparse`, `sklearn`, `os`, `logging`, `xml.etree.ElementTree`

## Pasos de Conversión

### Paso 1: Extraer Intervenciones de Documentos XML

El primer paso consiste en extraer las intervenciones de cada documento XML correspondiente a los intervinientes y convertirlas en un archivo CSV con una estructura específica.

El script `parserXMLtoCSV.py` realiza esta tarea. Este script:

- Lee archivos XML de un directorio especificado.
- Extrae datos específicos como número de diario, tipo de sesión, órgano, fecha, tipo de iniciativa, materias, extracto, proponentes, interviniente y el texto de las intervenciones.
- Combina los párrafos de discursos en un solo texto y elimina saltos de línea y comillas dobles para una mejor integridad del CSV.
- Genera un archivo `intervenciones.csv` con los datos organizados en las siguientes columnas: número de diario, tipo de sesión, órgano, fecha, tipo de iniciativa, materias, extracto, proponentes, interviniente y texto.

Para ejecutar este script, asegúrate de que los archivos XML estén en el directorio especificado en el script y luego ejecuta el siguiente comando:

```bash
python modeloAutores/parserXMLtoCSV.py
```

El script generará el archivo `intervenciones.csv` con todas las intervenciones de cada diputado en iniciativas concretas, organizadas línea por línea.

### Paso 2: Eliminar Intervinientes con Menos de 10 Intervenciones

Para filtrar los intervinientes que tienen menos de 10 intervenciones, ejecuta el siguiente script:

```bash
python modeloAutores/eliminar_pequenios.py modeloAutores/intervenciones.csv
```

Este paso generará el archivo `intervenciones_filtradas.csv`, eliminando a los intervinientes con menos de 10 intervenciones.

### Paso 3: Limpiar el Texto y Columnas Innecesarias

Para eliminar elementos no alfabéticos del texto y columnas no necesarias, utiliza el siguiente comando:

```bash
python modeloAutores/limpiar.py modeloAutores/intervenciones_filtradas.csv
```

Este comando creará el archivo `intervenciones_limpias.csv`, que contiene un dataset limpio y listo para su partición.

### Paso 4: Particionar el Dataset

El último paso es particionar el dataset en conjuntos de entrenamiento, validación y prueba:

```bash
python modeloAutores/particionEstratificada.py --dataset_path ./modeloAutores/intervenciones_limpias.csv --output_path split/
```

Esto generará los archivos particionados en la carpeta especificada (`split/`), adecuados para su uso con el software **Valla**.

## Atribución de Iniciativas Parlamentarias

Se ha añadido una nueva funcionalidad para la atribución de iniciativas parlamentarias, que permite extraer los textos presentes en una iniciativa y atribuirlos a su autor. Esta funcionalidad está contenida en la carpeta `modeloIniciativas`.

### Uso del Modelo de Atribución

Para utilizar el modelo de atribución de iniciativas, sigue los siguientes pasos:

1. **Ejecutar el Script de Modelo Individual**:

   - El script `modeloIndivdual.py` procesa un archivo XML de una iniciativa específica y predice los autores de las intervenciones. Para ejecutarlo, utiliza el siguiente comando:

   ```bash
   python modeloIniciativas/modeloIndivdual.py
   ```

   El script solicitará el nombre del archivo XML que deseas cargar. Asegúrate de que el archivo XML esté disponible en la ruta especificada en el script. Este script generará un modelo de atribución en base al documento CSV `intervenciones_filtradas.csv` y predecirá los autores de las intervenciones.

2. **Ejecutar el Script de Modelo de Iniciativas**:

   - El script `modeloIniciativas.py` procesa múltiples archivos XML y atribuye las intervenciones a sus respectivos autores. Este script requiere dos argumentos:

   - `--data_path`: Ruta a la carpeta que contiene los archivos XML de las iniciativas.
   - `--output_path`: Ruta a la carpeta donde se guardarán los resultados.

   Para ejecutarlo, utiliza el siguiente comando:

   ```bash
   python modeloIniciativas/modeloIniciativas.py --data_path /ruta/a/carpeta/iniciativas --output_path /ruta/a/carpeta/salida
   ```

   Este comando procesará todos los archivos XML en la carpeta especificada en `--data_path` y guardará los resultados en la carpeta especificada en `--output_path`.

3. **Analizar Resultados**:
   - El script `analisis.ipynb` contiene un análisis exploratorio de los resultados obtenidos con el modelo de atribución masiva. Puedes abrir y ejecutar este Jupyter Notebook para visualizar y analizar los resultados obtenidos.

### Ejemplo de Uso

Para utilizar el modelo con un archivo XML de ejemplo llamado `DSCA080023_1.xml`, coloca el archivo en la ruta especificada y ejecuta:

```bash
python modeloIniciativas/modeloIndivdual.py
```

Ingrese `DSCA080023_1.xml` cuando se le solicite. El modelo procesará el archivo y mostrará los resultados de atribución.

Para la ejecución del modelo masivo y con el objetivo de procesar múltiples archivos XML en una carpeta llamada `iniciativas` y guardar los resultados en una carpeta llamada `resultados`, ejecuta:

```bash
python modeloIniciativas/modeloIniciativas.py --data_path /ruta/a/iniciativas --output_path /ruta/a/resultados
```

## Estructura del Proyecto tras la ejecución de los scripts

```
.
├── README.md
├── modeloAutores
│   ├── eliminar_pequenios.py
│   ├── intervenciones.csv
│   ├── intervenciones_filtradas.csv
│   ├── limpiar.py
│   ├── parserXMLtoCSV.py
│   ├── split/
│   │   ├── diputados_train.csv
│   │   ├── diputados_AA_val.csv
│   │   └── diputados_AA_test.csv
│   └── particionEstratificada.py
└── modeloIniciativas
    ├── analisis.ipynb
    ├── modeloIndivdual.py
    └── modeloIniciativas.py
```

## Notas

- Asegúrate de tener todos los archivos XML en la misma carpeta que `parserXMLtoCSV.py` antes de iniciar el proceso.
- La carpeta `split/` debe existir o será creada automáticamente durante la partición.
- Revisa los archivos generados en cada paso para asegurar la calidad del procesamiento.
- Para utilizar la nueva funcionalidad de atribución de iniciativas, asegúrate de tener los archivos XML correspondientes en una sola carpeta y modificar la ruta a dicha carpeta en `modeloIniciativas.py`.

## Contacto

Para más información, puedes contactar con:

- **Nombre**: Juan Sánchez Fernández
- **Email**: j.sanchezfedez@gmail.com
