
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data import generate_partners, generate_sales, generate_activity, generate_social_activity
from visualization import render_network_graph, display_partner_details
from config import LEVELS, SOCIAL_METRICS, STATUS_OPTIONS, COLOR_MAP

### --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Partner Revenue & Activity Dashboard", page_icon="📊")
st.markdown("# Partner Revenue & Activity Dashboard")
st.markdown("This dashboard visualizes a partner hierarchy, revenue, activity data, and digital/social KPIs. Use the sidebar to filter or upload your own data.")

# --- Data Upload or Generation ---
uploaded = st.sidebar.file_uploader("Upload Partner Data (CSV)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    if 'df' not in st.session_state:
        st.session_state.df = generate_partners()
    df = st.session_state.df

if 'sales' not in st.session_state or st.sidebar.button("Regenerate Synthetic Dataset"):
    with st.spinner("Generating synthetic data..."):
        st.session_state.df = generate_partners()
        df = st.session_state.df
        st.session_state.sales = generate_sales(df)
        st.session_state.activity = generate_activity(df)
        st.session_state.social = generate_social_activity(df)
        st.success("✅ New synthetic data generated!")

sales = st.session_state.sales
activity = st.session_state.activity
social = st.session_state.social if 'social' in st.session_state else generate_social_activity(df)

# --- Sidebar Filters ---
st.sidebar.markdown("## Filters")

# Level filters
levels = df['level'].unique().tolist()
selected_levels = st.sidebar.multiselect("Filter by Level", levels, default=levels)

# Status filters
statuses = df['status'].unique().tolist()
selected_statuses = st.sidebar.multiselect("Filter by Status", statuses, default=statuses)

# Partner search functionality 
st.sidebar.markdown("## Search")
search_query = st.sidebar.text_input("Search Partner by Name or ID")
partner_names = df[(df['level'].isin(selected_levels)) & 
                   (df['status'].isin(selected_statuses))]['name'].tolist()

if search_query:
    # Filter partner list based on search
    partner_names = [name for name in partner_names if search_query.lower() in name.lower()]
    if len(partner_names) == 0:
        st.sidebar.warning("No partners found matching your search.")

# Partner selection
selected_partner = st.sidebar.selectbox("Select Partner", [None] + partner_names)

# Apply all filters
filtered_df = df[df['level'].isin(selected_levels) & df['status'].isin(selected_statuses)]

# If search is active, apply search filter
if search_query and not selected_partner:
    filtered_df = filtered_df[
        filtered_df['name'].str.lower().str.contains(search_query.lower()) |
        filtered_df['partner_id'].astype(str).str.contains(search_query)
    ]

# Filter related datasets
filtered_sales = sales[sales['partner_id'].isin(filtered_df['partner_id'])]
filtered_activity = activity[activity['partner_id'].isin(filtered_df['partner_id'])]
filtered_social = social[social['partner_id'].isin(filtered_df['partner_id'])]

# If a specific partner is selected
selected_partner_id = None
if selected_partner:
    selected_partner_id = df[df['name'] == selected_partner]['partner_id'].values[0]
    filtered_sales = filtered_sales[filtered_sales['partner_id'] == selected_partner_id]
    filtered_activity = filtered_activity[filtered_activity['partner_id'] == selected_partner_id]
    filtered_social = filtered_social[filtered_social['partner_id'] == selected_partner_id]

# --- Summary Statistics ---
# Revenue summary
summary = filtered_sales.groupby('partner_id').agg({'revenue':'sum'}).reset_index().merge(
    filtered_df[['partner_id','name','level','status']], on='partner_id')

# Activity summary
activity_summary = filtered_activity.groupby('partner_id').size().reset_index(name='activity_count').merge(
    filtered_df[['partner_id','name','level','status']], on='partner_id')

# Social metrics summary
social_summary = filtered_social.groupby('partner_id').agg({
    'posts': 'sum', 
    'shares': 'sum', 
    'sentiment': 'mean',
    'advocacy_score': 'mean',
    'reviews': 'sum'
}).reset_index().merge(filtered_df[['partner_id','name','level','status']], on='partner_id')

# Combined KPI summary for ranking
kpi_summary = summary.merge(
    activity_summary[['partner_id', 'activity_count']], 
    on='partner_id', how='left'
).merge(
    social_summary[['partner_id', 'posts', 'shares', 'sentiment', 'advocacy_score', 'reviews']],
    on='partner_id', how='left'
).fillna(0)

# Aggregate by level
level_revenue = filtered_sales.merge(filtered_df[['partner_id','level']], on='partner_id').groupby('level')['revenue'].sum()
level_activity = filtered_activity.merge(filtered_df[['partner_id','level']], on='partner_id').groupby('level').size()
level_social = filtered_social.merge(filtered_df[['partner_id','level']], on='partner_id').groupby('level').agg({
    'posts': 'sum', 
    'shares': 'sum',
    'advocacy_score': 'mean',
    'sentiment': 'mean'
})

# Convert dates for time series analysis
sales['date'] = pd.to_datetime(sales['date'])
activity['date'] = pd.to_datetime(activity['date'])
social['date'] = pd.to_datetime(social['date'])

# Time series summaries
revenue_time = filtered_sales.groupby('date')['revenue'].sum().reset_index()
activity_time = filtered_activity.groupby('date').size().reset_index(name='activity_count')
social_time = filtered_social.groupby('date').agg({
    'posts': 'sum', 
    'shares': 'sum',
    'sentiment': 'mean',
    'advocacy_score': 'mean',
    'reviews': 'sum'
}).reset_index()

# --- Top/Bottom Performers (multiple KPIs) ---
# Revenue
top_revenue = kpi_summary.sort_values('revenue', ascending=False).head(5)
bottom_revenue = kpi_summary.sort_values('revenue', ascending=True).head(5)

# Activity
top_activity = kpi_summary.sort_values('activity_count', ascending=False).head(5)
bottom_activity = kpi_summary.sort_values('activity_count', ascending=True).head(5)

# Social KPIs
top_advocacy = kpi_summary.sort_values('advocacy_score', ascending=False).head(5)
top_engagement = kpi_summary.sort_values('posts', ascending=False).head(5)
top_sentiment = kpi_summary.sort_values('sentiment', ascending=False).head(5)

# --- Tabs for UI ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Network Graph", "Partner Details", "Dashboard", "Social & Digital KPIs", "Performance", "Export"
])

# --- Tab 1: Network Graph ---
with tab1:
    st.markdown("## Partner Hierarchy Network")
    st.markdown("Visualize your entire partner network as an interactive graph. Each node represents a partner, sized by revenue, colored by level.")
    
    # Controls for the network graph
    net_cols = st.columns([3, 1])
    with net_cols[1]:
        st.markdown("### Network Controls")
        st.info("👆 Click on any node to see partner details")
        st.markdown("#### Network Legend")
        for level, color in COLOR_MAP.items():
            st.markdown(f"<span style='color:{color}'>●</span> {level}", unsafe_allow_html=True)
    
    with net_cols[0]:
        # Render the interactive network graph
        render_network_graph(filtered_df, selected_partner_id)

# --- Tab 2: Partner Details ---
with tab2:
    if selected_partner:
        # Show detailed partner information for the selected partner
        display_partner_details(df, sales, activity, social, selected_partner_id)
    else:
        st.markdown("## Partner Details")
        st.info("👈 Select a partner from the sidebar to view detailed information")
        
        # Show the partner table with enhanced fields when no specific partner is selected
        st.markdown("### Partner Dataset Table")
        display_cols = ['partner_id', 'name', 'level', 'status', 'join_date', 
                      'total_revenue', 'posts', 'shares', 'sentiment', 'advocacy_score']
        st.dataframe(filtered_df[display_cols], use_container_width=True)

# --- Tab 3: Dashboard ---
with tab3:
    st.markdown("## Revenue & Activity Overview")
    
    # Summary metrics in a single row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${filtered_sales['revenue'].sum():,.2f}")
    col2.metric("Total Activities", f"{filtered_activity.shape[0]:,}")
    col3.metric("Total Social Posts", f"{filtered_social['posts'].sum():,}")
    col4.metric("Avg Advocacy Score", f"{filtered_social['advocacy_score'].mean():.1f}/100")
    
    # Revenue and activity by partner level
    st.markdown("### Performance by Partner Level")
    level_cols = st.columns(2)
    
    with level_cols[0]:
        st.markdown("#### Revenue by Level")
        fig = px.bar(level_revenue.reset_index(), x='level', y='revenue',
                   color='level', color_discrete_map=COLOR_MAP,
                   title='Revenue by Partner Level')
        st.plotly_chart(fig, use_container_width=True)
    
    with level_cols[1]:
        st.markdown("#### Activity Count by Level")
        fig = px.bar(level_activity.reset_index(), x='level', y=0,
                   color='level', color_discrete_map=COLOR_MAP,
                   title='Activity Count by Partner Level')
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series charts
    st.markdown("### Trends Over Time")
    time_cols = st.columns(2)
    
    with time_cols[0]:
        fig1 = px.line(revenue_time, x='date', y='revenue', title='Revenue Over Time')
        st.plotly_chart(fig1, use_container_width=True)
    
    with time_cols[1]:
        fig2 = px.line(activity_time, x='date', y='activity_count', title='Activity Over Time')
        st.plotly_chart(fig2, use_container_width=True)

# --- Tab 4: Social & Digital KPIs ---
with tab4:
    st.markdown("## Social & Digital KPIs Dashboard")
    
    # Social metrics summary
    social_metric_cols = st.columns(4)
    social_metric_cols[0].metric("Total Posts", f"{filtered_social['posts'].sum():,}")
    social_metric_cols[1].metric("Total Shares", f"{filtered_social['shares'].sum():,}")
    social_metric_cols[2].metric("Avg Sentiment", f"{filtered_social['sentiment'].mean():.2f}")
    social_metric_cols[3].metric("Total Reviews", f"{filtered_social['reviews'].sum():,}")
    
    # Social metrics over time
    st.markdown("### Social Media Activity Over Time")
    
    # Posts and shares over time
    social_time_cols = st.columns(2)
    
    with social_time_cols[0]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=social_time['date'], y=social_time['posts'], 
                                mode='lines', name='Posts'))
        fig.update_layout(title='Posts Over Time', xaxis_title='Date', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)
    
    with social_time_cols[1]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=social_time['date'], y=social_time['shares'], 
                                mode='lines', name='Shares'))
        fig.update_layout(title='Shares Over Time', xaxis_title='Date', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment and advocacy over time
    sentiment_cols = st.columns(2)
    
    with sentiment_cols[0]:
        fig = px.line(social_time, x='date', y='sentiment', title='Average Sentiment Over Time')
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
    
    with sentiment_cols[1]:
        fig = px.line(social_time, x='date', y='advocacy_score', title='Average Advocacy Score Over Time')
        st.plotly_chart(fig, use_container_width=True)
    
    # Social metrics by partner level
    st.markdown("### Social KPIs by Partner Level")
    
    social_level_cols = st.columns(2)
    
    with social_level_cols[0]:
        fig = px.bar(level_social.reset_index(), x='level', y=['posts', 'shares'],
                   title='Social Activity by Partner Level',
                   color='level', color_discrete_map=COLOR_MAP,
                   barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with social_level_cols[1]:
        fig = px.bar(level_social.reset_index(), x='level', y=['advocacy_score', 'sentiment'],
                   title='Advocacy & Sentiment by Partner Level',
                   color='level', color_discrete_map=COLOR_MAP,
                   barmode='group')
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 5: Performance ---
with tab5:
    st.markdown("## Partner Performance Rankings")
    
    # KPI selection for ranking
    kpi_options = ["Revenue", "Activity Count", "Posts", "Shares", "Sentiment", "Advocacy Score"]
    selected_kpi = st.selectbox("Select KPI to Rank Partners", kpi_options)
    
    # Map selection to dataframe column
    kpi_column_map = {
        "Revenue": "revenue",
        "Activity Count": "activity_count",
        "Posts": "posts",
        "Shares": "shares",
        "Sentiment": "sentiment",
        "Advocacy Score": "advocacy_score"
    }
    
    selected_column = kpi_column_map[selected_kpi]
    
    # Display top and bottom performers for the selected KPI
    perf_cols = st.columns(2)
    
    with perf_cols[0]:
        st.markdown(f"### Top 10 by {selected_kpi}")
        top_performers = kpi_summary.sort_values(selected_column, ascending=False).head(10)
        
        if selected_kpi == "Revenue":
            top_performers[selected_column] = top_performers[selected_column].map('${:,.2f}'.format)
        
        st.dataframe(
            top_performers[['name', 'level', 'status', selected_column]], 
            use_container_width=True
        )
    
    with perf_cols[1]:
        st.markdown(f"### Bottom 10 by {selected_kpi}")
        bottom_performers = kpi_summary.sort_values(selected_column, ascending=True).head(10)
        
        if selected_kpi == "Revenue":
            bottom_performers[selected_column] = bottom_performers[selected_column].map('${:,.2f}'.format)
        
        st.dataframe(
            bottom_performers[['name', 'level', 'status', selected_column]], 
            use_container_width=True
        )
    
    # Multi-KPI view
    st.markdown("### Multi-KPI Performance View")
    
    # Allow selection of partners to compare
    partners_to_compare = st.multiselect(
        "Select Partners to Compare (max 5)", 
        options=kpi_summary['name'].tolist(),
        max_selections=5
    )
    
    if partners_to_compare:
        # Create a radar chart for multi-KPI comparison
        comparison_df = kpi_summary[kpi_summary['name'].isin(partners_to_compare)]
        
        # Normalize metrics for radar chart
        metrics_to_compare = ['revenue', 'activity_count', 'posts', 'shares', 'advocacy_score']
        normalized_df = comparison_df.copy()
        
        for metric in metrics_to_compare:
            max_val = kpi_summary[metric].max() if kpi_summary[metric].max() > 0 else 1
            normalized_df[f"{metric}_normalized"] = comparison_df[metric] / max_val * 100
        
        # Create radar chart
        fig = go.Figure()
        
        for _, row in normalized_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[f"{m}_normalized"] for m in metrics_to_compare],
                theta=['Revenue', 'Activity', 'Posts', 'Shares', 'Advocacy'],
                fill='toself',
                name=row['name']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Multi-KPI Performance Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select partners to compare their performance across multiple KPIs")

# --- Tab 6: Export ---
with tab6:
    st.markdown("## Export Summary Statistics")
    
    export_cols = st.columns(3)
    
    with export_cols[0]:
        st.markdown("### Revenue Data")
        st.download_button(
            label="Download Revenue Summary as CSV",
            data=summary.to_csv(index=False),
            file_name="revenue_summary.csv",
            mime="text/csv"
        )
    
    with export_cols[1]:
        st.markdown("### Activity Data")
        st.download_button(
            label="Download Activity Summary as CSV",
            data=activity_summary.to_csv(index=False),
            file_name="activity_summary.csv",
            mime="text/csv"
        )
    
    with export_cols[2]:
        st.markdown("### Social KPI Data")
        st.download_button(
            label="Download Social KPI Summary as CSV",
            data=social_summary.to_csv(index=False),
            file_name="social_summary.csv",
            mime="text/csv"
        )
    
    # Combined export
    st.markdown("### Complete Partner Performance Data")
    st.download_button(
        label="Download Complete KPI Dataset as CSV",
        data=kpi_summary.to_csv(index=False),
        file_name="partner_complete_kpi_summary.csv",
        mime="text/csv"
    )
    
    # Time series exports
    time_export_cols = st.columns(3)
    
    with time_export_cols[0]:
        st.download_button(
            label="Download Revenue Time Series",
            data=revenue_time.to_csv(index=False),
            file_name="revenue_time_series.csv",
            mime="text/csv"
        )
    
    with time_export_cols[1]:
        st.download_button(
            label="Download Activity Time Series",
            data=activity_time.to_csv(index=False),
            file_name="activity_time_series.csv",
            mime="text/csv"
        )
    
    with time_export_cols[2]:
        st.download_button(
            label="Download Social Time Series",
            data=social_time.to_csv(index=False),
            file_name="social_time_series.csv",
            mime="text/csv"
        )