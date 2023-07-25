import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import RPi.GPIO as GPIO
import serial
import csv

from . import *


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Total Alkalinity")
        self.geometry("1200x500")

        self.option_add("*font", "Arial 13")

        MassLabel = tk.Label(self, text="Insert initial Mass (g): ", padx=20)
        self.Input1 = tk.Entry(self, width=10)
        TemperatureLabel = tk.Label(self, text="Insert temperature (C): ", padx=20)
        self.Input2 = tk.Entry(self, width=10)
        SalinityLabel = tk.Label(self, text="Insert sample salinity (S): ", padx=20)
        self.Input3 = tk.Entry(self, width=10)
        TALabel = tk.Label(self, text="Total Alkalinity (umol/kg): ", padx=20)
        self.Output = tk.Entry(self, width=10)
        self.StartButton = tk.Button(
            self, text="Start", bg="green", padx=20, command=self.start
        )
        ExitButton = tk.Button(
            self, text="Exit", bg="red", padx=20, command=self.quitProgram
        )

        Button1 = tk.Button(self, text="Reset", padx=20, command=self.reset)
        Button2 = tk.Button(self, text="Fill", padx=20, command=self.fill)
        Button3 = tk.Button(self, text="Empty", padx=20, command=self.empty)
        Button4 = tk.Button(self, text="Wash", padx=20, command=self.wash)

        MassLabel.grid(row=0, column=0, sticky="NSEW")
        self.Input1.grid(row=1, column=0)
        TemperatureLabel.grid(row=0, column=1, sticky="NSEW")
        self.Input2.grid(row=1, column=1)
        SalinityLabel.grid(row=2, column=1, sticky="NSEW")
        self.Input3.grid(row=3, column=1)
        TALabel.grid(row=0, column=5, sticky="NSEW")
        self.Output.grid(row=1, column=5)
        self.Output.configure(state=tk.DISABLED)
        self.StartButton.grid(row=2, column=0)
        ExitButton.grid(row=4, column=0)

        Button1.grid(row=3, column=0)
        Button2.grid(row=4, column=2)
        Button3.grid(row=4, column=3)
        Button4.grid(row=4, column=4)

        self.fig, self.ax = plt.subplots(figsize=(3.5, 3), constrained_layout=True)
        self.ax.set_xlabel("Volume Added (L)")
        self.ax.set_ylabel("Emf (mV)")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(
            row=0, column=2, rowspan=4, columnspan=3, sticky="NSEW"
        )
        self.canvas.draw()

        self.syringePos = 0

        self.pins = pinSetup.Pins()

    def start(self):

        self.StartButton.configure(state=tk.DISABLED)

        try:
            self.s = serial.Serial("/dev/ttyACM0", baudrate=9600, bytesize=8, timeout=2)
        except serial.SerialException:
            print("Device Not Found!")
            self.quitProgram()

        if self.Input1.get() == "":
            tk.messagebox.showerror("Error!", "Please insert mass of sample!")
            self.StartButton.configure(state=tk.NORMAL)
            return
        else:
            sampleSize = float(self.Input1.get())
            self.Input1.configure(state=tk.DISABLED)
        if self.Input2.get() == "":
            tk.messagebox.showerror("Error", "Please insert temperature of sample!")
            self.StartButton.configure(state=tk.NORMAL)
            return
        else:
            temp = float(self.Input2.get())
            self.Input2.configure(state=tk.DISABLED)
        if self.Input3.get() == "":
            tk.messagebox.showerror("Error", "Please insert salinity of sample!")
            return
        else:
            salinity = float(self.Input3.get())
            self.Input3.configure(state=tk.DISABLED)
        if readpH.readpH(self.s)[0] == "":
            tk.messagebox.showerror("Error", "Please check connectivity of pH meter!")
            self.StartButton.configure(state=tk.NORMAL)
            return

        with open("data/electrodeCalibData.csv") as f:
            for line in f:
                slope, intercept, efficiency = line.split(",")

        emfi, pHi = float(readpH.readpH(self.s)[0]), float(readpH.readpH(self.s)[1])
        print(f"Initial pH: {pHi}, Initial emfi: {emfi}.")

        titration = classTitration.Titration(
            sampleSize, salinity, temp, np.array([pHi]), np.array([emfi]), np.array([0])
        )

        self.StartedLabel = tk.Label(
            self, text="Titration Started!", fg="green", pady=10
        )
        self.StartedLabel.grid(row=5, column=0)
        self.stopTitration = False

        self.StopButton = tk.Button(
            self, text="Stop Titration", padx=10, command=self.cancelTitration
        )
        self.StopButton.grid(row=5, column=1)

        self.Output.delete(0, tk.END)

        self.fill()

        self.update()
        self.after(1000, lambda: self.InitialTitration(titration))

    def InitialTitration(self, titration):

        if titration.pHs[-1] < 3.8:

            print("\nMoving to Second Step\n")
            self.after_cancel(self)
            self.AutoTitration(titration)

            return

        pHf = 3.79
        Cacid = 0.09760158624
        syringeStep = 0.000248621 / 1000 / 4  # liter per step
        acidVol = titration.requiredVol(Cacid, pHf)
        print(f"Required Vol: {acidVol}")
        numSteps = int(acidVol / syringeStep)
        print(f"Number of Steps: {numSteps}")
        targetPos = self.syringePos - numSteps

        if targetPos <= 0:
            GPIO.output(self.pins.CHANGE, GPIO.LOW)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * self.syringePos,
            )
            self.MoveSyringe(-1 * self.syringePos, self.pins, "1/4")
            self.tksleep(15000)
            emf, pH = float(readpH.readpH(self.s)[0]), float(readpH.readpH(self.s)[1])
            print(f"pH: {pH}, syringePos: {self.syringePos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            self.fill()

            self.after(1000, lambda: self.InitialTitration(titration))
            return

        elif targetPos > 0:  # move to position

            GPIO.output(self.pins.CHANGE, GPIO.LOW)
            self.MoveSyringe(-1 * numSteps, self.pins, "1/4")
            self.tksleep(15000)
            emf, pH = float(readpH.readpH(self.s)[0]), float(readpH.readpH(self.s)[1])
            print(f"pH: {pH}, syringePos: {self.syringePos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * numSteps,
            )
            self.plot(titration.volumeAdded, titration.emf)

            self.after(1000, lambda: self.InitialTitration(titration))
            return

    def AutoTitration(self, titration):

        pHi = titration.pHs[-1]
        pHf = pHi - 0.1
        Cacid = 0.09760158624
        syringeStep = 0.000248621 / 1000 / 4  # microliter per step
        acidVol = titration.requiredVol(Cacid, pHf)
        print(f"Required Vol: {acidVol}")
        numSteps = int(acidVol / syringeStep)
        print(f"Number of Steps: {numSteps}")
        targetPos = self.syringePos - numSteps

        if self.stopTitration == True:
            self.after_cancel(self)
            print("Titration Cancelled")
            return

        if titration.pHs[-1] < 3 or len(titration.pHs) > 25:

            self.after_cancel(self)
            print(f"Final pH: {titration.pHs[-1]}")
            TA, gamma, rsquare = titration.granCalc(0.09760158624)
            print(TA, gamma, rsquare)
            self.Output.configure(state=tk.NORMAL)
            self.Output.delete(0, tk.END)
            self.Output.insert(0, str(TA))
            self.Output.configure(state=tk.DISABLED)
            self.writeData(titration, TA)
            return

        if targetPos <= 0:
            GPIO.output(self.pins.CHANGE, GPIO.LOW)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * self.syringePos,
            )
            self.MoveSyringe(-1 * self.syringePos, self.pins, "1/4")
            self.tksleep(12000)
            emf, pH = float(readpH.readpH(self.s)[0]), float(readpH.readpH(self.s)[1])
            print(f"pH: {pH}, syringePos: {self.syringePos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            self.fill()

            self.after(1000, lambda: self.AutoTitration(titration))
            return

        elif targetPos > 0:  # move to position

            GPIO.output(self.pins.CHANGE, GPIO.LOW)
            self.MoveSyringe(-1 * numSteps, self.pins, "1/4")
            self.tksleep(12000)
            emf, pH = float(readpH.readpH(self.s)[0]), float(readpH.readpH(self.s)[1])
            print(f"pH: {pH}, syringePos: {self.syringePos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * numSteps,
            )
            self.plot(titration.volumeAdded, titration.emf)

            self.after(1000, lambda: self.AutoTitration(titration))
            return

    def MoveSyringe(self, step_count, pins, resolution):

        if step_count > 0:
            direction = 1
        else:
            direction = 0

        self.syringePos = self.syringePos + step_count

        step_count = abs(step_count)
        RESOLUTION = {
            "Full": (0, 0, 0),
            "Half": (1, 0, 0),
            "1/4": (0, 1, 0),
            "1/8": (1, 1, 0),
            "1/16": (0, 0, 1),
            "1/32": (1, 0, 1),
        }
        GPIO.output(pins.MODE, RESOLUTION[resolution])

        GPIO.output(pins.DIR, direction)
        for x in range(step_count):

            GPIO.output(pins.STEP, GPIO.HIGH)
            self.tksleep(1)
            GPIO.output(pins.STEP, GPIO.LOW)
            self.tksleep(1)

        return

    def tksleep(self, t):

        # waits for t milliseconds

        var = tk.IntVar(self)
        self.after(t, var.set, 1)
        self.wait_variable(var)

        return

    def plot(self, x, y):

        # print(f'Plotting: {x}, {y}')

        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

        return

    def fill(self):

        GPIO.output(self.pins.CHANGE, GPIO.HIGH)
        self.MoveSyringe(7000 - int(self.syringePos / 4), self.pins, "Full")

        return

    def empty(self):

        GPIO.output(self.pins.CHANGE, GPIO.LOW)
        self.MoveSyringe(-1 * self.syringePos, self.pins, "Full")

        return

    def wash(self):

        self.fill()
        self.empty()
        self.fill()
        self.empty()
        self.fill()
        self.empty()

        return

    def cancelTitration(self):

        print("Stopping next titration step ...")
        self.stopTitration = True

        return

    def writeData(self, titration, TA):

        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

        with open("data/" + filename + ".csv", "w") as f:

            writer = csv.writer(f, delimiter=",")
            writer.writerow(["Sample Size (g):"] + [str(titration.sampleSize * 1000)])
            writer.writerow(["Temperature (C):"] + [str(titration.T - 273.15)])
            writer.writerow(["Salinity:"] + [str(titration.S)])
            writer.writerow(["Emf:"] + [",".join(titration.emf.astype(str))])
            writer.writerow(
                ["Volume Added:"] + [",".join(titration.volumeAdded.astype(str))]
            )
            writer.writerow(["pH:"] + [",".join(titration.pHs.astype(str))])
            writer.writerow(["Total Alkalinity:"] + [str(TA)])

        self.reset()

        return

    def reset(self):

        self.StartButton.configure(state=tk.NORMAL)
        self.Input1.configure(state=tk.NORMAL)
        self.Input2.configure(state=tk.NORMAL)
        self.Input3.configure(state=tk.NORMAL)

        self.Input1.delete(0, tk.END)
        self.Input2.delete(0, tk.END)
        self.Input3.delete(0, tk.END)

        self.StartedLabel.destroy()
        self.StopButton.destroy()

        self.ax.clear()

        return

    def quitProgram(self):

        self.empty()
        self.destroy()

        return
