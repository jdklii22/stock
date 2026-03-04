def calculate_pivot(data):
    """
    Function to calculate the pivot point based on the provided data.
    """
    high = max(data['high'])
    low = min(data['low'])
    close = data['close'][-1]

    pivot = (high + low + close) / 3
    return pivot

if __name__ == '__main__':
    import pandas as pd
    # Load data
    # data = pd.read_csv('path_to_data.csv')
    # pivot_value = calculate_pivot(data)
    # print(f'Calculated Pivot: {pivot_value}')
