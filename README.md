# Conversión del Dataset de Diputados Andaluces para Valla

Este proyecto convierte un dataset de diputados andaluces en un formato adecuado para su uso con el software **Valla**. A continuación se detallan los pasos necesarios para realizar la conversión.

## Requisitos Previos

- **Python 3.x**
- Las bibliotecas de Python necesarias: `pandas`, `regex`, `argparse`, `sklearn`, `os`, `logging`

## Pasos de Conversión

### Paso 1: Extraer Intervenciones de Documentos XML

El primer paso consiste en extraer las intervenciones de cada documento XML correspondiente a los intervinientes y convertirlas en un archivo CSV con una estructura específica.

El script `parserXMLtoCSV.py` realiza esta tarea. Este script:

- Lee archivos XML de un directorio especificado.
- Extrae datos específicos como número de diario, tipo de sesión, órgano, fecha, tipo de iniciativa, materias, extracto, proponentes, interviniente y el texto de las intervenciones.
- Combina párrafos de discursos en un solo texto y elimina saltos de línea y comillas dobles para una mejor integridad del CSV.
- Genera un archivo `intervenciones.csv` con los datos organizados en las siguientes columnas: número de diario, tipo de sesión, órgano, fecha, tipo de iniciativa, materias, extracto, proponentes, interviniente y texto.

Para ejecutar este script, asegúrate de que los archivos XML estén en un directorio llamado `diputados` y luego ejecuta el siguiente comando:

```bash
python parserXMLtoCSV.py
```

El script generará el archivo `intervenciones.csv` con todas las intervenciones de cada diputado en iniciativas concretas, organizadas línea por línea.

### Paso 2: Eliminar Intervinientes con Menos de 10 Intervenciones

Para filtrar los intervinientes que tienen menos de 10 intervenciones, ejecuta el siguiente script:

```bash
python eliminar_pequenios.py intervenciones.csv
```

Este paso generará el archivo `intervenciones_filtradas.csv`, eliminando a los intervinientes con menos de 10 intervenciones.

### Paso 3: Limpiar el Texto y Columnas Innecesarias

Para eliminar elementos no alfabéticos del texto y columnas no necesarias, utiliza el siguiente comando:

```bash
python limpiar.py intervenciones_filtradas.csv
```

Este comando creará el archivo `intervenciones_limpias.csv`, que contiene un dataset limpio y listo para su partición.

### Paso 4: Particionar el Dataset

El último paso es particionar el dataset en conjuntos de entrenamiento, validación y prueba:

```bash
python particionEstratificada.py --dataset_path ./intervenciones_limpias.csv --output_path split/
```

Esto generará los archivos particionados en la carpeta especificada (`split/`), adecuados para su uso con el software **Valla**.

## Estructura del Proyecto

```
.
├── parserXMLtoCSV.py
├── eliminar_pequenios.py
├── limpiar.py
├── particionEstratificada.py
├── intervenciones.csv
├── intervenciones_filtradas.csv
├── intervenciones_limpias.csv
├── split/
│   ├── diputados_train.csv
│   ├── diputados_AA_val.csv
│   ├── diputados_AA_test.csv
└── README.md
```

## Notas

- Asegúrate de tener todos los archivos XML en la misma carpeta que `parserXMLtoCSV.py` antes de iniciar el proceso.
- La carpeta `split/` debe existir o será creada automáticamente durante la partición.
- Revisa los archivos generados en cada paso para asegurar la calidad del procesamiento.

## Contacto

Para más información, puedes contactar con:

- **Nombre**: Juan Sánchez Fernández
- **Email**: j.sanchezfedez@gmail.com
