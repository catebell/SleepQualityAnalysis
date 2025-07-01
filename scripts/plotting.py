#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, date, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
import os  # usare subprocess che è più sicuro !!!
import pandas as pd
import numpy as np
import time as chronometer


def plots(file):
    start = chronometer.time()
    dir_name = "temp-plot"  # DEFINE plot type (dir-to-save name) here
    if not os.path.isdir(os.path.join(dir_name)):
        os.mkdir(dir_name)
    if not os.path.isdir(os.path.join(dir_name, file[:-4])):
        os.mkdir(os.path.join(dir_name, file[:-4]))

        print(f"PLOTTING FOR {file}...")
        mpl.use("Agg")
        mpl.pyplot.rcParams["figure.figsize"] = [7.50, 3.50]
        mpl.pyplot.rcParams["figure.autolayout"] = True
        # temp = pd.DataFrame()
        filepath = os.path.join("nights", f"{file}.gz")
        std = pd.read_csv(
            filepath, header=0, index_col="time", parse_dates=True
        )  # usecols=['time','acc-std-dev']
        # temp = pd.read_csv(
        #     filepath, header=0, index_col="time", usecols=["time", "temp"],
        #     parse_dates=True
        # )
        print("done loading")
        year, month, day = tuple(list(map(int, (file[:10].split("_")))))
        d = date(year, month, day)
        delta = timedelta(1)
        mpl.pyplot.ioff()

        for i in range(6):
            try:
                d2 = d + delta
                ax1 = mpl.pyplot.subplot()
                ax1.set_xlim(
                    datetime.fromisoformat(f"{d} 21:00"),
                    datetime.fromisoformat(f"{d2} 09:00"),
                )
                date_form = mpl.dates.DateFormatter("%H")
                ax1.xaxis.set_major_formatter(date_form)
                ax1.set_ylim(0, 10)
                ax1.set_ylabel("light(C°)")  # DEFINE ax1 y_label
                (l1,) = ax1.plot(std["light"], color="orange")  # DEFINE ax1 data to plot
                ax2 = ax1.twinx()
                # ax2.set_ylim(0,0.4)
                ax2.set_ylabel("angle standard deviation")  # DEFINE ax2 y_label
                (l2,) = ax2.plot(std["ang-std-dev"], color="black")  # DEFINE ax2 data to plot
                ax1.legend([l1, l2], ["light", "ang-std-dev"], loc="upper right")  # DEFINE legend
                print(f"saving night between {d} and {d2}")
                mpl.pyplot.savefig(os.path.join(dir_name, file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
                d = d2
                mpl.pyplot.cla()
                mpl.pyplot.clf()
                mpl.pyplot.close("all")
            except Exception as e:
                print("EXCEPTION: " + str(e))
    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_x_y_z(file):
    print(f"PLOTTING x, y, z, acc-std-dev FOR {file}...")
    start = chronometer.time()

    if not os.path.isdir(os.path.join("plots_xyz_variations")):
        os.mkdir("plots_xyz_variations")
    if not os.path.isdir(os.path.join("plots_xyz_variations", file[:-4])):
        os.mkdir(os.path.join("plots_xyz_variations", file[:-4]))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    filepath = os.path.join("nights", f"{file}.gz")
    df = pd.read_csv(filepath, header=0, index_col="time", parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta

            ax = plt.subplot()
            ax.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            date_form = mpl.dates.DateFormatter("%H")
            ax.xaxis.set_major_formatter(date_form)

            ax.set_ylim(-3, 3)
            (l1,) = ax.plot(df['x'], color="lightgreen")  # DEFINE x data to plot
            (l2,) = ax.plot(df['y'], color="lightcoral")  # DEFINE y data to plot
            (l3,) = ax.plot(df['z'], color="lightblue")  # DEFINE z data to plot
            (l4,) = ax.plot(df['acc-std-dev'], color="black")
            ax.legend([l1, l2, l3, l4], ['x', 'y', 'z', 'acc-std-dev'], loc="upper right")  # DEFINE legend
            print(f"saving night between {d} and {d2}")
            plt.savefig(os.path.join("plots_xyz_variations", file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
            d = d2
            plt.cla()
            plt.clf()
            plt.close("all")
        except Exception as e:
            print("EXCEPTION: " + str(e))

    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_norm(file):
    print(f"PLOTTING norm, acc-std-dev FOR {file}...")
    start = chronometer.time()

    if not os.path.isdir(os.path.join("plots_norm_variations")):
        os.mkdir("plots_norm_variations")
    if not os.path.isdir(os.path.join("plots_norm_variations", file[:-4])):
        os.mkdir(os.path.join("plots_norm_variations", file[:-4]))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    filepath = os.path.join("nights", f"{file}.gz")
    df = pd.read_csv(filepath, header=0, index_col="time", parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta

            ax = plt.subplot()
            ax.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                        timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_form)

            ax.set_ylim(0, 3)
            (l1,) = ax.plot(df['norm'], color="grey")
            (l2,) = ax.plot(df['acc-std-dev'], color="black")
            plt.yticks(np.arange(0, 3, 0.1))
            plt.grid()
            ax.legend([l1, l2], ['norm', 'acc-std-dev'], loc="upper right")
            print(f"saving night between {d} and {d2}")
            plt.savefig(os.path.join("plots_norm_variations", file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
            d = d2
            plt.cla()
            plt.clf()
            plt.close("all")
        except Exception as e:
            print("EXCEPTION: " + str(e))

    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_angle(file):
    print(f"PLOTTING angle, ang-std-dev FOR {file}...")
    start = chronometer.time()

    if not os.path.isdir(os.path.join("plots_angle_variations")):
        os.mkdir("plots_angle_variations")
    if not os.path.isdir(os.path.join("plots_angle_variations", file[:-4])):
        os.mkdir(os.path.join("plots_angle_variations", file[:-4]))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    filepath = os.path.join("nights", f"{file}.gz")
    df = pd.read_csv(filepath, header=0, index_col="time", parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta

            ax = plt.subplot()
            ax.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                        timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_form)

            ax.set_ylim(-100, 100)
            (l1,) = ax.plot(df['angle'], color="pink")
            (l2,) = ax.plot(df['ang-std-dev'], color="red")
            plt.yticks(np.arange(-100, 100, 5))
            plt.grid()
            ax.legend([l1, l2], ['angle', 'ang-std-dev'], loc="upper right")
            print(f"saving night between {d} and {d2}")
            plt.savefig(os.path.join("plots_angle_variations", file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
            d = d2
            plt.cla()
            plt.clf()
            plt.close("all")
        except Exception as e:
            print("EXCEPTION: " + str(e))

    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_light_temp(file):
    print(f"PLOTTING light, temperature FOR {file}...")
    start = chronometer.time()

    if not os.path.isdir(os.path.join("plots_light_temp")):
        os.mkdir("plots_light_temp")
    if not os.path.isdir(os.path.join("plots_light_temp", file[:-4])):
        os.mkdir(os.path.join("plots_light_temp", file[:-4]))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    filepath = os.path.join("nights", f"{file}.gz")
    df = pd.read_csv(filepath, header=0, index_col="time", parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta
            ax1 = mpl.pyplot.subplot()
            ax1.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                        timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax1.xaxis.set_major_formatter(date_form)
            ax1.set_ylim(5, 15)
            ax1.set_ylabel("Light")
            (l1,) = ax1.plot(df['light'], color="orange")
            ax2 = ax1.twinx()
            ax2.set_ylim(20, 40)
            ax2.set_ylabel("Temperature (°C)")
            (l2,) = ax2.plot(df['temp '], color="purple")
            ax1.legend([l1, l2], ["light", "temp"], loc="upper right")
            print(f"saving night between {d} and {d2}")
            mpl.pyplot.savefig(os.path.join("plots_light_temp", file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
            d = d2
            mpl.pyplot.cla()
            mpl.pyplot.clf()
            mpl.pyplot.close("all")
        except Exception as e:
            print("EXCEPTION: " + str(e))

    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_theta_fi(file):
    print(f"PLOTTING theta, fi FOR {file}...")
    start = chronometer.time()

    if not os.path.isdir(os.path.join("plots_theta_fi")):
        os.mkdir("plots_theta_fi")
    if not os.path.isdir(os.path.join("plots_theta_fi", file[:-4])):
        os.mkdir(os.path.join("plots_theta_fi", file[:-4]))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    filepath = os.path.join("nights", f"{file}.gz")
    df = pd.read_csv(filepath, header=0, index_col="time", parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta
            ax1 = mpl.pyplot.subplot()
            ax1.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                        timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax1.xaxis.set_major_formatter(date_form)
            # ax1.set_ylim(5, 15)
            ax1.set_ylabel("Theta")
            (l1,) = ax1.plot(df['theta'], color="cyan")
            ax2 = ax1.twinx()
            # ax2.set_ylim(20, 40)
            ax2.set_ylabel("Fi")
            (l2,) = ax2.plot(df['fi'], color="salmon")
            ax1.legend([l1, l2], ["theta", "fi"], loc="upper right")
            print(f"saving night between {d} and {d2}")
            mpl.pyplot.savefig(os.path.join("plots_theta_fi", file[:-4], f"{file[:-4]}notte{d}-{d2}.png"))
            d = d2
            mpl.pyplot.cla()
            mpl.pyplot.clf()
            mpl.pyplot.close("all")
        except Exception as e:
            print("EXCEPTION: " + str(e))

    print(f"DONE PLOTTING in: {(chronometer.time() - start) / 60} minutes")


def plot_features(file):
    print(f"PLOTTING acc_dev_std, iqr FOR {file}.csv...")
    start_plot = chronometer.time()

    if not os.path.isdir(os.path.join("plots_features")):
        os.mkdir("plots_features")
    if not os.path.isdir(os.path.join("plots_features", file)):
        os.mkdir(os.path.join("plots_features", file))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    df_plot = pd.read_csv(os.path.join("engineered_features", f"{file}.csv"), header=0, index_col="datetime",
                          parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta

            ax = plt.subplot()
            ax.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                               timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_form)

            (l1,) = ax.plot(df_plot['acc_dev_std'], color="black")
            # to set ax scale range and scale:
            ax.set_ylim(0, 0.5)
            plt.yticks(np.arange(0, 0.5, 0.1))
            plt.grid()
            # to have axes with different scales:
            ax.set_ylabel("acc_dev_std")  # set first feature label
            ax2 = ax.twinx()
            ax2.set_ylabel("iqr")  # set second feature label
            ax2.set_ylim(0, 0.5)  # limit for second feature
            (l2,) = ax2.plot(df_plot['iqr'], color="violet")  # [if this active, comment following line, and vice-versa]
            # (l2,) = ax.plot(df_plot['iqr'], color="red")
            ax.legend([l1, l2], ['acc_dev_std', 'iqr'], loc="upper right")
            print(f"saving night between {d} and {d2}")
            plt.savefig(os.path.join("plots_features", file, f"{file}night{d}-{d2}.png"))
            d = d2
            plt.cla()
            plt.clf()
            plt.close("all")
        except Exception as ex:
            print("EXCEPTION: " + str(ex))

    print(f"DONE PLOTTING in: {(chronometer.time() - start_plot) / 60} minutes")


# initial plot
'''''
def plot_features(file):
    print(f"PLOTTING acc_dev_std, ang_dev_std FOR {file}.csv...")
    start_plot = chronometer.time()

    if not os.path.isdir(os.path.join("plots_features")):
        os.mkdir("plots_features")
    if not os.path.isdir(os.path.join("plots_features", file)):
        os.mkdir(os.path.join("plots_features", file))

    mpl.use("Agg")
    plt.rcParams["figure.figsize"] = [15, 7]
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams['lines.linewidth'] = 1
    df_plot = pd.read_csv(os.path.join("engineered_features", f"{file}.csv"), header=0, index_col="datetime",
                          parse_dates=True)
    print("done loading")
    year, month, day = tuple(list(map(int, (file[:10].split("_")))))
    d = date(year, month, day)
    delta = timedelta(1)
    plt.ioff()

    for i in range(6):
        try:
            d2 = d + delta

            ax = plt.subplot()
            ax.set_xlim(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"))
            plt.xticks(mpl.dates.drange(datetime.fromisoformat(f"{d} 21:00"), datetime.fromisoformat(f"{d2} 09:00"),
                                               timedelta(hours=1)))
            date_form = mpl.dates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_form)

            (l1,) = ax.plot(df_plot['acc_dev_std'], color="black")
            # to set ax scale range and scale:
            ax.set_ylim(0, 0.5)
            plt.yticks(np.arange(0, 0.5, 0.1))
            plt.grid()
            # to have axes with different scales:
            ax.set_ylabel("acc_dev_std")  # set first feature label
            ax2 = ax.twinx()
            ax2.set_ylim(0, 50)  # limit for ang_std_dev
            ax2.set_ylabel("ang_dev_std")  # set second feature label
            (l2,) = ax2.plot(df_plot['ang_dev_std'], color="red")  # [if this active, comment following line]
            # (l2,) = ax.plot(df_plot['iqr'], color="red")
            ax.legend([l1, l2], ['acc_dev_std', 'ang_dev_std'], loc="upper right")
            print(f"saving night between {d} and {d2}")
            plt.savefig(os.path.join("plots_features", file, f"{file}night{d}-{d2}.png"))
            d = d2
            plt.cla()
            plt.clf()
            plt.close("all")
        except Exception as ex:
            print("EXCEPTION: " + str(ex))

    print(f"DONE PLOTTING in: {(chronometer.time() - start_plot) / 60} minutes")
'''''