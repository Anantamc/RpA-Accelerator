import networkx as nx
from pyvis.network import Network
import tempfile
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import COLOR_MAP, SOCIAL_METRICS

def render_network_graph(filtered_df, selected_node=None):
    G = nx.DiGraph()
    
    # Add nodes with all partner attributes
    for _, row in filtered_df.iterrows():
        # Store all row data for detailed view
        G.add_node(row['partner_id'], 
                 label=row['name'], 
                 level=row['level'], 
                 join_date=row['join_date'],
                 status=row['status'],
                 posts=row['posts'],
                 shares=row['shares'],
                 sentiment=row['sentiment'],
                 advocacy_score=row['advocacy_score'],
                 engagement=row['engagement'],
                 total_revenue=row['total_revenue']
                 )
    
    # Add edges (relationships)
    for _, row in filtered_df.iterrows():
        if row['parent_id'] and row['parent_id'] in filtered_df['partner_id'].values:
            G.add_edge(row['parent_id'], row['partner_id'])
    
    # Create the network visualization
    net = Network(height="600px", width="100%", directed=True, notebook=False)
    
    # Set network options for better visualization
    net.set_options("""
    const options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "springLength": 100,
          "avoidOverlap": 1
        },
        "maxVelocity": 50,
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200
      }
    }
    """)
    
    # Add nodes to network with enhanced tooltips
    for node, data in G.nodes(data=True):
        # Size nodes by revenue for visual importance
        size = min(50, max(20, int(data['total_revenue'] / 2000)))
        
        # Create a detailed HTML tooltip
        tooltip = f"""
        <div style='font-family:Arial; max-width:300px; padding:10px; background:#f9f9f9; border:1px solid #ddd;'>
            <h3 style='margin:0 0 10px 0'>{data['label']}</h3>
            <table style='width:100%; border-collapse:collapse;'>
                <tr><td><b>Level:</b></td><td>{data['level']}</td></tr>
                <tr><td><b>Status:</b></td><td>{data['status']}</td></tr>
                <tr><td><b>Join Date:</b></td><td>{data['join_date']}</td></tr>
                <tr><td><b>Revenue:</b></td><td>${data['total_revenue']:,.2f}</td></tr>
                <tr><td><b>Advocacy Score:</b></td><td>{data['advocacy_score']}/100</td></tr>
                <tr><td><b>Sentiment:</b></td><td>{data['sentiment']}</td></tr>
                <tr><td><b>Posts:</b></td><td>{data['posts']}</td></tr>
                <tr><td><b>Shares:</b></td><td>{data['shares']}</td></tr>
                <tr><td><b>Engagement:</b></td><td>{data['engagement']}/100</td></tr>
            </table>
        </div>
        """
        
        # Highlight selected node if any
        border_width = 3 if node == selected_node else 1
        border_color = "#FF0000" if node == selected_node else "#000000"
        
        net.add_node(
            node,
            label=data['label'],
            title=tooltip,
            color=COLOR_MAP.get(data['level'], '#cccccc'),
            size=size,
            borderWidth=border_width,
            borderWidthSelected=4,
            borderColor=border_color
        )
    
    # Add edges to the network
    for source, target in G.edges():
        net.add_edge(source, target, arrows='to')
    
    # Save and display the network
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = tmp_file.name
    
    # Display graph in Streamlit
    st.components.v1.html(open(tmp_path, 'r', encoding='utf-8').read(), height=650)
    os.remove(tmp_path)

def display_partner_details(partner_df, sales_df, activity_df, social_df, partner_id):
    """Display detailed information about a selected partner"""
    partner = partner_df[partner_df['partner_id'] == partner_id].iloc[0]
    
    # Main metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${partner['total_revenue']:,.2f}")
    col2.metric("Status", partner['status'])
    col3.metric("Advocacy Score", f"{partner['advocacy_score']}/100")
    col4.metric("Sentiment", f"{partner['sentiment']:.2f}")
    
    # Create tabs for detailed information
    tabs = st.tabs(["Overview", "Revenue", "Activity", "Social Metrics", "Hierarchy"])
    
    # Tab 1: Overview
    with tabs[0]:
        st.subheader(f"{partner['name']} Overview")
        
        # Basic information
        st.markdown(f"""
        | Attribute | Value |
        | --- | --- |
        | Partner ID | {partner['partner_id']} |
        | Level | {partner['level']} |
        | Join Date | {partner['join_date']} |
        | Status | {partner['status']} |
        | Total Revenue | ${partner['total_revenue']:,.2f} |
        """)
        
        # Social/digital metrics
        st.subheader("Digital & Social Metrics")
        metrics_cols = st.columns(4)
        metrics_cols[0].metric("Posts", partner['posts'])
        metrics_cols[1].metric("Shares", partner['shares'])
        metrics_cols[2].metric("Sentiment", f"{partner['sentiment']:.2f}")
        metrics_cols[3].metric("Advocacy", f"{partner['advocacy_score']}/100")
    
    # Tab 2: Revenue
    with tabs[1]:
        partner_sales = sales_df[sales_df['partner_id'] == partner_id].copy()
        
        if not partner_sales.empty:
            # Show revenue over time
            partner_sales['date'] = pd.to_datetime(partner_sales['date'])
            revenue_by_date = partner_sales.groupby('date')['revenue'].sum().reset_index()
            
            fig = px.line(revenue_by_date, x='date', y='revenue', 
                         title=f"{partner['name']} Revenue Over Time")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent transactions
            st.subheader("Recent Transactions")
            st.dataframe(
                partner_sales.sort_values('date', ascending=False)
                .head(10)[['date', 'revenue', 'transaction_id', 'product']]
            )
        else:
            st.info("No sales data available for this partner.")
    
    # Tab 3: Activity
    with tabs[2]:
        partner_activity = activity_df[activity_df['partner_id'] == partner_id].copy()
        
        if not partner_activity.empty:
            # Activity breakdown
            st.subheader("Activity Breakdown")
            activity_counts = partner_activity['activity_type'].value_counts().reset_index()
            activity_counts.columns = ['activity_type', 'count']
            
            fig = px.bar(activity_counts, x='activity_type', y='count',
                       title=f"{partner['name']} Activity Breakdown")
            st.plotly_chart(fig, use_container_width=True)
            
            # Activity timeline
            partner_activity['date'] = pd.to_datetime(partner_activity['date'])
            activity_timeline = partner_activity.groupby('date').size().reset_index(name='activities')
            
            fig = px.line(activity_timeline, x='date', y='activities',
                        title=f"{partner['name']} Activity Timeline")
            st.plotly_chart(fig, use_container_width=True)
            
            # Recent activities
            st.subheader("Recent Activities")
            st.dataframe(
                partner_activity.sort_values('date', ascending=False)
                .head(10)[['date', 'activity_type', 'duration_minutes']]
            )
        else:
            st.info("No activity data available for this partner.")
    
    # Tab 4: Social Metrics
    with tabs[3]:
        partner_social = social_df[social_df['partner_id'] == partner_id].copy()
        
        if not partner_social.empty:
            # Convert to datetime for time series
            partner_social['date'] = pd.to_datetime(partner_social['date'])
            
            # Sentiment over time
            st.subheader("Sentiment Over Time")
            fig = px.line(partner_social, x='date', y='sentiment',
                        title=f"{partner['name']} Sentiment Trend")
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)
            
            # Posts and shares over time
            st.subheader("Social Media Activity")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=partner_social['date'], y=partner_social['posts'], name='Posts'))
            fig.add_trace(go.Bar(x=partner_social['date'], y=partner_social['shares'], name='Shares'))
            fig.update_layout(title=f"{partner['name']} Social Media Activity",
                            barmode='stack', xaxis_title='Date', yaxis_title='Count')
            st.plotly_chart(fig, use_container_width=True)
            
            # Advocacy score over time
            st.subheader("Advocacy Score")
            fig = px.line(partner_social, x='date', y='advocacy_score',
                        title=f"{partner['name']} Advocacy Score Trend")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No social data available for this partner.")
    
    # Tab 5: Hierarchy
    with tabs[4]:
        st.subheader("Hierarchical Position")
        
        # Show parent information if exists
        if not pd.isna(partner['parent_id']):
            parent = partner_df[partner_df['partner_id'] == partner['parent_id']].iloc[0]
            st.markdown(f"### Parent: {parent['name']}")
            st.markdown(f"""
            | Attribute | Value |
            | --- | --- |
            | Partner ID | {parent['partner_id']} |
            | Level | {parent['level']} |
            | Status | {parent['status']} |
            """)
        else:
            st.markdown("### This partner is at the top of the hierarchy")
        
        # Show children information
        children = partner_df[partner_df['parent_id'] == partner_id]
        if not children.empty:
            st.markdown(f"### Children ({len(children)})")
            st.dataframe(children[['partner_id', 'name', 'level', 'status', 'total_revenue']])
        else:
            st.markdown("### This partner has no children")

def create_time_series_charts(data_df, date_col, value_col, title, color=None):
    """Helper function to create time series charts"""
    if data_df.empty:
        return None
    
    fig = px.line(data_df, x=date_col, y=value_col, title=title, color=color)
    return fig
