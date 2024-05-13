import numpy as np
from scipy.stats import norm
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk

class HimalayaOptionPricer:
    """Monte Carlo simulator for Himalaya options.

    Args:
        initial_asset_values (list): Initial stock prices for each asset.
        strike_price (float): Strike price of the option.
        volatility (float): Volatility of the asset prices.
        mean (float): Drift or mean of the asset prices.
        num_simulations (int): Number of Monte Carlo simulations.
        num_assets (int): Number of assets.
        confidence_level (float): Confidence level for calculating bounds.

    Methods:
        generate_time_vector(): Generates the time vector.
        simulate_trajectory(time_vector): Simulates asset price trajectories.
        calculate_payoff(trajectory): Calculates the payoff based on Himalaya option logic.
        simulate_monte_carlo(): Performs Monte Carlo simulations.
        monte_carlo_convergence(payoffs): Calculates convergence metrics.
        generate_convergence_curve(): Generates the convergence curve.

    Attributes:
        initial_asset_values (list): Initial stock prices for each asset.
        strike_price (float): Strike price of the option.
        volatility (float): Volatility of the asset prices.
        mean (float): Drift or mean of the asset prices.
        num_simulations (int): Number of Monte Carlo simulations.
        num_assets (int): Number of assets.
        confidence_level (float): Confidence level for calculating bounds.
    """

    def __init__(self, initial_asset_values, strike_price, volatility, mean, num_simulations, num_assets, confidence_level):
        self.initial_asset_values = initial_asset_values
        self.strike_price = strike_price
        self.volatility = volatility
        self.mean = mean
        self.num_simulations = num_simulations
        self.num_assets = num_assets
        self.confidence_level = confidence_level

    def generate_time_vector(self):
        """Generates the time vector.

        Returns:
            list: Time vector.
        """
        return [i for i in range(self.num_assets)]

    def simulate_trajectory(self, time_vector):
        """Simulates asset price trajectories.

        Args:
            time_vector (list): Time vector.

        Returns:
            list: List of asset price trajectories.
        """
        trajectories = []
        for i in range(len(self.initial_asset_values)):
            trajectory = [np.log(self.initial_asset_values[i])]
            for j in range(1, len(time_vector)):
                dt = time_vector[j] - time_vector[j-1]
                trajectory.append(trajectory[-1] + (self.mean - (self.volatility**2) / 2) * dt + self.volatility * np.sqrt(dt) * np.random.normal(0, 1))
            trajectories.append(trajectory)
        return trajectories

    def calculate_payoff(self, trajectory):
        """Calculates the payoff based on Himalaya option logic.

        Args:
            trajectory (list): Asset price trajectory.

        Returns:
            float: Payoff of the option.
        """
        payoffs = [np.exp(trajectory[j]) for j in range(len(trajectory))]
        max_payoff = np.max(payoffs)
        return np.max(max_payoff - self.strike_price, 0)

    def simulate_monte_carlo(self):
        """Performs Monte Carlo simulations.

        Returns:
            list: List of payoffs from each simulation.
        """
        time_vector = self.generate_time_vector()
        payoffs = []
        for _ in range(self.num_simulations):
            trajectories = self.simulate_trajectory(time_vector)
            payoffs.append(self.calculate_payoff(trajectories))
        return payoffs

    def monte_carlo_convergence(self, payoffs):
        """Calculates convergence metrics.

        Args:
            payoffs (list): List of payoffs.

        Returns:
            tuple: Moving average, lower bound, and upper bound.
        """
        alpha = norm.ppf(self.confidence_level)
        moving_average = []
        standard_deviation = []
        lower_bound = []
        upper_bound = []
        for i in range(len(payoffs)):
            moving_average.append(np.mean(payoffs[:i + 1]))
            standard_deviation.append(np.std(payoffs[:i + 1]))
            lower_bound.append(moving_average[-1] - alpha * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
            upper_bound.append(moving_average[-1] + alpha * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
        return moving_average, lower_bound, upper_bound

    def generate_convergence_curve(self):
        """Generates the convergence curve.

        Returns:
            Figure: Matplotlib figure for the convergence curve.
        """
        payoffs = self.simulate_monte_carlo()
        moving_average, lower_bound, upper_bound = self.monte_carlo_convergence(payoffs)
        fig = Figure(figsize=(10, 4))
        plot = fig.add_subplot(111)
        plot.plot(range(self.num_simulations - 1), moving_average[1:], 'g', label="Moving Average")
        plot.plot(range(self.num_simulations - 1), lower_bound[1:], 'r', label="Lower Bound")
        plot.plot(range(self.num_simulations - 1), upper_bound[1:], 'r', label="Upper Bound")
        plot.set_xlabel("Number of Simulations")
        plot.set_ylabel("Price")
        final_price = moving_average[-1]
        error = upper_bound[-1] - lower_bound[-1]
        plot.set_title(f"Convergence Curve\nFinal price: {final_price:.4f}, Error: {error:.4f}")
        plot.grid()
        plot.legend()
        return fig


class HimalayaOptionPricerGUI:
    """GUI for Himalaya Option Pricer."""
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.root.geometry('800x800')
        self.root.title('Himalaya Option Pricer')
        self.root['bg'] = '#2471A3'
        self.root.resizable(height=True, width=True)
        self.canvas = None

        style = ttk.Style()
        style.configure('TEntry', padding=(10, 5), relief='flat', background='white', borderwidth=0, bordercolor='#2471A3', focuscolor='none')
        style.configure('TButton', padding=(10, 5), relief='flat', background='#2471A3', borderwidth=0, bordercolor='black', focuscolor='#2471A3', foreground='black')
        style.configure('TLabel', padding=(10, 5), relief='flat', background='#2471A3', borderwidth=0, bordercolor='white', foreground='black')

        self.initial_stock_price_entry = ttk.Entry(self.root, style='TEntry')
        self.strike_price_entry = ttk.Entry(self.root, style='TEntry')
        self.volatility_entry = ttk.Entry(self.root, style='TEntry')
        self.drift_entry = ttk.Entry(self.root, style='TEntry')
        self.num_simulations_entry = ttk.Entry(self.root, style='TEntry')
        self.num_assets_entry = ttk.Entry(self.root, style='TEntry')
        self.maturity_entry = ttk.Entry(self.root, style = 'TEntry')
        self.confidence_interval_entry = ttk.Entry(self.root, style='TEntry')

        initial_stock_price_label = ttk.Label(self.root, text='Initial Stock Price (S_0)', style='TLabel')
        initial_stock_price_label.pack()
        self.initial_stock_price_entry.pack()

        strike_price_label = ttk.Label(self.root, text='Strike Price (K)', style='TLabel')
        strike_price_label.pack()
        self.strike_price_entry.pack()

        drift_label = ttk.Label(self.root, text='Drift (mu)', style='TLabel')
        drift_label.pack()
        self.drift_entry.pack()

        volatility_label = ttk.Label(self.root, text='Volatility (sigma)', style='TLabel')
        volatility_label.pack()
        self.volatility_entry.pack()

        num_simulations_label = ttk.Label(self.root, text='Number of Simulations (Ns)', style='TLabel')
        num_simulations_label.pack()
        self.num_simulations_entry.pack()

        num_assets_label = ttk.Label(self.root, text='Number of Assets (Na)', style='TLabel')
        num_assets_label.pack()
        self.num_assets_entry.pack()

        maturity_label = ttk.Label(self.root, text = 'Maturity', style = 'TLabel')
        maturity_label.pack()
        self.maturity_entry.pack()

        confidence_interval_label = ttk.Label(self.root, text='Confidence Level (alpha)', style='TLabel')
        confidence_interval_label.pack()
        self.confidence_interval_entry.pack()

        self.button = ttk.Button(self.root, text='Generate Convergence Graph', command=self.plot_convergence_curve, style='TButton')
        self.button.pack()

    def plot_convergence_curve(self):
        initial_stock_price_str = self.initial_stock_price_entry.get()
        initial_stock_prices = [float(price) for price in initial_stock_price_str.split(',')]
        strike_price_values = [float(x) for x in self.strike_price_entry.get().split(',')]
        volatility = float(self.volatility_entry.get())
        drift = float(self.drift_entry.get())
        num_simulations = int(self.num_simulations_entry.get())
        confidence_interval = float(self.confidence_interval_entry.get())
        maturity = int(self.maturity_entry.get())

        option_pricer = HimalayaOptionPricer(initial_stock_prices, strike_price_values, volatility, drift, num_simulations, maturity, confidence_interval)
        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()

        fig = option_pricer.generate_convergence_curve()
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()


    def run(self):
        """Run the GUI."""
        self.root.mainloop()


# Run the GUI
option_pricer_gui = HimalayaOptionPricerGUI()
option_pricer_gui.run()
