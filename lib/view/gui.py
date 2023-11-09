# Standard libraries
import csv
import tkinter as tk
from datetime import datetime

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local libraries
from lib.services.ph import orion_star
from lib.services.pump import norgren
from lib.services.titration import gran

"""
*** High Level Titration Procedure ***

Open-cell titration procedure for determination of total alkalinity in sea
water, according to Dickson (2007) SOP 3b:

- Known amount of seawater is placed in an open cell
- Hydrochloric acid titrant of known acid concentration placed next to cell
- Sea water sample is acidified to a pH between 3.5-4.0 with a single aliquot
  of titrant
- Seawater solution is stirred for a defined period of time to allow escape
  of evolved CO2
- Titration is then continued in small steps until reaching pH 3.0
- Total alkalinity is computed from e.m.f. and the volume of titrant dispensed,
  using a nonlinear least-squares approach

"""

"""
*** Titration Steps ***

Again according to Dickson (2007) SOP 3b:

- With slow stirring, dispense enough hydrochloric acid to bring the sample
  to a pH just above 3.5.
- Increase the stirring rate until it is vigorous but not splashing. Turn on
  air flow through the solution.
- Leave the acidified sample stirring for at least 6 minutes to allow for CO2
  degassing.
- Titrate the sample using 0.05 cm^3 increments to a final pH of ca. 3.0
  (~20 increments). After each addition, record the total dispensed volume to
  0.001 cm^3, the e.m.f. to 0.00001 V, and the sample temperature to 0.01 C.

"""


"""
Subclassing Tk vs root = Tk()? What's the recommended way?
"""

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.pump = norgren.VersaPumpV6()
        # self.pump = pump_interface.PumpInterface()
        # self.pump.set_sleep_func(self.sleep_msecs)

        self.ph_meter = orion_star.OrionStarA215()
        # self.ph_meter = ph_modules.pH_meter_A211(PH_SERIAL_PORT)
        # self.ph_meter = ph_modules.pH_meter_simulated()



        """
        Should probably break out all the UI initialization into a separate
        function for clarity
        """
        self.title("Total Alkalinity")

        """
        Ideally set geometry to something more general
        """
        self.geometry("1200x500")

        self.option_add("*font", "Arial 13")

        """
        Input field definition and titles
        """
        self.initial_mass_label = tk.Label(self, text="Insert initial Mass (g): ", padx=20)
        self.initial_mass_input = tk.Entry(self, width=10)

        self.temperature_label = tk.Label(self, text="Insert temperature (C): ", padx=20)
        self.temperature_input = tk.Entry(self, width=10)

        self.salinity_label = tk.Label(self, text="Insert sample salinity (S): ", padx=20)
        self.salinity_input = tk.Entry(self, width=10)

        self.total_alk_label = tk.Label(self, text="Total Alkalinity (umol/kg): ", padx=20)
        self.total_alk_output = tk.Entry(self, width=10)

        """
        Button definitions, same attribute declaration badness
        """
        self.start_button = tk.Button(
            self, text="Start", bg="green", padx=20, command=self.start
        )

        self.exit_button = tk.Button(
            self, text="Exit", bg="red", padx=20, command=self.quit_program
        )

        self.wm_exit_handler = self.protocol("WM_DELETE_WINDOW", self.quit_program)

        self.reset_button = tk.Button(self, text="Reset", padx=20, command=self.reset)
        self.fill_button = tk.Button(self, text="Fill", padx=20, command=self.pump.fill)
        self.empty_button = tk.Button(self, text="Empty", padx=20, command=self.pump.empty)
        self.wash_button = tk.Button(self, text="Wash", padx=20, command=self.pump.wash)

        """
        Grid arrangement of input fields, buttons
        """
        self.initial_mass_label.grid(row=0, column=0, sticky="NSEW")
        self.initial_mass_input.grid(row=1, column=0)

        self.temperature_label.grid(row=0, column=1, sticky="NSEW")
        self.temperature_input.grid(row=1, column=1)

        self.salinity_label.grid(row=2, column=1, sticky="NSEW")
        self.salinity_input.grid(row=3, column=1)

        self.total_alk_label.grid(row=0, column=5, sticky="NSEW")
        self.total_alk_output.grid(row=1, column=5)
        self.total_alk_output.configure(state=tk.DISABLED)

        self.start_button.grid(row=2, column=0)
        self.exit_button.grid(row=4, column=0)

        self.reset_button.grid(row=3, column=0)
        self.fill_button.grid(row=4, column=2)
        self.empty_button.grid(row=4, column=3)
        self.wash_button.grid(row=4, column=4)

        """
        General TkApp stuff
        """
        self.fig, self.ax = plt.subplots(figsize=(3.5, 3), constrained_layout=True)
        self.ax.set_xlabel("Volume Added (L)")
        self.ax.set_ylabel("Emf (mV)")
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(
            row=0, column=2, rowspan=4, columnspan=3, sticky="NSEW"
        )
        self.canvas.draw()

    def start(self):
        """
        Manage inputs and return if anything is missing. Probably should avoid
        manually enabling/disabling buttons and just add a status/state display
        with some internal blocking based on state of the system
        """
        self.start_button.configure(state=tk.DISABLED)

        if self.initial_mass_input.get() == "":
            tk.messagebox.showerror("Error", "Please insert mass of sample!")
            self.start_button.configure(state=tk.NORMAL)
            return
        else:
            sampleSize = float(self.initial_mass_input.get())
            self.initial_mass_input.configure(state=tk.DISABLED)
        if self.temperature_input.get() == "":
            tk.messagebox.showerror("Error", "Please insert temperature of sample!")
            self.start_button.configure(state=tk.NORMAL)
            return
        else:
            temp = float(self.temperature_input.get())
            self.temperature_input.configure(state=tk.DISABLED)
        if self.salinity_input.get() == "":
            tk.messagebox.showerror("Error", "Please insert salinity of sample!")
            return
        else:
            salinity = float(self.salinity_input.get())
            self.salinity_input.configure(state=tk.DISABLED)

        """
        Something breaks when you try to start with incomplete input for any
        of the above, error boxes show but all the buttons get disabled.
        If you then hit reset, you get tk.tkapp has no attr 'StartedLabel' due
        to the attribute not having been created yet
        """

        """
        There was a check below for functionality of the ph meter, but all it
        did was see if the serial port opened without crashing the whole program.
        We should have more robust checking here before running.
        """

        # if not self.ph_meter.device_functional():
        #     tk.messagebox.showerror("Error", "Please check connectivity of pH meter!")
        #     self.start_button.configure(state=tk.NORMAL)
        #     return

        """
        What if you try to open the app and one of the devices isn't connected?
        Where should that be handled?
        """

        """
        Check pump is ready...does this belong here?
        """
        init_pump = self.pump.initialize_pump()
        if not init_pump['host_ready']:
            tk.messagebox.showerror("Error", "Pump initialization failed!")
            return

        """
        Get initial pH/emf input for titration. Can we not just get temp
        here as well and obviate the need for temp input by the user? *YES*
        """
        meas_initial = self.ph_meter.get_measurement()
        pHi = meas_initial["pH"]
        emfi = meas_initial["mV"]

        print(f"Initial pH: {pHi}, Initial emfi: {emfi}.")

        """
        Initialize main titration object
        """
        titration = gran.ModifiedGranTitration(
            sampleSize, salinity, temp, np.array([pHi]),
            np.array([emfi]), np.array([0])
        )

        """
        New labels/buttons after the fact...change
        """
        self.StartedLabel = tk.Label(
            self, text="Titration Started!", fg="green", pady=10
        )
        self.StartedLabel.grid(row=5, column=0)
        self.stop_titration = False

        self.StopButton = tk.Button(
            self, text="Stop Titration", padx=10, command=self.cancel_titration
        )
        self.StopButton.grid(row=5, column=1)

        self.total_alk_output.delete(0, tk.END)

        """
        Fill syringe with acid to prepare for dosing
        """
        self.pump.fill()

        return

        """
        Bulk update of everything in the app; dangerous. Should probably
        override the parent method if we want to use this.
        """
        self.update()

        """
        Passing the titration object
        """
        self.after(1000, lambda: self.initial_titration(titration))

    """
    For extensibility purposes, the high-level interface should not have to
    know the calibrated volume/step of the pump, since this will change
    depending on the hardware. It should just be a call to dispense a certain
    volume.
    """
    def initial_titration(self, titration):
        """
        Check if last pH reading is below 3.8, if so move to auto titration...

        Using after_cancel(self) is real bad, just wholesale cancels
        every update of the parent
        """
        if titration.pHs[-1] < 3.8:
            print("\nMoving to Second Step\n")
            self.after_cancel(self)
            self.auto_titration(titration)

            return

        """
        pHf: ?
        Cacid: ?
        syringeStep: calibrated volume/step of the pump

        Additional input box for Titrant acid concentration
        """
        pHf = 3.79
        Cacid = 0.09760158624
        syringeStep = 0.000248621 / 1000 / 4  # liter per step

        """
        Get the volume of acid required to dose at the next step
        """
        acidVol = titration.requiredVol(Cacid, pHf)
        print(f"Required Vol: {acidVol}")

        """
        Get the number of steps corresponding to the required volume of acid,
        and calculate the next target position
        """
        numSteps = int(acidVol / syringeStep)
        print(f"Number of Steps: {numSteps}")
        targetPos = self.pump.syringe_pos - numSteps

        """
        First block: contingency for when the syringe is nearing empty and volume needs
        to be added to finish the titration. Dispenses whatever the syringe
        has left and re-fills.
        """
        """
        Second block: normal operation; dispenses the desired amount and adds the ph, emf,
        and volume added to their own arrays...should just have some log for
        every step rather than constantly using -1 indexing.
        """
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

    """
    Why is this necessary? Looks like it's just implementing the same logic.
    """
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
            self.total_alk_output.configure(state=tk.NORMAL)
            self.total_alk_output.delete(0, tk.END)
            self.total_alk_output.insert(0, str(TA))
            self.total_alk_output.configure(state=tk.DISABLED)
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

    """
    Is this actually required?
    """
    def sleep_msecs(self, t):
        """
        Sleep for t milliseconds
        """
        # tkApp wants to do things this way, don't just use time.sleep()!
        var = tk.IntVar(self)
        self.after(t, var.set, 1)
        self.wait_variable(var)

    """
    Plot what? Where?
    """
    def plot(self, x, y):
        # print(f'Plotting: {x}, {y}')

        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

    """
    Probably a better way to do this
    """
    def cancel_titration(self):
        print("Stopping next titration step ...")
        self.stop_titration = True

    """
    Write titration and final TA measurement to csv on the host, change logic
    """
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

    """
    Is this overriding a parent method?
    """
    def reset(self):
        self.start_button.configure(state=tk.NORMAL)
        self.initial_mass_input.configure(state=tk.NORMAL)
        self.temperature_input.configure(state=tk.NORMAL)
        self.salinity_input.configure(state=tk.NORMAL)

        self.initial_mass_input.delete(0, tk.END)
        self.temperature_input.delete(0, tk.END)
        self.salinity_input.delete(0, tk.END)

        self.StartedLabel.destroy()
        self.StopButton.destroy()

        self.ax.clear()

    """
    Careful not to override parent method
    """
    def quit_program(self):
        # self.pump.empty()
        self.quit()
