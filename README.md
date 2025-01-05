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

### 3. AI Financial Assistant with Smart Symbol Detectionf
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

### URL Routing and Redirection

To prevent URL recursion issues (multiple `/_app` in the URL), the following configuration is used:

1. **Index Page Redirection**
   ```html
   <script>
       function redirectToApp() {
           const currentPath = window.location.pathname;
           // Only redirect if we're not already at /_app
           if (!currentPath.includes('/_app')) {
               const baseUrl = window.location.origin;
               window.location.replace(baseUrl + '/_app');
           }
       }
       setTimeout(redirectToApp, 1000);
   </script>
   ```

2. **Cloudflare Pages Routing Rules** (`public/_redirects`)
   ```
   /_app/* /_app 200!
   /* /_app 200!
   ```
   - First rule handles all paths under `/_app`
   - Second rule redirects everything else to `/_app`
   - The `!` ensures the rules are applied without further processing

3. **Streamlit Base URL Configuration**
   ```toml
   [server]
   baseUrlPath = "_app"
   enableXsrfProtection = false
   
   [browser]
   serverAddress = "0.0.0.0"
   gatherUsageStats = false
   serverPort = 8501
   ```

## Deployment Guide

### Deploying to Cloudflare Pages

1. **Prerequisites**
   - A GitHub account
   - A Cloudflare account
   - Your DeepSeek API key

2. **Set Up Cloudflare Pages**
   1. Log in to your Cloudflare account
   2. Go to Pages > Create a project
   3. Connect your GitHub account
   4. Select your repository
   5. Configure build settings:
      - Framework preset: None
      - Build command: `python start.py`
      - Build output directory: `public`
      - Root directory: `/`
      - Environment variables:
        ```
        PYTHON_VERSION=3.11
        ```

3. **Environment Variables**
   In Cloudflare Pages settings:
   1. Go to Settings > Environment Variables
   2. Add the following variables:
      ```
      DEEPSEEK_API_KEY=your_api_key_here
      PYTHON_VERSION=3.11
      STREAMLIT_SERVER_PORT=8501
      STREAMLIT_SERVER_ADDRESS=0.0.0.0
      STREAMLIT_SERVER_HEADLESS=true
      STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
      STREAMLIT_SERVER_BASE_URL=/_app
      ```

   Note: Make sure to replace `your_api_key_here` with your actual DeepSeek API key.

4. **Advanced Build Settings**
   In your project's Settings > Builds & deployments:
   1. Set the Production branch: main
   2. Build configurations:
      - Set "Build command timeout" to 20 minutes
      - Enable "Always use latest framework version"
   3. Environment:
      - Set Python version to 3.11
      - Add `requirements.txt` to the dependency cache

5. **Important Files**
   The repository contains several configuration files for proper deployment:

   - `public/index.html`: Handles redirection and provides a loading screen
     ```html
     <!DOCTYPE html>
     <html>
     <head>
         <title>Stock Trading App</title>
         <!-- Styles and loading animation -->
     </head>
     <body>
         <div class="container">
             <h1>Stock Trading App</h1>
             <div class="spinner"></div>
             <div class="loading">Loading application...</div>
         </div>
         <!-- Redirect script -->
     </body>
     </html>
     ```

   - `public/_redirects`: Configures routing rules
     ```
     /* /_app 200!
     /_app/* /_app 200!
     ```

   - `public/_headers`: Sets security and caching headers
     ```
     /*
       X-Frame-Options: DENY
       X-Content-Type-Options: nosniff
       Referrer-Policy: no-referrer
       Permissions-Policy: document-domain=()
       Cache-Control: no-cache, no-store, must-revalidate

     /_app/*
       Cache-Control: no-cache, no-store, must-revalidate
     ```

   - `.streamlit/config.toml`: Configures Streamlit settings
     ```toml
     [server]
     port = 8501
     address = "0.0.0.0"
     headless = true
     baseUrlPath = "_app"
     enableCORS = true
     enableXsrfProtection = false
     maxUploadSize = 200
     runOnSave = true

     [browser]
     serverAddress = "0.0.0.0"
     gatherUsageStats = false
     serverPort = 8501

     [theme]
     primaryColor = "#E694FF"
     backgroundColor = "#00172B"
     secondaryBackgroundColor = "#0083B8"
     textColor = "#DCDCDC"
     ```

6. **After Deployment**
   - Your app will be available at: `https://your-project.pages.dev`
   - It will automatically redirect to: `https://your-project.pages.dev/_app`
   - If you encounter any issues:
     1. Clear your browser cache
     2. Check the deployment logs in Cloudflare Pages
     3. Verify all environment variables are set correctly
     4. Ensure the build command completed successfully

7. **Troubleshooting**
   - If the app shows "Unable to connect":
     - Wait a few minutes for the deployment to fully complete
     - Check if the app is running by visiting `/_app` directly
     - Verify the environment variables are set correctly
   - If you see a blank page:
     - Clear your browser cache
     - Check the browser console for any errors
     - Verify the redirect rules are working properly

8. **Development vs Production**
   - Local development:
     - App runs on: `http://localhost:8501`
     - Environment variables from `.env` file
   - Production (Cloudflare Pages):
     - App runs on: `https://your-project.pages.dev/_app`
     - Environment variables from Cloudflare Pages settings

## Troubleshooting URL Issues

If you encounter URL-related issues:

1. **Multiple `/_app` in URL**
   - Clear browser cache
   - Access the base URL: `https://your-project.pages.dev`
   - The redirect script will handle the routing

2. **Blank Page or Loading Issues**
   - Check browser console for errors
   - Verify Cloudflare Pages build logs
   - Ensure all configuration files are present
   - Try accessing `/_app` directly

3. **Connection Issues**
   - Wait for deployment to complete
   - Check environment variables
   - Verify build command execution

## Advanced Deployment Configuration

For reliable deployment on Cloudflare Pages, the following configuration files are essential:

1. **Build Requirements** (`requirements-build.txt`)
   ```
   streamlit==1.29.0
   numpy==1.24.3
   pandas==2.0.3
   yfinance==0.2.33
   plotly==5.18.0
   deepseek-ai==0.1.0
   python-dotenv==1.0.0
   ```

2. **Process Management** (`start.py`)
   ```python
   import subprocess
   import os
   import sys
   import time

   def main():
       # Set environment variables
       os.environ["STREAMLIT_SERVER_PORT"] = "8501"
       os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
       os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
       os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
       os.environ["STREAMLIT_SERVER_BASE_URL"] = "/_app"
       os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
       os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"

       # Create public directory
       if not os.path.exists("public"):
           os.makedirs("public")

       # Install dependencies
       print("Installing dependencies...")
       subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt"])

       # Run Streamlit
       print("Starting Streamlit app...")
       process = subprocess.Popen([
           sys.executable,
           "-m",
           "streamlit",
           "run",
           "app.py",
           "--server.port=8501",
           "--server.address=0.0.0.0",
           "--server.headless=true",
           "--server.baseUrlPath=_app",
           "--server.enableCORS=true",
           "--server.enableXsrfProtection=false",
           "--browser.gatherUsageStats=false"
       ])

       # Keep running
       try:
           while True:
               time.sleep(1)
       except KeyboardInterrupt:
           process.terminate()
           process.wait()

   if __name__ == "__main__":
       main()
   ```

3. **CORS and Security Headers** (`public/_headers`)
   ```
   /*
     Access-Control-Allow-Origin: *
     Access-Control-Allow-Methods: GET, POST, OPTIONS
     Access-Control-Allow-Headers: *
     X-Frame-Options: DENY
     X-Content-Type-Options: nosniff
     Referrer-Policy: no-referrer
     Permissions-Policy: document-domain=()
     Cache-Control: no-cache, no-store, must-revalidate

   /_app/*
     Access-Control-Allow-Origin: *
     Access-Control-Allow-Methods: GET, POST, OPTIONS
     Access-Control-Allow-Headers: *
     Cache-Control: no-cache, no-store, must-revalidate
   ```

4. **Loading Page with Error Handling** (`public/index.html`)
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Stock Trading App</title>
       <style>
           body {
               font-family: Arial, sans-serif;
               background-color: #00172B;
               color: #DCDCDC;
           }
           .container {
               max-width: 600px;
               margin: 50px auto;
               text-align: center;
           }
           .error {
               color: #ff6b6b;
               margin-top: 20px;
               display: none;
           }
           .spinner {
               border: 4px solid #f3f3f3;
               border-top: 4px solid #E694FF;
               border-radius: 50%;
               width: 40px;
               height: 40px;
               animation: spin 1s linear infinite;
           }
       </style>
   </head>
   <body>
       <div class="container">
           <h1>Stock Trading App</h1>
           <div class="spinner"></div>
           <div class="loading">Loading application...</div>
           <div class="error">
               Unable to connect. Retrying...
               <div style="margin-top: 10px;">
                   <button onclick="retryConnection()">Retry Now</button>
               </div>
           </div>
       </div>
       <script>
           let retryCount = 0;
           const maxRetries = 3;

           function showError() {
               document.querySelector('.spinner').style.display = 'none';
               document.querySelector('.loading').style.display = 'none';
               document.querySelector('.error').style.display = 'block';
           }

           function retryConnection() {
               document.querySelector('.spinner').style.display = 'block';
               document.querySelector('.loading').style.display = 'block';
               document.querySelector('.error').style.display = 'none';
               redirectToApp();
           }

           function redirectToApp() {
               const currentPath = window.location.pathname;
               if (!currentPath.includes('/_app')) {
                   const baseUrl = window.location.origin;
                   const targetUrl = baseUrl + '/_app';
                   
                   fetch(targetUrl)
                       .then(response => {
                           if (response.ok) {
                               window.location.replace(targetUrl);
                           } else {
                               throw new Error('App not ready');
                           }
                       })
                       .catch(error => {
                           console.error('Error connecting to app:', error);
                           retryCount++;
                           if (retryCount < maxRetries) {
                               setTimeout(redirectToApp, 2000);
                           } else {
                               showError();
                           }
                       });
               }
           }

           setTimeout(redirectToApp, 1000);
       </script>
   </body>
   </html>
   ```

### Deployment Troubleshooting

1. **Loading Screen Issues**
   - Clear browser cache
   - Check browser console (F12) for errors
   - Verify all configuration files are present
   - Check Cloudflare Pages deployment logs

2. **Connection Problems**
   - The app will automatically retry 3 times
   - Manual retry button available if all attempts fail
   - Check if the app is accessible at `/_app` directly
   - Verify environment variables in Cloudflare Pages settings

3. **CORS and Security**
   - Headers are configured for proper CORS support
   - Security headers prevent common web vulnerabilities
   - Caching is disabled to ensure fresh content
   - XSRF protection is disabled for Cloudflare compatibility

4. **Build Process**
   - Uses specific package versions in `requirements-build.txt`
   - Creates necessary directories automatically
   - Proper process management with error handling
   - Configures Streamlit for headless operation

5. **URL Handling**
   - Base URL is set to `/_app`
   - Automatic redirection from root URL
   - Prevents URL recursion issues
   - Health check before redirecting

6. **Environment Variables**
   Make sure these are set in Cloudflare Pages:
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   PYTHON_VERSION=3.11
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   STREAMLIT_SERVER_BASE_URL=/_app
   ```

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
