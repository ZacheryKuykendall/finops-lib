import pandas as pd

# Function to calculate resource utilization rate
def calculate_utilization_rate(data: pd.DataFrame) -> float:
    utilized = data[data['utilization'] > 0]
    return len(utilized) / len(data) if len(data) > 0 else 0

# Function to calculate percentage of cloud waste
def calculate_cloud_waste(data: pd.DataFrame) -> float:
    waste = data[data['utilization'] == 0]
    return len(waste) / len(data) if len(data) > 0 else 0

# Function to calculate cost allocation rate
def calculate_cost_allocation(data: pd.DataFrame) -> float:
    allocated = data[data['tags'].apply(lambda x: 'owner' in x and x['owner'])]
    return len(allocated) / len(data) if len(data) > 0 else 0

# Function to calculate unit cost efficiency
def calculate_unit_cost(data: pd.DataFrame) -> float:
    return data['cost'].sum() / data['output'].sum() if data['output'].sum() > 0 else float('inf')

# Function to calculate discount coverage
def calculate_discount_coverage(data: pd.DataFrame) -> float:
    discounted = data[data['discount'] > 0]
    return discounted['cost'].sum() / data['cost'].sum() if data['cost'].sum() > 0 else 0

# Function to calculate cloud spend variance
def calculate_spend_variance(actual: float, forecast: float) -> float:
    return abs(actual - forecast) / forecast if forecast > 0 else float('inf')

# Function to calculate composite cost efficiency score
def calculate_composite_score(data: pd.DataFrame, forecast: float) -> float:
    utilization_rate = calculate_utilization_rate(data)
    cloud_waste = calculate_cloud_waste(data)
    cost_allocation = calculate_cost_allocation(data)
    unit_cost = calculate_unit_cost(data)
    discount_coverage = calculate_discount_coverage(data)
    spend_variance = calculate_spend_variance(data['cost'].sum(), forecast)

    # Composite score calculation
    score = (
        (1 - cloud_waste) * 0.30 +
        discount_coverage * 0.25 +
        cost_allocation * 0.15 +
        (1 / unit_cost if unit_cost != float('inf') else 0) * 0.15 +
        (1 - spend_variance) * 0.15
    )
    return score 