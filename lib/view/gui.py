# Standard libraries
import csv
import tkinter as tk
from datetime import datetime

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local libraries
from lib.services.titration import titration_class
from lib.services.pump import pump_interface
from lib.services.ph import ph_modules

PH_SERIAL_PORT = "/dev/ttyACM0"

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.pump = pump_interface.PumpInterface()
        self.pump.set_sleep_func(self.sleep_msecs)

        self.ph_meter = ph_modules.pH_meter_A211(PH_SERIAL_PORT)
        # self.ph_meter = ph_modules.pH_meter_simulated()

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
            self, text="Exit", bg="red", padx=20, command=self.quit_program
        )

        wm_exit_handler = self.protocol("WM_DELETE_WINDOW", self.quit_program)

        Button1 = tk.Button(self, text="Reset", padx=20, command=self.reset)
        Button2 = tk.Button(self, text="Fill", padx=20, command=self.pump.fill)
        Button3 = tk.Button(self, text="Empty", padx=20, command=self.pump.empty)
        Button4 = tk.Button(self, text="Wash", padx=20, command=self.pump.wash)

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

    def start(self):
        self.StartButton.configure(state=tk.DISABLED)

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
        if not self.ph_meter.device_functional():
            tk.messagebox.showerror("Error", "Please check connectivity of pH meter!")
            self.StartButton.configure(state=tk.NORMAL)
            return

        # This isn't used at the moment -- need to implement this
        # with open("data/electrodeCalibData.csv") as f:
        #     for line in f:
        #         slope, intercept, efficiency = line.split(",")

        emfi, pHi = self.ph_meter.read_emf_pH()
        print(f"Initial pH: {pHi}, Initial emfi: {emfi}.")

        titration = titration_class.Titration(
            sampleSize, salinity, temp, np.array([pHi]), np.array([emfi]), np.array([0])
        )

        self.StartedLabel = tk.Label(
            self, text="Titration Started!", fg="green", pady=10
        )
        self.StartedLabel.grid(row=5, column=0)
        self.stop_titration = False

        self.StopButton = tk.Button(
            self, text="Stop Titration", padx=10, command=self.cancel_titration
        )
        self.StopButton.grid(row=5, column=1)

        self.Output.delete(0, tk.END)

        self.pump.fill()

        self.update()
        self.after(1000, lambda: self.initial_titration(titration))

    def initial_titration(self, titration):
        if titration.pHs[-1] < 3.8:
            print("\nMoving to Second Step\n")
            self.after_cancel(self)
            self.auto_titration(titration)

            return

        pHf = 3.79
        Cacid = 0.09760158624
        syringeStep = 0.000248621 / 1000 / 4  # liter per step
        acidVol = titration.requiredVol(Cacid, pHf)
        print(f"Required Vol: {acidVol}")
        numSteps = int(acidVol / syringeStep)
        print(f"Number of Steps: {numSteps}")
        targetPos = self.pump.syringe_pos - numSteps

        if targetPos <= 0:
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * self.pump.syringe_pos,
            )
            self.pump.move_syringe(-1 * self.pump.syringe_pos, "1/4")
            self.sleep_msecs(15000)
            emf, pH = self.ph_meter.read_emf_pH()
            print(f"pH: {pH}, syringePos: {self.pump.syringe_pos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            self.pump.fill()

            self.after(1000, lambda: self.initial_titration(titration))
            return

        elif targetPos > 0:  # move to position
            self.pump.move_syringe(-1 * numSteps, "1/4")
            self.sleep_msecs(15000)
            emf, pH = self.ph_meter.read_emf_pH()
            print(f"pH: {pH}, syringePos: {self.pump.syringe_pos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * numSteps,
            )
            self.plot(titration.volumeAdded, titration.emf)

            self.after(1000, lambda: self.initial_titration(titration))
            return

    def auto_titration(self, titration):
        pHi = titration.pHs[-1]
        pHf = pHi - 0.1
        Cacid = 0.09760158624
        syringeStep = 0.000248621 / 1000 / 4  # microliter per step
        acidVol = titration.requiredVol(Cacid, pHf)
        print(f"Required Vol: {acidVol}")
        numSteps = int(acidVol / syringeStep)
        print(f"Number of Steps: {numSteps}")
        targetPos = self.pump.syringe_pos - numSteps

        if self.stop_titration:
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
            self.write_data(titration, TA)
            return

        if targetPos <= 0:
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * self.pump.syringe_pos,
            )
            self.pump.move_syringe(-1 * self.pump.syringe_pos, "1/4")
            self.sleep_msecs(12000)
            emf, pH = self.ph_meter.read_emf_pH()
            print(f"pH: {pH}, syringePos: {self.pump.syringe_pos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            self.pump.fill()

            self.after(1000, lambda: self.auto_titration(titration))
            return

        elif targetPos > 0:  # move to position
            self.pump.move_syringe(-1 * numSteps, "1/4")
            self.sleep_msecs(12000)
            emf, pH = self.ph_meter.read_emf_pH()
            print(f"pH: {pH}, syringePos: {self.pump.syringe_pos}")
            titration.pHs = np.append(titration.pHs, pH)
            titration.emf = np.append(titration.emf, emf)
            titration.volumeAdded = np.append(
                titration.volumeAdded,
                titration.volumeAdded[-1] + syringeStep * numSteps,
            )
            self.plot(titration.volumeAdded, titration.emf)

            self.after(1000, lambda: self.auto_titration(titration))
            return

    def sleep_msecs(self, t):
        """
        Sleep for t milliseconds
        """

        # tkApp wants to do things this way, don't just use time.sleep()!
        var = tk.IntVar(self)
        self.after(t, var.set, 1)
        self.wait_variable(var)

    def plot(self, x, y):
        # print(f'Plotting: {x}, {y}')

        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

    def cancel_titration(self):
        print("Stopping next titration step ...")
        self.stop_titration = True

    def write_data(self, titration, TA):
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

    def quit_program(self):
        self.pump.empty()
        self.quit()
