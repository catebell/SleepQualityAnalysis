#!/usr/bin/env python3
# coding: utf-8
import os
import pandas as pd
import numpy as np
import time as chronometer
from datetime import datetime


def parser(array):
    """
    funzione definita per essere usata come parser delle date,
    sostanzialmente trasforma stringhe in datetime ne ho definito uno
    custom perchè credo i braccialetti ogni tanto generino dei dati
    con orario ad esempio 01:01:60 dove per il software in realtà
    dovrebbe essere 01:02:00 visto che 60 secondi espliciti non hanno
    molto senso
    """
    try:
        dt = array.split(sep=" ")
        if len(dt) > 1:
            date = dt[0]
            time = dt[1]
        else:
            return "NaN"
        h, m, s = tuple((time.split(sep=":")))

    except ValueError:
        print(array)
    time = [h, m, s]
    for t in enumerate(time):
        if abs(float(t[1]) - 60) < 0.001:
            return "NaN"
    return datetime.fromisoformat(f"{date} {time[0]}:{time[1]}:{time[2]}")


def extract(file, values_to_extract):
    """
    Funzione per l'estrazione delle notti dai csv completi. Qui si
    scelgono inoltre i valori che vengono tenuti ed elaborati in
    qualche modo e che saranno poi inseriti in c30 e trasferiti in un
    file csv pronto ad essere plottato.  Sono abbastanza certo che per
    rendere tutto molto più efficiente sia in tempo che in spazio sia
    conveniente non salvare tutto su file per poi plottarlo ma farlo
    direttamente, per motivi di debugging era più semplice così in
    modo da poter avere un controllo su tutti i passaggi.
    """
    start = chronometer.time()
    filepath = os.path.join("nights", file)
    if not os.path.isfile(os.path.join("nights", f"{file}.gz")):
        print(f"EXTRACTING " + str(values_to_extract) + " FROM {file}...")

        for chunk in pd.read_csv(f"csvs/{file}.gz", header=0, chunksize=10000, index_col='time', parse_dates=True,
                                 date_parser=parser):
            # print(chunk.keys())  # -> key 'temp' is actually 'temp '
            chunk.dropna()
            try:
                c = chunk.between_time("21:00", "09:00")
                if not c.empty and len(c) > 1:
                    # print("CHUNK:\n" + str(c))
                    c = c.dropna()
                    c = c.sort_index()
                    c = c[c.index.notnull()]  # remove rows with null datetime (NaT)
                    epoch = "30s"  # scelta della durata dell'epoca della rolling window

                    # nella sezione di codice seguente si scelgono i
                    # dati da tenere e in che modo elaborarli prima di
                    # inserirli nella time-series vera e propria. Al
                    # momento è stato fatto in modo molto poco serio
                    # commentando e togliendo commenti, ovviamente se
                    # fosse necessario fare modifiche molto spesso si
                    # può fare di molto meglio inserendo dei parametri
                    # alla funzione.

                    c['temp '] = c['temp '].rolling(epoch).mean()
                    c['light'] = c['light'].rolling(epoch).mean()
                    # Funzione descritta nella documentazione di axivity su come ottenere i dati della
                    # luminostià nelle unità di misura corrette:
                    c['light'] = 10 * (c['light'] / 341)
                    # Funzione descritta nella documentazione di axivity su
                    # come ottenere i dati della temperatura in gradi Celsius:
                    #c['temp '] = (c['temp '] - 171) / 3.142

                    c['x'] = c['x'].rolling(epoch).mean()  # ax
                    c['y'] = c['y'].rolling(epoch).mean()  # ay
                    c['z'] = c['z'].rolling(epoch).mean()  # az
                    c['norm'] = np.sqrt(np.square(c[['x', 'y', 'z']]).sum(axis=1))

                    # Funzione per ricavare l'angolo tra z (l'asse perpendicolare alla pelle) e il terreno,
                    # descritta nel paper di Van Hees(2015):
                    c['angle'] = (np.arctan(c['z'] / np.sqrt(np.square(c[["x", "y"]]).sum(axis=1))) * 180 / np.pi)
                    c['acc-std-dev'] = c['norm'].rolling(epoch).std()
                    c['ang-std-dev'] = c['angle'].rolling(epoch).std()

                    # COORDINATE POLARI (commentare le righe seguenti se non servono, rallentano il processo)
                    '''''
                    # r = distanza dal punto P = (x,y,z) dall'origine O
                    # c['r'] = c['norm']
                    # theta = angolo tra asse x>0 e la retta passante per O e Q (proiezione di P sul piano xy)
                    c['theta'] = None
                    # fi = colatitudine, angolo tra l'asse z>0 e la retta passante per O e P
                    c['fi'] = None

                    for index, row in c.iterrows():
                        if row['x'] != 0 or row['y'] != 0 or row['z'] != 0:
                            if row['x'] == 0:
                                if row['y'] > 0:
                                    c.at[index, 'theta'] = np.pi/2
                                elif row['y'] < 0:
                                    c.at[index, 'theta'] = 3 * np.pi/2
                                elif row['y'] == 0:
                                    print("(x,y,z) = (0,0,...), theta not defined")
                            elif row['x'] > 0 and row['y'] >= 0:
                                c.at[index, 'theta'] = np.arctan(row['y']/row['x'])
                            elif row['x'] > 0 > row['y'] or row['x'] < 0 < row['y']:
                                c.at[index, 'theta'] = np.arctan(row['y'] / row['x']) + 2 * np.pi
                            elif row['x'] < 0 and row['y'] <= 0:
                                c.at[index, 'theta'] = np.arctan(row['y']/row['x']) + np.pi

                            c.at[index, 'fi'] = np.arccos(row['z'] / row['norm'])
                        else:
                            print("x,y,z are (0,0,0), theta and fi not defined")
                        # FINE DELLA PARTE SULLE COORDINATE POLARI
                        '''''
                    c30 = c[values_to_extract]
                    if not os.path.isfile(filepath):
                        c30.to_csv(filepath)
                    else:
                        c30.to_csv(filepath, mode="a", header=False)
            except Exception as e:
                # pass
                print("EXCEPTION: " + str(e))
                # il pass commentato è presente per evitare la
                # stampa di un warning durante la conversione il
                # warning dice "index must be monotonic" è dovrebbe
                # essere segnalato solo quando il valore della
                # time-series usato come indice non è ordinato in
                # modo crescente, avendo io esplicitamente ordinato
                # l'indice nel codice credo sia un problema di
                # monotonia stretta/larga e non sembra causare
                # effettivamente problemi.
        os.system(f"gzip -f {filepath}")  # usare gzip.open !!!
        print(f"EXTRACTION DONE in: {(chronometer.time() - start) / 60} minutes")
