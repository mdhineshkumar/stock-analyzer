/**
 * Stock Analyzer Pro - Main JavaScript
 * Handles interactive functionality and dynamic content loading
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Load popular stocks on the home page
    if (document.getElementById('popular-stocks')) {
        loadPopularStocks();
    }
    
    // Initialize search functionality
    initSearch();
    
    // Initialize tooltips and popovers
    initBootstrapComponents();
    
    // Add smooth scrolling
    addSmoothScrolling();
}

/**
 * Load popular stocks for the home page
 */
async function loadPopularStocks() {
    const popularStocksContainer = document.getElementById('popular-stocks');
    if (!popularStocksContainer) return;
    
    // Show loading state
    popularStocksContainer.innerHTML = '<div class="col-12 text-center"><div class="loading"></div></div>';
    
    const popularSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
    const stockCards = [];
    
    try {
        // Fetch data for each popular stock
        for (const symbol of popularSymbols) {
            try {
                const response = await fetch(`/api/stock/${symbol}?period=1mo`);
                if (response.ok) {
                    const data = await response.json();
                    if (!data.error) {
                        stockCards.push(createStockCard(data));
                    }
                }
            } catch (error) {
                console.error(`Error fetching ${symbol}:`, error);
            }
        }
        
        // Display stock cards
        if (stockCards.length > 0) {
            popularStocksContainer.innerHTML = stockCards.join('');
        } else {
            popularStocksContainer.innerHTML = `
                <div class="col-12 text-center">
                    <p class="text-muted">Unable to load stock data at the moment.</p>
                </div>
            `;
        }
        
        // Add click handlers to stock cards
        addStockCardHandlers();
        
    } catch (error) {
        console.error('Error loading popular stocks:', error);
        popularStocksContainer.innerHTML = `
            <div class="col-12 text-center">
                <p class="text-danger">Error loading stock data. Please try again later.</p>
            </div>
        `;
    }
}

/**
 * Create a stock card element
 */
function createStockCard(stockData) {
    const changeClass = stockData.price_change >= 0 ? 'positive' : 'negative';
    const changeIcon = stockData.price_change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    
    return `
        <div class="col-md-4 col-lg-3 mb-3">
            <div class="stock-card" data-symbol="${stockData.symbol}">
                <div class="stock-symbol">${stockData.symbol}</div>
                <div class="stock-price">$${stockData.current_price}</div>
                <div class="stock-change ${changeClass}">
                    <i class="fas ${changeIcon} me-1"></i>
                    $${Math.abs(stockData.price_change)} (${Math.abs(stockData.price_change_pct)}%)
                </div>
                <div class="mt-3">
                    <span class="badge bg-${getRecommendationColor(stockData.recommendation)}">
                        ${stockData.recommendation}
                    </span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Get color class for recommendation badge
 */
function getRecommendationColor(recommendation) {
    switch (recommendation) {
        case 'BUY': return 'success';
        case 'SELL': return 'danger';
        case 'HOLD': return 'warning';
        default: return 'secondary';
    }
}

/**
 * Add click handlers to stock cards
 */
function addStockCardHandlers() {
    const stockCards = document.querySelectorAll('.stock-card');
    stockCards.forEach(card => {
        card.addEventListener('click', function() {
            const symbol = this.dataset.symbol;
            if (symbol) {
                window.location.href = `/stock/${symbol}`;
            }
        });
    });
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.querySelector('input[name="symbol"]');
    if (!searchInput) return;
    
    // Add autocomplete functionality
    searchInput.addEventListener('input', debounce(async function() {
        const query = this.value.trim();
        
        // Clear stored symbol when user manually types
        this.removeAttribute('data-selected-symbol');
        
        if (query.length < 2) return;
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const results = await response.json();
                showSearchSuggestions(results, this);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300));
    
    // Add form validation
    const searchForm = searchInput.closest('form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const input = searchInput.value.trim();
            if (!input) {
                e.preventDefault();
                showAlert('Please enter a stock symbol or name', 'warning');
                return;
            }
            
            // Use stored symbol if available (from search suggestions)
            let symbol = searchInput.getAttribute('data-selected-symbol');
            
            // If no stored symbol, extract from input format
            if (!symbol) {
                if (input.includes(' - ')) {
                    symbol = input.split(' - ')[0];
                } else {
                    symbol = input;
                }
            }
            
            // Update the input with just the symbol for submission
            searchInput.value = symbol.toUpperCase();
            
            // Clear the stored symbol
            searchInput.removeAttribute('data-selected-symbol');
        });
    }
}

/**
 * Show search suggestions
 */
function showSearchSuggestions(suggestions, inputElement) {
    // Remove existing suggestions
    removeSearchSuggestions();
    
    if (suggestions.length === 0) return;
    
    // Create suggestions dropdown
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    suggestionsContainer.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    `;
    
    suggestions.forEach(stock => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        suggestionItem.style.cssText = `
            padding: 10px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s;
        `;
        
        // Display both symbol and company name
        suggestionItem.innerHTML = `
            <div style="font-weight: bold; color: #333;">${stock.symbol}</div>
            <div style="font-size: 0.9em; color: #666;">${stock.name}</div>
        `;
        
        suggestionItem.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        suggestionItem.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'white';
        });
        
        suggestionItem.addEventListener('click', function() {
            // Store the symbol in a data attribute for form submission
            inputElement.setAttribute('data-selected-symbol', stock.symbol);
            inputElement.value = stock.display;
            removeSearchSuggestions();
            inputElement.focus();
        });
        
        suggestionsContainer.appendChild(suggestionItem);
    });
    
    // Position the suggestions dropdown
    const inputRect = inputElement.getBoundingClientRect();
    suggestionsContainer.style.top = `${inputRect.bottom}px`;
    suggestionsContainer.style.left = `${inputRect.left}px`;
    suggestionsContainer.style.width = `${inputRect.width}px`;
    
    document.body.appendChild(suggestionsContainer);
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function closeSuggestions(e) {
        if (!suggestionsContainer.contains(e.target) && e.target !== inputElement) {
            removeSearchSuggestions();
            document.removeEventListener('click', closeSuggestions);
        }
    });
}

/**
 * Remove search suggestions
 */
function removeSearchSuggestions() {
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
}

/**
 * Initialize Bootstrap components
 */
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Add smooth scrolling to anchor links
 */
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format percentage
 */
function formatPercentage(value, decimals = 2) {
    return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Add loading state to button
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

/**
 * Handle API errors gracefully
 */
function handleApiError(error, userMessage = 'An error occurred. Please try again.') {
    console.error('API Error:', error);
    showAlert(userMessage, 'danger');
}

/**
 * Refresh stock data
 */
async function refreshStockData(symbol) {
    try {
        const response = await fetch(`/api/stock/${symbol}`);
        if (response.ok) {
            const data = await response.json();
            if (!data.error) {
                // Update the page with new data
                location.reload();
            } else {
                showAlert(`Error: ${data.error}`, 'danger');
            }
        }
    } catch (error) {
        handleApiError(error, 'Failed to refresh stock data');
    }
}

// Export functions for use in other scripts
window.StockAnalyzer = {
    showAlert,
    formatNumber,
    formatCurrency,
    formatPercentage,
    refreshStockData,
    handleApiError
}; 