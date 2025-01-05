# Stock StarLink AI App 

A modern, interactive stock trading application built with Streamlit that provides real-time stock data, interactive charts, and AI-powered financial advice.

## Features

### 1. Stock Search and Information
- Search stocks by either symbol (e.g., AAPL) or company name
- Real-time stock data fetching using Yahoo Finance API
- Display of key metrics:
  - Current Price
  - Market Cap
  - Trading Volume
  - 52-Week High/Low

### 2. Interactive Charts
- Interactive candlestick charts showing stock price movements
- Historical data visualization
- Price trends with Open, High, Low, and Close values
- Responsive chart design that adapts to screen size

### 3. AI Financial Assistant with Smart Symbol Detection
- Powered by Deepseek's AI model
- Intelligent stock symbol extraction from conversations
- Automatic search field population with mentioned symbols
- Get expert financial advice and insights
- Ask questions about:
  - Stock analysis
  - Trading strategies
  - Market trends
  - Company information

### 4. Smart Features
- Automatic stock symbol detection in AI responses
- Validates extracted symbols against real stock data
- Supports multiple symbol formats:
  - $SYMBOL format (e.g., $AAPL)
  - Symbol followed by keywords (e.g., AAPL stock)
  - Explicit mentions (e.g., symbol: AAPL)
- Session state management for persistent symbol tracking
- Helpful suggestions for detected symbols

### 5. Detailed Company Information
- Company sector and industry
- Key financial metrics
- Expandable information panels
- Comprehensive stock details

## Technologies Used

### Frontend
- **Streamlit**: v1.29.0
  - Modern Python framework for creating web applications
  - Interactive widgets and components
  - Responsive layout system
  - Real-time data updates
  - Built-in caching mechanism

### Data Visualization
- **Plotly**: v5.18.0
  - Interactive financial charts
  - Candlestick patterns
  - Custom chart layouts
  - Real-time data plotting

### AI Integration
- **Deepseek AI**
  - Advanced language model for financial analysis
  - Natural language processing
  - Real-time stock recommendations
  - Market trend analysis

### Data Sources
- **Yahoo Finance (yfinance)**: v0.2.33
  - Real-time stock data
  - Historical price information
  - Company fundamentals
  - Market indicators

### Backend & Utilities
- **Python**: v3.11.0
  - Core programming language
  - Asynchronous operations
  - Data processing
  - API integrations

- **Pandas**: v2.1.4
  - Data manipulation
  - Time series analysis
  - Statistical calculations
  - DataFrame operations

- **NumPy**: v1.24.3
  - Numerical computations
  - Array operations
  - Mathematical functions
  - Statistical analysis

### API & Networking
- **Requests**: v2.31.0
  - HTTP client
  - API communications
  - Data fetching
  - Error handling

### Environment & Configuration
- **Python-dotenv**: v1.0.0
  - Environment variable management
  - Secure configuration
  - API key storage
  - Development/production settings

### Version Control & Deployment
- **Git**
  - Source code management
  - Version tracking
  - Collaborative development
  - Deployment automation

- **Cloudflare Pages**
  - Web hosting
  - Continuous deployment
  - SSL/TLS security
  - Global CDN distribution

### Development Tools
- **VS Code** (Recommended IDE)
  - Python integration
  - Git integration
  - Debugging tools
  - Extension support

### Key Features Implementation
- **Session State Management**
  - User preferences storage
  - Symbol tracking
  - State persistence
  - Cross-page data sharing

- **Responsive Design**
  - Mobile-friendly layout
  - Adaptive charts
  - Flexible components
  - Cross-browser compatibility

- **Real-time Processing**
  - Live stock updates
  - Instant AI responses
  - Dynamic chart updates
  - Automated symbol detection

### Security Features
- **Environment Variables**
  - Secure API key storage
  - Configuration management
  - Deployment variables
  - Access control

- **Error Handling**
  - Graceful error recovery
  - User-friendly messages
  - API failure handling
  - Data validation

This tech stack was chosen for its reliability, performance, and seamless integration capabilities, making the Stock StarLink AI App a robust and scalable solution for stock market analysis and AI-powered trading insights.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stock-trading-app
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Create a `.env` file in the root directory
- Add your Deepseek API key:
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Usage Guide

### Starting the Application
```bash
streamlit run app.py
```

### Stock Search
1. Use the sidebar to select search method:
   - Symbol: Direct stock symbol search (e.g., MSFT for Microsoft)
   - Company Name: Search by company name
2. Enter your search term in the text input field
3. View real-time stock information and charts

### Using the AI Assistant
1. Navigate to the "AI Financial Assistant" section
2. Ask any question about stocks or trading
3. The assistant will:
   - Provide detailed financial advice
   - Automatically detect mentioned stock symbols
   - Update the search field with detected symbols
   - Show suggestions for viewing stock details

Example questions:
- "What do you think about Apple's stock?"
- "Should I invest in Microsoft?"
- "Tell me about Tesla's performance"

### Using the Charts
- Interactive candlestick chart shows price movements
- Hover over data points to see detailed information
- Use the chart controls to zoom and pan
- Export chart data if needed

## Deployment on Cloudflare Pages

### Prerequisites
1. A GitHub account
2. A Cloudflare account
3. Your project pushed to a GitHub repository

### Deployment Steps

1. **Prepare Your Repository**
   ```bash
   # Initialize git repository (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit changes
   git commit -m "Initial commit"
   
   # Add your GitHub repository as remote
   git remote add origin your-github-repo-url
   
   # Push to GitHub
   git push -u origin main
   ```

2. **Set Up Cloudflare Pages**
   1. Log in to your Cloudflare account
   2. Go to Pages > Create a project
   3. Connect your GitHub account
   4. Select your repository
   5. Configure build settings:
      - Framework preset: None
      - Build command: `chmod +x start.sh && ./start.sh`
      - Build output directory: `public`
      - Root directory: `/`
      - Environment variables:
        ```
        PYTHON_VERSION=3.11
        PORT=8501
        ```

3. **Environment Variables**
   In Cloudflare Pages settings:
   1. Go to Settings > Environment Variables
   2. Add the following variables:
      ```
      DEEPSEEK_API_KEY=your_api_key_here
      STREAMLIT_SERVER_PORT=8501
      STREAMLIT_SERVER_ADDRESS=0.0.0.0
      STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
      STREAMLIT_SERVER_BASE_URL_PATH=/app
      ```

4. **Advanced Build Settings**
   In your project's Settings > Builds & deployments:
   1. Set the Production branch: main
   2. Build configurations:
      - Set "Build command timeout" to 20 minutes
      - Enable "Always use latest framework version"
   3. Environment:
      - Set Python version to 3.11
      - Add `requirements.txt` to the dependency cache

### Post-Deployment

1. **Custom Domain (Optional)**
   1. Go to your project's settings in Cloudflare Pages
   2. Click on "Custom Domains"
   3. Add your domain and follow the DNS configuration instructions

2. **Monitoring**
   1. Monitor your app's performance in the Cloudflare dashboard
   2. Check build logs for any issues
   3. Set up notifications for failed deployments

3. **Updating the App**
   1. Push changes to your GitHub repository
   2. Cloudflare will automatically rebuild and deploy

### Troubleshooting

1. **Build Failures**
   - Check build logs in Cloudflare Pages
   - Verify all dependencies are in `requirements.txt`
   - Ensure environment variables are set correctly

2. **Runtime Errors**
   - Check the application logs
   - Verify API keys and environment variables
   - Test locally before deploying

3. **Performance Issues**
   - Monitor resource usage
   - Check Cloudflare Analytics
   - Consider caching strategies

### Security Notes

1. **Environment Variables**
   - Never commit `.env` file to repository
   - Use Cloudflare's environment variables
   - Rotate API keys periodically

2. **API Access**
   - Set up appropriate CORS policies
   - Use rate limiting
   - Monitor API usage

### Maintenance

1. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Test updates locally before deploying

2. **Backup**
   - Regularly backup your code
   - Keep local copies of configuration
   - Document any custom settings

For additional support or questions about deployment, refer to [Cloudflare Pages documentation](https://developers.cloudflare.com/pages/).

## Dependencies

- Python 3.6+
- Streamlit
- yfinance
- plotly
- pandas
- python-dotenv
- requests

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Deepseek API key is correctly set in the `.env` file
   - Verify the API key is valid and active

2. **Stock Data Not Loading**
   - Check your internet connection
   - Verify the stock symbol is correct
   - Ensure Yahoo Finance API is accessible

3. **Symbol Detection Issues**
   - Make sure the symbol follows standard formats
   - Verify the symbol exists in the stock market
   - Check if the symbol is actively traded

4. **Chart Display Issues**
   - Clear browser cache
   - Refresh the page
   - Check for adequate screen space

### Support

For additional support or feature requests, please open an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
