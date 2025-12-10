"""
FutureTools.io Tracker - Streamlit Application
A comprehensive tool to track and explore AI tools from FutureTools.io
"""

import streamlit as st
import pandas as pd
from scraper import FutureToolsScraper, save_to_csv, load_from_csv
from datetime import datetime
import os
import json


# Page configuration
st.set_page_config(
    page_title="FutureTools.io Tracker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .tool-name {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .tool-category {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .tool-pricing {
        display: inline-block;
        background-color: #F3E5F5;
        color: #7B1FA2;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
    }
    .stats-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1976D2;
    }
    .stats-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'tools_data' not in st.session_state:
    st.session_state.tools_data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'scraping_in_progress' not in st.session_state:
    st.session_state.scraping_in_progress = False


def load_cached_data():
    """Load cached data from CSV file"""
    if os.path.exists("futuretools_cache.csv"):
        tools = load_from_csv("futuretools_cache.csv")
        if tools:
            st.session_state.tools_data = tools
            # Load metadata
            if os.path.exists("cache_metadata.json"):
                with open("cache_metadata.json", "r") as f:
                    metadata = json.load(f)
                    st.session_state.last_update = metadata.get("last_update")
            return True
    return False


def save_cached_data(tools):
    """Save data to cache"""
    save_to_csv(tools, "futuretools_cache.csv")
    metadata = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tool_count": len(tools)
    }
    with open("cache_metadata.json", "w") as f:
        json.dump(metadata, f)
    st.session_state.last_update = metadata["last_update"]


def display_tool_card(tool):
    """Display a single tool card"""
    st.markdown(f"""
        <div class="tool-card">
            <div class="tool-name">{tool.get('name', 'Unknown Tool')}</div>
            <p>{tool.get('description', 'No description available')}</p>
            <div>
                {' '.join([f'<span class="tool-category">{cat}</span>' for cat in tool.get('categories', 'Uncategorized').split(', ')])}
                {' '.join([f'<span class="tool-pricing">{price}</span>' for price in tool.get('pricing', 'Not specified').split(', ')])}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if tool.get('url'):
        st.markdown(f"[🔗 Visit Tool]({tool['url']})")
    st.markdown("---")


def main():
    """Main application"""

    # Header
    st.markdown('<div class="main-header">🤖 FutureTools.io Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Track and explore AI tools from FutureTools.io</div>', unsafe_allow_html=True)

    # Load cached data on startup
    if not st.session_state.tools_data and not st.session_state.scraping_in_progress:
        with st.spinner("Loading cached data..."):
            load_cached_data()

    # Sidebar
    st.sidebar.title("⚙️ Configuration")

    # Scraping mode selection
    scrape_mode = st.sidebar.radio(
        "Select Scraping Mode",
        ["Newly Added (Last 24 Hours)", "Full Update (All Tools)", "View Cached Data"]
    )

    # Info about scraping modes
    if scrape_mode == "Full Update (All Tools)":
        st.sidebar.info("⚠️ Full update scrapes ALL tools from the website (~2000+ tools). This may take 5-10 minutes. You can filter by category after scraping.")
    elif scrape_mode == "Newly Added (Last 24 Hours)":
        st.sidebar.info("⏱️ Scrapes only the most recently added tools (usually 1-10 tools).")

    # Scrape button
    if scrape_mode != "View Cached Data":
        st.sidebar.markdown("---")
        scrape_button = st.sidebar.button("🚀 Start Scraping", type="primary", use_container_width=True)

        if scrape_button:
            st.session_state.scraping_in_progress = True

            with st.spinner("Scraping in progress... This may take several minutes."):
                scraper = FutureToolsScraper(headless=True)

                if scrape_mode == "Newly Added (Last 24 Hours)":
                    st.info("🔍 Scraping newly added tools from the last 24 hours...")
                    tools = scraper.scrape_newly_added()
                else:
                    st.info("🔍 Scraping ALL tools from FutureTools.io... This will take 5-10 minutes.")
                    tools = scraper.scrape_all_tools()

                if tools:
                    st.session_state.tools_data = tools
                    save_cached_data(tools)
                    st.success(f"✅ Successfully scraped {len(tools)} tools!")
                else:
                    st.warning("⚠️ No tools found. The website might have changed its structure.")

            st.session_state.scraping_in_progress = False
            st.rerun()

    # Display cache info
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Cache Information")
    if st.session_state.last_update:
        st.sidebar.info(f"Last updated: {st.session_state.last_update}")
        st.sidebar.info(f"Tools in cache: {len(st.session_state.tools_data)}")
    else:
        st.sidebar.info("No cached data available")

    # Clear cache button
    if st.sidebar.button("🗑️ Clear Cache"):
        if os.path.exists("futuretools_cache.csv"):
            os.remove("futuretools_cache.csv")
        if os.path.exists("cache_metadata.json"):
            os.remove("cache_metadata.json")
        st.session_state.tools_data = []
        st.session_state.last_update = None
        st.sidebar.success("Cache cleared!")
        st.rerun()

    # Main content area
    if st.session_state.tools_data:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(st.session_state.tools_data)}</div>
                    <div class="stats-label">Total Tools</div>
                </div>
            """, unsafe_allow_html=True)

        # Extract unique categories and pricing
        all_categories = set()
        all_pricing = set()
        for tool in st.session_state.tools_data:
            cats = tool.get('categories', '').split(', ')
            all_categories.update([c for c in cats if c and c != 'Uncategorized'])
            prices = tool.get('pricing', '').split(', ')
            all_pricing.update([p for p in prices if p and p != 'Not specified'])

        with col2:
            st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(all_categories)}</div>
                    <div class="stats-label">Categories</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            free_tools = len([t for t in st.session_state.tools_data if 'Free' in t.get('pricing', '')])
            st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{free_tools}</div>
                    <div class="stats-label">Free Tools</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            paid_tools = len([t for t in st.session_state.tools_data if 'Paid' in t.get('pricing', '')])
            st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{paid_tools}</div>
                    <div class="stats-label">Paid Tools</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Filters
        st.subheader("🔍 Filter Tools")

        col1, col2, col3 = st.columns(3)

        with col1:
            search_query = st.text_input("🔎 Search by name or description", "")

        with col2:
            filter_categories = st.multiselect(
                "Filter by Category",
                options=sorted(all_categories),
                default=[]
            )

        with col3:
            filter_pricing = st.multiselect(
                "Filter by Pricing",
                options=sorted(all_pricing),
                default=[]
            )

        # Apply filters
        filtered_tools = st.session_state.tools_data

        if search_query:
            filtered_tools = [
                t for t in filtered_tools
                if search_query.lower() in t.get('name', '').lower() or
                   search_query.lower() in t.get('description', '').lower()
            ]

        if filter_categories:
            filtered_tools = [
                t for t in filtered_tools
                if any(cat in t.get('categories', '') for cat in filter_categories)
            ]

        if filter_pricing:
            filtered_tools = [
                t for t in filtered_tools
                if any(price in t.get('pricing', '') for price in filter_pricing)
            ]

        # Display results
        st.markdown("---")
        st.subheader(f"📋 Showing {len(filtered_tools)} Tools")

        # Export options
        col1, col2 = st.columns([6, 1])
        with col2:
            if filtered_tools:
                df = pd.DataFrame(filtered_tools)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export CSV",
                    data=csv,
                    file_name=f"futuretools_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

        # Display tools
        if filtered_tools:
            # Pagination
            tools_per_page = 10
            total_pages = (len(filtered_tools) - 1) // tools_per_page + 1

            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )

            start_idx = (page - 1) * tools_per_page
            end_idx = min(start_idx + tools_per_page, len(filtered_tools))

            st.info(f"Showing tools {start_idx + 1} to {end_idx} of {len(filtered_tools)}")

            for tool in filtered_tools[start_idx:end_idx]:
                display_tool_card(tool)
        else:
            st.warning("No tools found matching your filters.")

    else:
        # Empty state
        st.info("👈 Select a scraping mode from the sidebar and click 'Start Scraping' to begin!")

        st.markdown("""
        ### How to use this app:

        1. **Newly Added (Last 24 Hours)**: Scrapes only the tools added in the last 24 hours (fastest, ~1-10 tools)
        2. **Full Update (All Tools)**: Scrapes ALL tools from FutureTools.io (~2000+ tools, takes 5-10 minutes)
        3. **View Cached Data**: View previously scraped data without scraping again

        ### Features:
        - Filter tools by category, pricing, or search term after scraping
        - Export filtered results to CSV
        - View detailed information about each tool
        - Cache data for faster access

        ### Important Notes:
        - **Full scraping loads ALL tools** from the website regardless of filters, because the website uses client-side filtering
        - After scraping, use the filter section above to narrow down by category or pricing
        - Categories and pricing filters work on already-scraped data
        - Pricing information may show "Check tool page" as it's not always available on list pages
        - Data is cached locally for quick access
        """)


if __name__ == "__main__":
    main()
