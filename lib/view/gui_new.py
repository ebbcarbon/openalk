# Standard libraries
import csv
import tkinter as tk
from datetime import datetime
from enum import Enum, auto
from typing import Tuple

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local libraries
from lib.services.ph import orion_star
from lib.services.pump import norgren
from lib.services.titration import gran


class SystemStates(Enum):
    READY = auto()
    PROCESSING = auto()
    STOPPING = auto()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.pump = norgren.VersaPumpV6()

        self.ph_meter = orion_star.OrionStarA215()

        self.system_state = None

        self._sleep_var = tk.IntVar(self)
        self._stop_titration = False

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

        self.acid_conc_label = tk.Label(self, text="Insert acid concentration (M): ", padx=20)
        self.acid_conc_input = tk.Entry(self, width=10)

        self.total_alk_label = tk.Label(self, text="Total Alkalinity (umol/kg): ", padx=20)
        self.total_alk_output = tk.Entry(self, width=10)

        self.state_label = tk.Label(
            self, text="Ready", fg="green", pady=10
        )

        """
        Button definitions
        """
        self.start_button = tk.Button(
            self, text="Start", bg="green", padx=20, command=self.start_titration
        )

        self.stop_button = tk.Button(
            self, text="Stop Titration", padx=10, command=self.stop_titration
        )

        self.exit_button = tk.Button(
            self, text="Exit", bg="red", padx=20, command=self.quit_program
        )

        self.wm_exit_handler = self.protocol("WM_DELETE_WINDOW", self.quit_program)

        self.reset_button = tk.Button(self, text="Reset", padx=20, command=self.reset_interface)
        self.fill_button = tk.Button(self, text="Fill", padx=20, command=self.pump.fill)
        self.empty_button = tk.Button(self, text="Empty", padx=20, command=self.pump.empty)
        self.wash_button = tk.Button(self, text="Wash", padx=20, command=self.pump.wash)

        self.export_button = tk.Button(self, text="Export Data", padx=20, command=self.export_data)

        """
        Grid arrangement of input fields, buttons
        """
        self.initial_mass_label.grid(row=0, column=0, sticky="NSEW")
        self.initial_mass_input.grid(row=1, column=0)

        self.temperature_label.grid(row=0, column=1, sticky="NSEW")
        self.temperature_input.grid(row=1, column=1)
        self.temperature_input.configure(state=tk.DISABLED)

        self.salinity_label.grid(row=2, column=1, sticky="NSEW")
        self.salinity_input.grid(row=3, column=1)

        self.acid_conc_label.grid(row=2, column=0, sticky="NSEW")
        self.acid_conc_input.grid(row=3, column=0)

        self.total_alk_label.grid(row=0, column=5, sticky="NSEW")
        self.total_alk_output.grid(row=1, column=5)
        self.total_alk_output.configure(state=tk.DISABLED)

        self.start_button.grid(row=4, column=0)

        self.stop_button.grid(row=4, column=1)
        self.stop_button.configure(state=tk.DISABLED)

        self.reset_button.grid(row=5, column=0)
        self.exit_button.grid(row=5, column=1)

        self.fill_button.grid(row=4, column=2)
        self.empty_button.grid(row=4, column=3)
        self.wash_button.grid(row=4, column=4)
        self.export_button.grid(row=3, column=5)

        self.state_label.grid(row=6, column=0)

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

        self.system_state = SystemStates.READY

    def check_pump_ready(self) -> bool:
        init_pump = self.pump.initialize_pump()
        if not init_pump['host_ready']:
            tk.messagebox.showerror("Error", "Pump connection failed.")
            return False
        return True

    def check_ph_meter_ready(self) -> bool:
        test_measurement = self.ph_meter.get_measurement()
        if not test_measurement:
            tk.messagebox.showerror("Error", "pH meter connection failed.")
            return False
        return True

    def disable_inputs(self) -> None:
        self.start_button.configure(state=tk.DISABLED)
        self.initial_mass_input.configure(state=tk.DISABLED)
        self.salinity_input.configure(state=tk.DISABLED)
        self.acid_conc_input.configure(state=tk.DISABLED)

    def reset_inputs(self) -> None:
        self.start_button.configure(state=tk.NORMAL)
        self.initial_mass_input.configure(state=tk.NORMAL)
        self.salinity_input.configure(state=tk.NORMAL)
        self.acid_conc_input.configure(state=tk.NORMAL)

    def check_inputs(self) -> Tuple[bool, str, str, str]:
        sample_mass = self.initial_mass_input.get()
        salinity = self.salinity_input.get()
        acid_conc = self.acid_conc_input.get()

        valid = True
        if not sample_mass:
            tk.messagebox.showerror("Error", "Please provide sample mass.")
            valid = False
        if not salinity:
            tk.messagebox.showerror("Error", "Please provide sample salinity.")
            valid = False
        if not acid_conc:
            tk.messagebox.showerror("Error", "Please provide acid concentration.")
            valid = False

        return valid, sample_mass, salinity, acid_conc

    def disable_manual_pump_controls(self) -> None:
        self.fill_button.configure(state=tk.DISABLED)
        self.empty_button.configure(state=tk.DISABLED)
        self.wash_button.configure(state=tk.DISABLED)

    def reset_manual_pump_controls(self) -> None:
        self.fill_button.configure(state=tk.NORMAL)
        self.empty_button.configure(state=tk.NORMAL)
        self.wash_button.configure(state=tk.NORMAL)

    def clear_outputs(self) -> None:
        self.total_alk_output.configure(state=tk.NORMAL)
        self.total_alk_output.delete(0, tk.END)
        self.total_alk_output.configure(state=tk.DISABLED)

    def update_ta_output(self, value: float) -> None:
        self.total_alk_output.configure(state=tk.NORMAL)
        self.total_alk_output.insert(0, str(value))
        self.total_alk_output.configure(state=tk.DISABLED)

    def start_titration(self) -> None:

        self.disable_inputs()
        self.disable_manual_pump_controls()
        self.clear_outputs()

        inputs_valid, sample_mass, salinity, acid_conc = self.check_inputs()

        if not inputs_valid:
            self.reset_inputs()
            self.reset_manual_pump_controls()
            return

        if not self.check_pump_ready():
            self.reset_inputs()
            self.reset_manual_pump_controls()
            return

        if not self.check_ph_meter_ready():
            self.reset_inputs()
            self.reset_manual_pump_controls()
            return

        meas_initial = self.ph_meter.get_measurement()
        ph_initial = meas_initial["pH"]
        emf_initial = meas_initial["mV"]
        temp_initial = meas_initial["temp"]

        self.temperature_input.configure(state=tk.NORMAL)
        self.temperature_input.insert(0, temp_initial)
        self.temperature_input.configure(state=tk.DISABLED)

        self.system_state = SystemStates.PROCESSING
        self.stop_button.configure(state=tk.NORMAL)
        self.state_label.configure(text="Titration started")

        titration = gran.ModifiedGranTitration(
            float(sample_mass), float(salinity), float(temp_initial),
            np.array([float(ph_initial)]), np.array([float(emf_initial)]),
            np.array([0])
        )

        print("Filling syringe...")
        self.pump.fill()
        self.tksleep(15)

        """Fix this"""
        self.initial_titration(titration, float(acid_conc))

    def initial_titration(self, titration: gran.ModifiedGranTitration,
                              acid_conc: float) -> None:
        # Stopping logic. Need to think of a better way to do this.
        # Need to reset interface after this!!
        # Where does the syringe empty to in this case?
        if self._stop_titration:
            self.after_cancel(self.initial_titration)
            print("Titration cancelled.")
            self._stop_titration = False
            return

        # Check if last pH reading is below 3.8, if so move to next step
        if titration.pHs[-1] < 3.8:
            print("Moving to second titration step")
            self.after_cancel(self.initial_titration)
            self.auto_titration(titration, acid_conc)
            return

        pHf = 3.79

        self.run_titration_step(titration, acid_conc, pHf)

        # Schedule next titration step, setting time=0 makes it run
        # immediately whenever the mainloop is not busy
        self.after(0, self.initial_titration, titration, acid_conc)

    def auto_titration(self, titration: gran.ModifiedGranTitration,
                          acid_conc: float) -> None:
        # Stopping logic. Need to think of a better way to do this.
        if self._stop_titration:
            self.after_cancel(self.auto_titration)
            print("Titration cancelled.")
            self._stop_titration = False
            return

        """
        Stop if last pH less than 3, or if number of steps > 25(??)
        """
        if titration.pHs[-1] < 3 or len(titration.pHs) > 25:
            self.after_cancel(self.auto_titration)
            print(f"Final pH: {titration.pHs[-1]}")

            TA, gamma, rsquare = titration.granCalc(acid_conc)
            print(f"TA: {TA}, Gamma: {gamma}, Rsq: {rsquare}")

            self.update_ta_output(TA)

            self.write_data(titration, TA)

            """There was originally a call to reset everything here, fix this"""
            # self.reset()
            return

        """This stage goes much more slowly, in increments of 0.1 pH"""
        pHi = titration.pHs[-1]
        pHf = pHi - 0.1

        self.run_titration_step(titration, acid_conc, pHf)

        # Schedule next titration step, setting time=0 makes it run
        # immediately whenever the mainloop is not busy
        self.after(0, self.auto_titration, titration, acid_conc)

    def run_titration_step(self, titration: gran.ModifiedGranTitration,
                              acid_conc: float, pHf: float) -> None:
        # Get the volume of acid required to dose at the next step, in liters
        required_acid_volume_liters = titration.requiredVol(acid_conc, pHf)

        required_acid_volume_ul = round(required_acid_volume_liters * 1e6, 2)

        if not self.pump.check_volume_available(required_acid_volume_liters):
            print("Volume low, re-filling...")
            self.pump.fill()
            self.tksleep(15)

        # Dispense required volume of acid
        print(f"Dispensing: {required_acid_volume_ul} uL")
        self.pump.dispense(required_acid_volume_liters)
        # Wait 15 seconds to equilibrate
        self.tksleep(15)

        # Take pH, emf measurements
        step_measurement = self.ph_meter.get_measurement()
        pH = step_measurement["pH"]
        emf = step_measurement["mV"]
        print(f"pH: {pH}, emf: {emf}")

        # Add last measurements to titration
        titration.pHs = np.append(titration.pHs, float(pH))
        titration.emf = np.append(titration.emf, float(emf))

        titration.volumeAdded = np.append(
            titration.volumeAdded,
            titration.volumeAdded[-1] + required_acid_volume_liters,
        )

        # Plot current step
        self.plot(titration.volumeAdded, titration.emf)

    def plot(self, x: np.array, y: np.array) -> None:
        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

    """
    Bad writer logic. Header should be something like:
    time, titration_step, sample_mass_g, temp_C, salinity, emf_mV,
    volume_added_L, pH, total_alkalinity_umol_kg
    """
    def write_data(self, titration, TA) -> None:
        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

        with open(filename + ".csv", "w") as f:
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

    def export_data(self) -> None:
        default_filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        filepath = tk.filedialog.asksaveasfilename(
                      initialfile=default_filename,
                      defaultextension=".csv",
                      filetypes=[("CSV", "*.csv")]
        )
        with open(filepath, "w") as f:
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

    def stop_titration(self) -> None:
        self._stop_titration = True
        print("Stopping titration before next step...")

    def reset_interface(self):
        pass

    def tksleep(self, time: float) -> None:
        '''Tkinter-compatible emulation of time.sleep(seconds)'''
        self.after(time*1000, self._sleep_var.set, 1)
        self.wait_variable(self._sleep_var)

    def quit_program(self):
        if self.system_state == SystemStates.PROCESSING:
            mb = tk.messagebox.askyesnocancel("Warning",
                "Titration in progress, are you sure you want to quit?")
            if mb:
                self.quit()
            else:
                return
        self.quit()
