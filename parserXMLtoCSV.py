# Parser para extraer del Corpus de Intervenciones Parlamentarias del Parlamento Andaluz
# los datos de los discursos de los diputados y convertirlos en un archivo CSV
# con las siguientes columnas:
# - Número diario
# - Tipo de sesión
# - Órgano
# - Fecha
# - Tipo de iniciativa
# - Materias
# - Extracto
# - Proponentes
# - Interviniente
# - Texto


import csv
import os
import xml.etree.ElementTree as ET
import re

def procesar_xml(archivo_xml, nombre_archivo):
    tree = ET.parse(archivo_xml)
    root = tree.getroot()

    numero_diario = root.findtext('.//numero_diario', default="")
    tipo_sesion = root.findtext('.//tipo_sesion', default="")
    organo = root.findtext('.//organo', default="")
    fecha = "{}-{}-{}".format(root.findtext('.//fecha/dia'), root.findtext('.//fecha/mes'), root.findtext('.//fecha/anio'))
    tipo_iniciativa = root.findtext('.//iniciativa/tipo_iniciativa', default="")
    materias = root.findtext('.//iniciativa/materias', default="")
    extracto = root.findtext('.//iniciativa/extracto', default="")
    proponentes = root.findtext('.//iniciativa/proponentes', default="")
    
    # En el corpus por diputado únicamente hay un interviniente por archivo
    patron_nombre = re.compile(r'^(.+)_[A-Z]+[0-9]+_[0-9]+')
    match = patron_nombre.match(nombre_archivo)
    if match:
        # El nombre y apellidos quedan en el primer grupo de la expresión regular
        interviniente = match.group(1)  
    else:
        # Por defecto, si no hay coincidencia, mantenemos el nombre del archivo
        interviniente = nombre_archivo  

    discursos = root.findall('.//iniciativa/intervencion/discurso/parrafo')

    # Concatenamos los párrafos de los discursos en un solo texto
    texto = " ".join([parrafo.text for parrafo in discursos if parrafo.text is not None])

    # Eliminamos saltos de línea y comillas dobles y devolvemos los datos en una lista
    return [numero_diario, tipo_sesion, organo, fecha, tipo_iniciativa, materias, extracto, proponentes, interviniente, texto.replace('\n', ' ').replace('"', "'")]

def main():
    # Epecificar la ruta al directorio XML con el Corpus organizado por interviniente
    directorio_xml = 'diputados/'
    archivo_csv = 'intervenciones.csv'


    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file,delimiter='\t')
        writer.writerow(["numero_diario", "tipo_sesion", "organo", "fecha", "tipo_iniciativa", "materias", "extracto", "proponentes", "interviniente", "texto"])

        for filename in os.listdir(directorio_xml):
            if filename.endswith('.xml'):
                archivo_xml = os.path.join(directorio_xml, filename)
                nombre = os.path.splitext(filename)[0]
                fila_csv = procesar_xml(archivo_xml, nombre)
                writer.writerow(fila_csv)

if __name__ == "__main__":
    main()
