"""
Stock Analysis Engine
Provides technical analysis, market sentiment, and buy/sell recommendations
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        
    def get_stock_data(self, symbol, period="1y"):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if data.empty:
                return None, f"No data found for {symbol}"
            return data, None
        except Exception as e:
            return None, f"Error fetching data for {symbol}: {str(e)}"
    
    def calculate_technical_indicators(self, data):
        """Calculate various technical indicators"""
        if data is None or data.empty:
            return None
            
        df = data.copy()
        
        # Moving averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # MACD
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # Bollinger Bands
        df['BB_Upper'] = ta.volatility.bollinger_hband(df['Close'])
        df['BB_Lower'] = ta.volatility.bollinger_lband(df['Close'])
        df['BB_Middle'] = ta.volatility.bollinger_mavg(df['Close'])
        
        # Volume indicators
        df['Volume_SMA'] = ta.volume.volume_sma(df['Close'], df['Volume'])
        
        # Stochastic
        df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        
        return df
    
    def calculate_volatility(self, data):
        """Calculate volatility metrics"""
        if data is None or data.empty:
            return None
            
        returns = data['Close'].pct_change().dropna()
        
        volatility_metrics = {
            'daily_volatility': returns.std(),
            'annualized_volatility': returns.std() * np.sqrt(252),
            'max_drawdown': (data['Close'] / data['Close'].expanding().max() - 1).min(),
            'var_95': returns.quantile(0.05),
            'cvar_95': returns[returns <= returns.quantile(0.05)].mean()
        }
        
        return volatility_metrics
    
    def calculate_risk_metrics(self, data):
        """Calculate risk-adjusted return metrics"""
        if data is None or data.empty:
            return None
            
        returns = data['Close'].pct_change().dropna()
        excess_returns = returns - self.risk_free_rate / 252
        
        risk_metrics = {
            'sharpe_ratio': excess_returns.mean() / returns.std() * np.sqrt(252),
            'sortino_ratio': excess_returns.mean() / returns[returns < 0].std() * np.sqrt(252),
            'calmar_ratio': returns.mean() * 252 / abs((data['Close'] / data['Close'].expanding().max() - 1).min()),
            'total_return': (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
        }
        
        return risk_metrics
    
    def generate_signals(self, data):
        """Generate buy/sell signals based on technical analysis"""
        if data is None or data.empty:
            return None
            
        signals = {}
        
        # Moving average crossover
        if data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1] and \
           data['SMA_20'].iloc[-2] <= data['SMA_50'].iloc[-2]:
            signals['MA_Crossover'] = 'BUY'
        elif data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1] and \
             data['SMA_20'].iloc[-2] >= data['SMA_50'].iloc[-2]:
            signals['MA_Crossover'] = 'SELL'
        else:
            signals['MA_Crossover'] = 'HOLD'
        
        # MACD signals
        if data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1] and \
           data['MACD'].iloc[-2] <= data['MACD_Signal'].iloc[-2]:
            signals['MACD'] = 'BUY'
        elif data['MACD'].iloc[-1] < data['MACD_Signal'].iloc[-1] and \
             data['MACD'].iloc[-2] >= data['MACD_Signal'].iloc[-2]:
            signals['MACD'] = 'SELL'
        else:
            signals['MACD'] = 'HOLD'
        
        # RSI signals
        rsi_current = data['RSI'].iloc[-1]
        if rsi_current < 30:
            signals['RSI'] = 'BUY'
        elif rsi_current > 70:
            signals['RSI'] = 'SELL'
        else:
            signals['RSI'] = 'HOLD'
        
        # Bollinger Bands
        close_current = data['Close'].iloc[-1]
        bb_upper = data['BB_Upper'].iloc[-1]
        bb_lower = data['BB_Lower'].iloc[-1]
        
        if close_current <= bb_lower:
            signals['Bollinger_Bands'] = 'BUY'
        elif close_current >= bb_upper:
            signals['Bollinger_Bands'] = 'SELL'
        else:
            signals['Bollinger_Bands'] = 'HOLD'
        
        # Stochastic signals
        stoch_k = data['Stoch_K'].iloc[-1]
        stoch_d = data['Stoch_D'].iloc[-1]
        
        if stoch_k < 20 and stoch_d < 20:
            signals['Stochastic'] = 'BUY'
        elif stoch_k > 80 and stoch_d > 80:
            signals['Stochastic'] = 'SELL'
        else:
            signals['Stochastic'] = 'HOLD'
        
        return signals
    
    def calculate_signal_strength(self, signals):
        """Calculate overall signal strength"""
        if not signals:
            return 0, 'NEUTRAL'
        
        buy_count = sum(1 for signal in signals.values() if signal == 'BUY')
        sell_count = sum(1 for signal in signals.values() if signal == 'SELL')
        hold_count = sum(1 for signal in signals.values() if signal == 'HOLD')
        
        total_signals = len(signals)
        
        if buy_count > sell_count:
            strength = (buy_count / total_signals) * 100
            recommendation = 'BUY'
        elif sell_count > buy_count:
            strength = (sell_count / total_signals) * 100
            recommendation = 'SELL'
        else:
            strength = 50
            recommendation = 'HOLD'
        
        return strength, recommendation
    
    def analyze_stock(self, symbol, period="1y"):
        """Complete stock analysis"""
        # Get data
        data, error = self.get_stock_data(symbol, period)
        if error:
            return {'error': error}
        
        # Calculate indicators
        data_with_indicators = self.calculate_technical_indicators(data)
        
        # Calculate metrics
        volatility = self.calculate_volatility(data)
        risk_metrics = self.calculate_risk_metrics(data)
        signals = self.generate_signals(data_with_indicators)
        signal_strength, recommendation = self.calculate_signal_strength(signals)
        
        # Current price info
        current_price = data['Close'].iloc[-1]
        price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
        price_change_pct = (price_change / data['Close'].iloc[-2]) * 100
        
        analysis_result = {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'price_change_pct': round(price_change_pct, 2),
            'volume': data['Volume'].iloc[-1],
            'signals': signals,
            'signal_strength': round(signal_strength, 1),
            'recommendation': recommendation,
            'volatility': volatility,
            'risk_metrics': risk_metrics,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_points': len(data)
        }
        
        return analysis_result
    
    def get_market_sentiment(self, symbol):
        """Get market sentiment indicators"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            sentiment_indicators = {
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
            
            return sentiment_indicators
        except Exception as e:
            return {'error': f"Error fetching sentiment data: {str(e)}"}

# Example usage
if __name__ == "__main__":
    analyzer = StockAnalyzer()
    
    # Test with a popular stock
    symbol = "AAPL"
    print(f"Analyzing {symbol}...")
    
    result = analyzer.analyze_stock(symbol)
    if 'error' not in result:
        print(f"Current Price: ${result['current_price']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Signal Strength: {result['signal_strength']}%")
        print(f"Signals: {result['signals']}")
    else:
        print(f"Error: {result['error']}") 