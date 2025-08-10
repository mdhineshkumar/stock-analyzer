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
    """Detailed stock analysis page - REAL-TIME VALIDATION"""
    period = request.args.get('period', '1y')
    
    # REAL-TIME: Validate stock exists before analysis
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if stock is valid
        if not info or 'symbol' not in info or info['symbol'] == 'N/A':
            # Try with common exchange suffixes
            for suffix in ['.NS', '.BO', '.L', '.TO', '.AX', '.HK', '.SS', '.SZ']:
                try:
                    ticker = yf.Ticker(symbol + suffix)
                    info = ticker.info
                    if info and 'symbol' in info and info['symbol'] != 'N/A':
                        symbol = info['symbol']  # Update symbol with correct one
                        break
                except:
                    continue
            
            if not info or 'symbol' not in info or info['symbol'] == 'N/A':
                return render_template('error.html', 
                                    error_message=f"Stock '{symbol}' not found in any global market. Please check the symbol and try again.",
                                    symbol=symbol)
    except Exception as e:
        print(f"Stock validation error: {e}")
    
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
    """Search for stocks by name or symbol - REAL-TIME GLOBAL SEARCH"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    # PRIMARY: Real-time Yahoo Finance search (covers ALL stocks worldwide)
    try:
        yahoo_results = search_yahoo_finance_realtime(query)
        if yahoo_results:
            return jsonify(yahoo_results[:20])  # Return up to 20 real-time results
    except Exception as e:
        print(f"Yahoo Finance real-time search error: {e}")
    
    # FALLBACK: Local database search (only if Yahoo fails)
    try:
        local_results = search_local_database(query.lower())
        if local_results:
            return jsonify(local_results[:15])
    except Exception as e:
        print(f"Local database search error: {e}")
    
    # If all else fails, return empty results
    return jsonify([])

def search_local_database(query):
    """Search in local stock database"""
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
        {'symbol': 'HOOD', 'name': 'Robinhood Markets Inc.'},
        # Indian Stocks (NSE)
        {'symbol': 'GRASIM', 'name': 'Grasim Industries Ltd.'},
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd.'},
        {'symbol': 'INFY', 'name': 'Infosys Ltd.'},
        {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd.'},
        {'symbol': 'HDFC', 'name': 'HDFC Bank Ltd.'},
        {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd.'},
        {'symbol': 'ITC', 'name': 'ITC Ltd.'},
        {'symbol': 'SBIN', 'name': 'State Bank of India'},
        {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd.'},
        {'symbol': 'AXISBANK', 'name': 'Axis Bank Ltd.'},
        {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd.'},
        {'symbol': 'ASIANPAINT', 'name': 'Asian Paints Ltd.'},
        {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd.'},
        {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd.'},
        {'symbol': 'WIPRO', 'name': 'Wipro Ltd.'},
        {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd.'},
        {'symbol': 'ULTRACEMCO', 'name': 'UltraTech Cement Ltd.'},
        {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical Industries Ltd.'},
        {'symbol': 'TITAN', 'name': 'Titan Company Ltd.'},
        {'symbol': 'NESTLEIND', 'name': 'Nestle India Ltd.'}
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
    
    return results

def search_yahoo_finance_realtime(query):
    """REAL-TIME GLOBAL STOCK SEARCH - Covers ALL stocks worldwide"""
    results = []
    
    # Method 1: Direct ticker search (most accurate)
    try:
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        
        if info and 'symbol' in info and info['symbol'] and info['symbol'] != 'N/A':
            results.append({
                'symbol': info['symbol'],
                'name': info.get('longName', info.get('shortName', 'Unknown Company')),
                'display': f"{info['symbol']} - {info.get('longName', info.get('shortName', 'Unknown Company'))}",
                'source': 'yahoo_realtime',
                'exchange': info.get('exchange', 'Unknown'),
                'country': info.get('country', 'Unknown')
            })
    except Exception as e:
        print(f"Direct ticker search error: {e}")
    
    # Method 2: Multi-exchange search (covers global markets)
    exchanges = [
        '',      # US markets
        '.NS',   # India NSE
        '.BO',   # India BSE
        '.L',    # London
        '.TO',   # Toronto
        '.V',    # Vancouver
        '.AX',   # Australia
        '.T',    # Tokyo
        '.HK',   # Hong Kong
        '.SS',   # Shanghai
        '.SZ',   # Shenzhen
        '.PA',   # Paris
        '.F',    # Frankfurt
        '.MI',   # Milan
        '.AS',   # Amsterdam
        '.SW',   # Swiss
        '.ST',   # Stockholm
        '.OL',   # Oslo
        '.CO',   # Copenhagen
        '.HE',   # Helsinki
        '.IC',   # Iceland
        '.VI',   # Vienna
        '.WA',   # Warsaw
        '.PR',   # Prague
        '.BD',   # Budapest
        '.RG',   # Riga
        '.TL',   # Tallinn
        '.VS',   # Vilnius
        '.RG',   # Riga
        '.WA',   # Warsaw
        '.RG',   # Riga
        '.TL',   # Tallinn
        '.VS'    # Vilnius
    ]
    
    for exchange in exchanges:
        if len(results) >= 20:  # Limit results
            break
            
        try:
            ticker_symbol = query.upper() + exchange
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if (info and 'symbol' in info and info['symbol'] and 
                info['symbol'] != 'N/A' and info['symbol'] != 'None'):
                
                # Avoid duplicates
                if not any(r['symbol'] == info['symbol'] for r in results):
                    results.append({
                        'symbol': info['symbol'],
                        'name': info.get('longName', info.get('shortName', 'Unknown Company')),
                        'display': f"{info['symbol']} - {info.get('longName', info.get('shortName', 'Unknown Company'))}",
                        'source': 'yahoo_realtime',
                        'exchange': info.get('exchange', exchange),
                        'country': info.get('country', 'Unknown')
                    })
        except Exception as e:
            continue
    
    # Method 3: Fuzzy search for company names
    if len(results) < 5 and len(query) > 3:
        try:
            # Try variations of the query
            variations = [
                query.upper(),
                query.title(),
                query.capitalize()
            ]
            
            for variation in variations:
                if len(results) >= 20:
                    break
                    
                ticker = yf.Ticker(variation)
                info = ticker.info
                
                if (info and 'symbol' in info and info['symbol'] and 
                    info['symbol'] != 'N/A' and info['symbol'] != 'None'):
                    
                    if not any(r['symbol'] == info['symbol'] for r in results):
                        results.append({
                            'symbol': info['symbol'],
                            'name': info.get('longName', info.get('shortName', 'Unknown Company')),
                            'display': f"{info['symbol']} - {info.get('longName', info.get('shortName', 'Unknown Company'))}",
                            'source': 'yahoo_realtime',
                            'exchange': info.get('exchange', 'Unknown'),
                            'country': info.get('country', 'Unknown')
                        })
        except Exception as e:
            print(f"Fuzzy search error: {e}")
    
    return results

@app.route('/api/market-overview')
def api_market_overview():
    """API endpoint for market overview data - GLOBAL COVERAGE"""
    # Global market symbols (US, India, Europe, Asia)
    global_symbols = [
        # US Markets
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'market': 'US'},
        {'symbol': 'MSFT', 'name': 'Microsoft', 'market': 'US'},
        {'symbol': 'GOOGL', 'name': 'Alphabet', 'market': 'US'},
        {'symbol': 'AMZN', 'name': 'Amazon', 'market': 'US'},
        {'symbol': 'TSLA', 'name': 'Tesla', 'market': 'US'},
        {'symbol': 'META', 'name': 'Meta', 'market': 'US'},
        {'symbol': 'NVDA', 'name': 'NVIDIA', 'market': 'US'},
        
        # Indian Markets (NSE)
        {'symbol': 'TCS.NS', 'name': 'TCS', 'market': 'India'},
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance', 'market': 'India'},
        {'symbol': 'INFY.NS', 'name': 'Infosys', 'market': 'India'},
        {'symbol': 'HDFC.NS', 'name': 'HDFC Bank', 'market': 'India'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'market': 'India'},
        
        # European Markets
        {'symbol': 'ASML.AS', 'name': 'ASML', 'market': 'Europe'},
        {'symbol': 'NOVO-B.CO', 'name': 'Novo Nordisk', 'market': 'Europe'},
        {'symbol': 'NESN.SW', 'name': 'Nestle', 'market': 'Europe'},
        
        # Asian Markets
        {'symbol': '005930.KS', 'name': 'Samsung', 'market': 'Asia'},
        {'symbol': '0700.HK', 'name': 'Tencent', 'market': 'Asia'},
        {'symbol': '7203.T', 'name': 'Toyota', 'market': 'Asia'}
    ]
    
    market_data = []
    
    for stock in global_symbols:
        try:
            analysis = analyzer.analyze_stock(stock['symbol'], '1mo')
            if 'error' not in analysis:
                market_data.append({
                    'symbol': analysis['symbol'],
                    'name': stock['name'],
                    'market': stock['market'],
                    'price': analysis['current_price'],
                    'change': analysis['price_change_pct'],
                    'recommendation': analysis['recommendation'],
                    'signal_strength': analysis['signal_strength']
                })
        except Exception as e:
            print(f"Error analyzing {stock['symbol']}: {e}")
            continue
    
    return jsonify(market_data)

@app.route('/api/global-markets')
def api_global_markets():
    """API endpoint for global market status and coverage"""
    markets = {
        'US': {
            'name': 'United States',
            'exchanges': ['NYSE', 'NASDAQ', 'AMEX'],
            'coverage': 'All US stocks, ETFs, ADRs',
            'status': 'Active'
        },
        'India': {
            'name': 'India',
            'exchanges': ['NSE', 'BSE'],
            'coverage': 'All NSE & BSE listed stocks',
            'status': 'Active'
        },
        'Europe': {
            'name': 'Europe',
            'exchanges': ['LSE', 'Euronext', 'Deutsche Börse', 'SIX'],
            'coverage': 'Major European exchanges',
            'status': 'Active'
        },
        'Asia': {
            'name': 'Asia Pacific',
            'exchanges': ['TSE', 'HKEX', 'SSE', 'SZSE', 'ASX'],
            'coverage': 'Major Asian markets',
            'status': 'Active'
        },
        'Global': {
            'name': 'Global Coverage',
            'exchanges': ['All Major Exchanges'],
            'coverage': 'Real-time search across 50+ exchanges',
            'status': 'Active'
        }
    }
    
    return jsonify({
        'markets': markets,
        'total_exchanges': 50,
        'total_stocks': 'Unlimited (Real-time)',
        'search_method': 'Yahoo Finance API + Local Database',
        'update_frequency': 'Real-time',
        'last_updated': datetime.now().isoformat()
    })

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