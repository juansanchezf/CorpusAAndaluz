import pandas as pd
import csv
import xml.etree.ElementTree as ET
import re
import os
import unicodedata
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn import metrics
from sklearn.utils import resample
import shutil
import argparse


def procesar_etiq_intervienen(etiq_intervienen):
    if etiq_intervienen is not None:
        texto_intervienen = etiq_intervienen.text
    else:
        texto_intervienen = ""
        print("No hay diputados que intervengan en la iniciativa")
    nombre_completo_pattern = r'(D\.\s|Dña\.\s)([^,]+)'
    matches = re.findall(nombre_completo_pattern, texto_intervienen)
    nombres_completos = []
    
    for prefix, nombre_completo in matches:
        nombre_completo = nombre_completo.strip()
        nombre_limpio =  nombre_completo.upper().replace("-", "--")
        nombre_limpio =  nombre_limpio.replace(" ", "-")
        nombre_limpio = nombre_limpio.replace("\n", " ").replace("\r", " ").strip()
        nombres_completos.append(nombre_limpio)
    return nombres_completos

def comprobar_compuesto(nombre):
    palabras = nombre.split("-")
    extraer = palabras.count("") + 2
    palabras = [palabra for palabra in palabras if palabra]
    apellidos = "-".join(palabras[-(extraer):])

    return apellidos

def obtener_apellidos_guiones(root):
    etiq_intervienen = root.find('.//intervienen')
    nombres_completos = procesar_etiq_intervienen(etiq_intervienen)
    nombres_completos = eliminar_punto_final(nombres_completos)
    etiq_presidente = root.find('.//presidente')
    nombre_presidente = procesar_etiq_presidente(etiq_presidente)

    if nombre_presidente is not None and nombre_presidente not in nombres_completos and comprobar_presidente(root):
        nombres_completos.append(nombre_presidente)

    nombres_completos = eliminar_punto_final(nombres_completos)
    nombres_completos_limpios = [limpiar_nombre(nombre) for nombre in nombres_completos]
    apellidos = [comprobar_compuesto(nombre) for nombre in nombres_completos_limpios]

    return apellidos

def procesar_etiq_presidente(etiq_presidente):
    if etiq_presidente is not None:
        texto_presidente = etiq_presidente.text.strip()
        presidente_nombre_pattern = r'(Excma\.|Excmo\.|Ilmo.|Ilma.)\s(Sr\.|Sra\.)\s(Dña\.|D\.)\s([\w\s\.]+)'
        match = re.search(presidente_nombre_pattern, texto_presidente)
        if match:
            nombre_presidente = match.group(4).strip().upper().replace(" ", "-")
            return nombre_presidente
        else:
            print("No se ha encontrado el nombre del presidente/a")
            return None
    else:
        print("No hay presidente/a en la iniciativa")
        return None
    
def eliminar_punto_final(nombres):
    nombres_sin_punto = []
    for nombre in nombres:
        if nombre.endswith("."):
            nombre = nombre[:-1]
        nombres_sin_punto.append(nombre)
    return nombres_sin_punto

def comprobar_presidente(root):
    etiq_presidente = root.find('.//presidente')
    if etiq_presidente is not None:
        texto_presidente = etiq_presidente.text.strip()
        presidente_nombre_pattern = r'(Excma\.|Excmo\.|Ilmo.|Ilma.)\s(Sr\.|Sra\.)\s(Dña\.|D\.)\s([\w\s\.]+)'
        match = re.search(presidente_nombre_pattern, texto_presidente)
        if match:
            nombre_presidente_comprobar = match.group(4)

    palabras = nombre_presidente_comprobar.split()
    nombre_presidente_comprobar = " ".join(palabras[-2:]).upper()

    if nombre_presidente_comprobar:
        for intervencion in root.findall('.//intervencion'):
            if intervencion is not None:
                interviniente = intervencion.find('.//interviniente')
                palabras = interviniente.text.split()
                nombre = " ".join(palabras[2:4]).upper()
                nombre = nombre.replace(".", "")
                nombre = nombre.replace(",", "")
                if nombre == nombre_presidente_comprobar:
                    return True

def comprobar_intervinientes(root, apellidos):
    for intervencion in root.findall('.//intervencion'):
        if intervencion is not None:
            nombre = intervencion.find('.//interviniente').text
            patron_interviniente = r'^(El señor|La señora)\s+'
            nombre = re.sub(patron_interviniente, '', nombre)
            nombre = nombre.split(',')[0]
            nombre = '-'.join(nombre.split())
            nombre = limpiar_nombre(nombre)
            
            if nombre not in apellidos:
                apellidos.append(nombre)

def normalizar_tildes(text):
    if isinstance(text, str):
        return unicodedata.normalize('NFC', text)
    return text

def limpiar_nombre(nombre_completo):
    particulas = ['DEL', 'DE', 'LA', 'LOS', 'LAS', 'Y']
    patron_particulas = r'\b(?:' + '|'.join(particulas) + r')\b'
    nombre_limpio = re.sub(patron_particulas, ' ', nombre_completo)
    nombre_limpio = re.sub(r'- - -', '-', nombre_limpio)
    nombre_limpio = re.sub(r'- -', '-', nombre_limpio)
    nombre_limpio = nombre_limpio.strip('-')

    palabras = nombre_limpio.split('-')
    if palabras[0] == '' or palabras[0] == ' ':
        palabras.pop(0)
    nombre_limpio = '-'.join(palabras)
    return nombre_limpio

def preparar_datos(diccionario):
    textos = []
    autores = []
    for autor, lista_textos in diccionario.items():
        for texto in lista_textos:
            textos.append(preprocesar_texto(texto))
            autores.append(autor)
    return textos, autores

def segmentar_texto(texto):
    # Usar una expresión regular para dividir el texto en segmentos basados en las etiquetas
    segmentos = re.split(r'<<INTERVENCIÓN_FIN>>', texto)
    # Limpiar y procesar cada segmento
    segmentos_limpios = [preprocesar_texto(segmento.replace('<<INTERVENCIÓN_INICIO>>', '').strip()) for segmento in segmentos if segmento.strip()]

    return segmentos_limpios

def obtener_apellidos_limpios(nombre):
    nombre = limpiar_nombre(nombre)
    palabras = nombre.split()
    nombre = " ".join(palabras[2:4]).upper()
    nombre = nombre.replace(".", "")
    nombre = nombre.replace(",", "")
    nombre = nombre.replace(" ", "-")
    
    return nombre

def limpiar_texto(texto):
    """
    Eliminamos caractesres especiales del texto de intervención 
    como guiones, comillas o corchetes.
    """
    # Eliminar carácteres especiales
    texto = texto.replace('…', '')
    texto = texto.replace('-', '')
    texto = texto.replace('–', '')
    texto = texto.replace('—', '')
    texto = texto.replace('•', '')
    texto = texto.replace('“', '')
    texto = texto.replace('”', '')
    texto = texto.replace('‘', '')
    texto = texto.replace('’', '')
    texto = texto.replace('...', '')

    # Eliminar texto entre corchetes
    texto = re.sub(r'\[.*?\]', '', texto)

    # Eliminar espacios en blanco
    texto = ' '.join(texto.split())
    return texto

def preprocesar_texto(texto):
    """
    Preprocesado sencillo del texto
    """
    texto = texto.lower()  # Convertir a minúsculas
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar puntuación
    texto = ' '.join(texto.split())  # Eliminar espacios extra
    return texto

def procesar_archivo(path):
    tree = ET.parse(path)
    root = tree.getroot()
    etiq_intervienen = root.find('.//intervienen')
    nombres_completos = procesar_etiq_intervienen(etiq_intervienen)
    etiq_presidente = root.find('.//presidente')
    nombre_presidente = procesar_etiq_presidente(etiq_presidente)

    if nombre_presidente is not None and nombre_presidente not in nombres_completos and comprobar_presidente(root):
        nombres_completos.append(nombre_presidente)

    nombres_completos = eliminar_punto_final(nombres_completos)
    apellidos = obtener_apellidos_guiones(root)

    comprobar_intervinientes(root, apellidos)

    texto_completo = []

    # Para cada intervención y cada párrafo obtenemos el texto limpio
    for intervencion in root.findall('.//intervencion'):
        texto_intervencion = []
        for parrafo in intervencion.findall('.//parrafo'):
            if parrafo.text:
                texto_intervencion.append(limpiar_texto(parrafo.text))
        texto_intervencion = " ".join(texto_intervencion)

        # Solo añade los textos con más de 300 carácteres, lo que equivale a unas 60 palabras
        if len(texto_intervencion) > 300:
            texto_completo.append("<<INTERVENCIÓN_INICIO>> " + texto_intervencion + " <<INTERVENCIÓN_FIN>>")

    texto_completo = '\n'.join(texto_completo)

    # Lo primero que haremos es cargar nuestro dataset con todas las intervenciones totales
    df = pd.read_csv('/Users/juan/Desktop/TFG/code/datasets/diputados/diputados_dip/intervenciones_filtradas_menos10.csv', delimiter='\t')
    
    # Eliminamos todas las columnas menos interviniente, texto y numero_diario
    df = df.drop(columns=['tipo_sesion', 'organo', 'fecha', 'tipo_iniciativa', 'materias','extracto', 'proponentes'])
    
    # Normalizar las tildes de nombres_completos
    df['interviniente'] = df['interviniente'].apply(normalizar_tildes)
    nombres_completos = [normalizar_tildes(nombre) for nombre in nombres_completos]

    # Limpiar los nombres completos
    nombres_completos = [limpiar_nombre(nombre) for nombre in nombres_completos]

    # Almacenamos el numero de la iniciativa que estamos clasificando
    numero_iniciativa = root.find('.//numero_diario').text

    # Creamos un diccionario con los textos de cada interviniente
    dic_textos = {interviniente: [] for interviniente in nombres_completos}

    # Añadimos los textos al diccionario
    for index, row in df.iterrows():
        autor = row['interviniente']
        texto = row['texto']
        numero_diario = str(row['numero_diario'])

        # Si el autor está en el diccionario y la intervención no es de la misma iniciativa
        if autor in dic_textos and numero_iniciativa != numero_diario:
            dic_textos[autor].append(texto)

    # Limpiamos los textos 
    for autor in dic_textos:
        dic_textos[autor] = [
            limpiar_texto(texto) 
            if not (isinstance(texto, float) and math.isnan(texto)) 
            else None 
            for texto in dic_textos[autor]
        ]
        dic_textos[autor] = [texto for texto in dic_textos[autor] if texto is not None]

    textos, autores = preparar_datos(dic_textos)

    # Creamos un dataframe a partir de los textos y autores
    new_df = pd.DataFrame({'texto': textos, 'autor': autores})

    # Balanceamos el conjunto de datos
    min_count = new_df['autor'].value_counts().min()

    # Almaceno el numero de autores en new_df
    if min_count < len(new_df['autor'].unique()):
        min_count = len(new_df['autor'].unique())

    df_balanceado = pd.DataFrame()
    for autor in new_df['autor'].unique():
        df_author = new_df[new_df['autor'] == autor]
        if len(df_author) < min_count:
            df_author_resampled = resample(df_author, replace=True, n_samples=min_count, random_state=42)
        else:
            df_author_resampled = resample(df_author, replace=False, n_samples=min_count, random_state=42)
        
        df_balanceado = pd.concat([df_balanceado, df_author_resampled])

    X_train, X_test, y_train, y_test = train_test_split(df_balanceado['texto'], df_balanceado['autor'], test_size=0.2,stratify=df_balanceado['autor'] ,random_state=42)


    # Crear y entrenar el modelo 
    modelo = make_pipeline(TfidfVectorizer(), 
                           LogisticRegression(multi_class='multinomial', dual=False))
    modelo.fit(X_train, y_train)

    # Predecir los autores de las intervenciones
    intervenciones_plano = segmentar_texto(texto_completo)
    atribuciones = []
    for intervencion in intervenciones_plano:
        if intervencion:
            autor_pred = modelo.predict([intervencion])[0]
            atribuciones.append((intervencion, autor_pred))

    # Calcular las métricas
    dic_atribuciones_ciertas = {}
    dic_atribuciones_ciertas = {autor: [] for autor in apellidos}


    for intervencion in root.findall('.//intervencion'):
        interviniente = intervencion.find('.//interviniente').text
        nombre = obtener_apellidos_limpios(interviniente)

        texto_intervencion = []
        for parrafo in intervencion.findall('.//parrafo'):
            if parrafo.text:
                texto_intervencion.append(parrafo.text)
        texto_intervencion = " ".join(texto_intervencion)
        texto_intervencion = limpiar_texto(texto_intervencion)
        texto_intervencion = preprocesar_texto(texto_intervencion)

        dic_atribuciones_ciertas[nombre].append(texto_intervencion)

    resultados = {autor: {'TP': 0, 'FP': 0, 'Parrafos': 0} for autor in apellidos}

    for atribucion in atribuciones:
        texto, autor  = atribucion
        autor = autor.split("-")
        autor = "-".join(autor[-2:])
        if autor in dic_atribuciones_ciertas and texto in dic_atribuciones_ciertas[autor]:
            resultados[autor]['TP'] += 1
        else:
            if autor in resultados:
                resultados[autor]['FP'] += 1

    return resultados


def procesar_carpeta(path):
    df_iniciativas = pd.DataFrame(columns=['iniciativa', 'num_intervinientes', 'TP', 'FP'])
    df_autores = pd.DataFrame(columns=['Autor', 'TP','FP'])
    iteracion = 0

    for archivo in os.listdir(path):
        if archivo.endswith('.xml'):
            print(f'Procesando archivo {iteracion}: {archivo}')
            path_completo = os.path.join(path, archivo)

            try:
                resultados = procesar_archivo(path_completo)

                num_intervinientes = len(resultados)
                TP_totales = sum([datos['TP'] for autor, datos in resultados.items()])
                FP_totales = sum([datos['FP'] for autor, datos in resultados.items()])
                
                nueva_iniciativa = {'iniciativa': archivo, 'num_intervinientes': num_intervinientes, 'TP': TP_totales, 'FP': FP_totales}
                print(f'Iniciativa: {archivo}')
                df_iniciativas.loc[len(df_iniciativas)] = nueva_iniciativa
                df_iniciativas = df_iniciativas.reset_index(drop=True)

                for autor, datos in resultados.items():
                    if autor in df_autores['Autor'].values:
                        df_autores.loc[df_autores['Autor'] == autor, 'TP'] += datos['TP']
                        df_autores.loc[df_autores['Autor'] == autor, 'FP'] += datos['FP']
                    else:
                        nuevo_autor = {'Autor': autor, 'TP': datos['TP'], 'FP': datos['FP']}
                        df_autores.loc[len(df_autores)] = nuevo_autor
                        df_autores = df_autores.reset_index(drop=True)

            except Exception as e:
                print(f'Error al procesar el archivo {archivo}: {e}')
                continue

            iteracion += 1
            print(f'Iteración {iteracion} completada')
        
    return df_iniciativas, df_autores

def guardarDFs(df_iniciativas, df_autores, output_path):
    df_iniciativas['parrafos'] = df_iniciativas['TP'] + df_iniciativas['FP']
    df_iniciativas['precision'] = df_iniciativas['TP'] / df_iniciativas['parrafos']

    # Fusionar el dataframe de diputados con el de nombres
    df_nombres = pd.read_csv('/Users/juan/Desktop/TFG/code/datasets/lista-dip.csv')
    df_nombres['apellidos'] = df_nombres['nombre'].apply(lambda x: '-'.join(x.split('-')[-2:]))
    df_autores['apellidos'] = df_autores['Autor'].apply(lambda x: '-'.join(x.split("-")[-2:]))

    df_intervenciones = pd.merge(df_autores, df_nombres, on='apellidos', how='inner')
    df_intervenciones = df_intervenciones.drop(columns=['apellidos', 'Autor'])
    df_intervenciones = df_intervenciones[['nombre', 'intervenciones', 'TP', 'FP']]
    df_intervenciones = df_intervenciones.reset_index(drop=True)
    df_intervenciones['precision'] = df_intervenciones['TP'] / (df_intervenciones['TP'] + df_intervenciones['FP'])
    df_intervenciones = df_intervenciones.rename(columns={'nombre': 'interviniente'})

    df_iniciativas.to_csv(output_path + "/iniciativas.csv", index=False)
    df_intervenciones.to_csv(output_path + "/intervenciones.csv", index=False)


    
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", help="Path a la carpeta con las iniciativas", required=True)
    parser.add_argument("--output_path", help="Path a la carpeta de salida", required=True)
    args = parser.parse_args()
    
    # Procesar la carpeta
    df_iniciativas, df_autores = procesar_carpeta(args.data_path)
    
    # Guardar los resultados
    guardarDFs(df_iniciativas, df_autores, args.output_path)
    
    