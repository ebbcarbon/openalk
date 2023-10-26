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
        # self.pump = pump_interface.PumpInterface()
        # self.pump.set_sleep_func(self.sleep_msecs)

        self.ph_meter = orion_star.OrionStarA215()
        # self.ph_meter = ph_modules.pH_meter_A211(PH_SERIAL_PORT)
        # self.ph_meter = ph_modules.pH_meter_simulated()

        self.system_state = None
        self._sleep_var = tk.IntVar(self)

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

    def start_titration(self) -> None:

        self.disable_inputs()
        self.disable_manual_pump_controls()

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

        self.pump.fill()
        self.tksleep(15)

        """Fix this"""
        self.initial_titration(titration, float(acid_conc))

    def initial_titration(self, titration: gran.ModifiedGranTitration, acid_conc: float) -> None:

        """Placeholder for stopping logic"""
        # stop_titration = False
        # if stop_titration:
        #     print("titration stopping")

        """
        Check if last pH reading is below 3.8, if so move to auto titration...

        Using after_cancel(self) is real bad, just wholesale cancels
        every update of the parent
        """
        # if titration.pHs[-1] < 3.8:
        #     print("Moving to Second Step")
        #     self.after_cancel(self)
        #     self.auto_titration(titration)
        #
        #     return

        pHf = 3.79

        """
        Get the volume of acid required to dose at the next step, in liters
        """
        required_acid_volume_liters = titration.requiredVol(acid_conc, pHf)

        if not self.pump.check_volume_available(required_acid_volume_liters):
            self.pump.fill()
            self.tksleep(15)

        # Normal operation
        # Dispense required volume of acid
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

        # Schedule next titration step
        self.after(1000, self.initial_titration, titration)
        return

    def second_titration(self, titration: gran.ModifiedGranTitration) -> None:
        """Placeholder for stopping logic"""
        # stop_titration = False
        # if stop_titration:
        #     print("titration stopping")




    def plot(self, x: np.array, y: np.array) -> None:
        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

    def stop_titration(self):
        pass

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
