# FutureTools.io Tracker

A comprehensive Streamlit application for tracking and exploring AI tools from [FutureTools.io](https://www.futuretools.io). This application allows you to scrape, filter, and analyze AI tools with an intuitive interface.

## Features

- **Newly Added Tools**: Scrape tools added in the last 24 hours
- **Category-Based Scraping**: Filter by specific categories to reduce scraping time
- **Advanced Filtering**: Search and filter by name, description, category, and pricing
- **Data Caching**: Store scraped data locally for quick access
- **CSV Export**: Export filtered results to CSV format
- **Responsive UI**: Clean and intuitive interface with statistics dashboard

## Categories Supported

- AI Detection
- Aggregators
- Automation & Agents
- Avatar
- Chat
- Copywriting
- Finance
- For Fun
- Gaming
- Generative Art
- Generative Code
- Generative Video
- Image Improvement
- Image Scanning
- Inspiration
- Marketing
- Motion Capture
- Music
- Podcasting
- Productivity
- Prompt Guides
- Research
- Self-Improvement
- Social Media
- Speech-To-Text
- Text-To-Speech
- Translation
- Video Editing
- Voice Modulation

## Pricing Filters

- Free
- Freemium
- GitHub
- Google Colab
- Open Source
- Paid

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium scraping)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd future_tools_tracker_claude_code
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

### 1. Scraping Modes

#### Newly Added (Last 24 Hours)
- Scrapes only tools added in the past 24 hours
- Fastest scraping option
- Ideal for daily updates

#### Full Update with Category Filter
- Select specific categories to scrape
- Reduces scraping time significantly
- Recommended for comprehensive but targeted scraping

#### View Cached Data
- View previously scraped data
- No scraping required
- Instant access to stored tools

### 2. Filtering Tools

After scraping, you can filter tools by:
- **Search**: Search by tool name or description
- **Category**: Filter by one or more categories
- **Pricing**: Filter by pricing model (Free, Paid, etc.)

### 3. Exporting Data

- Click the "Export CSV" button to download filtered results
- CSV includes all tool information: name, description, categories, pricing, URL

### 4. Cache Management

- View last update time and tool count in the sidebar
- Clear cache to force fresh scraping
- Cache is automatically updated after each scrape

## Project Structure

```
future_tools_tracker_claude_code/
├── app.py                    # Main Streamlit application
├── scraper.py               # Web scraping logic
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── futuretools_cache.csv   # Cached data (generated)
└── cache_metadata.json     # Cache metadata (generated)
```

## Deployment to Streamlit Cloud

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))

### Steps

1. **Prepare your repository**:
   - Push your code to GitHub
   - Ensure `requirements.txt` and `app.py` are in the root directory

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure settings** (if needed):
   - Go to app settings
   - Add any required secrets or environment variables
   - Set Python version to 3.8+

### Important Notes for Deployment

- **Chrome Driver**: Streamlit Cloud includes Chrome and ChromeDriver, so the app should work without modifications
- **Memory Limits**: Be aware of Streamlit Cloud's resource limits. Large scraping operations might timeout
- **Scraping Duration**: Full scraping may take several minutes. Users should be patient
- **Alternative**: For production use, consider scheduling scraping jobs separately and using the app only for viewing/filtering cached data

### Configuration for Streamlit Cloud

Create a `packages.txt` file in the root directory (if needed):
```
chromium
chromium-driver
```

Create a `.streamlit/config.toml` file for custom settings:
```toml
[server]
maxUploadSize = 200

[browser]
gatherUsageStats = false
```

## Troubleshooting

### Scraping Issues

1. **No tools found**: The website structure may have changed. Check the console for errors.
2. **Timeout errors**: Try scraping fewer categories or increase timeout values in `scraper.py`
3. **Chrome driver issues**: Ensure Chrome browser is installed and up to date

### Performance Issues

1. **Slow scraping**: Use category filters to reduce the number of tools to scrape
2. **Memory errors**: Clear cache and scrape in smaller batches
3. **App freezing**: Refresh the page and try again

## Technical Details

### Web Scraping

- **Framework**: Selenium WebDriver with Chrome
- **Parser**: BeautifulSoup4 with lxml
- **Strategy**: Dynamic content loading with scroll detection
- **Pagination**: Automatic detection and handling

### Data Storage

- **Format**: CSV files for portability
- **Caching**: Local file-based caching
- **Metadata**: JSON-based cache metadata

### UI Framework

- **Streamlit**: Modern Python web framework
- **Styling**: Custom CSS for enhanced UI
- **Responsiveness**: Mobile-friendly design

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes. Please respect FutureTools.io's terms of service and robots.txt when scraping.

## Disclaimer

This tool is designed for personal use and educational purposes. Please ensure you comply with FutureTools.io's terms of service and use rate limiting to avoid overloading their servers.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
