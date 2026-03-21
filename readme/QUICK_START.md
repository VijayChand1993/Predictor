# 🚀 Quick Start Guide - Streamlit Dashboard

## ⚡ Fastest Way to Run

### Option 1: One-Line Start (Recommended)

```bash
./run_dashboard.sh
```

This script will:
- ✅ Activate virtual environment
- ✅ Check and install dependencies
- ✅ Start FastAPI server (port 8000)
- ✅ Start Streamlit dashboard (port 8501)
- ✅ Handle cleanup on exit (Ctrl+C)

### Option 2: Manual Start

**Terminal 1 - FastAPI Backend:**
```bash
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Streamlit Dashboard:**
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

## 🔧 First Time Setup

If you haven't installed the new dependencies yet:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

This will install:
- `streamlit` - Dashboard framework
- `plotly` - Interactive charts
- `pandas` - Data processing
- `numpy` - Numerical operations
- `requests` - API client

## 🌐 Access the Dashboard

Once running, open your browser to:

- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **FastAPI API**: http://localhost:8000

## 📝 Using the Dashboard

### Step 1: Configure Settings (Sidebar)

1. **Chart ID**: Enter the UUID of your natal chart
   - Default: `04ecf146-d0e1-4e72-8c30-fb8bba03e2e5`

2. **Calculation Date**: Choose the date for score calculation
   - Default: `2026-03-20`

3. **Calculation Time**: Set the time
   - Default: `12:00`

4. **Timeline Settings**:
   - Start Date: `2026-03-01`
   - End Date: `2026-03-31`
   - Interval: `1` day

### Step 2: Generate Dashboard

Click the **🚀 Generate Dashboard** button

The app will:
- Fetch data from 4 API endpoints
- Process and visualize the data
- Display results in 3 tabs

### Step 3: Explore Visualizations

**Tab 1: 🌟 Planet Scores**
- Stacked bar chart (component breakdown)
- Radar chart (top 3 planets)
- Component weights pie chart
- Heatmap (all components)
- Detailed data table

**Tab 2: 🏠 House Activation**
- House scores bar chart
- Top houses pie chart
- Strongest house gauge
- House details table

**Tab 3: 📈 Timeline & Analysis**
- Planet influence timeline
- House activation heatmap
- Statistical insights
- Trend analysis

## 🐛 Troubleshooting

### Error: "Connection refused" or "Error fetching data"

**Solution**: Make sure FastAPI is running
```bash
# Check if FastAPI is running
curl http://localhost:8000/health

# If not, start it
uvicorn main:app --reload
```

### Error: "Module not found"

**Solution**: Install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Port already in use"

**Solution**: Use different ports
```bash
# For FastAPI (if 8000 is busy)
uvicorn main:app --reload --port 8001

# For Streamlit (if 8501 is busy)
streamlit run streamlit_app.py --server.port 8502
```

Then update `API_BASE_URL` in `streamlit_app.py` if you changed FastAPI port.

### Error: "Chart ID not found"

**Solution**: Use a valid chart ID from your database
```bash
# List available charts
curl http://localhost:8000/chart/list
```

## 📊 Example Chart IDs

If you need test data, here are some chart IDs that should exist:
- `04ecf146-d0e1-4e72-8c30-fb8bba03e2e5`
- `07c4ab6b-e2d5-4832-920e-95a2285da9c3`
- `1d51de8f-ba5c-4608-9653-ce6acc4a5ab3`

## 🛑 Stopping the Services

### If using run_dashboard.sh:
Press `Ctrl+C` - it will stop both services automatically

### If running manually:
Press `Ctrl+C` in each terminal window

## 💡 Tips

1. **Bookmark the dashboard**: Add http://localhost:8501 to your bookmarks
2. **Keep FastAPI running**: Leave it running in the background while you work
3. **Refresh data**: Click "Generate Dashboard" again to refresh with new settings
4. **Download charts**: Use the camera icon on any Plotly chart to download as PNG
5. **Zoom and pan**: All charts are interactive - click and drag to zoom

## 📚 More Information

- Full documentation: See `STREAMLIT_README.md`
- API documentation: http://localhost:8000/docs
- Project README: See `README.md`

## ✅ Verification Checklist

Before reporting issues, verify:
- [ ] Virtual environment is activated
- [ ] All dependencies are installed (`pip list | grep streamlit`)
- [ ] FastAPI is running (check http://localhost:8000/docs)
- [ ] Chart ID exists in database
- [ ] Date range is valid
- [ ] No firewall blocking ports 8000 or 8501

---

**Need help?** Check the full documentation in `STREAMLIT_README.md`

