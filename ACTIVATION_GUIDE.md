# 🚀 GenX Trading System Activation Guide

Welcome! This guide provides all the steps you need to activate your GenX automated trading system. Please follow the steps carefully to connect the trading robot (Expert Advisor) to your Exness account and begin trading.

---

## ❗ **Step 1: Start the Signal Server on Your VM**

The signal server on your Google VM is the heart of the system, delivering trading signals to your local MetaTrader terminal. This server is currently offline. You must restart it before proceeding.

1.  **Log in to your Google VM.**
2.  Open a terminal and navigate to the project directory.
3.  Run the following command to start the web server in the background:

    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8080 &
    ```

4.  **Verify it's working:** Open `http://34.71.143.222:8080/MT4_Signals.csv` in your web browser. You should see a CSV file with trading data. If you see this, you can proceed to the next step.

---

## 📂 **Step 2: Install the Gold Master EA in MetaTrader**

Now, let's install the specialized Gold Master EA into your MetaTrader 4 platform.

1.  Locate the EA file in this project: `expert-advisors/GenX_Gold_Master_EA.mq4`.
2.  **Open your MetaTrader 4 terminal.**
3.  Go to `File` -> `Open Data Folder` in the top menu.
4.  In the folder that opens, navigate to `MQL4` -> `Experts`.
5.  **Copy the `GenX_Gold_Master_EA.mq4` file** into this `Experts` folder.
6.  Return to MetaTrader 4, right-click on "Expert Advisors" in the "Navigator" panel, and click **Refresh**.
7.  `GenX_Gold_Master_EA` should now appear in the list.

---

## ⚙️ **Step 3: Configure the EA for Trading**

This is the most important step. We will configure the EA with safe settings to start.

1.  In MetaTrader 4, open a chart for a gold pair (e.g., **XAUUSD**).
2.  Drag the **`GenX_Gold_Master_EA`** from the Navigator onto the chart.
3.  A settings window will appear. Go to the **"Inputs"** tab.
4.  **Set the following recommended settings for beginners:**

    | Parameter                 | Recommended Value                                     | Description                                                 |
    | ------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
    | `VMSignalURL`             | `http://34.71.143.222:8080/MT4_Signals.csv` | **Leave as is.** This points to your signal server.        |
    | `EnableTrading`           | `false`                                               | **Crucial!** Start in test mode to monitor behavior first.  |
    | `BaseRiskPercent`         | `1.0`                                                 | Risk 1% of your account per trade. A safe starting point.   |
    | `Trade_XAUUSD`            | `true`                                                | Enable trading on Gold/USD.                             |
    | `Trade_XAUEUR`            | `true`                                                | Enable trading on Gold/Euro.                            |
    | `Trade_XAUGBP`            | `true`                                                | Enable trading on Gold/British Pound.                   |
    | `MaxTotalTrades`          | `3`                                                   | Limit the EA to a maximum of 3 open trades at once.       |
    | `MagicNumber`             | `888888`                                              | A unique ID for the EA's trades. You can leave this as is.  |

5.  Click **OK**.

---

## ✅ **Step 4: Verify the Setup**

After clicking OK, you need to confirm the EA is running correctly.

1.  **Check for the Smiley Face:** Look at the top-right corner of the chart. A **smiley face** (😊) means the EA is active. A sad face means it's disabled.
2.  **Check the "Experts" Tab:** At the bottom of the MetaTrader terminal, click the "Experts" tab. You should see messages from the EA, such as:
    *   `GenX Gold Master EA Starting...`
    *   `Found X gold signals from VM`
    *   `Processing signal: XAUUSD BUY Confidence: 85%`

If you see these messages, the EA is successfully connecting to your signal server and reading the signals. Because `EnableTrading` is set to `false`, it will not place any trades yet.

---

## 🚀 **Step 5: Go Live and Start Trading**

After you have monitored the EA's behavior in test mode for at least a few hours and are comfortable with the signals it's receiving, you can activate live trading.

1.  Right-click on the chart and select `Expert Advisors` -> `Properties`.
2.  Go to the **"Inputs"** tab.
3.  Change the `EnableTrading` parameter from `false` to **`true`**.
4.  Click **OK**.

The EA will now begin to execute trades on your Exness account based on the signals from your VM.

---

## 🚨 **Troubleshooting**

*   **Problem: Sad face (😞) in the corner of the chart.**
    *   **Solution:** Make sure the "AutoTrading" button at the top of your MetaTrader window is enabled (it should be green).

*   **Problem: "Cannot connect to server" or no signals found in the "Experts" tab.**
    *   **Solution:** This means your signal server on the VM is down. Please repeat **Step 1** of this guide to restart it.

*   **Problem: The EA is not opening any trades.**
    *   **Solution:** Double-check that `EnableTrading` is set to `true`. Also, ensure your Exness account is approved for automated trading.

**Congratulations! Your GenX automated trading system is now active.** Remember to monitor its performance regularly, especially in the first few days.