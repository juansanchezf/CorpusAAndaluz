import os
import regex as re
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import logging


def carga_dataset(path: str) -> pd.DataFrame:
    """
    Carga un dataset en formato csv
    """
    return pd.read_csv(path, delimiter='\t')


def asignar_id_autor(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Asigna un ID incremental a cada interviniente único y reestructura el DataFrame.
    """
    # Mapear cada interviniente a un ID único
    autor_id_map = {interv: idx for idx, interv in enumerate(
        dataset['interviniente'].unique())}
    dataset['author_id'] = dataset['interviniente'].map(autor_id_map)

    # Estructurar el DataFrame para tener autor_id y texto en columnas
    structured_data = dataset[['author_id', 'texto']]
    return structured_data


def preprocesar_texto(texto):
    texto = re.sub(r'^[-—–]\s*', '', texto)  # Eliminar el guion inicial
    texto = re.sub(r'\[.*?\]', '', texto)  # Eliminar texto entre corchetes
    # Eliminar guiones entre números (fechas)
    texto = re.sub(r'(?<=\d)[-—–](?=\d)', ' ', texto)
    # Eliminar guiones y rayas en todo el texto
    texto = re.sub(r'[-—–]\s*', '', texto)
    return texto.strip()


def split_dataset(dataset: pd.DataFrame):
    """
    Divide el dataset en train, validation y test
    """
    train_data, temp_data = train_test_split(
        dataset, test_size=0.3, random_state=42, stratify=dataset['author_id'])
    val_data, test_data = train_test_split(
        temp_data, test_size=0.5, random_state=42, stratify=temp_data['author_id'])

    return train_data, val_data, test_data


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Divide el dataset en train, validation y test')
    parser.add_argument('--dataset_path', type=str, default='/Users/juan/Desktop/TFG/code/divisiones/raw/intervenciones_limpio_mas50.csv',
                        help='Ruta del dataset a dividir')
    parser.add_argument('--output_path', type=str,
                        default='/Users/juan/Desktop/TFG/code/divisiones/processed', help='Ruta donde guardar los datasets divididos')

    argumentos = parser.parse_args()

    # Cargamos el dataset
    logging.info('Cargando el dataset...')
    dataset = carga_dataset(argumentos.dataset_path)

    logging.info('Asignando ID a los autores...')
    dataset = asignar_id_autor(dataset)

    # Preprocesamos el texto eliminando caracteres no deseados
    logging.info('Preprocesando el texto...')
    dataset['texto'] = dataset['texto'].apply(preprocesar_texto)

    # Dividimos el dataset
    logging.info('Dividiendo el dataset en train, validation y test...')
    train_data, val_data, test_data = split_dataset(dataset)

    # Guardamos los datasets
    logging.info('Guardando los datasets...')
    os.makedirs(argumentos.output_path, exist_ok=True)
    train_data.to_csv(os.path.join(argumentos.output_path,
                      'diputados_train.csv'), index=False)
    val_data.to_csv(os.path.join(argumentos.output_path,
                    'diputados_AA_val.csv'), index=False)
    test_data.to_csv(os.path.join(argumentos.output_path,
                     'diputados_AA_test.csv'), index=False)

    logging.info('Proceso finalizado')
