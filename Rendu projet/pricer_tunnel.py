import numpy as np
from scipy.stats import norm
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class TunnelOptionPricer:
    """
    Pricing tunnel option
    """
    def __init__(self, S_0, K, sigma, mu, Ns, IC, alpha, beta, maturity):
        """
        Initialize the TunnelOptionPricer class with the given parameters.

        Args:
            S_0 (float): Initial asset price
            K (list): Strike prices
            sigma (float): Volatility
            mu (float): Drift
            Ns (int): Number of simulations
            IC (float): Confidence interval
            alpha (float): First coupon rate
            beta (float): Second coupon rate
            maturity (int): Maturity in years
        """
        self.S_0 = S_0
        self.K = K
        self.sigma = sigma
        self.mu = mu
        self.Ns = Ns
        self.IC = IC
        self.alpha = alpha
        self.beta = beta
        self.maturity = maturity

    def generate_t(self):
        """Generates the time vector."""
        return np.arange(0, self.maturity, 1/4)

    def simulate_gbm(self, t):
        S = [self.S_0]
        for i in range(1, len(t)):
            dt = t[i] - t[i-1]
            S.append(S[-1] * np.exp((self.mu-(self.sigma**2)/2)*dt + self.sigma*np.sqrt(dt)*np.random.normal(0, 1)))
        return S

    def payoff(self, S):
        payoff = 0
        for i in S[1:len(S)-1]:
            if self.K[0] < i < self.K[1]:
                payoff += i/self.S_0 * self.alpha
            elif i > self.K[1]:
                payoff += i/self.S_0 * self.beta
            else:
                payoff = 0
        return payoff + np.max([S[-1]/self.S_0 - self.K[1], 0])

    def simulate_monte_carlo(self):
        t = self.generate_t()
        P = []
        for _ in range(self.Ns):
            S = self.simulate_gbm(t)
            P.append(self.payoff(S))
        return P

    def convergence_mc(self, P):
        a = norm.ppf(self.IC)
        M = []
        ET = []
        b_inf = []
        b_sup = []
        for i in range(len(P)):
            M.append(np.mean(P[:i+1]))
            ET.append(np.std(P[:i+1]))
            b_inf.append(M[-1] - a*ET[-1]/np.sqrt(i) if i > 0 else M[-1])
            b_sup.append(M[-1] + a*ET[-1]/np.sqrt(i) if i > 0 else M[-1])
        return M, b_inf, b_sup

    def generate_convergence_curve(self):
        P = self.simulate_monte_carlo()
        M, b_inf, b_sup = self.convergence_mc(P)
        fig = Figure(figsize=(10, 4))
        plot = fig.add_subplot(111)
        plot.plot(range(self.Ns-1), M[1:], 'g', label="Moyenne")
        plot.plot(range(self.Ns-1), b_inf[1:], 'r', label="Borne inférieure")
        plot.plot(range(self.Ns-1), b_sup[1:], 'r', label="Borne supérieure")
        plot.set_xlabel("Nombre de simulations")
        plot.set_ylabel("Prix")
        final_price = M[-1]
        error = b_sup[-1] - b_inf[-1]
        plot.set_title(f"Courbe d'évolution du prix en fonction du nombre de simulation de Monte Carlo\nFinal price: {final_price:.4f}, Error: {error:.4f}")
        plot.grid()
        plot.legend()
        return fig


class OptionPricerGUI:
    """Display GUI for tunnel option pricer."""

    def __init__(self):
        """Initialize the form."""
        self.root = tk.Tk()
        self.root.geometry('800x800')
        self.root.title('Tunnel Option Pricer')
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
        self.alpha_entry = ttk.Entry(self.root, style='TEntry')  # New entry for beta
        self.beta_entry = ttk.Entry(self.root, style='TEntry')  # New entry for beta
        self.maturity_entry = ttk.Entry(self.root, style='TEntry')
        self.confidence_interval_entry = ttk.Entry(self.root, style='TEntry')
        self.num_simulations_entry = ttk.Entry(self.root, style='TEntry')

        initial_stock_price_label = ttk.Label(self.root, text='Initial Stock Price (S_0)', style='TLabel')
        initial_stock_price_label.pack()
        self.initial_stock_price_entry.pack()

        strike_price_label = ttk.Label(self.root, text='Strike Prices (K)', style='TLabel')
        strike_price_label.pack()
        self.strike_price_entry.pack()

        volatility_label = ttk.Label(self.root, text='Volatility (sigma)', style='TLabel')
        volatility_label.pack()
        self.volatility_entry.pack()

        drift_label = ttk.Label(self.root, text='Drift (mu)', style='TLabel')
        drift_label.pack()
        self.drift_entry.pack()


        alpha_label = ttk.Label(self.root, text='Alpha', style='TLabel')
        alpha_label.pack()
        self.alpha_entry.pack()

        beta_label = ttk.Label(self.root, text='Beta', style='TLabel')
        beta_label.pack()
        self.beta_entry.pack()

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
        strike_price_values = [float(x) for x in self.strike_price_entry.get().split(',')]
        volatility = float(self.volatility_entry.get())
        drift = float(self.drift_entry.get())
        alpha = float(self.alpha_entry.get())
        beta = float(self.beta_entry.get())
        num_simulations = int(self.num_simulations_entry.get())
        confidence_interval = float(self.confidence_interval_entry.get())
        maturity = int(self.maturity_entry.get())

        # Create an instance of the OptionPricer
        option_pricer_instance = TunnelOptionPricer(initial_stock_price, strike_price_values, volatility, drift, num_simulations, confidence_interval, alpha, beta, maturity)

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
