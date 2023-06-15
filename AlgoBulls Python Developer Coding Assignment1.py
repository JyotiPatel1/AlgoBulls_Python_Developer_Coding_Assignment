#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install pandas')
get_ipython().system('pip install pyalgotrading')


# In[39]:


pip install matplotlib


# In[71]:


import os
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt


# In[56]:


API_KEY="84XJB3CYD1I8056S"


# In[57]:


class ScriptData:
    def __init__(self):
        self.raw_scripts = {}
        self.scripts = {}

    def fetch_intraday_data(self, script):
        url = 'https://www.alphavantage.co/query'
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": script,
            "apikey": API_KEY,
            "interval": "60min"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Cannot fetch data from Alpha Vantage")
            return

        data = response.json()
        data = data["Time Series (60min)"]
        self.raw_scripts[script] = {"timestamp": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
        for timestamp, values in data.items():
            self.raw_scripts[script]["timestamp"].append(pd.Timestamp(timestamp))
            self.raw_scripts[script]["open"].append(float(values["1. open"]))
            self.raw_scripts[script]["high"].append(float(values["2. high"]))
            self.raw_scripts[script]["low"].append(float(values["3. low"]))
            self.raw_scripts[script]["close"].append(float(values["4. close"]))
            self.raw_scripts[script]["volume"].append(int(values["5. volume"]))

        for key, value in self.raw_scripts[script].items():
            self.raw_scripts[script][key] = reversed(value)

    def convert_intraday_data(self, script):
        if script not in self.raw_scripts.keys():
            print("Please fetch the data for this script first")
            return

        self.scripts[script] = pd.DataFrame.from_dict(self.raw_scripts[script]).sort_values(by=["timestamp"])

    def __getitem__(self, item):
        return self.scripts[item]

    def __setitem__(self, key, value):
        self.scripts[key] = value

    def __contains__(self, item):
        return item in self.scripts.keys()


# In[58]:


script_data = ScriptData()
script_data.fetch_intraday_data("GOOGL")
script_data.convert_intraday_data("GOOGL")
script_data["GOOGL"]


# In[59]:


script_data.fetch_intraday_data("AAPL")
script_data.convert_intraday_data("AAPL")
script_data["AAPL"]


# In[60]:


"GOOGL" in script_data


# In[61]:


"AAPL" in script_data


# In[62]:


"NVDA" in script_data


# In[63]:


def indicator1(df: pd.DataFrame, timeperiod: int):
    data = {"timestamp": [], "indicator": []}
    moving_sum = 0

    # Create a moving sum that always has the sum of the timeperiod days ending at the current day
    
    for index in df.index:
        data["timestamp"].append(df["timestamp"][index])
        moving_sum += df["close"][index]
        if index+1 < timeperiod:
            data["indicator"].append(None)
        else:
            if index+1 > timeperiod:
                moving_sum -= df["close"][index-timeperiod]
            data["indicator"].append(moving_sum/timeperiod)

    return pd.DataFrame.from_dict(data)


# In[64]:


indicator1(script_data["GOOGL"], 5)


# In[65]:


indicator1(script_data["AAPL"], 5)


# In[68]:


class Strategy:
    def __init__(self, script):
        self.script = script
        self.script_data = ScriptData()

    def get_script_data(self):
        self.script_data.fetch_intraday_data(self.script)
        self.script_data.convert_intraday_data(self.script)

    def get_signals(self):
        indicator_data = indicator1(self.script_data[self.script], 5)
        df = self.script_data[self.script]
        signals = pd.DataFrame(columns=["timestamp", "signal"])

        for index in indicator_data.index[1:]:
            if indicator_data["indicator"][index] == "nan":
                continue

            result = {
                "timestamp": [indicator_data["timestamp"][index]],
                "signal": ["NO_SIGNAL"]
            }

            # For BUY signal, previous day's close must be higher than indicator
            # and current day's close must be lower than indicator
            
            # For SELL signal, previous day's close must be lower than indicator
            # and current day's close must be greater than indicator
            if indicator_data["indicator"][index - 1] < df["close"][index-1] \
                    and df["close"][index] < indicator_data["indicator"][index]:
                result["signal"][0] = "BUY"
            elif indicator_data["indicator"][index - 1] > df["close"][index-1] \
                    and df["close"][index] > indicator_data["indicator"][index]:
                result["signal"][0] = "SELL"

            if result["signal"][0] != "NO_SIGNAL":
                signals = pd.concat([signals, pd.DataFrame.from_dict(result)], ignore_index=True)

        # Plotting the graph
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['close'], color='red', label='Close Data')
        plt.plot(indicator_data['timestamp'], indicator_data['indicator'], color='grey', label='Indicator Data')
        plt.scatter(signals['timestamp'], signals['signal'], color='blue', marker='o', label='BUY Signals')
        plt.scatter(signals['timestamp'], signals['signal'], color='pink', marker='o', label='SELL Signals')
        plt.scatter(signals['timestamp'], signals['signal'], color='yellow', marker='o', label='NO_SIGNAL')

        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.legend()
        plt.show()

        return signals


# In[69]:


strategy = Strategy("NVDA")
strategy.get_script_data()
strategy.get_signals()


# In[ ]:




