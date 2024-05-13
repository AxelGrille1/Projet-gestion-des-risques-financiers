from scipy.stats import norm
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class NapoleonOptionPricer:
    """
    Class for pricing Napoleon option.

    Payoff = Fixed Coupon + min(Cap, Performance)
    """
    def __init__(self, initial_stock_price, volatility, drift, maturity, confidence_interval, num_simulations, fixed_coupon, floor):
        """
        Initializes the NapoleonOptionPricer.

        Args:
            initial_stock_price (float): Initial stock price.
            volatility (float): Volatility.
            drift (float): Drift.
            maturity (float): Maturity of the option in years.
            confidence_interval (float): Confidence interval.
            num_simulations (int): Number of simulations.
            fixed_coupon (float): Fixed coupon.
            floor (float): Floor value for the option.
        """
        self.initial_stock_price = initial_stock_price
        self.volatility = volatility
        self.drift = drift
        self.maturity = maturity
        self.confidence_interval = confidence_interval
        self.num_simulations = num_simulations
        self.fixed_coupon = fixed_coupon
        self.floor = floor

    def generate_t(self):
        """Generates the time vector.

        Returns:
            List: Time vector.
        """
        trading_days_per_year = 252
        t = int(self.maturity * trading_days_per_year)  
        return list(range(t))


    def simulate_geometric_brownian_motion(self, time_vector):
        """
        Simulates a Geometric Brownian Motion (GBM) trajectory.

        Args:
            time_vector (np.ndarray): Time vector.

        Returns:
            List: GBM trajectory.
        """
        S = [self.initial_stock_price]
        for i in range(1, len(time_vector)):
            dt = time_vector[i] - time_vector[i-1]
            S.append(S[-1] * np.exp((self.drift - (self.volatility**2)/2) * dt + self.volatility * np.sqrt(dt) * np.random.normal(0, 1)))
        return S

    def calculate_option_payoff(self, stock_trajectory):
        """
        Calculates the payoff of a given trajectory.

        Args:
            stock_trajectory (List): Trajectory.

        Returns:
            float: Payoff of the option.
        """
        payoff = 0
        for i in range(int(len(stock_trajectory)/12)):
            for j in range(12):
                monthly_returns = [stock_trajectory[j] / stock_trajectory[j - 1] - 1 for j in range(1, len(stock_trajectory))]
                monthly_returns_grouped = [monthly_returns[i:i+12] for i in range(0, len(monthly_returns), 12)]

            for returns_group in monthly_returns_grouped:
                min_monthly_return = min(returns_group) if returns_group else 0
                payoff += max(self.fixed_coupon + min_monthly_return, self.floor)

        return payoff

    def simulate_monte_carlo(self):
        """
        Simulates Ns trajectories and calculates the payoff of each.

        Returns:
            List: The payoff of each trajectory.
        """
        time_vector = self.generate_t()
        payoff_list = []
        for _ in range(self.num_simulations):
            stock_trajectory = self.simulate_geometric_brownian_motion(time_vector)
            payoff_list.append(self.calculate_option_payoff(stock_trajectory))
        return payoff_list

    def monte_carlo_convergence(self, payoff_list):
        """
        Generates Monte Carlo's convergence curve.

        Args:
            payoff_list (List): List of option payoffs.

        Returns:
            M (List): Vector of the moving average.
            lower_bound (List): Vector of the lower bound.
            upper_bound (List): Vector of the upper bound.
        """
        a = norm.ppf(self.confidence_interval)
        moving_average = []
        standard_deviation = []
        lower_bound = []
        upper_bound = []
        for i in range(len(payoff_list)):
            moving_average.append(np.mean(payoff_list[:i+1]))
            standard_deviation.append(np.std(payoff_list[:i+1]))
            lower_bound.append(moving_average[-1] - a * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
            upper_bound.append(moving_average[-1] + a * standard_deviation[-1] / np.sqrt(i) if i > 0 else moving_average[-1])
        return moving_average, lower_bound, upper_bound

    def generate_convergence_curve(self):
        """
        Generates a convergence curve plot.

        Returns:
            Figure: The convergence curve plot.
        """
        payoff_list = self.simulate_monte_carlo()
        moving_average, lower_bound, upper_bound = self.monte_carlo_convergence(payoff_list)
        fig = Figure(figsize=(10, 4))
        plot = fig.add_subplot(111)
        plot.plot(range(self.num_simulations-1), moving_average[1:], 'g', label="Moyenne")
        plot.plot(range(self.num_simulations-1), lower_bound[1:], 'r', label="Borne inférieure")
        plot.plot(range(self.num_simulations-1), upper_bound[1:], 'r', label="Borne supérieure")
        plot.set_xlabel("Nombre de simulations")
        plot.set_ylabel("Prix")
        final_price = moving_average[-1]
        error = upper_bound[-1] - lower_bound[-1]
        plot.set_title(f"Courbe d'évolution du prix en fonction du nombre de simulation de Monte Carlo\nFinal price: {final_price:.4f}, Error: {error:.4f}")
        plot.grid()
        plot.legend()
        return fig


class NapoleonOptionPricerGUI:
    """Display GUI for Napoleon option pricer."""

    def __init__(self):
        """Initialize the form."""
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.title('Napoleon Option Pricer')
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
        self.volatility_entry = ttk.Entry(self.root, style='TEntry')
        self.drift_entry = ttk.Entry(self.root, style='TEntry')
        self.maturity_entry = ttk.Entry(self.root, style='TEntry')
        self.confidence_interval_entry = ttk.Entry(self.root, style='TEntry')
        self.num_simulations_entry = ttk.Entry(self.root, style='TEntry')
        self.fixed_coupon_entry = ttk.Entry(self.root, style='TEntry')
        self.floor_entry = ttk.Entry(self.root, style='TEntry')

        initial_stock_price_label = ttk.Label(self.root, text='Initial Stock Price (S_0)', style='TLabel')
        initial_stock_price_label.pack()
        self.initial_stock_price_entry.pack()

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

        fixed_coupon_label = ttk.Label(self.root, text='Fixed Coupon', style='TLabel')
        fixed_coupon_label.pack()
        self.fixed_coupon_entry.pack()

        floor_label = ttk.Label(self.root, text='Floor', style='TLabel')
        floor_label.pack()
        self.floor_entry.pack()

        self.button = ttk.Button(self.root, text='Generate Convergence Graph', command=self.plotConvergence, style='TButton')
        self.button.pack()

    def plotConvergence(self):
        initial_stock_price = float(self.initial_stock_price_entry.get())
        volatility = float(self.volatility_entry.get())
        drift = float(self.drift_entry.get())
        maturity = float(self.maturity_entry.get())
        confidence_interval = float(self.confidence_interval_entry.get())
        num_simulations = int(self.num_simulations_entry.get())
        fixed_coupon = float(self.fixed_coupon_entry.get())
        floor = float(self.floor_entry.get())

        # Create an instance of the NapoleonOptionPricer
        option_pricer_instance = NapoleonOptionPricer(initial_stock_price, volatility, drift, maturity, confidence_interval, num_simulations, fixed_coupon, floor)

        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()

        fig = option_pricer_instance.generate_convergence_curve()
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def run(self):
        self.root.mainloop()

# Run the GUI
option_pricer_gui = NapoleonOptionPricerGUI()
option_pricer_gui.run()
