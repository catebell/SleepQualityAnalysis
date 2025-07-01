#!/usr/bin/env python3
# coding: utf-8

import os  # usare subprocess che è più sicuro !!!
import subprocess

from nights import extract
from plotting import plot_norm, plot_angle, plot_light_temp, plot_theta_fi, plot_x_y_z
import time

"""
1) convertire il .cwa (cartella 'data') in .csv (cartella 'csvs')
2) estrarre le notti dal .csv con cui sostituire i vecchi file csv
3) plottare
"""


def clear(filename):
    # os.remove(os.path.join("csvs", filename))
    os.remove(os.path.join("nights", f"{filename}.gz"))


for file in os.listdir("data"):
    if not os.path.isdir(os.path.join("csvs")):
        os.mkdir("csvs")

    start = time.time()
    filecsv = file[:-4] + ".csv"
    out = os.path.join("csvs", filecsv)

    # if there is no existing corresponding csv file, creates it:
    if not os.path.exists(f"{out}.gz"):
        print("file " + file + " to csv " + filecsv)
        print("CONVERTING .cwa into .csv...")
        # print(f"EXECUTING echo 'time,x,y,z,light,temp' > {out}")
        os.system(f"echo time,x,y,z,light,temp > {out}")
        print("DONE")
        # print(f"EXECUTING cwa-convert {os.path.join('data', file)} -light -tempc "f">> {out} 2> NUL")
        print("EXTRACTING DATA... (requires some time)")
        # if directory AX3-Utils-Win-3 not present, download cwa-convert e paste in the next line its path
        os.system(f"{os.path.join('../AX3-Utils-Win-3', 'cwa-convert.exe')}"
                  f" {os.path.join('data', file)} -light -tempc "f">> {out} 2> NUL")
        print("DONE\nCOMPRESSING...")
        os.system(f"gzip -f {out}")
        print("FINISHED COMPRESSING")

    print(f"{file} processed in: {(time.time() - start) / 60} minutes")

    # use and move up only blocks of code needed:
'''''

 # extract data we need from that defined in nights.py:
    if not os.path.exists(os.path.join("nights", f"{filecsv}.gz")):
        # extract(filecsv, ['x', 'y', 'z', 'norm', 'acc-std-dev', 'angle', 'ang-std-dev'])
        extract(filecsv, ['light', 'temp ', 'theta', 'fi'])

    if not os.path.exists(os.path.join("plots_light_temp", file[:-4])):
        # extract(filecsv, ['light', 'temp '])
        plot_light_temp(filecsv)
        # clear(filecsv)

    if not os.path.exists(os.path.join("plots_theta_fi", file[:-4])):
        # extract(filecsv, ['theta', 'fi'])
        plot_theta_fi(filecsv)
        # clear(filecsv)


    if not os.path.exists(os.path.join("plots_norm_variations", file[:-4])):
        # extract(filecsv, ['norm', 'acc-std-dev'])
        plot_norm(filecsv)
        # clear(filecsv)

    if not os.path.exists(os.path.join("plots_angle_variations", file[:-4])):
        # extract(filecsv, ['angle', 'ang-std-dev'])
        plot_angle(filecsv)
        # clear(filecsv)

    if not os.path.exists(os.path.join("plots_xyz_variations", file[:-4])):
        # extract(filecsv, ['x', 'y', 'z', 'acc-std-dev'])
        plot_x_y_z(filecsv)
        # clear(filecsv)
'''''
