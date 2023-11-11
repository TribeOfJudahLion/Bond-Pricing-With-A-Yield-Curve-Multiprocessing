import pandas as pd
import numpy as np
from multiprocessing import Pool
import time  # Import time module for benchmarking


def read_yield_curve(file_path):
    return pd.read_csv(file_path)


def read_bond_data(file_path):
    return pd.read_csv(file_path)


def calculate_bond_price(yield_curve, face_value, coupon_rate, frequency, maturity):
    maturity = int(maturity)
    frequency = int(frequency)
    price = 0
    for period in range(1, maturity * frequency + 1):
        cash_flow = (face_value * coupon_rate) / frequency if period < maturity * frequency else (
                                                                                                         face_value * coupon_rate) / frequency + face_value
        yield_rate = np.interp(period / frequency, yield_curve['Maturity'], yield_curve['Yield']) / 100
        discounted_cash_flow = cash_flow / ((1 + yield_rate / frequency) ** period)
        price += discounted_cash_flow
    return price


def bond_pricing_worker(args):
    return calculate_bond_price(*args)


def calculate_bond_prices_parallel(yield_curve, bonds, num_workers=20):
    with Pool(processes=num_workers) as pool:
        results = pool.map(bond_pricing_worker, [(yield_curve, *bond) for bond in bonds])
    return results


if __name__ == "__main__":
    start_time = time.time()  # Start timing

    yield_curve_file_path = 'yield_curve.csv'
    bond_file_path = 'bonds.csv'

    # Reading data timing
    read_start_time = time.time()
    yield_curve = read_yield_curve(yield_curve_file_path)
    bond_data = read_bond_data(bond_file_path)
    read_end_time = time.time()

    bonds = bond_data[['Face Value', 'Coupon Rate', 'Frequency', 'Maturity']].values.tolist()
    num_workers = 8  # Number of workers

    # Calculation timing
    calc_start_time = time.time()
    prices = calculate_bond_prices_parallel(yield_curve, bonds, num_workers=num_workers)
    calc_end_time = time.time()

    # Formatting and saving output
    output_lines = []
    for i, (bond, price) in enumerate(zip(bonds, prices)):
        line = f"Bond {i + 1}: Face Value: ${bond[0]}, Coupon Rate: {bond[1] * 100}%, Frequency: {bond[2]} per year, Maturity: {bond[3]} years, Price: ${price:.2f}"
        output_lines.append(line)

    with open('bond_pricing_results.txt', 'w') as file:
        file.write('\n'.join(output_lines))

    end_time = time.time()  # End timing

    # Print execution times
    print(f"Total Execution Time: {end_time - start_time} seconds")
    print(f"Data Reading Time: {read_end_time - read_start_time} seconds")
    print(f"Calculation Time: {calc_end_time - calc_start_time} seconds")
    print("Results saved to bond_pricing_results.txt")
