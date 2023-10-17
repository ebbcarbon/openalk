# Standard libraries
import csv
import tkinter as tk
from datetime import datetime
from enum import Enum, auto

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local libraries
from lib.services.ph import orion_star
from lib.services.pump import norgren_pump
from lib.services.titration import modified_gran


class SystemStates(Enum):
    READY = auto()
    PROCESSING = auto()
    STOPPING = auto()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.system_state = None

        self.pump = norgren_pump.NorgrenPump()
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

        self.state_label = tk.Label(
            self, text="Ready", fg="green", pady=10
        )

        """
        Button definitions, same attribute declaration badness
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
        self.fill_button = tk.Button(self, text="Fill", padx=20, command=self.pump.fill_syringe)
        self.empty_button = tk.Button(self, text="Empty", padx=20, command=self.pump.empty_syringe)
        self.wash_button = tk.Button(self, text="Wash", padx=20, command=self.pump.wash_syringe)

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

        self.state_label.grid(row=5, column=0)

        self.total_alk_label.grid(row=0, column=5, sticky="NSEW")
        self.total_alk_output.grid(row=1, column=5)
        self.total_alk_output.configure(state=tk.DISABLED)

        self.start_button.grid(row=2, column=0)
        self.stop_button.grid(row=5, column=1)
        self.stop_button.configure(state=tk.DISABLED)
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

        self.system_state = SystemStates.READY

    def check_pump_ready(self) -> bool:
        init_pump = self.pump.initialize_pump()
        return init_pump['host_ready']

    def check_ph_meter_ready(self) -> bool:
        test_meas = self.ph_meter.get_measurement()
        return test_meas is not None

    def start_titration(self):

        self.start_button.configure(state=tk.DISABLED)

        if self.initial_mass_input.get() == "":
            tk.messagebox.showerror("Error", "Please insert mass of sample!")
            self.start_button.configure(state=tk.NORMAL)
            return
        else:
            sampleSize = float(self.initial_mass_input.get())
            self.initial_mass_input.configure(state=tk.DISABLED)

        # if self.temperature_input.get() == "":
        #     tk.messagebox.showerror("Error", "Please insert temperature of sample!")
        #     self.start_button.configure(state=tk.NORMAL)
        #     self.initial_mass_input.configure(state=tk.NORMAL)
        #     return
        # else:
        #     temp = float(self.temperature_input.get())
        #     self.temperature_input.configure(state=tk.DISABLED)

        if self.salinity_input.get() == "":
            tk.messagebox.showerror("Error", "Please insert salinity of sample!")
            self.start_button.configure(state=tk.NORMAL)
            self.initial_mass_input.configure(state=tk.NORMAL)
            # self.temperature_input.configure(state=tk.NORMAL)
            return
        else:
            salinity = float(self.salinity_input.get())
            self.salinity_input.configure(state=tk.DISABLED)

        pump_ready = self.check_pump_ready()
        if not pump_ready:
            tk.messagebox.showerror("Error", "Pump connection failed!")
            self.start_button.configure(state=tk.NORMAL)
            return

        ph_meter_ready = self.check_ph_meter_ready()
        if not ph_meter_ready:
            tk.messagebox.showerror("Error", "pH meter connection failed!")
            self.start_button.configure(state=tk.NORMAL)
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

        titration = modified_gran.ModifiedGranTitration(
            sampleSize, salinity, float(temp_initial), np.array([ph_initial]),
            np.array([emf_initial]), np.array([0])
        )

        self.pump.fill_syringe()

        return

    def initial_titration(self):
        pass

    def second_titration(self):
        pass

    def stop_titration(self):
        pass

    def reset_interface(self):
        pass

    def quit_program(self):
        if self.system_state == SystemStates.PROCESSING:
            mb = tk.messagebox.askyesnocancel("Warning",
                "Titration in progress, are you sure you want to quit?")
            if mb:
                self.quit()
            else:
                return
        self.quit()
