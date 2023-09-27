import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Investing Back Test Application")

# Slider to choose the number of stocks in the strategy
num_stocks = st.slider("Select the Number of Stocks", min_value=1, max_value=5, value=2)

# Create a list to store the selected models and strategies
selected_models = []
selected_strategies = []

# Generate dropdowns and radio buttons based on the number of stocks selected
for i in range(num_stocks):
    model = st.selectbox(f"Select Model {i+1}", ["AAPL", "MSFT", "GOOGL", "AMZN"], key=f"model_{i}")  # Unique key
    strategy = st.radio(f"Select Strategy for {model}", ["Long", "Short"], key=f"strategy_{i}")  # Unique key
    selected_models.append(model)
    selected_strategies.append(strategy)

# Slider to choose the time horizon (number of years)
time_horizon = st.slider("Select the Time Horizon (Years)", min_value=1, max_value=10, value=1)

if st.button("Get Data and Plot"):
    plt.figure(figsize=(10, 6))
    cumulative_return = 1.0  # Initialize cumulative return for the combined strategy

    for i in range(num_stocks):
        model = selected_models[i]
        strategy = selected_strategies[i]

        # Fetch data for the selected stock from Yahoo Finance
        data = yf.download(model, period=f"{time_horizon}y")

        # Calculate daily returns
        data['Daily Return'] = data['Adj Close'].pct_change()

        # Calculate cumulative returns based on the selected strategy
        if strategy == "Long":
            data['Cumulative Return'] = (1 + data['Daily Return']).cumprod()
        else:
            data['Cumulative Return'] = (1 - data['Daily Return']).cumprod()

        cumulative_return *= data['Cumulative Return']  # Update cumulative return with the current stock's return

        # Plot cumulative returns for individual stocks
        #plt.plot(data.index, data['Cumulative Return'], label=f"{model} ({strategy})")

    # Plot cumulative return for the combined strategy
    plt.plot(data.index, cumulative_return, label="Combined Strategy", linestyle='--', linewidth=2)

    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.title(f"Cumulative Returns Over {time_horizon} Years")
    plt.legend()

    # Calculate and display the total cumulative return
    # Calculate and display the total cumulative return
    total_return = cumulative_return.iloc[-1] - 1.0  # Extract the final cumulative return value
    total_return_percentage = total_return * 100
    formatted_total_return = f"{total_return:.2f} ({total_return_percentage:.2f}%)"
    st.write(f"Total Cumulative Return Over {time_horizon} Years: {formatted_total_return}")
    st.pyplot(plt)

