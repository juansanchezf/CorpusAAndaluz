import pandas as pd
import argparse

def limpiar_intervenciones(archivo_entrada):
    print(f'Leyendo archivo {archivo_entrada} y limpiando')
    df = pd.read_csv(archivo_entrada, delimiter='\t')
    df['dia'] = df['fecha'].apply(lambda x: x.split('-')[0])
    df['mes'] = df['fecha'].apply(lambda x: x.split('-')[1])
    df['año'] = df['fecha'].apply(lambda x: x.split('-')[2])
    df['mes'] = df['mes'].apply(lambda x: x.replace('enero', '1'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('febrero', '2'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('marzo', '3'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('abril', '4'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('mayo', '5'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('junio', '6'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('julio', '7'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('agosto', '8'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('septiembre', '9'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('octubre', '10'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('noviembre', '11'))
    df['mes'] = df['mes'].apply(lambda x: x.replace('diciembre', '12'))

    df = df.drop(columns=['fecha','numero_diario','tipo_sesion', 'organo', 'tipo_iniciativa', 'materias', 'extracto', 'proponentes'])
    df = df[df['texto'].apply(type) != float]
    df.to_csv('intervenciones_limpias.csv', sep='\t', index=False)

    # Eliminar aquellas intervenciones cuyo valor de texto es NaN

    print(f'Archivo limpio guardado como intervenciones_limpias.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Elimina las columnas no necesarias para el análisis.')
    parser.add_argument('archivo_entrada', type=str, help='Archivo CSV de entrada con las intervenciones')
    args = parser.parse_args()

    limpiar_intervenciones(args.archivo_entrada)
