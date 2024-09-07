# Telegram to MT5 Copier

This project is a powerful tool that allows users to copy trading signals from Telegram channels directly to MetaTrader 5 (MT5) accounts. It features a user-friendly GUI built with PyQt5, automated trade execution, and advanced signal parsing capabilities.

## Features

- **Telegram Integration**: Connect to multiple Telegram channels and parse trading signals in real-time.
- **Multi-Account Support**: Manage and execute trades on multiple MT5 accounts simultaneously.
- **Signal Analysis**: Utilizes regex for accurate and flexible parsing of various signal formats.
- **Custom Defaults**: Set default values for trade parameters like volume, slippage, and stop loss.
- **Magic Keys**: Quickly modify open positions with features like partial closes, break-even, and trailing stops.
- **Analytics**: Track your trading performance with built-in analytics tools.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/telegram-to-mt5-copier.git
   cd telegram-to-mt5-copier
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the DWX MT4 Server (optional, for MT4 support):
   - Download the DWX MT4 server files from [https://github.com/darwinex/dwx-zeromq-connector](https://github.com/darwinex/dwx-zeromq-connector)
   - Copy the `DWX_ZeroMQ_Server_v2.0.1_RC8.mq4` file to your MT4 `Experts` folder
   - Restart MT4 and drag the expert advisor onto a chart

## Configuration

1. Create a `config.py` file in the project root with your Telegram API credentials:
   ```python
   api_id = 'your_api_id'
   api_hash = 'your_api_hash'
   ```

2. Update the database connection in `gui/employee.db` if necessary.

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Log in with your Telegram account.

3. Add Telegram channels to monitor for signals.

4. Configure your MT5 accounts in the MT5 page.

5. Set up default values and excluded symbols in the Defaults page.

6. Start copying trades by clicking the "Start Copy" button on the Home page.

7. Use the Magic Keys page to manage open positions.

## Signal Parsing

The application uses regex patterns to analyze and parse trading signals from Telegram messages. This allows for flexible recognition of various signal formats. You can customize the parsing logic in the `functions.py` file to match the specific format of your signal providers.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## Disclaimer

Trading foreign exchange on margin carries a high level of risk and may not be suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to invest in foreign exchange, you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with foreign exchange trading, and seek advice from an independent financial advisor if you have any doubts.
