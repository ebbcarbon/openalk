# Standard libraries
import csv
import logging
import tkinter as tk
from datetime import datetime
from enum import Enum, auto
from typing import Tuple, Callable

# Third-party libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Local libraries
from lib.services.ph import orion_star
from lib.services.pump import norgren
from lib.services.titration import gran

logger = logging.getLogger(__name__)

FIRST_TITRATION_PH_TARGET = 3.8
SECOND_TITRATION_PH_TARGET = 3.0

class SystemStates(Enum):
    """Enum values to be used with the self._system_state attribute.
    """
    DISCONNECTED = auto()
    READY = auto()
    RUNNING = auto()
    STOPPING = auto()


class App(tk.Tk):
    """Main Tkinter interface class.

    Args:
        None.

    Returns:
        None.
    """
    def __init__(self) -> None:
        super().__init__()

        self.pump = norgren.VersaPumpV6()

        self.ph_meter = orion_star.OrionStarA215()

        self._sleep_var = tk.IntVar(self)
        self._stop_titration = False

        self.build_UI()

        self._system_state = SystemStates.DISCONNECTED

    def build_UI(self) -> None:
        """Draws the main UI window before starting.

        Args:
            None.

        Returns:
            None.
        """
        self.title("Total Alkalinity")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        win_width = screen_width
        win_height = screen_height

        posx = int((screen_width - win_width) / 2)
        posy = int((screen_height - win_height) / 2)

        self.geometry(f"{win_width}x{win_height}+{posx}+{posy}")

        self.option_add("*font", "Arial 13")

        # Frame definition and titles
        self.inputs_frame = tk.LabelFrame(self,
            padx=10, pady=10, relief=tk.RIDGE, borderwidth=3,
            text="Inputs"
        )
        self.main_controls_frame = tk.LabelFrame(self,
            padx=20, pady=10, relief=tk.RIDGE, borderwidth=3,
            text="Titration Controls"
        )
        self.display_frame = tk.LabelFrame(self,
            padx=10, pady=10, relief=tk.RIDGE, borderwidth=3,
            text="Display"
        )
        self.pump_controls_frame = tk.LabelFrame(self,
            padx=20, pady=10, relief=tk.RIDGE, borderwidth=3,
            text="Pump Controls"
        )
        self.outputs_frame = tk.LabelFrame(self,
            padx=20, pady=20, relief=tk.RIDGE, borderwidth=3,
            text="Outputs"
        )
        self.status_frame = tk.LabelFrame(self,
            padx=0, pady=20, relief=tk.RIDGE, borderwidth=3,
            text="System Status"
        )

        # Input field definition and titles
        self.initial_mass_label = tk.Label(self.inputs_frame,
            text="Insert sample mass (g): ", padx=10
        )
        self.initial_mass_input = tk.Entry(self.inputs_frame, width=10)

        self.temperature_label = tk.Label(self.inputs_frame,
            text="Insert temperature (C): ", padx=10
        )
        self.temperature_input = tk.Entry(self.inputs_frame, width=10)

        self.salinity_label = tk.Label(self.inputs_frame,
            text="Insert sample salinity (S): ", padx=10, pady=10
        )
        self.salinity_input = tk.Entry(self.inputs_frame, width=10)

        self.acid_conc_label = tk.Label(self.inputs_frame,
            text="Insert titrant acid concentration (M): ", padx=10, pady=10
        )
        self.acid_conc_input = tk.Entry(self.inputs_frame, width=10)

        self.total_alk_label = tk.Label(self.outputs_frame,
            text="Total Alkalinity (umol/kg): ", padx=20
        )
        self.total_alk_output = tk.Label(self.outputs_frame,
            text="N/A", padx=20)

        self.status_label = tk.Label(self.status_frame,
            text="Disconnected", fg="red", pady=10
        )

        # Button definitions
        self.start_button = tk.Button(self.main_controls_frame, width=5,
            text="Start", bg="green", padx=20, command=self.start_titration
        )
        self.stop_button = tk.Button(self.main_controls_frame, width=5,
            text="Stop", padx=20, command=self.stop_titration
        )
        self.wm_exit_handler = self.protocol(
            "WM_DELETE_WINDOW", self.quit_program
        )
        self.reset_button = tk.Button(self.main_controls_frame, width=5,
            text="Reset", padx=20, command=self.reset_interface
        )
        self.fill_button = tk.Button(self.pump_controls_frame, width=5,
            text="Fill", padx=20, command=self.pump.fill
        )
        self.empty_button = tk.Button(self.pump_controls_frame, width=5,
            text="Empty", padx=20, command=self.pump.empty
        )
        self.wash_button = tk.Button(self.pump_controls_frame, width=5,
            text="Wash", padx=20, command=self.pump.wash
        )
        self.connect_devices_button = tk.Button(self,
            text="Connect Devices", padx=20, command=self.connect_devices
        )

        # Grid arrangement of input fields, buttons
        self.initial_mass_label.grid(row=0, column=0, sticky="NSEW")
        self.initial_mass_input.grid(row=1, column=0)

        self.temperature_label.grid(row=0, column=1, sticky="NSEW")
        self.temperature_input.grid(row=1, column=1)
        self.temperature_input.configure(state=tk.DISABLED)

        self.salinity_label.grid(row=2, column=1, sticky="NSEW")
        self.salinity_input.grid(row=3, column=1)

        self.acid_conc_label.grid(row=2, column=0, sticky="NSEW")
        self.acid_conc_input.grid(row=3, column=0)

        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_label.grid(row=0, column=0, sticky="NSEW")

        self.total_alk_label.grid(row=2, column=5, sticky="NSEW")
        self.total_alk_output.grid(row=3, column=5)

        self.main_controls_frame.grid_columnconfigure(0, weight=1)
        self.start_button.grid(row=0, column=0, pady=5)
        self.stop_button.grid(row=1, column=0, pady=5)
        self.reset_button.grid(row=2, column=0, pady=5)

        self.pump_controls_frame.grid_columnconfigure(0, weight=1)
        self.fill_button.grid(row=0, column=0, pady=5)
        self.empty_button.grid(row=1, column=0, pady=5)
        self.wash_button.grid(row=2, column=0, pady=5)
        self.connect_devices_button.grid(row=6, column=2)

        self.inputs_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=0)
        self.main_controls_frame.grid(row=1, column=0, padx=10)
        self.pump_controls_frame.grid(row=1, column=1, padx=10)
        self.display_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=20)
        self.status_frame.grid(row=0, column=3, padx=10, pady=0, sticky="EW")
        self.outputs_frame.grid(row=1, column=3, padx=10, pady=0)

        # Embed matplotlib object
        self.fig, self.ax = plt.subplots(figsize=(4, 3),
                                          constrained_layout=True)
        self.ax.set_xlabel("Volume Added (L)")
        self.ax.set_ylabel("Emf (mV)")
        self.canvas = FigureCanvasTkAgg(self.fig, self.display_frame)
        self.canvas.get_tk_widget().grid(
            row=0, column=0, rowspan=1, columnspan=1, sticky="NSEW"
        )
        self.canvas.draw()

    def connect_devices(self) -> bool:
        """Opens serial connections to the pump and pH meter.

        Args:
            None.

        Returns:
            bool: True if all connections are successful, False otherwise.
        """
        pump_serial = self.pump.open_serial_port()
        if not pump_serial:
            tk.messagebox.showerror(
                "Error", "Pump serial connection failed."
            )
            return False

        pump_init = self.pump.initialize_pump()
        if not pump_init['host_ready']:
            tk.messagebox.showerror(
                "Error", "Pump initialization failed."
            )
            return False

        ph_meter_serial = self.ph_meter.open_serial_port()
        if not ph_meter_serial:
            tk.messagebox.showerror(
                "Error", "pH meter serial connection failed."
            )
            return False

        self._system_state = SystemStates.READY
        self.status_label.configure(text="Ready", fg="green")
        tk.messagebox.showinfo(
            "Success", "Device connection successful."
        )
        return True

    def check_pump_ready(self) -> bool:
        """Checks if the pump module initializes properly. Called on startup.

        Args:
            None.

        Returns:
            bool: True if ready, False otherwise.
        """
        init_pump = self.pump.initialize_pump()
        if not init_pump['host_ready']:
            tk.messagebox.showerror(
                "Error", "Pump connection failed."
            )
            return False
        return True

    def check_ph_meter_ready(self) -> bool:
        """Checks if the pH meter is giving valid readings. Called on startup.

        Args:
            None.

        Returns:
            bool: True if ready, False otherwise.
        """
        test_measurement = self.ph_meter.get_measurement()
        if not test_measurement:
            tk.messagebox.showerror(
                "Error", "pH meter connection failed."
            )
            return False
        return True

    def disable_inputs(self) -> None:
        """Helper function to disable all UI inputs at once at the
        beginning of a run.

        Args:
            None.

        Returns:
            None.
        """
        self.initial_mass_input.configure(state=tk.DISABLED)
        self.salinity_input.configure(state=tk.DISABLED)
        self.acid_conc_input.configure(state=tk.DISABLED)

    def enable_inputs(self) -> None:
        """Helper function to re-enable all UI inputs at once after
        a run has ended.

        Args:
            None.

        Returns:
            None.
        """
        self.initial_mass_input.configure(state=tk.NORMAL)
        self.salinity_input.configure(state=tk.NORMAL)
        self.acid_conc_input.configure(state=tk.NORMAL)

    def clear_display(self) -> None:
        """Clears the display data from the last run.

        Args:
            None.

        Returns:
            None.
        """
        self.ax.clear()
        self.ax.set_xlabel("Volume Added (L)")
        self.ax.set_ylabel("Emf (mV)")
        self.canvas.draw()

    def reset_interface(self) -> None:
        """Resets all the interface elements at the end of a run.

        Args:
            None.

        Returns:
            None.
        """
        self.enable_inputs()
        self.clear_inputs()
        self.enable_manual_controls()

    def check_inputs(self) -> Tuple[bool, float, float, float]:
        """Checks if the user has provided all the necessary information
        about the sample before the run.

        Args:
            None.

        Returns:
            tuple containing:
             - bool: True if all inputs are valid, False otherwise.
             - float: user-provided sample mass casted to float.
             - float: user-provided salinity casted to float.
             - float: user-provided acid concentration casted to float.
        """
        sample_mass_input_value = self.initial_mass_input.get()
        salinity_input_value = self.salinity_input.get()
        acid_conc_input_value = self.acid_conc_input.get()

        inputs_valid = True
        try:
            sample_mass = float(sample_mass_input_value)
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Please provide a valid value for sample mass."
            )
            inputs_valid = False

        try:
            salinity = float(salinity_input_value)
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Please provide a valid value for salinity."
            )
            inputs_valid = False

        try:
            acid_conc = float(acid_conc_input_value)
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Please provide a valid value for acid concentration."
            )
            inputs_valid = False

        if not inputs_valid:
            return inputs_valid, 0, 0, 0

        return inputs_valid, sample_mass, salinity, acid_conc

    def disable_manual_controls(self) -> None:
        """Helper function to disable all manual controls at the beginning
        of a run.

        Args:
            None.

        Returns:
            None.
        """
        self.start_button.configure(state=tk.DISABLED)
        self.fill_button.configure(state=tk.DISABLED)
        self.empty_button.configure(state=tk.DISABLED)
        self.wash_button.configure(state=tk.DISABLED)
        self.connect_devices_button.configure(state=tk.DISABLED)

    def enable_manual_controls(self) -> None:
        """Helper function to re-enable all manual controls at the end of a run.

        Args:
            None.

        Returns:
            None.
        """
        self.start_button.configure(state=tk.NORMAL)
        self.fill_button.configure(state=tk.NORMAL)
        self.empty_button.configure(state=tk.NORMAL)
        self.wash_button.configure(state=tk.NORMAL)
        self.connect_devices_button.configure(state=tk.NORMAL)

    def clear_inputs(self) -> None:
        """Helper function to clear UI inputs before the next run.

        Args:
            None.

        Returns:
            None.
        """
        self.initial_mass_input.delete(0, tk.END)
        self.salinity_input.delete(0, tk.END)
        self.acid_conc_input.delete(0, tk.END)

        self.temperature_input.configure(state=tk.NORMAL)
        self.temperature_input.delete(0, tk.END)
        self.temperature_input.configure(state=tk.DISABLED)

    def clear_outputs(self) -> None:
        """Helper function to clear UI outputs before the next run.

        Args:
            None.

        Returns:
            None.
        """
        self.total_alk_output.configure(text="N/A")

    def update_ta_output(self, value: float) -> None:
        """Updates the total alkalinity reading at the end of a run.

        Args:
            value (float): the estimated total alkalinity resulting from
                the titration process.

        Returns:
            None.
        """
        self.total_alk_output.configure(text=str(round(value, 3)))

    def get_phmeter_measurements(self) -> Tuple[float, float, float]:
        """Polls the pH meter for the current measurements of pH, emf,
        and temperature.

        Args:
            None.

        Returns:
            tuple containing:
             - float: pH value from the meter casted to float.
             - float: emf value from the meter casted to float.
             - float: temperature value from the meter casted to float.
        """
        try:
            meas = self.ph_meter.get_measurement()
        except IndexError as e:
            logger.info("pH measurement failed, trying again...")
            meas = self.ph_meter.get_measurement()

        ph_meas = meas["pH"]
        emf_meas = meas["mV"]
        temp_meas = meas["temp"]

        return float(ph_meas), float(emf_meas), float(temp_meas)

    def start_titration(self) -> None:
        """Starts the main titration routine after gathering the
        necessary data.

        Args:
            None.

        Returns:
            None.
        """

        if self._system_state == SystemStates.DISCONNECTED:
            tk.messagebox.showerror(
                "Error", "Please connect devices before starting."
            )
            return

        self.disable_inputs()
        self.disable_manual_controls()
        self.clear_display()
        self.clear_outputs()

        inputs_valid, sample_mass, salinity, acid_conc = self.check_inputs()

        if not inputs_valid:
            self.enable_inputs()
            self.enable_manual_controls()
            return

        self.status_label.configure(text="Waiting for pH measurement...")
        # For some unknown reason, unless there's a small sleep here
        # tk will go immediately to the ph measurement without updating the UI
        self.tksleep(1)

        ph_init, emf_init, temp_init = self.get_phmeter_measurements()

        self.status_label.configure(text="Titration in progress")

        self.temperature_input.configure(state=tk.NORMAL)
        self.temperature_input.insert(0, temp_init)
        self.temperature_input.configure(state=tk.DISABLED)

        titration = gran.ModifiedGranTitration(
            sample_mass, salinity, acid_conc, temp_init, ph_init, emf_init
        )

        self._system_state = SystemStates.RUNNING

        logger.info("Filling syringe...")
        self.pump.fill()
        self.tksleep(15)

        self.initial_titration(titration)

    def initial_titration(self, titration: gran.ModifiedGranTitration) -> None:
        """Runs the initial titration procedure from the starting pH to
        the first target pH where data will be collected.

        Args:
            titration (ModifiedGranTitration): gran titration object.

        Returns:
            None.
        """
        if self._stop_titration:
            self.handle_stop_command(self.initial_titration)
            return

        last_ph = titration.get_last_ph()

        # Check if last pH reading is below target, if so move to next step
        if last_ph < FIRST_TITRATION_PH_TARGET:
            self.after_cancel(self.initial_titration)
            logger.info("Reached pH target. Moving to second titration step...")
            self.auto_titration(titration)
            return

        # Shoot for slightly below target to make sure target is reached
        stepwise_ph_target = FIRST_TITRATION_PH_TARGET - 0.01

        self.run_titration_step(titration, stepwise_ph_target)

        # Schedule next titration step, setting time=0 makes it run
        # immediately whenever the mainloop is not busy
        self.after(0, self.initial_titration, titration)

    def auto_titration(self, titration: gran.ModifiedGranTitration) -> None:
        """Runs the second titration, in smaller steps, to collect data
        for the total alkalinity estimate.

        Args:
            titration (ModifiedGranTitration): gran titration object.

        Returns:
            None.
        """
        if self._stop_titration:
            self.handle_stop_command(self.auto_titration)
            return

        last_ph = titration.get_last_ph()

        # Check if last pH reading is below target, if so stop the routine
        # and run calculations
        if last_ph < SECOND_TITRATION_PH_TARGET:
            self.status_label.configure(text="Finished", fg="green")
            logger.info("Titration finished.")
            logger.info(f"Final pH: {last_ph}")
            self.finish_titration(titration)
            return

        # Collect data moving downward in steps of 0.1 pH
        stepwise_ph_target = last_ph - 0.1

        self.run_titration_step(titration, stepwise_ph_target)

        # Schedule next titration step, setting time=0 makes it run
        # immediately whenever the mainloop is not busy
        self.after(0, self.auto_titration, titration)

    def run_titration_step(self, titration: gran.ModifiedGranTitration,
                                  ph_target: float) -> None:
        """Handles the addition of acid and gathers measurements at
        each individual titration step.

        Args:
            titration (ModifiedGranTitration): gran titration object.
            ph_target (float): desired pH at the end of the step.

        Returns:
            None.
        """
        # Get the volume of acid required to dose at the next step, in liters
        required_acid_vol_liters = titration.calc_required_acid_vol(ph_target)

        required_acid_vol_ul = round(required_acid_vol_liters * 1e6, 2)

        if not self.pump.check_volume_available(required_acid_vol_liters):
            logger.info("Volume low, re-filling...")
            self.pump.fill()
            self.tksleep(15)

        # Dispense required volume of acid
        logger.info(f"Dispensing: {required_acid_vol_ul} uL")
        self.pump.dispense(required_acid_vol_liters)
        self.status_label.configure(text="Dosing...")

        # Wait 5 seconds to dispense acid
        self.tksleep(5)

        self.status_label.configure(text="Waiting for pH measurement...")
        self.tksleep(1)

        # Take pH, emf measurements -- this call is blocking
        pH, emf, _ = self.get_phmeter_measurements()
        logger.info(f"pH: {pH}, emf: {emf}")

        self.status_label.configure(text="Titration in progress")

        # Add last measurements to titration
        titration.add_step_data(pH, emf, required_acid_vol_liters)

        # Plot current step
        self.plot(titration.volume_array, titration.emf_array)

    def finish_titration(self, titration: gran.ModifiedGranTitration) -> None:
        """Handles the calculations, writes data, and cleans up after the
        titration is finished.

        Args:
            titration (ModifiedGranTitration): gran titration object.

        Returns:
            None.
        """
        self.after_cancel(self.auto_titration)

        total_alkalinity, gamma, rsq = titration.gran_polynomial_fit()
        logger.info(f"TA: {total_alkalinity}, Gamma: {gamma}, Rsq: {rsq}")

        self.update_ta_output(total_alkalinity)

        self.write_data(titration, total_alkalinity)

        self.reset_interface()

        tk.messagebox.showinfo(
            "Info", "Titration finished."
        )
        self._system_state = SystemStates.READY
        self.status_label.configure(text="Ready", fg="green")

    def handle_stop_command(self, func: Callable) -> None:
        """Handles the stop command when requested in the middle of a run.

        Args:
            func (Callable): the titration function to cancel. Should be either
                self.initial_titration or self.auto_titration.

        Returns:
            None.
        """
        self.after_cancel(func)
        logger.info("Titration cancelled.")
        self._stop_titration = False

        self.reset_interface()
        self._system_state = SystemStates.READY
        self.status_label.configure(text="Ready", fg="green")

        tk.messagebox.showinfo(
            "Info", "Titration cancelled."
        )

    def plot(self, x: np.ndarray, y: np.ndarray) -> None:
        """Displays the updated titration data on the UI after each step.

        Args:
            x (np.ndarray): array of volume measurements.
            y (np.ndarray): array of emf measurements.

        Returns:
            None.
        """
        if len(x) >= 3:
            self.ax.scatter(x[2:], y[2:], color="blue")
            self.ax.autoscale()
            self.canvas.draw()

    def write_data(self, titration: gran.ModifiedGranTitration,
                      total_alkalinity: float) -> None:
        """Dumps the titration data to a csv file on the host.

        Args:
            titration (ModifiedGranTitration): gran titration object.
            total_alkalinity (float): estimated total alkalinity value.

        Returns:
            None.
        """
        filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

        header = ["total_volume_added_L", "emf_mV", "pH", "sample_mass_g",
                  "temp_C", "salinity", "acid_conc_M", "total_alk_umol_kg"]

        with open(filename + ".csv", "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(header)

            firstrow = [titration.volume_array[0], titration.emf_array[0],
                titration.ph_array[0], titration.sample_mass_kg * 1000,
                titration.temp_K - 273.15, titration.salinity,
                titration.acid_conc_M, round(total_alkalinity, 3)]
            writer.writerow(firstrow)

            for vol,emf,ph in zip(titration.volume_array[1:],
                    titration.emf_array[1:], titration.ph_array[1:]):
                rowarray = [vol, emf, ph]
                writer.writerow(rowarray)

    def stop_titration(self) -> None:
        """Gives the signal to stop the titration process in the middle
        of a run.

        Args:
            None.

        Returns:
            None.
        """
        if not self._system_state == SystemStates.RUNNING:
            return

        self._stop_titration = True
        logger.info("Stopping titration before next step...")
        self._system_state = SystemStates.STOPPING
        self.status_label.configure(text="Stopping...", fg="red")

    def tksleep(self, time: float) -> None:
        """Tkinter-compatible emulation of time.sleep(seconds).

        Args:
            time (float): time (in seconds) to wait before proceeding.

        Returns:
            None.
        """
        self.after(time * 1000, self._sleep_var.set, 1)
        self.wait_variable(self._sleep_var)

    def quit_program(self):
        """Handles any close event and prompts for confirmation.

        Args:
            None.

        Returns:
            None.
        """
        msg = "Are you sure you want to quit?"
        if self._system_state == SystemStates.RUNNING:
            msg = "   ***Titration in progress***\nAre you sure you want to quit?"

        mb = tk.messagebox.askyesnocancel("Warning", msg)
        if mb:
            self.quit()
        else:
            return
