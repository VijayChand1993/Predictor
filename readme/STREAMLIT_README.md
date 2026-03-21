# 🔮 Vedic Astrology Scoring Dashboard

A comprehensive Streamlit dashboard for visualizing Vedic astrology scoring data from the Predictor API.

## 📋 Features

### 🌟 Planet Scores Tab
- **Stacked Bar Chart**: Shows weighted component breakdown for all planets
- **Radar Chart**: Compares top 3 planets across all components
- **Component Weights Pie Chart**: Displays the weight distribution (Dasha 35%, Transit 25%, etc.)
- **Component Heatmap**: Matrix view of all planet-component scores
- **Detailed Data Table**: Complete breakdown with both weighted and raw values

### 🏠 House Activation Tab
- **House Activation Scores**: Stacked bar chart showing planet and aspect contributions
- **Top Houses Distribution**: Pie chart of the 6 most activated houses
- **Strongest House Gauge**: Visual indicator of the most activated house
- **House Details Table**: Complete information including planets in house and aspecting planets

### 📈 Timeline & Analysis Tab
- **Planet Influence Timeline**: Line chart showing how planet scores change over time
- **House Activation Heatmap**: Time-based heatmap of house activation
- **Statistical Insights**: Volatility and stability metrics
- **Trend Analysis**: Score changes and percentage trends for planets and houses

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Dashboard framework
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `requests` - API calls

### 2. Ensure FastAPI Server is Running

The dashboard requires the FastAPI backend to be running:

```bash
uvicorn main:app --reload
```

The API should be accessible at `http://localhost:8000`

## 🎯 Usage

### Start the Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Configure Settings

1. **Chart ID**: Enter the UUID of the natal chart (default: `04ecf146-d0e1-4e72-8c30-fb8bba03e2e5`)
2. **Calculation Date & Time**: Set when to calculate scores
3. **Timeline Settings**:
   - Start Date: Beginning of timeline analysis
   - End Date: End of timeline analysis
   - Interval: Days between samples (1-30)

### Generate Visualizations

Click the **🚀 Generate Dashboard** button to:
1. Fetch data from all API endpoints
2. Process and visualize the data
3. Display interactive charts across 3 tabs

## 📊 API Endpoints Used

The dashboard calls the following endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/scoring/calculate` | POST | Get planet scores with component breakdown |
| `/house-activation/calculate` | POST | Get house activation scores |
| `/visualization/{chart_id}/timeline` | GET | Get timeline data for planet scores |
| `/visualization/{chart_id}/heatmap` | GET | Get house activation heatmap data |

## 🎨 Visualizations

### Color Scheme

**Component Colors:**
- 🟣 Dasha (35%) - Purple `#6366f1`
- 🔵 Transit (25%) - Blue `#3b82f6`
- 🟢 Strength (20%) - Green `#10b981`
- 🟠 Aspect (12%) - Orange `#f59e0b`
- 🟡 Motion (8%) - Yellow `#eab308`

**House Colors:**
- 🟣 Planet Score - Purple `#8b5cf6`
- 🌸 Aspect Score - Pink `#ec4899`

### Interactive Features

All charts support:
- ✅ Hover tooltips with detailed information
- ✅ Zoom and pan
- ✅ Legend filtering (click to hide/show)
- ✅ Download as PNG
- ✅ Responsive layout

## 🔧 Configuration

### API Base URL

To change the API endpoint, edit `streamlit_app.py`:

```python
API_BASE_URL = "http://localhost:8000"  # Change this if needed
```

### Default Values

Default chart ID and dates can be modified in the sidebar configuration section.

## 📝 Example Workflow

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Launch the dashboard**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Configure settings** in the sidebar

4. **Click "Generate Dashboard"** to fetch and visualize data

5. **Explore the 3 tabs**:
   - Planet Scores - Component analysis
   - House Activation - House-level insights
   - Timeline & Analysis - Temporal trends

## 🐛 Troubleshooting

### Connection Error

If you see "Error fetching data":
- Ensure FastAPI server is running on `http://localhost:8000`
- Check that the chart ID exists in the database
- Verify the date range is valid

### Missing Dependencies

If imports fail:
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

If port 8501 is busy:
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 📚 Technical Details

- **Framework**: Streamlit 1.28+
- **Visualization**: Plotly 5.17+
- **Data Processing**: Pandas 2.0+
- **API Client**: Requests 2.31+

## 🎯 Future Enhancements

Potential additions:
- Export data to CSV/Excel
- Save/load dashboard configurations
- Compare multiple charts side-by-side
- Custom date range presets
- Real-time updates
- PDF report generation

