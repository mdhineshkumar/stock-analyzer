"""
Flask Web Application for Stock Analysis
Provides a beautiful web interface for analyzing stocks
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from stock_analyzer import StockAnalyzer
import plotly.graph_objs as go
import plotly.utils
import json
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

analyzer = StockAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Analyze a specific stock"""
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').upper()
        period = request.form.get('period', '1y')
        
        if symbol:
            return redirect(url_for('stock_detail', symbol=symbol, period=period))
    
    return render_template('analyze.html')

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """Detailed stock analysis page"""
    period = request.args.get('period', '1y')
    
    # Get stock analysis
    analysis = analyzer.analyze_stock(symbol, period)
    sentiment = analyzer.get_market_sentiment(symbol)
    
    if 'error' in analysis:
        return render_template('error.html', error=analysis['error'], symbol=symbol)
    
    # Get historical data for charts
    data, _ = analyzer.get_stock_data(symbol, period)
    if data is not None:
        data_with_indicators = analyzer.calculate_technical_indicators(data)
        
        # Create price chart
        price_chart = create_price_chart(data_with_indicators, symbol)
        
        # Create RSI chart
        rsi_chart = create_rsi_chart(data_with_indicators, symbol)
        
        # Create MACD chart
        macd_chart = create_macd_chart(data_with_indicators, symbol)
        
        charts = {
            'price': price_chart,
            'rsi': rsi_chart,
            'macd': macd_chart
        }
    else:
        charts = {}
    
    return render_template('stock_detail.html', 
                         analysis=analysis, 
                         sentiment=sentiment, 
                         charts=charts,
                         symbol=symbol)

@app.route('/api/stock/<symbol>')
def api_stock_data(symbol):
    """API endpoint for stock data"""
    period = request.args.get('period', '1y')
    analysis = analyzer.analyze_stock(symbol, period)
    return jsonify(analysis)

@app.route('/api/search')
def search_stocks():
    """Search for stocks by name or symbol"""
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    # Stock database with names and symbols
    stock_database = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices'},
        {'symbol': 'INTC', 'name': 'Intel Corporation'},
        {'symbol': 'CRM', 'name': 'Salesforce Inc.'},
        {'symbol': 'ORCL', 'name': 'Oracle Corporation'},
        {'symbol': 'ADBE', 'name': 'Adobe Inc.'},
        {'symbol': 'PYPL', 'name': 'PayPal Holdings'},
        {'symbol': 'SQ', 'name': 'Block Inc.'},
        {'symbol': 'UBER', 'name': 'Uber Technologies'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
        {'symbol': 'BAC', 'name': 'Bank of America Corp.'},
        {'symbol': 'WMT', 'name': 'Walmart Inc.'},
        {'symbol': 'HD', 'name': 'The Home Depot Inc.'},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
        {'symbol': 'PG', 'name': 'Procter & Gamble Co.'},
        {'symbol': 'UNH', 'name': 'UnitedHealth Group Inc.'},
        {'symbol': 'MA', 'name': 'Mastercard Inc.'},
        {'symbol': 'V', 'name': 'Visa Inc.'},
        {'symbol': 'DIS', 'name': 'The Walt Disney Company'},
        {'symbol': 'KO', 'name': 'The Coca-Cola Company'},
        {'symbol': 'PEP', 'name': 'PepsiCo Inc.'},
        {'symbol': 'ABT', 'name': 'Abbott Laboratories'},
        {'symbol': 'TMO', 'name': 'Thermo Fisher Scientific'},
        {'symbol': 'AVGO', 'name': 'Broadcom Inc.'},
        {'symbol': 'QCOM', 'name': 'QUALCOMM Incorporated'},
        {'symbol': 'TXN', 'name': 'Texas Instruments'},
        {'symbol': 'HON', 'name': 'Honeywell International'},
        {'symbol': 'LMT', 'name': 'Lockheed Martin Corporation'},
        {'symbol': 'RTX', 'name': 'Raytheon Technologies'},
        {'symbol': 'CAT', 'name': 'Caterpillar Inc.'},
        {'symbol': 'DE', 'name': 'Deere & Company'},
        {'symbol': 'BA', 'name': 'The Boeing Company'},
        {'symbol': 'GE', 'name': 'General Electric Company'},
        {'symbol': 'IBM', 'name': 'International Business Machines'},
        {'symbol': 'CSCO', 'name': 'Cisco Systems Inc.'},
        {'symbol': 'VZ', 'name': 'Verizon Communications'},
        {'symbol': 'T', 'name': 'AT&T Inc.'},
        {'symbol': 'CMCSA', 'name': 'Comcast Corporation'},
        {'symbol': 'CHTR', 'name': 'Charter Communications'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
        {'symbol': 'SPOT', 'name': 'Spotify Technology'},
        {'symbol': 'ZM', 'name': 'Zoom Video Communications'},
        {'symbol': 'SHOP', 'name': 'Shopify Inc.'},
        {'symbol': 'ROKU', 'name': 'Roku Inc.'},
        {'symbol': 'SNAP', 'name': 'Snap Inc.'},
        {'symbol': 'TWTR', 'name': 'Twitter Inc.'},
        {'symbol': 'PINS', 'name': 'Pinterest Inc.'},
        {'symbol': 'LYFT', 'name': 'Lyft Inc.'},
        {'symbol': 'DASH', 'name': 'DoorDash Inc.'},
        {'symbol': 'ABNB', 'name': 'Airbnb Inc.'},
        {'symbol': 'SNOW', 'name': 'Snowflake Inc.'},
        {'symbol': 'PLTR', 'name': 'Palantir Technologies'},
        {'symbol': 'COIN', 'name': 'Coinbase Global Inc.'},
        {'symbol': 'HOOD', 'name': 'Robinhood Markets Inc.'}
    ]
    
    # Search by both symbol and name
    results = []
    for stock in stock_database:
        if (query in stock['symbol'].lower() or 
            query in stock['name'].lower()):
            results.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'display': f"{stock['symbol']} - {stock['name']}"
            })
    
    return jsonify(results[:15])

@app.route('/api/market-overview')
def api_market_overview():
    """API endpoint for market overview data"""
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    market_data = []
    
    for symbol in popular_symbols:
        try:
            analysis = analyzer.analyze_stock(symbol, '1mo')
            if 'error' not in analysis:
                market_data.append({
                    'symbol': analysis['symbol'],
                    'price': analysis['current_price'],
                    'change': analysis['price_change_pct'],
                    'recommendation': analysis['recommendation'],
                    'signal_strength': analysis['signal_strength']
                })
        except:
            continue
    
    return jsonify(market_data)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/dashboard')
def dashboard():
    """Market overview dashboard"""
    # Get analysis for popular stocks
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    market_overview = []
    
    for symbol in popular_symbols:
        try:
            analysis = analyzer.analyze_stock(symbol, '1mo')
            if 'error' not in analysis:
                market_overview.append(analysis)
        except:
            continue
    
    return render_template('dashboard.html', market_overview=market_overview)

def create_price_chart(data, symbol):
    """Create interactive price chart with technical indicators"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price',
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ))
    
    # Moving averages
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA_20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='#FF9800', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA_50'],
        mode='lines',
        name='SMA 50',
        line=dict(color='#2196F3', width=2)
    ))
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['BB_Upper'],
        mode='lines',
        name='BB Upper',
        line=dict(color='#9E9E9E', width=1, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['BB_Lower'],
        mode='lines',
        name='BB Lower',
        line=dict(color='#9E9E9E', width=1, dash='dash'),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_rsi_chart(data, symbol):
    """Create RSI chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='#9C27B0', width=2)
    ))
    
    # Overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig.add_hline(y=50, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title=f'{symbol} RSI (14)',
        xaxis_title='Date',
        yaxis_title='RSI',
        template='plotly_white',
        height=300,
        yaxis=dict(range=[0, 100])
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_macd_chart(data, symbol):
    """Create MACD chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='#2196F3', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MACD_Signal'],
        mode='lines',
        name='Signal',
        line=dict(color='#FF9800', width=2)
    ))
    
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['MACD'] - data['MACD_Signal'],
        name='Histogram',
        marker_color='#4CAF50'
    ))
    
    fig.update_layout(
        title=f'{symbol} MACD',
        xaxis_title='Date',
        yaxis_title='MACD',
        template='plotly_white',
        height=300
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 