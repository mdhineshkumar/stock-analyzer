# Stock Analyzer Pro 🚀

A comprehensive, AI-powered stock analysis application that provides technical analysis, market sentiment, and intelligent buy/sell recommendations for stocks.

## ✨ Features

### 🎯 **Core Analysis**
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic
- **AI Recommendations**: Smart buy/sell signals with confidence scores
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Calmar ratio, volatility analysis
- **Market Sentiment**: P/E ratios, market cap, beta, sector information

### 📊 **Interactive Charts**
- **Price Charts**: Candlestick charts with technical indicators
- **RSI Charts**: Relative Strength Index with overbought/oversold levels
- **MACD Charts**: Moving Average Convergence Divergence with histogram
- **Responsive Design**: Works on all devices

### 🌐 **Web Interface**
- **Modern UI**: Beautiful, responsive design with Bootstrap 5
- **Real-time Data**: Live stock data from Yahoo Finance
- **Search Functionality**: Autocomplete stock search
- **Dashboard**: Market overview of popular stocks

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-analyzer
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
stock-analyzer/
├── app.py                 # Flask web application
├── stock_analyzer.py      # Core analysis engine
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html       # Home page
│   ├── analyze.html     # Stock search page
│   └── stock_detail.html # Stock analysis page
└── static/              # Static assets
    ├── css/
    │   └── style.css    # Custom styles
    └── js/
        └── main.js      # JavaScript functionality
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### API Keys (Optional)
For enhanced functionality, you can add API keys:

```env
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
QUANDL_API_KEY=your-quandl-key
```

## 📊 Usage

### 1. **Home Page**
- View market overview
- Quick access to popular stocks
- Learn about features

### 2. **Analyze Stocks**
- Enter any stock symbol (e.g., AAPL, MSFT, GOOGL)
- Select time period (1 month to 5 years)
- Get comprehensive analysis

### 3. **Stock Analysis**
- **Price Information**: Current price, change, volume
- **AI Recommendation**: Buy/Sell/Hold with confidence score
- **Technical Signals**: Individual indicator signals
- **Charts**: Interactive price, RSI, and MACD charts
- **Risk Metrics**: Volatility and risk-adjusted returns
- **Market Sentiment**: Fundamental indicators

## 🧠 Technical Analysis

### Indicators Used

#### **Trend Indicators**
- **Simple Moving Averages (SMA)**: 20-day and 50-day
- **Exponential Moving Averages (EMA)**: 12-day and 26-day
- **MACD**: Moving Average Convergence Divergence

#### **Momentum Indicators**
- **RSI (14)**: Relative Strength Index
- **Stochastic**: %K and %D lines

#### **Volatility Indicators**
- **Bollinger Bands**: Upper, middle, and lower bands
- **Volume SMA**: Volume moving average

### Signal Generation

The AI recommendation system analyzes multiple technical indicators:

1. **Moving Average Crossover**: 20-day vs 50-day SMA
2. **MACD Signals**: MACD line vs signal line
3. **RSI Levels**: Overbought (>70) vs oversold (<30)
4. **Bollinger Bands**: Price position relative to bands
5. **Stochastic**: %K and %D positioning

**Recommendation Logic**:
- **BUY**: Majority of indicators show bullish signals
- **SELL**: Majority of indicators show bearish signals
- **HOLD**: Mixed or neutral signals

## 🔒 Security & Disclaimer

### Important Disclaimers
- **Educational Purpose**: This tool is for educational and research purposes only
- **Not Financial Advice**: Always consult with a qualified financial advisor
- **Data Accuracy**: While we strive for accuracy, data may have delays or errors
- **Investment Risk**: All investments carry risk of loss

### Security Features
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure session management
- XSS protection

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. **Using Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Using Docker**:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

3. **Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   export SECRET_KEY=your-production-secret-key
   ```

## 🔧 Customization

### Adding New Indicators
1. Modify `stock_analyzer.py`
2. Add new calculation methods
3. Update signal generation logic
4. Add to chart generation

### Styling Changes
1. Edit `static/css/style.css`
2. Modify Bootstrap variables
3. Update color schemes and layouts

### Adding New Data Sources
1. Implement new data fetcher class
2. Update API endpoints
3. Add error handling

## 📈 Performance Optimization

### Caching
- Implement Redis for session storage
- Cache frequently accessed stock data
- Use CDN for static assets

### Database Integration
- Add PostgreSQL for user accounts
- Store analysis history
- Implement watchlists

### API Optimization
- Implement rate limiting
- Add request queuing
- Use async processing

## 🐛 Troubleshooting

### Common Issues

1. **Installation Errors**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **Data Fetching Issues**
   - Check internet connection
   - Verify stock symbol validity
   - Check API rate limits

3. **Chart Display Problems**
   - Ensure JavaScript is enabled
   - Check browser console for errors
   - Verify Plotly.js is loaded

### Debug Mode
Enable debug mode for detailed error messages:
```python
app.run(debug=True)
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone <your-fork>
cd stock-analyzer
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
python app.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance**: Stock data provider
- **Bootstrap**: UI framework
- **Plotly**: Charting library
- **TA-Lib**: Technical analysis library

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Documentation**: Check this README and code comments

## 🔮 Future Roadmap

- [ ] **Real-time Updates**: WebSocket integration
- [ ] **Portfolio Management**: Track multiple stocks
- [ ] **Backtesting**: Historical strategy testing
- [ ] **Mobile App**: React Native application
- [ ] **Advanced AI**: Machine learning models
- [ ] **Social Features**: Share analysis and insights

---

**Happy Trading! 📈**

*Remember: Past performance does not guarantee future results. Always do your own research and consult with financial professionals.* 