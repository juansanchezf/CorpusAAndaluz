import pandas as pd
import argparse

def eliminar_pequenios(archivo_entrada):
    df = pd.read_csv(archivo_entrada, delimiter='\t')
    intervenciones = df.groupby('interviniente').size()

    print(f'Existen {len(intervenciones)} intervinientes en el corpus')
    print(f'Eliminando intervinientes con menos de 10 intervenciones')

    intervenciones = intervenciones[intervenciones >= 10]
    print(f'Quedan {len(intervenciones)} intervinientes con más de 10 intervenciones en el corpus')
    df = df[df.interviniente.isin(intervenciones.index)]

    archivo_salida = 'intervenciones_filtradas.csv'
    df.to_csv(archivo_salida, sep='\t', index=False)
    print(f'Archivo filtrado guardado como {archivo_salida}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filtra intervinientes con menos de 10 intervenciones.')
    parser.add_argument('archivo_entrada', type=str, help='Archivo CSV de entrada con las intervenciones')
    args = parser.parse_args()

    eliminar_pequenios(args.archivo_entrada)
