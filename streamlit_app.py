"""
Vedic Astrology Scoring Dashboard - Streamlit App

A comprehensive dashboard for visualizing Vedic astrology scoring data
including planet scores, house activation, and timeline analysis.
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Vedic Astrology Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Title
st.title("🔮 Vedic Astrology Scoring Dashboard")
st.info("⚡ **Powered by Unified Analysis Pipeline** - Complete astrological analysis in one API call with intelligent time segmentation and explainability!")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Chart ID input
    chart_id = st.text_input(
        "Chart ID",
        value="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
        help="Enter the UUID of the natal chart"
    )
    
    # Calculation date
    calc_date = st.date_input(
        "Calculation Date",
        value=datetime(2026, 3, 20),
        help="Date for score calculation"
    )
    
    # Time input
    calc_time = st.time_input(
        "Calculation Time",
        value=datetime.strptime("12:00", "%H:%M").time(),
        help="Time for score calculation"
    )
    
    st.markdown("---")
    
    # Timeline configuration
    st.subheader("📅 Timeline Settings")
    
    start_date = st.date_input(
        "Start Date",
        value=datetime(2026, 3, 1),
        help="Start date for timeline analysis"
    )
    
    end_date = st.date_input(
        "End Date",
        value=datetime(2026, 3, 31),
        help="End date for timeline analysis"
    )
    
    interval_days = st.slider(
        "Interval (days)",
        min_value=1,
        max_value=30,
        value=1,
        help="Days between timeline samples"
    )
    
    st.markdown("---")
    
    # Submit button
    submit_button = st.button(
        "🚀 Generate Dashboard",
        type="primary",
        use_container_width=True
    )

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Main content
if submit_button:
    # Combine date and time
    calculation_datetime = datetime.combine(calc_date, calc_time)
    
    # Show loading spinner
    with st.spinner("🔄 Fetching complete analysis from unified pipeline..."):
        try:
            # Use the unified pipeline endpoint for complete analysis
            pipeline_response = requests.post(
                f"{API_BASE_URL}/analyze/full",
                json={
                    "chart_id": chart_id,
                    "calculation_date": calculation_datetime.isoformat(),
                    "include_timeline": True,
                    "timeline_start_date": datetime.combine(start_date, datetime.min.time()).isoformat(),
                    "timeline_end_date": datetime.combine(end_date, datetime.max.time()).isoformat(),
                    "include_subdomains": True
                },
                timeout=120  # Longer timeout for complete analysis
            )
            pipeline_response.raise_for_status()
            pipeline_data = pipeline_response.json()

            # Extract components from pipeline response
            scoring_data = {
                "chart_id": pipeline_data["chart_id"],
                "planet_scores": pipeline_data["current_planet_scores"]
            }

            house_data = {
                "chart_id": pipeline_data["chart_id"],
                "house_activation": pipeline_data["current_house_activation"]
            }

            domain_data = {
                "chart_id": pipeline_data["chart_id"],
                "domain_analysis": {
                    "overall_life_quality": pipeline_data["current_domain_analysis"]["overall_life_quality"],
                    "strongest_domain": pipeline_data["current_domain_analysis"]["strongest_domain"],
                    "weakest_domain": pipeline_data["current_domain_analysis"]["weakest_domain"],
                    "domains": pipeline_data["current_domain_analysis"]["domains"]
                }
            }

            # Extract timeline data if available
            if pipeline_data.get("timeline_analysis"):
                domain_timeline_data = {
                    "timeline": pipeline_data["timeline_analysis"]
                }
            else:
                # Fallback: fetch domain timeline separately if not in pipeline
                domain_timeline_response = requests.post(
                    f"{API_BASE_URL}/domain-analysis/timeline",
                    json={
                        "chart_id": chart_id,
                        "start_date": datetime.combine(start_date, datetime.min.time()).isoformat(),
                        "end_date": datetime.combine(end_date, datetime.max.time()).isoformat(),
                        "interval_days": interval_days,
                        "include_events": True
                    },
                    timeout=60
                )
                domain_timeline_response.raise_for_status()
                domain_timeline_data = domain_timeline_response.json()

            # Fetch visualization data (still separate as these are visualization-specific)
            timeline_response = requests.get(
                f"{API_BASE_URL}/visualization/{chart_id}/timeline",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "interval_days": interval_days
                },
                timeout=60
            )
            timeline_response.raise_for_status()
            timeline_data = timeline_response.json()

            # Fetch heatmap data
            heatmap_response = requests.get(
                f"{API_BASE_URL}/visualization/{chart_id}/heatmap",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "interval_days": 7  # Weekly for heatmap
                },
                timeout=60
            )
            heatmap_response.raise_for_status()
            heatmap_data = heatmap_response.json()

            # Store in session state
            st.session_state.pipeline_data = pipeline_data  # Store complete pipeline response
            st.session_state.pipeline_summary = pipeline_data.get("summary", {})  # Store summary
            st.session_state.scoring_data = scoring_data
            st.session_state.house_data = house_data
            st.session_state.timeline_data = timeline_data
            st.session_state.heatmap_data = heatmap_data
            st.session_state.domain_data = domain_data
            st.session_state.domain_timeline_data = domain_timeline_data
            st.session_state.data_loaded = True
            st.session_state.chart_id = chart_id
            st.session_state.calc_datetime = calculation_datetime

            st.success("✅ Complete analysis loaded successfully via unified pipeline!")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.stop()

# Display dashboard if data is loaded
if st.session_state.data_loaded:
    scores = st.session_state.scoring_data["planet_scores"]["scores"]
    house_activations = st.session_state.house_data["house_activation"]["house_activations"]

    # Top metrics row
    st.header("📊 Overview")

    # Get top 3 planets
    top_planets = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:3]

    # Get top 3 houses
    top_houses = sorted(
        house_activations.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:3]

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            label=f"🥇 {top_planets[0][0]}",
            value=f"{top_planets[0][1]['score']:.2f}",
            delta="Top Planet"
        )

    with col2:
        st.metric(
            label=f"🥈 {top_planets[1][0]}",
            value=f"{top_planets[1][1]['score']:.2f}",
            delta="2nd"
        )

    with col3:
        st.metric(
            label=f"🥉 {top_planets[2][0]}",
            value=f"{top_planets[2][1]['score']:.2f}",
            delta="3rd"
        )

    with col4:
        st.metric(
            label=f"🏠 House {top_houses[0][0]}",
            value=f"{top_houses[0][1]['score']:.2f}",
            delta="Top House"
        )

    with col5:
        st.metric(
            label=f"🏠 House {top_houses[1][0]}",
            value=f"{top_houses[1][1]['score']:.2f}",
            delta="2nd"
        )

    with col6:
        st.metric(
            label=f"🏠 House {top_houses[2][0]}",
            value=f"{top_houses[2][1]['score']:.2f}",
            delta="3rd"
        )

    st.markdown("---")

    # Create tabs
    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Quick Analysis",
        "🌟 Planet Scores",
        "🏠 House Activation",
        "📈 Timeline & Analysis",
        "🎯 Domain Analysis"
    ])

    # ==================== TAB 0: QUICK ANALYSIS ====================
    with tab0:
        st.header("⚡ Quick Life Analysis")
        st.markdown("*One-shot analysis powered by the unified pipeline*")

        # Get summary from pipeline
        summary = st.session_state.get('pipeline_summary', {})

        if summary:
            # Hero metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="🌟 Overall Life Quality",
                    value=f"{summary.get('overall_life_quality', 0):.1f}/100",
                    help="Average score across all life domains"
                )

            with col2:
                st.metric(
                    label="🏆 Strongest Area",
                    value=summary.get('strongest_domain', 'N/A'),
                    delta=f"{summary.get('strongest_domain_score', 0):.1f}",
                    delta_color="normal"
                )

            with col3:
                st.metric(
                    label="⚠️ Needs Attention",
                    value=summary.get('weakest_domain', 'N/A'),
                    delta=f"{summary.get('weakest_domain_score', 0):.1f}",
                    delta_color="inverse"
                )

            st.markdown("---")

            # Key Insights
            st.subheader("💡 Top Insights")

            insights = summary.get('key_insights', [])
            if insights:
                for i, insight in enumerate(insights[:5], 1):
                    st.info(f"**{i}.** {insight}")
            else:
                st.warning("No insights available")

            st.markdown("---")

            # Domain Scores Overview
            st.subheader("📊 Life Domain Scores")

            domain_scores = summary.get('domain_scores', {})
            if domain_scores:
                # Create bar chart
                df_domains = pd.DataFrame([
                    {"Domain": domain, "Score": score}
                    for domain, score in domain_scores.items()
                ]).sort_values('Score', ascending=True)

                fig_quick = px.bar(
                    df_domains,
                    x='Score',
                    y='Domain',
                    orientation='h',
                    title='Life Domain Scores',
                    color='Score',
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 100],
                    height=400
                )

                fig_quick.update_layout(
                    xaxis_title='Score (0-100)',
                    yaxis_title='',
                    showlegend=False
                )

                st.plotly_chart(fig_quick, use_container_width=True)

                # Domain scores table
                st.dataframe(
                    df_domains.sort_values('Score', ascending=False).style.background_gradient(
                        subset=['Score'],
                        cmap='RdYlGn',
                        vmin=0,
                        vmax=100
                    ),
                    use_container_width=True,
                    height=300
                )
            else:
                st.warning("No domain scores available")

            st.markdown("---")

            # Analysis metadata
            st.caption(f"📅 Analysis generated at: {summary.get('analysis_timestamp', 'N/A')}")
        else:
            st.info("👆 Click 'Generate Dashboard' to see your quick analysis")


    # ==================== TAB 1: PLANET SCORES ====================
    with tab1:
        st.header("🌟 Planet Influence Scores")

        # Stacked Horizontal Bar Chart
        st.subheader("📊 Component Breakdown")

        # Prepare data for stacked bar chart
        planets = []
        dasha_vals = []
        transit_vals = []
        strength_vals = []
        motion_vals = []
        total_scores = []

        for planet, info in sorted(scores.items(),
                                  key=lambda x: x[1]["score"],
                                  reverse=True):
            planets.append(planet)
            wc = info["weighted_components"]
            dasha_vals.append(wc["dasha"])
            transit_vals.append(wc["transit"])
            strength_vals.append(wc["strength"])
            motion_vals.append(wc["motion"])
            total_scores.append(info["score"])

        # Create stacked bar chart
        fig_stacked = go.Figure()

        fig_stacked.add_trace(go.Bar(
            name='Dasha (40%)',
            y=planets,
            x=dasha_vals,
            orientation='h',
            marker=dict(color='#6366f1'),
            hovertemplate='<b>%{y}</b><br>Dasha: %{x:.2f}<extra></extra>'
        ))

        fig_stacked.add_trace(go.Bar(
            name='Transit (30%)',
            y=planets,
            x=transit_vals,
            orientation='h',
            marker=dict(color='#3b82f6'),
            hovertemplate='<b>%{y}</b><br>Transit: %{x:.2f}<extra></extra>'
        ))

        fig_stacked.add_trace(go.Bar(
            name='Strength (22%)',
            y=planets,
            x=strength_vals,
            orientation='h',
            marker=dict(color='#10b981'),
            hovertemplate='<b>%{y}</b><br>Strength: %{x:.2f}<extra></extra>'
        ))

        fig_stacked.add_trace(go.Bar(
            name='Motion (8%)',
            y=planets,
            x=motion_vals,
            orientation='h',
            marker=dict(color='#eab308'),
            hovertemplate='<b>%{y}</b><br>Motion: %{x:.2f}<extra></extra>'
        ))

        fig_stacked.update_layout(
            barmode='stack',
            title='Planet Scores - Weighted Component Breakdown',
            xaxis_title='Weighted Score',
            yaxis_title='Planet',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='closest'
        )

        st.plotly_chart(fig_stacked, use_container_width=True)

        # Two columns for additional visualizations
        col1, col2 = st.columns(2)

        with col1:
            # Radar chart for top 3 planets
            st.subheader("🎯 Top 3 Planets Comparison")

            top_3_planets = sorted(scores.items(),
                                  key=lambda x: x[1]["score"],
                                  reverse=True)[:3]

            fig_radar = go.Figure()

            for planet, info in top_3_planets:
                breakdown = info["breakdown"]

                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        breakdown["dasha"],
                        breakdown["transit"],
                        breakdown["strength"],
                        breakdown["motion"]
                    ],
                    theta=['Dasha', 'Transit', 'Strength', 'Motion'],
                    fill='toself',
                    name=f"{planet} ({info['score']:.2f})"
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Component Comparison (Raw Scores)",
                height=450,
                showlegend=True
            )

            st.plotly_chart(fig_radar, use_container_width=True)

        with col2:
            # Component weights pie chart
            st.subheader("⚖️ Scoring Component Weights")

            weights = {
                'Dasha': 40,
                'Transit': 30,
                'Strength': 22,
                'Motion': 8
            }

            fig_pie = go.Figure(data=[go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=0.4,
                marker=dict(colors=['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#eab308']),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Weight: %{value}%<extra></extra>'
            )])

            fig_pie.update_layout(
                title='Component Weight Distribution',
                height=450,
                showlegend=False
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        # Heatmap of all components
        st.subheader("🔥 Component Heatmap")

        heatmap_data_list = []
        for planet, info in scores.items():
            breakdown = info["breakdown"]
            heatmap_data_list.append({
                'Planet': planet,
                'Dasha': breakdown["dasha"],
                'Transit': breakdown["transit"],
                'Strength': breakdown["strength"],
                'Motion': breakdown["motion"]
            })

        df_heatmap = pd.DataFrame(heatmap_data_list)
        df_heatmap = df_heatmap.set_index('Planet')

        fig_heatmap = px.imshow(
            df_heatmap,
            labels=dict(x="Component", y="Planet", color="Score"),
            x=df_heatmap.columns,
            y=df_heatmap.index,
            color_continuous_scale='RdYlGn',
            aspect="auto",
            title="Planet-Component Score Matrix (Raw Values)"
        )

        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Detailed data table
        st.subheader("📋 Detailed Score Breakdown")

        table_data = []
        for planet, info in scores.items():
            wc = info["weighted_components"]
            bd = info["breakdown"]
            table_data.append({
                'Planet': planet,
                'Total Score': round(info["score"], 2),
                'Dasha (W)': wc["dasha"],
                'Transit (W)': wc["transit"],
                'Strength (W)': wc["strength"],
                'Motion (W)': wc["motion"],
                'Dasha (R)': bd["dasha"],
                'Transit (R)': bd["transit"],
                'Strength (R)': bd["strength"],
                'Motion (R)': bd["motion"]
            })

        df_table = pd.DataFrame(table_data)
        df_table = df_table.sort_values('Total Score', ascending=False)

        # Format numeric columns
        df_table_formatted = df_table.copy()
        df_table_formatted['Total Score'] = df_table_formatted['Total Score'].apply(lambda x: f"{x:.2f}")
        df_table_formatted['Dasha (W)'] = df_table_formatted['Dasha (W)'].apply(lambda x: f"{x:.2f}")
        df_table_formatted['Transit (W)'] = df_table_formatted['Transit (W)'].apply(lambda x: f"{x:.2f}")
        df_table_formatted['Strength (W)'] = df_table_formatted['Strength (W)'].apply(lambda x: f"{x:.2f}")
        df_table_formatted['Motion (W)'] = df_table_formatted['Motion (W)'].apply(lambda x: f"{x:.2f}")
        df_table_formatted['Dasha (R)'] = df_table_formatted['Dasha (R)'].apply(lambda x: f"{x:.0f}")
        df_table_formatted['Transit (R)'] = df_table_formatted['Transit (R)'].apply(lambda x: f"{x:.0f}")
        df_table_formatted['Strength (R)'] = df_table_formatted['Strength (R)'].apply(lambda x: f"{x:.0f}")
        df_table_formatted['Motion (R)'] = df_table_formatted['Motion (R)'].apply(lambda x: f"{x:.0f}")

        st.dataframe(
            df_table_formatted,
            use_container_width=True,
            height=400
        )

        st.caption("(W) = Weighted values, (R) = Raw values")

        # Planet Explanations
        st.subheader("💡 Planet Influence Explanations")

        st.markdown("**Understanding why each planet has its current score:**")

        # Show explanations for top 3 planets
        top_3_planets = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:3]

        for idx, (planet, info) in enumerate(top_3_planets, 1):
            emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"

            with st.expander(f"{emoji} **{planet}** - Score: {info['score']:.2f}"):
                if info.get('explanations'):
                    for explanation in info['explanations']:
                        st.markdown(f"• {explanation}")
                else:
                    st.info("No explanations available for this planet")

    # ==================== TAB 2: HOUSE ACTIVATION ====================
    with tab2:
        st.header("🏠 House Activation Analysis")

        # Horizontal bar chart for house scores
        st.subheader("📊 House Activation Scores")

        house_names = []
        house_total_scores = []
        house_raw_scores = []

        for house_num, house_info in sorted(house_activations.items(),
                                           key=lambda x: x[1]["score"],
                                           reverse=True):
            house_names.append(f"House {house_num}")
            house_total_scores.append(house_info["score"])
            house_raw_scores.append(house_info["raw_score"])

        # Bar chart for houses (normalized scores)
        fig_houses = go.Figure()

        fig_houses.add_trace(go.Bar(
            name='Normalized Score',
            y=house_names,
            x=house_total_scores,
            orientation='h',
            marker=dict(color='#8b5cf6'),
            hovertemplate='<b>%{y}</b><br>Score: %{x:.2f}<extra></extra>',
            text=[f"{score:.1f}" for score in house_total_scores],
            textposition='auto'
        ))

        fig_houses.update_layout(
            title='House Activation Scores (Normalized to 100)',
            xaxis_title='Activation Score',
            yaxis_title='House',
            height=600,
            showlegend=False
        )

        st.plotly_chart(fig_houses, use_container_width=True)

        # Two columns for additional visualizations
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart of house distribution
            st.subheader("🥧 Top Houses Distribution")

            top_6_houses = sorted(house_activations.items(),
                                 key=lambda x: x[1]["score"],
                                 reverse=True)[:6]

            house_labels = [f"House {h[0]}" for h in top_6_houses]
            house_values = [h[1]["score"] for h in top_6_houses]

            fig_house_pie = go.Figure(data=[go.Pie(
                labels=house_labels,
                values=house_values,
                hole=0.3,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Score: %{value:.2f}<extra></extra>'
            )])

            fig_house_pie.update_layout(
                title='Top 6 Houses by Total Score',
                height=400
            )

            st.plotly_chart(fig_house_pie, use_container_width=True)

        with col2:
            # Gauge chart for strongest house
            st.subheader("🎯 Strongest House")

            strongest_house = max(house_activations.items(),
                                 key=lambda x: x[1]["score"])

            avg_score = sum(h["score"] for h in house_activations.values()) / 12
            max_score = max(h["score"] for h in house_activations.values())

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=strongest_house[1]["score"],
                title={'text': f"House {strongest_house[0]}"},
                delta={'reference': avg_score},
                gauge={
                    'axis': {'range': [0, max_score * 1.2]},
                    'bar': {'color': "#8b5cf6"},
                    'steps': [
                        {'range': [0, avg_score * 0.7], 'color': "#fee2e2"},
                        {'range': [avg_score * 0.7, avg_score * 1.3], 'color': "#fef3c7"},
                        {'range': [avg_score * 1.3, max_score * 1.2], 'color': "#d1fae5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': avg_score
                    }
                }
            ))

            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)

        # House details table
        st.subheader("📋 House Activation Details")

        house_table_data = []
        for house_num, house_info in house_activations.items():
            # Get contributors (planets contributing to this house)
            contributors = house_info.get("contributors", {})
            contributor_list = ", ".join([f"{planet}: {score:.1f}" for planet, score in contributors.items()])

            house_table_data.append({
                'House': house_num,
                'Normalized Score': round(house_info["score"], 2),
                'Raw Score': round(house_info["raw_score"], 2),
                'Contributors': contributor_list if contributor_list else "None"
            })

        df_houses = pd.DataFrame(house_table_data)
        df_houses = df_houses.sort_values('Normalized Score', ascending=False)

        # Format numeric columns
        df_houses_formatted = df_houses.copy()
        df_houses_formatted['Normalized Score'] = df_houses_formatted['Normalized Score'].apply(lambda x: f"{x:.2f}")
        df_houses_formatted['Raw Score'] = df_houses_formatted['Raw Score'].apply(lambda x: f"{x:.2f}")

        st.dataframe(
            df_houses_formatted,
            use_container_width=True,
            height=500
        )

    # ==================== TAB 3: TIMELINE & ANALYSIS ====================
    with tab3:
        st.header("📈 Timeline & Trend Analysis")

        # Planet scores over time
        st.subheader("📊 Planet Influence Timeline")

        # Convert timeline data to DataFrame
        timeline_df_list = []
        for dataset in st.session_state.timeline_data["datasets"]:
            planet = dataset["label"]
            for point in dataset["data"]:
                timeline_df_list.append({
                    'Date': point['x'],
                    'Score': point['y'],
                    'Planet': planet
                })

        df_timeline = pd.DataFrame(timeline_df_list)
        df_timeline['Date'] = pd.to_datetime(df_timeline['Date'])

        # Create line chart
        fig_timeline = px.line(
            df_timeline,
            x='Date',
            y='Score',
            color='Planet',
            title=f'Planet Influence Over Time ({start_date} to {end_date})',
            markers=True,
            height=500
        )

        fig_timeline.update_layout(
            xaxis_title='Date',
            yaxis_title='Normalized Score',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        # House activation heatmap over time
        st.subheader("🔥 House Activation Heatmap")

        # Prepare heatmap data
        heatmap_api_data = st.session_state.heatmap_data

        rows = len(heatmap_api_data["row_labels"])
        cols = len(heatmap_api_data["col_labels"])
        z = np.zeros((rows, cols))

        for cell in heatmap_api_data["cells"]:
            z[cell["row"] - 1][cell["col"]] = cell["value"]

        # Create heatmap
        fig_heatmap_time = go.Figure(data=go.Heatmap(
            z=z,
            x=heatmap_api_data["col_labels"],
            y=heatmap_api_data["row_labels"],
            colorscale='RdYlGn',
            hoverongaps=False,
            hovertemplate='House: %{y}<br>Period: %{x}<br>Score: %{z:.2f}<extra></extra>',
            colorbar=dict(title="Activation<br>Score")
        ))

        fig_heatmap_time.update_layout(
            title=f'House Activation Over Time ({start_date} to {end_date})',
            xaxis_title='Time Period',
            yaxis_title='House',
            height=600,
            xaxis={'side': 'bottom'},
            yaxis={'autorange': 'reversed'}
        )

        st.plotly_chart(fig_heatmap_time, use_container_width=True)

        # Statistics and insights
        st.subheader("📊 Statistical Insights")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Most volatile planet
            planet_volatility = df_timeline.groupby('Planet')['Score'].std()
            most_volatile = planet_volatility.idxmax()
            volatility_value = planet_volatility.max()

            st.metric(
                label="Most Volatile Planet",
                value=most_volatile,
                delta=f"σ = {volatility_value:.3f}"
            )

        with col2:
            # Most stable planet
            least_volatile = planet_volatility.idxmin()
            stability_value = planet_volatility.min()

            st.metric(
                label="Most Stable Planet",
                value=least_volatile,
                delta=f"σ = {stability_value:.3f}"
            )

        with col3:
            # Average house activation
            avg_house_activation = np.mean(z)

            st.metric(
                label="Avg House Activation",
                value=f"{avg_house_activation:.2f}",
                delta="Across all periods"
            )

        # Trend analysis
        st.subheader("📈 Trend Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Planet score trends
            st.write("**Planet Score Trends**")

            trend_data = []
            for planet in df_timeline['Planet'].unique():
                planet_data = df_timeline[df_timeline['Planet'] == planet].sort_values('Date')
                if len(planet_data) > 1:
                    first_score = planet_data.iloc[0]['Score']
                    last_score = planet_data.iloc[-1]['Score']
                    change = last_score - first_score
                    pct_change = (change / first_score * 100) if first_score != 0 else 0

                    trend_data.append({
                        'Planet': planet,
                        'Start Score': round(first_score, 2),
                        'End Score': round(last_score, 2),
                        'Change': round(change, 2),
                        'Change %': round(pct_change, 1)
                    })

            df_trends = pd.DataFrame(trend_data)
            df_trends = df_trends.sort_values('Change %', ascending=False)

            # Format numeric columns
            df_trends_formatted = df_trends.copy()
            df_trends_formatted['Start Score'] = df_trends_formatted['Start Score'].apply(lambda x: f"{x:.2f}")
            df_trends_formatted['End Score'] = df_trends_formatted['End Score'].apply(lambda x: f"{x:.2f}")
            df_trends_formatted['Change'] = df_trends_formatted['Change'].apply(lambda x: f"{x:.2f}")
            df_trends_formatted['Change %'] = df_trends_formatted['Change %'].apply(lambda x: f"{x:.1f}%")

            st.dataframe(
                df_trends_formatted,
                use_container_width=True,
                height=350
            )

        with col2:
            # House activation trends
            st.write("**Most Active Houses (Average)**")

            house_avg_scores = []
            for i, house_label in enumerate(heatmap_api_data["row_labels"]):
                avg_score = np.mean(z[i, :])
                house_avg_scores.append({
                    'House': house_label,
                    'Average Score': round(avg_score, 2),
                    'Max Score': round(np.max(z[i, :]), 2),
                    'Min Score': round(np.min(z[i, :]), 2)
                })

            df_house_trends = pd.DataFrame(house_avg_scores)
            df_house_trends = df_house_trends.sort_values('Average Score', ascending=False)

            # Format numeric columns
            df_house_trends_formatted = df_house_trends.copy()
            df_house_trends_formatted['Average Score'] = df_house_trends_formatted['Average Score'].apply(lambda x: f"{x:.2f}")
            df_house_trends_formatted['Max Score'] = df_house_trends_formatted['Max Score'].apply(lambda x: f"{x:.2f}")
            df_house_trends_formatted['Min Score'] = df_house_trends_formatted['Min Score'].apply(lambda x: f"{x:.2f}")

            st.dataframe(
                df_house_trends_formatted,
                use_container_width=True,
                height=350
            )

    # ==================== TAB 4: DOMAIN ANALYSIS ====================
    with tab4:
        st.header("🎯 Life Domain Analysis")

        # Get domain data from session state
        domain_analysis = st.session_state.domain_data['domain_analysis']
        domain_timeline = st.session_state.domain_timeline_data

        # Top metrics row - Overall Life Quality and Top/Bottom Domains
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Overall Life Quality",
                value=f"{domain_analysis['overall_life_quality']:.1f}",
                delta="Average of all domains"
            )

        with col2:
            st.metric(
                label="🏆 Strongest Domain",
                value=domain_analysis['strongest_domain'],
                delta="Top performing area"
            )

        with col3:
            st.metric(
                label="⚠️ Weakest Domain",
                value=domain_analysis['weakest_domain'],
                delta="Needs attention"
            )

        st.markdown("---")

        # Explanations Section - Key Insights
        st.subheader("💡 Key Insights & Explanations")

        # Show explanations for top 3 domains
        sorted_domains = sorted(
            domain_analysis['domains'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        col1, col2, col3 = st.columns(3)

        for idx, (col, (domain_name, domain_info)) in enumerate(zip([col1, col2, col3], sorted_domains[:3])):
            with col:
                emoji = "🏆" if idx == 0 else "🥈" if idx == 1 else "🥉"
                st.markdown(f"### {emoji} {domain_name}")
                st.markdown(f"**Score: {domain_info['score']:.1f}/100**")

                if domain_info.get('explanations'):
                    st.markdown("**Why this score?**")
                    for explanation in domain_info['explanations']:
                        st.markdown(f"• {explanation}")
                else:
                    st.info("No explanations available")

        st.markdown("---")

        # Multi-Line Timeline Chart
        st.subheader("📊 Domain Trends Over Time")

        st.info("💡 **Intelligent Segmentation**: Timeline uses automatic Moon/Sun sign change detection for optimal calculation points, not fixed intervals!")

        # Convert timeline data to DataFrame
        timeline_df_list = []
        for time_point in domain_timeline['timeline']['timeline']:
            date = time_point['date']
            for domain_name, score in time_point['domains'].items():
                timeline_df_list.append({
                    'Date': date,
                    'Score': score,
                    'Domain': domain_name
                })

        df_domain_timeline = pd.DataFrame(timeline_df_list)
        df_domain_timeline['Date'] = pd.to_datetime(df_domain_timeline['Date'], format='ISO8601')

        # Create multi-line chart
        fig_domain_timeline = px.line(
            df_domain_timeline,
            x='Date',
            y='Score',
            color='Domain',
            title=f'Life Domain Scores Over Time ({start_date} to {end_date})',
            markers=True,
            height=500
        )

        fig_domain_timeline.update_layout(
            xaxis_title='Date',
            yaxis_title='Domain Score (0-100)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_domain_timeline, use_container_width=True)

        st.markdown("---")

        # Current State Radar Chart
        st.subheader("🎯 Current Life Balance")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Prepare data for radar chart
            domain_names = []
            domain_scores = []

            for domain_name, domain_info in domain_analysis['domains'].items():
                domain_names.append(domain_name)
                domain_scores.append(domain_info['score'])

            # Create radar chart
            fig_radar = go.Figure()

            fig_radar.add_trace(go.Scatterpolar(
                r=domain_scores,
                theta=domain_names,
                fill='toself',
                name='Current State',
                line=dict(color='rgb(99, 110, 250)', width=2),
                fillcolor='rgba(99, 110, 250, 0.3)'
            ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=False,
                title="Life Balance Radar",
                height=500
            )

            st.plotly_chart(fig_radar, use_container_width=True)

        with col2:
            st.markdown("### 📈 Domain Scores")
            for domain_name, domain_info in sorted(
                domain_analysis['domains'].items(),
                key=lambda x: x[1]['score'],
                reverse=True
            ):
                score = domain_info['score']
                st.metric(
                    label=domain_name,
                    value=f"{score:.1f}",
                    delta=None
                )

        st.markdown("---")

        # Domain Heatmap
        st.subheader("🔥 Domain Intensity Heatmap")

        # Prepare heatmap data
        heatmap_domains = []
        heatmap_dates = []
        heatmap_scores = []

        for time_point in domain_timeline['timeline']['timeline']:
            date_str = pd.to_datetime(time_point['date']).strftime('%Y-%m-%d')
            for domain_name, score in time_point['domains'].items():
                heatmap_domains.append(domain_name)
                heatmap_dates.append(date_str)
                heatmap_scores.append(score)

        df_heatmap = pd.DataFrame({
            'Domain': heatmap_domains,
            'Date': heatmap_dates,
            'Score': heatmap_scores
        })

        # Pivot for heatmap
        heatmap_pivot = df_heatmap.pivot(index='Domain', columns='Date', values='Score')

        fig_heatmap_domain = px.imshow(
            heatmap_pivot,
            labels=dict(x="Date", y="Domain", color="Score"),
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            color_continuous_scale='RdYlGn',
            aspect="auto",
            title="Domain Scores Over Time"
        )

        fig_heatmap_domain.update_layout(height=400)
        st.plotly_chart(fig_heatmap_domain, use_container_width=True)

        st.markdown("---")

        # Planet Drivers Panel
        st.subheader("🌟 Planet Drivers by Domain")

        st.markdown("**Top 3 planets influencing each life domain:**")

        # Create columns for planet drivers
        num_domains = len(domain_analysis['domains'])
        cols_per_row = 2

        domain_items = list(domain_analysis['domains'].items())

        for i in range(0, num_domains, cols_per_row):
            cols = st.columns(cols_per_row)

            for j in range(cols_per_row):
                idx = i + j
                if idx < num_domains:
                    domain_name, domain_info = domain_items[idx]

                    with cols[j]:
                        st.markdown(f"**{domain_name}**")
                        st.markdown(f"*Score: {domain_info['score']:.1f}*")

                        # Show top 3 driving planets
                        for k, planet_driver in enumerate(domain_info['driving_planets'][:3], 1):
                            emoji = "🥇" if k == 1 else "🥈" if k == 2 else "🥉"
                            st.metric(
                                label=f"{emoji} {planet_driver['planet']}",
                                value=f"{planet_driver['contribution']:.2f}",
                                delta=f"Score: {planet_driver['planet_score']:.1f}"
                            )

                        st.markdown("---")

        # Subdomain Breakdown
        st.subheader("📋 Subdomain Breakdown")

        # Create expandable sections for each domain
        for domain_name, domain_info in domain_analysis['domains'].items():
            with st.expander(f"**{domain_name}** - Score: {domain_info['score']:.1f}"):

                # Show explanations first
                if domain_info.get('explanations'):
                    st.markdown("**📖 Detailed Explanation:**")
                    for explanation in domain_info['explanations']:
                        st.markdown(f"• {explanation}")
                    st.markdown("---")

                # Show house and planet contributions
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label="House Contribution",
                        value=f"{domain_info['house_contribution']:.2f}",
                        delta="60% weight"
                    )

                with col2:
                    st.metric(
                        label="Planet Contribution",
                        value=f"{domain_info['planet_contribution']:.2f}",
                        delta="40% weight"
                    )

                # Show subdomains if available
                if domain_info['subdomains']:
                    st.markdown("**Subdomains:**")

                    subdomain_names = []
                    subdomain_scores = []

                    for subdomain_name, subdomain_info in domain_info['subdomains'].items():
                        subdomain_names.append(subdomain_name)
                        subdomain_scores.append(subdomain_info['score'])

                    # Create bar chart for subdomains
                    fig_subdomain = go.Figure(data=[
                        go.Bar(
                            x=subdomain_scores,
                            y=subdomain_names,
                            orientation='h',
                            marker=dict(
                                color=subdomain_scores,
                                colorscale='RdYlGn',
                                showscale=False
                            )
                        )
                    ])

                    fig_subdomain.update_layout(
                        title=f"Subdomain Scores for {domain_name}",
                        xaxis_title="Score",
                        yaxis_title="Subdomain",
                        height=max(200, len(subdomain_names) * 40)
                    )

                    st.plotly_chart(fig_subdomain, use_container_width=True)

                # Show house scores
                if domain_info['house_scores']:
                    st.markdown("**House Activations:**")

                    house_data_list = []
                    for house_num, house_score in domain_info['house_scores'].items():
                        house_data_list.append({
                            'House': f"House {house_num}",
                            'Score': house_score
                        })

                    df_houses = pd.DataFrame(house_data_list)
                    df_houses = df_houses.sort_values('Score', ascending=False)

                    st.dataframe(df_houses, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Domain Comparison Table
        st.subheader("📊 Domain Comparison Table")

        comparison_data = []
        for domain_name, domain_info in domain_analysis['domains'].items():
            # Get top driving planet
            top_planet = domain_info['driving_planets'][0]['planet'] if domain_info['driving_planets'] else "N/A"

            comparison_data.append({
                'Domain': domain_name,
                'Score': domain_info['score'],
                'House Contribution': domain_info['house_contribution'],
                'Planet Contribution': domain_info['planet_contribution'],
                'Top Driver': top_planet,
                'Subdomains': len(domain_info['subdomains'])
            })

        df_comparison = pd.DataFrame(comparison_data)
        df_comparison = df_comparison.sort_values('Score', ascending=False)

        # Format numeric columns
        df_comparison_formatted = df_comparison.copy()
        df_comparison_formatted['Score'] = df_comparison_formatted['Score'].apply(lambda x: f"{x:.2f}")
        df_comparison_formatted['House Contribution'] = df_comparison_formatted['House Contribution'].apply(lambda x: f"{x:.2f}")
        df_comparison_formatted['Planet Contribution'] = df_comparison_formatted['Planet Contribution'].apply(lambda x: f"{x:.2f}")

        st.dataframe(
            df_comparison_formatted,
            use_container_width=True,
            height=350
        )

else:
    # Show instructions when no data is loaded
    st.info("👈 Please configure the settings in the sidebar and click '🚀 Generate Dashboard' to view visualizations.")

    st.markdown("""
    ### 📖 How to Use This Dashboard

    1. **Enter Chart ID**: Provide the UUID of the natal chart you want to analyze
    2. **Set Calculation Date & Time**: Choose when to calculate the scores
    3. **Configure Timeline**: Set start/end dates and interval for timeline analysis
    4. **Generate Dashboard**: Click the button to fetch and visualize data

    ### 📊 Available Visualizations

    #### 🌟 Planet Scores Tab
    - Stacked bar chart showing component breakdown
    - Radar chart comparing top 3 planets
    - Component weight distribution
    - Detailed score heatmap and data table

    #### 🏠 House Activation Tab
    - House activation scores with planet contributions
    - Top houses distribution
    - Strongest house gauge
    - Detailed house activation table

    #### 📈 Timeline & Analysis Tab
    - Planet influence timeline over selected period
    - House activation heatmap over time
    - Statistical insights (volatility, stability)
    - Trend analysis for planets and houses

    #### 🎯 Domain Analysis Tab
    - Overall life quality score and strongest/weakest domains
    - Multi-line timeline chart showing domain trends over time
    - Radar chart for current life balance across all 7 domains
    - Domain intensity heatmap over time
    - Planet drivers panel showing top 3 influencing planets per domain
    - Subdomain breakdown with bar charts and house activations
    - Domain comparison table with sortable scores and contributions

    ### 🔗 API Endpoints Used
    - `POST /scoring/calculate` - Planet scores
    - `POST /house-activation/calculate` - House activation
    - `GET /visualization/{chart_id}/timeline` - Timeline data
    - `GET /visualization/{chart_id}/heatmap` - Heatmap data
    - `POST /domain-analysis/calculate` - Domain analysis with subdomains
    - `POST /domain-analysis/timeline` - Domain timeline data
    """)

