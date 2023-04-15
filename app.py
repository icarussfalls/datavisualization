from flask import Flask, render_template
import sqlite3
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trades')
def trades():
    conn = sqlite3.connect('trades.db')
    trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()
    trades_df.drop('id', axis =1, inplace=True )
    # Convert time column to datetime object
    trades_df['time'] = pd.to_datetime(trades_df['time'])

    # Remove trades without exit price
    trades_df = trades_df[trades_df['exit_price'].notna()]

    # Calculate profit/loss for each trade
    trades_df['Profit/Loss'] = trades_df.apply(lambda row: row['qty'] * (row['exit_price'] - row['entry_price']) if row['trade_type'] == 'BUY' else row['qty'] * (row['entry_price'] - row['exit_price']), axis=1)
    trades_df['Profit/Loss'] = trades_df['Profit/Loss'].round(2)

    # Calculate cumulative profit/loss
    trades_df['Cumulative P/L'] = trades_df['Profit/Loss'].cumsum()
    trades_df['Cumulative P/L'] = trades_df['Cumulative P/L'].round(2)

    # Create a scatter plot of cumulative profit/loss over time
    fig = go.Figure(data=go.Scatter(x=trades_df['time'], y=trades_df['Cumulative P/L'], mode='lines'))

    fig.update_layout(title='Cumulative Profit/Loss Over Time', xaxis_title='Time', yaxis_title='Cumulative Profit/Loss')

    chart = fig.to_html(full_html=False)

    # Create a dataframe of open positions
    open_positions_df = trades_df[trades_df['exit_price'].isna()]

    return render_template('trades.html', trades=trades_df, chart=chart, open_positions=open_positions_df)


@app.route('/open_positions')
def open_positions():
    conn = sqlite3.connect('trades.db')
    open_positions_df = pd.read_sql_query("SELECT * FROM trades WHERE exit_price IS NULL", conn)
    conn.close()
    open_positions_df.drop('id', axis=1, inplace=True)
    open_positions_df['time'] = pd.to_datetime(open_positions_df['time'])
    return render_template('open_positions.html', positions=open_positions_df)

@app.route('/update_trades')
def update_trades():
    conn = sqlite3.connect('trades.db')
    trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()

    # Convert time column to datetime object
    trades_df['time'] = pd.to_datetime(trades_df['time'])

    # Remove trades without exit price
    trades_df = trades_df[trades_df['exit_price'].notna()]

    # Calculate profit/loss for each trade
    trades_df['Profit/Loss'] = trades_df.apply(lambda row: row['qty'] * (row['exit_price'] - row['entry_price']) if row['trade_type'] == 'BUY' else row['qty'] * (row['entry_price'] - row['exit_price']), axis=1)
    trades_df['Profit/Loss'] = trades_df['Profit/Loss'].round(2)

    # Calculate cumulative profit/loss
    trades_df['Cumulative P/L'] = trades_df['Profit/Loss'].cumsum()
    trades_df['Cumulative P/L'] = trades_df['Cumulative P/L'].round(2)

    # Create a scatter plot of cumulative profit/loss over time
    fig = go.Figure(data=go.Scatter(x=trades_df['time'], y=trades_df['Cumulative P/L'], mode='lines'))

    fig.update_layout(title='Cumulative Profit/Loss Over Time', xaxis_title='Time', yaxis_title='Cumulative Profit/Loss')

    chart = fig.to_html(full_html=False)

    # Create a dataframe of open positions
    open_positions_df = trades_df[trades_df['exit_price'].isna()]

    updated_data = {
        'trades': trades_df.to_dict('records'),
        'chart': chart,
        'open_positions': open_positions_df.to_dict('records')
    }

    return updated_data






if __name__ == '__main__':
    app.run(debug=True)
