# Librairies
import math
import tkinter as tk
from tkinter import ttk
import pandas as pd


file_path = "/Users/axelgrille/Documents/Cours/Gestion des risques/Credit_Portfolio.xlsx"

# Reading the rating codes
rating_codes = pd.read_excel(
    file_path,
    sheet_name="Params",
    usecols="A",
    skiprows=5,
    nrows=19,
    header=None
).iloc[:, 0].tolist()

PD_Y1 = pd.read_excel(
    file_path,
    sheet_name="Params",
    usecols="B",
    skiprows=5,
    nrows=19,
    header=None
).iloc[:, 0].to_dict()

PD_Y3 = pd.read_excel(
    file_path,
    sheet_name="Params",
    usecols="C",
    skiprows=5,
    nrows=19,
    header=None
).iloc[:, 0].to_dict()

PD_Y5 = pd.read_excel(
    file_path,
    sheet_name="Params",
    usecols="D",
    skiprows=5,
    nrows=19,
    header=None
).iloc[:, 0].to_dict()

# Creating dictionaries for each maturity year with rating codes as keys
PD_Y1 = {rating_codes[i]: PD_Y1[i] for i in range(len(rating_codes))}
PD_Y3 = {rating_codes[i]: PD_Y3[i] for i in range(len(rating_codes))}
PD_Y5 = {rating_codes[i]: PD_Y5[i] for i in range(len(rating_codes))}

MaturityYear = {1: PD_Y1, 3: PD_Y3, 5: PD_Y5}

countryList = [["France", 0.60, "Ba1", 0.35], ["Etats-Unis", 0.4, "Baa1", 0.2], ["Autres", 0.65, "B1", 0.5]]

# Exemple de données pour les garanties
warrantiesTab = {"Immobilier": 0.20, "Titres": 0.3, "Véhicule": 0.4, "Autres": 0.5}


class RarocDefault:
    """
    This class sets the standard parameters for any RaRoC
    """

    def __init__(self, correlation, f, credit, liquidity, TSR, taxRate):
        """
        Initialize RaRoC default parameters.

        Parameters:
        - correlation: Correlation coefficient
        - f: Factor
        - credit: credit factor
        - liquidity: Liquidity factor
        - TSR: Total Shareholder Return factor
        - taxRate: Tax rate
        """
        self.correlation = correlation
        self.f = f
        self.credit = credit
        self.liquidity = liquidity
        self.TSR = TSR
        self.taxRate = taxRate


class CustomerMaturity:
    """
    This class represents customer's maturity
    """

    def __init__(self, warranties, warrantAmount):
        """
        Initialize customer's maturity parameters.

        Parameters:
        - warranties: Type of warranties
        - warrantAmount: Warrant amount
        """
        self.warranties = warranties
        self.warrantAmount = warrantAmount


class CustomerData:
    """
    This class represents the customer who takes a credit
    """

    def __init__(self, autorization, utilization, maturity, rating, country):
        """
        Initialize customer data.

        Parameters:
        - autorization: Authorization amount
        - utilization: Utilization rate
        - maturity: Maturity period
        - rating: Credit rating
        - country: Country of the customer
        """
        self.autorization = autorization
        self.utilization = utilization
        self.maturity = maturity
        self.rating = rating
        self.country = country


def creditWarranties(customerMaturity):
    """
    Calculate the value of credit warranties.

    Parameters:
    - customerMaturity: Customer's maturity object

    Returns:
    - value of credit warranties
    """
    haircut = warrantiesTab.get(customerMaturity.warranties)
    value = int(customerMaturity.warrantAmount) * (1 - haircut)
    return value


def countryData(customerData):
    """
    Get country data.

    Parameters:
    - customerData: Customer's data object

    Returns:
    - Tuple with LGD (Loss Given Default), country rating, and transfer rate
    """
    for i in countryList:
        if i[0] == customerData.country:
            lgdCountry = i[1]
            countryRating = i[2]
            transferRate = i[3]
    return lgdCountry, countryRating, transferRate


def rarocCalcul(margin, customerData, customerMaturity, EAD, RarocDefault):
    """
    Calculate RAROC (Risk-Adjusted Return on Capital).

    Parameters:
    - margin: Profit margin
    - customerData: Customer's data object
    - customerMaturity: Customer's maturity object
    - EAD: Exposure at Default
    - RarocDefault: RarocDefault object
    """
    pnbCredit = round(float(customerData.autorization) * margin)
    print(f"PNB: {pnbCredit}")

    creditCost = round(float(RarocDefault.liquidity) * pnbCredit)
    print(f"Credit Cost : {creditCost}")

    liquidityCost = round(float(customerData.autorization) * float(RarocDefault.liquidity))
    print(f"Liquidity Cost : {liquidityCost}")

    credit = pnbCredit - creditCost - liquidityCost
    lgd, countryRating, transferRate = countryData(customerData)

    countryPD = round(MaturityYear.get(int(customerData.maturity)).get(countryRating), 2)

    if countryPD > MaturityYear.get(int(customerData.maturity)).get(customerData.rating):
        pdAdjusted = MaturityYear.get(int(customerData.maturity)).get(customerData.rating) * (1 - transferRate) + countryPD * transferRate
    else:
        pdAdjusted = MaturityYear.get(int(customerData.maturity)).get(customerData.rating)

    print(f"LGD : {lgd * 100} %")
    print(f"EAD : {EAD}")
    print(f"garantiesCredit : {creditWarranties(customerMaturity)}")

    expectedLoss = round(
        pdAdjusted * lgd * (EAD - creditWarranties(customerMaturity)), 3)  # calcul EL
    print(f"Expected Loss : {expectedLoss}")

    riskAdjusted = credit - expectedLoss

    economicCapital = round(
        float(RarocDefault.f) *
        math.sqrt(float(RarocDefault.correlation) *
                  pdAdjusted * (1 - pdAdjusted)) * lgd *
        (EAD - creditWarranties(customerMaturity)), 3)
    print(f"Economic Capital : {economicCapital}")

    ecoCapital = economicCapital * float(RarocDefault.TSR)
    taxes = (ecoCapital + riskAdjusted) * float(RarocDefault.taxRate)
    raroc = (riskAdjusted + ecoCapital - taxes) / economicCapital

    print(f"RAROC : {raroc} %")

def load_and_display_portfolio_data():
    """
    Load data from an Excel file and display the first 10 rows of the 'Portfolio' table.
    The Excel file path is hardcoded in the function.

    Returns:
    pandas.DataFrame or str: The first 10 rows of the 'Portfolio' table, or an error message.
    """
    try:
        # Load the Excel file from a specified path
        data = pd.read_excel(file_path, sheet_name="Portfolio", header=0)

        # Return the first 10 rows
        return data.head(10)
    except Exception as e:
        return f"An error occurred: {e}"

#print(load_and_display_portfolio_data())


# Création d'instances de classes
raroc_default = RarocDefault(correlation=0.5, f=0.1, credit=0.05, liquidity=0.02, TSR=0.1, taxRate=0.3)

customer_maturity = CustomerMaturity(warranties="Immobilier", warrantAmount=100000)

customer_data = CustomerData(autorization=500000, utilization=0.4, maturity=5, rating="Ba2", country="France")

# Appel de la fonction rarocCalcul
rarocCalcul(margin=0.02, customerData=customer_data, customerMaturity=customer_maturity, EAD=200000, RarocDefault=raroc_default)


class RarocCalculatorGUI:

    """Graphical User Interface for RaRoC calculation.

    This class creates a simple user interface using Tkinter to collect the
    necessary data and then call the RaRoC calculation function.

    Attributes:
        root (tk.Tk): The main window of the graphical interface.

    Methods:
        __init__(self, root):
            Initializes the graphical interface and creates the necessary widgets.

        create_widgets(self):
            Creates the necessary widgets for data input.

        plot_result(self):
            Calls the RaRoC calculation function with the provided data and
            displays the result in a pop-up window.

        run(self):
            Runs the Tkinter main loop for the graphical interface.

    """
    def __init__(self, root):
        """Initialize the graphical interface."""

        self.root = root
        self.root.title("RaRoC Calculator")
        self.root.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        """Create necessary widgets for data input."""
        self.label_margin = ttk.Label(self.root, text="Marge:")
        self.entry_margin = ttk.Entry(self.root)

        self.label_autorization = ttk.Label(self.root, text="Autorisation:")
        self.entry_autorization = ttk.Entry(self.root)

        self.label_utilization = ttk.Label(self.root, text="Utilisation:")
        self.entry_utilization = ttk.Entry(self.root)

        self.label_maturity = ttk.Label(self.root, text="Maturité:")
        self.entry_maturity = ttk.Entry(self.root)

        self.label_rating = ttk.Label(self.root, text="Note:")
        self.entry_rating = ttk.Entry(self.root)

        self.label_country = ttk.Label(self.root, text="Pays:")
        self.entry_country = ttk.Entry(self.root)

        self.button_calculate = ttk.Button(self.root, text="Calculer", command=self.calculate_raroc)

        # Positionnement des widgets
        self.label_margin.grid(row=0, column=0, pady=5)
        self.entry_margin.grid(row=0, column=1, pady=5)

        self.label_autorization.grid(row=1, column=0, pady=5)
        self.entry_autorization.grid(row=1, column=1, pady=5)

        self.label_utilization.grid(row=2, column=0, pady=5)
        self.entry_utilization.grid(row=2, column=1, pady=5)

        self.label_maturity.grid(row=3, column=0, pady=5)
        self.entry_maturity.grid(row=3, column=1, pady=5)

        self.label_rating.grid(row=4, column=0, pady=5)
        self.entry_rating.grid(row=4, column=1, pady=5)

        self.label_country.grid(row=5, column=0, pady=5)
        self.entry_country.grid(row=5, column=1, pady=5)

        self.button_calculate.grid(row=6, column=0, columnspan=2, pady=10)

    def calculate_raroc(self):
        """Call the RaRoC calculation function and display the result."""

        margin = float(self.entry_margin.get())
        autorization = float(self.entry_autorization.get())
        utilization = float(self.entry_utilization.get())
        maturity = float(self.entry_maturity.get())
        rating = self.entry_rating.get()
        country = self.entry_country.get()

        # Création des instances nécessaires (RarocDefault, CustomerMaturity, CustomerData)
        raroc_default = RarocDefault(correlation=0.5, f=0.1, loan=0.05, liquidity=0.02, TSR=0.1, taxRate=0.3)
        customer_maturity = CustomerMaturity(warranties="Immobilier", warrantAmount=100000)
        customer_data = CustomerData(autorization=autorization, utilization=utilization, maturity=maturity, rating=rating, country=country)

        # Appel de la fonction rarocCalcul
        rarocCalcul(margin=margin, customerData=customer_data, customerMaturity=customer_maturity, EAD=200000, RarocDefault=raroc_default)


if __name__ == "__main__":
    """Run the Tkinter main loop."""
    root = tk.Tk()
    app = RarocCalculatorGUI(root)
    root.mainloop()
