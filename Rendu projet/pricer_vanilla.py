import numpy as np
from scipy.stats import norm
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk


class McSimul: 
    """
    Class for pricing vanilla options using Monte Carlo simulation.
    
    Attributes:
        initial_stock_price (float): Initial stock price.
        strike_price (float): Strike price.
        volatility (float): Volatility.
        drift (float): Drift.
        maturity (float): Maturity of the option in years.
        confidence_interval (float): Confidence interval.
        num_simulations (int): Number of simulations.
    """
    def __init__(self, initial_stock_price, strike_price, volatility, drift, maturity, confidence_interval, num_simulations):
        self.initial_stock_price = initial_stock_price
        self.strike_price = strike_price
        self.volatility = volatility
        self.drift = drift
        self.maturity = maturity
        self.confidence_interval = confidence_interval
        self.num_simulations = num_simulations

    def generate_time_vector(self):
        """Generate time vector.

        Returns:
            np.ndarray: Time vector.
        """
        t_1 = np.arange(0, 60/252, 1/252)
        t_2 = np.arange(self.maturity-59/252, self.maturity, 1/252)
        return np.concatenate((t_1, t_2), axis=0)

    def simulate_gbm(self, time_vector):
        """Simulate a Geometric Brownian Motion (GBM) trajectory.

        Args:
            time_vector (np.ndarray): Time vector.

        Returns:
            List: GBM trajectory.
        """
        stock_prices = [self.initial_stock_price]
        for i in range(1, len(time_vector)):
            dt = time_vector[i] - time_vector[i-1]
            stock_prices.append(stock_prices[-1] * np.exp((self.drift - (self.volatility**2)/2) * dt + self.volatility * np.sqrt(dt) * np.random.normal(0, 1)))
        return stock_prices

    def calculate_payoff(self, stock_prices):
        """Calculate the payoff of a trajectory.

        Args:
            stock_prices (List): Trajectory.

        Returns:
            float: Payoff of the asset.
        """
        return np.max([np.mean(stock_prices[61:]) / np.mean(stock_prices[:60]) - self.strike_price, 0])

    def simulate_monte_carlo(self):
        """Simulate num_simulations trajectories and calculate the payoff of each.

        Returns:
            List: The payoff of each trajectory.
        """
        time_vector = self.generate_time_vector()
        payoffs = []
        for _ in range(int(self.num_simulations)):
            stock_prices = self.simulate_gbm(time_vector)
            payoffs.append(self.calculate_payoff(stock_prices))
        return payoffs

    def perform_monte_carlo(self, payoffs):
        """Perform a Monte Carlo method.

        Returns:
            moving_average (List): Vector of the moving average.
            lower_bound (List): Vector of the lower bound.
            upper_bound (List): Vector of the upper bound.
        """
        a = norm.ppf(self.confidence_interval)
        moving_average = []
        standard_deviation = []
        lower_bound = []
        upper_bound = []
        for i in range(len(payoffs)):
            moving_average.append(np.mean(payoffs[:i+1]))
            standard_deviation.append(np.std(payoffs[:i+1]))
            lower_bound.append(moving_average[-1] - a * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
            upper_bound.append(moving_average[-1] + a * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
        return moving_average, lower_bound, upper_bound

    def generate_convergence_curve(self):
        """Generate a convergence curve plot.

        Returns:
            Figure: The convergence curve plot.
        """
        payoffs = self.simulate_monte_carlo()
        moving_average, lower_bound, upper_bound = self.perform_monte_carlo(payoffs)
        fig = Figure(figsize=(10, 4))
        plot = fig.add_subplot(111)
        plot.plot(range(int(self.num_simulations)-1), moving_average[1:], 'g', label="Mean")
        plot.plot(range(int(self.num_simulations)-1), lower_bound[1:], 'r', label="Lower boundary")
        plot.plot(range(int(self.num_simulations)-1), upper_bound[1:], 'r', label="Upper boundary")
        plot.set_xlabel("Number of simulations")
        plot.set_ylabel("Price")
        final_price = moving_average[-1]
        error = upper_bound[-1] - lower_bound[-1]
        plot.set_title(f"Price evolution curve as a function of the number of Monte Carlo simulations\nFinal price: {final_price:.4f}, Error: {error:.4f}")
        plot.grid()
        plot.legend()
        return fig



class OptionPricerGUI:
    """Display GUI for vanilla option pricer."""

    def __init__(self):
        """Initialize the form."""
        self.root = tk.Tk()
        self.root.geometry('800x800')
        self.root.title('Vanilla Option Pricer')
        self.root['bg'] = '#2471A3'
        self.root.resizable(height=True, width=True)
        self.canvas = None

        style = ttk.Style()

        # Entry style
        style.configure('TEntry', padding=(10, 5), relief='flat', background='white', borderwidth=0, bordercolor='#2471A3', focuscolor='none')

        # Button style
        style.configure('TButton', padding=(10, 5), relief='flat', background='#2471A3', borderwidth=0, bordercolor='black', focuscolor='#2471A3', foreground='black')

        # Label style
        style.configure('TLabel', padding=(10, 5), relief='flat', background='#2471A3', borderwidth=0, bordercolor='white', foreground='black')



        # Define attributes for input entries
        self.initial_stock_price_entry = ttk.Entry(self.root, style='TEntry')
        self.strike_price_entry = ttk.Entry(self.root, style='TEntry')
        self.volatility_entry = ttk.Entry(self.root, style='TEntry')
        self.drift_entry = ttk.Entry(self.root, style='TEntry')
        self.maturity_entry = ttk.Entry(self.root, style='TEntry')
        self.confidence_interval_entry = ttk.Entry(self.root, style='TEntry')
        self.num_simulations_entry = ttk.Entry(self.root, style='TEntry')

        initial_stock_price_label = ttk.Label(self.root, text='Initial Stock Price (S_0)', style='TLabel')
        initial_stock_price_label.pack()
        self.initial_stock_price_entry.pack()

        strike_price_label = ttk.Label(self.root, text='Strike Price (K)', style='TLabel')
        strike_price_label.pack()
        self.strike_price_entry.pack()

        volatility_label = ttk.Label(self.root, text='Volatility (sigma)', style='TLabel')
        volatility_label.pack()
        self.volatility_entry.pack()

        drift_label = ttk.Label(self.root, text='Drift (mu)', style='TLabel')
        drift_label.pack()
        self.drift_entry.pack()

        maturity_label = ttk.Label(self.root, text='Maturity', style='TLabel')
        maturity_label.pack()
        self.maturity_entry.pack()

        confidence_interval_label = ttk.Label(self.root, text='Confidence Interval (IC)', style='TLabel')
        confidence_interval_label.pack()
        self.confidence_interval_entry.pack()

        num_simulations_label = ttk.Label(self.root, text='Number of Simulations (Ns)', style='TLabel')
        num_simulations_label.pack()
        self.num_simulations_entry.pack()

        self.button = ttk.Button(self.root, text='Generate Convergence Graph', command=self.plotConvergence, style='TButton')
        self.button.pack()

    def plotConvergence(self):
        initial_stock_price = float(self.initial_stock_price_entry.get())
        strike_price = float(self.strike_price_entry.get())
        volatility = float(self.volatility_entry.get())
        drift = float(self.drift_entry.get())
        num_simulations = int(self.num_simulations_entry.get())
        confidence_interval = float(self.confidence_interval_entry.get())
        maturity = int(self.maturity_entry.get())

        # Create an instance of the OptionPricer
        option_pricer_instance = McSimul(initial_stock_price, strike_price, volatility, drift, maturity, confidence_interval, num_simulations)

        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()

        fig = option_pricer_instance.generate_convergence_curve()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def run(self):
        self.root.mainloop()

# Run the GUI
option_pricer_gui = OptionPricerGUI()
option_pricer_gui.run()
