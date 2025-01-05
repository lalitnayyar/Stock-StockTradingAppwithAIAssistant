# Stock Trading Application

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
   5. Configure your build settings:
      - Framework preset: None
      - Build command: `pip install -r requirements.txt && streamlit run app.py`
      - Build output directory: `/`
      - Root directory: `/`

3. **Environment Variables**
   1. In Cloudflare Pages settings, go to Environment Variables
   2. Add your environment variables:
      - Add `DEEPSEEK_API_KEY` with your API key
      - Add `PYTHON_VERSION=3.11.0`

4. **Deploy**
   1. Click on "Save and Deploy"
   2. Wait for the build and deployment to complete
   3. Your app will be available at: `your-project-name.pages.dev`

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
