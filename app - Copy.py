import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import random
from datetime import datetime, timedelta
import tempfile
import os

### --- Synthetic Data Generation ---
def generate_partners(num_partners=30):
    levels = ['Distributor', 'Agent', 'Ambassador']
    data = []
    data.append({
        'partner_id': 1,
        'name': 'Root Distributor',
        'level': 'Distributor',
        'parent_id': None,
        'join_date': (datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
    })
    for i in range(2, num_partners + 1):
        level = random.choices(levels, weights=[0.2, 0.5, 0.3])[0]
        parent_candidates = [d for d in data if levels.index(d['level']) < levels.index(level)]
        parent = random.choice(parent_candidates) if parent_candidates else data[0]
        data.append({
            'partner_id': i,
            'name': f'Partner {i}',
            'level': level,
            'parent_id': parent['partner_id'],
            'join_date': (datetime.now() - timedelta(days=random.randint(1, 900))).strftime('%Y-%m-%d')
        })
    return pd.DataFrame(data)

def generate_sales(partners, num_days=60):
    sales = []
    for _, p in partners.iterrows():
        for _ in range(random.randint(5, 30)):
            date = datetime.now() - timedelta(days=random.randint(0, num_days))
            revenue = round(random.uniform(100, 2000), 2)
            sales.append({
                'partner_id': p['partner_id'],
                'date': date.strftime('%Y-%m-%d'),
                'revenue': revenue
            })
    return pd.DataFrame(sales)

def generate_activity(partners, num_days=60):
    activity = []
    for _, p in partners.iterrows():
        for _ in range(random.randint(10, 50)):
            date = datetime.now() - timedelta(days=random.randint(0, num_days))
            activity_type = random.choice(['Login', 'Call', 'Meeting', 'Demo'])
            activity.append({
                'partner_id': p['partner_id'],
                'date': date.strftime('%Y-%m-%d'),
                'activity_type': activity_type
            })
    return pd.DataFrame(activity)

### --- Streamlit App ---
st.set_page_config(page_title="Partner Revenue & Activity Dashboard", layout="wide")

st.markdown("# Partner Revenue & Activity Dashboard")
st.markdown("This dashboard visualizes a synthetic partner hierarchy, revenue, and activity data. Use the sidebar to filter or upload your own data.")

# --- Data Upload or Generation ---
uploaded = st.sidebar.file_uploader("Upload Partner Data (CSV)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    if 'df' not in st.session_state:
        st.session_state.df = generate_partners()
    df = st.session_state.df

if 'sales' not in st.session_state or st.button("Regenerate Synthetic Dataset"):
    st.session_state.sales = generate_sales(df)
    st.session_state.activity = generate_activity(df)
sales = st.session_state.sales
activity = st.session_state.activity

# --- Sidebar Filters ---
levels = df['level'].unique().tolist()
selected_levels = st.sidebar.multiselect("Filter by Level", levels, default=levels)
partner_names = df[df['level'].isin(selected_levels)]['name'].tolist()
selected_partner = st.sidebar.selectbox("Select Individual Partner (optional)", [None] + partner_names)

filtered_df = df[df['level'].isin(selected_levels)]
filtered_sales = sales[sales['partner_id'].isin(filtered_df['partner_id'])]
filtered_activity = activity[activity['partner_id'].isin(filtered_df['partner_id'])]
if selected_partner:
    pid = df[df['name'] == selected_partner]['partner_id'].values[0]
    filtered_sales = filtered_sales[filtered_sales['partner_id'] == pid]
    filtered_activity = filtered_activity[filtered_activity['partner_id'] == pid]

# --- Summary Statistics ---
summary = filtered_sales.groupby('partner_id').agg({'revenue':'sum'}).reset_index().merge(
    filtered_df[['partner_id','name','level']], on='partner_id')
activity_summary = filtered_activity.groupby('partner_id').size().reset_index(name='activity_count').merge(
    filtered_df[['partner_id','name','level']], on='partner_id')

level_revenue = filtered_sales.merge(filtered_df[['partner_id','level']], on='partner_id').groupby('level')['revenue'].sum()
level_activity = filtered_activity.merge(filtered_df[['partner_id','level']], on='partner_id').groupby('level').size()

sales['date'] = pd.to_datetime(sales['date'])
activity['date'] = pd.to_datetime(activity['date'])

revenue_time = filtered_sales.groupby('date')['revenue'].sum().reset_index()
activity_time = filtered_activity.groupby('date').size().reset_index(name='activity_count')

# --- Top/Bottom Performers ---
top_revenue = summary.sort_values('revenue', ascending=False).head(5)
bottom_revenue = summary.sort_values('revenue', ascending=True).head(5)
top_activity = activity_summary.sort_values('activity_count', ascending=False).head(5)
bottom_activity = activity_summary.sort_values('activity_count', ascending=True).head(5)

# --- Tabs for UI ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Network Graph", "Partner Table", "Dashboard", "Performance", "Export"
])

# --- Tab 1: Network Graph ---
with tab1:
    st.markdown("### Partner Hierarchy Network")
    G = nx.DiGraph()
    for _, row in filtered_df.iterrows():
        G.add_node(row['partner_id'], label=row['name'], level=row['level'], join_date=row['join_date'])
    for _, row in filtered_df.iterrows():
        if row['parent_id'] and row['parent_id'] in filtered_df['partner_id'].values:
            G.add_edge(row['parent_id'], row['partner_id'])
    net = Network(height="600px", width="100%", directed=True, notebook=False)
    color_map = {'Distributor': '#1f77b4', 'Agent': '#2ca02c', 'Ambassador': '#d62728'}
    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=data['label'],
            title=f"Name: {data['label']}<br>Level: {data['level']}<br>Join Date: {data['join_date']}",
            color=color_map.get(data['level'], '#cccccc')
        )
    for source, target in G.edges():
        net.add_edge(source, target)
    net.toggle_physics(True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = tmp_file.name
    st.components.v1.html(open(tmp_path, 'r', encoding='utf-8').read(), height=650)
    os.remove(tmp_path)
    st.info("To exit the Streamlit app and return to the PowerShell prompt, press Ctrl+C in the terminal window.")

# --- Tab 2: Partner Table ---
with tab2:
    st.markdown("## Partner Dataset Table")
    st.dataframe(df, use_container_width=True)
    st.info("This table shows all partners, their levels, parent relationships, and join dates.")

# --- Tab 3: Dashboard ---
with tab3:
    st.markdown("## Revenue & Activity Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Revenue", f"${filtered_sales['revenue'].sum():,.2f}")
    col2.metric("Total Activity Count", f"{filtered_activity.shape[0]:,}")
    st.markdown("### Revenue by Partner Level")
    st.bar_chart(level_revenue)
    st.markdown("### Activity Count by Partner Level")
    st.bar_chart(level_activity)
    st.markdown("### Revenue Over Time")
    fig1 = px.line(revenue_time, x='date', y='revenue', title='Revenue Over Time')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("### Activity Over Time")
    fig2 = px.line(activity_time, x='date', y='activity_count', title='Activity Over Time')
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 4: Performance ---
with tab4:
    st.markdown("## Top & Bottom Performers")
    st.markdown("### Top 5 by Revenue")
    st.dataframe(top_revenue[['name','level','revenue']], use_container_width=True)
    st.markdown("### Bottom 5 by Revenue")
    st.dataframe(bottom_revenue[['name','level','revenue']], use_container_width=True)
    st.markdown("### Top 5 by Activity")
    st.dataframe(top_activity[['name','level','activity_count']], use_container_width=True)
    st.markdown("### Bottom 5 by Activity")
    st.dataframe(bottom_activity[['name','level','activity_count']], use_container_width=True)

# --- Tab 5: Export ---
with tab5:
    st.markdown("## Export Summary Statistics")
    st.download_button(
        label="Download Revenue Summary as CSV",
        data=summary.to_csv(index=False),
        file_name="revenue_summary.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download Activity Summary as CSV",
        data=activity_summary.to_csv(index=False),
        file_name="activity_summary.csv",
        mime="text/csv"
    )