import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


def randomized_response(value, epsilon=1.0):
    """
    Apply randomized response to a binary value.
    Args:
    value (int): The original binary value (0 or 1).
    epsilon (float): Privacy budget parameter.

    Returns:
    int: The noised value (0 or 1).
    """
    p = np.exp(epsilon) / (1 + np.exp(epsilon))
    if np.random.rand() < p:
        return value
    else:
        return 1 - value


# We first retrieve the original counts, then we perturbate the bits for a noised count,
# and lastly we denoise the result to get our statistic for a comparing it with the original counts
def analyze_data(data, epsilon=1.0):
    original_count = data['HvyAlcoholConsump'].sum()
    data.loc[:, 'HvyAlcoholConsump_noised'] = data['HvyAlcoholConsump'].apply(lambda x: randomized_response(x, epsilon))

    noised_count = data['HvyAlcoholConsump_noised'].sum()

    # Denoise the count
    total_count = len(data)
    p = np.exp(epsilon) / (1 + np.exp(epsilon))
    denoised_proportion = (noised_count / total_count - (1 - p)) / (2 * p - 1)
    denoised_count = denoised_proportion * total_count

    return original_count, noised_count, denoised_count


# Load the features dataset
features_path = '../dataset/features.csv'
data = pd.read_csv(features_path, index_col=0)

# Different input sizes to test
input_sizes = [1000, 10000, 30000, 50000, 100000, 150000, len(data)]
results = []

for size in input_sizes:
    if size > len(data):
        continue  # Skip sizes larger than the dataset (shouldn't happen for our hardcoded stuff)

    original_counts = []
    noised_counts = []
    denoised_counts = []
    runtimes = []

    for _ in range(10):  # Run 10 times for each size for better representation
        subset_data = data.head(size).copy()  # Make a copy to avoid SettingWithCopyWarning

        # Measure runtime
        start_time = time.time()
        original_count, noised_count, denoised_count = analyze_data(subset_data, epsilon=1.0)
        end_time = time.time()
        runtime = end_time - start_time
        original_counts.append(original_count)
        noised_counts.append(noised_count)
        denoised_counts.append(denoised_count)
        runtimes.append(runtime)

    # Calculate means
    mean_original_count = np.mean(original_counts)
    mean_noised_count = np.mean(noised_counts)
    mean_denoised_count = np.mean(denoised_counts)
    mean_runtime = np.mean(runtimes)

    # Calculate relative error based on input size
    relative_error = abs(mean_denoised_count - mean_original_count) / size

    results.append((size, mean_original_count, mean_noised_count, mean_denoised_count, relative_error, mean_runtime))

# Print the results and calculate relative error
for size, mean_original_count, mean_noised_count, mean_denoised_count, relative_error, mean_runtime in results:
    print(f"Size: {size}")
    print(f"Mean original count of HvyAlcoholConsump == 1: {mean_original_count}")
    print(f"Mean noised count of HvyAlcoholConsump == 1: {mean_noised_count}")
    print(f"Mean denoised count of HvyAlcoholConsump == 1: {mean_denoised_count}")
    print(f"Relative error: {relative_error}")
    print(f"Mean runtime: {mean_runtime}")
    print("\n")

# Extract sizes, relative errors, and runtimes for plots
sizes = [result[0] for result in results]
relative_errors = [result[4] for result in results]
runtimes = [result[5] for result in results]

# input size vs relative error
plt.figure(figsize=(10, 6))
plt.plot(sizes, relative_errors, marker='o')
plt.xlabel('Input Size')
plt.ylabel('Relative Error')
plt.title('Relative Error vs Input Size')
# plt.xscale('log')
plt.grid(True)
plt.show()

# Plot input size against runtime
plt.figure(figsize=(10, 6))
plt.plot(sizes, runtimes, marker='o')
plt.xlabel('Input Size')
plt.ylabel('Runtime (seconds)')
plt.title('Runtime vs Input Size')
# plt.xscale('log')
plt.grid(True)
plt.show()
