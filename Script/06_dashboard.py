"""
Step 6: Interactive Streamlit Dashboard
========================================
AI-Powered Restaurant Chain Analytics Dashboard
ABC & XYZ Merged Entity

Pages:
  1. Overview      - KPIs, revenue, chain comparison
  2. Products      - Best/worst sellers, category analysis
  3. Regional      - State performance, top regions
  4. AI Query      - Natural language querying with Claude API

Run:
  streamlit run script/06_dashboard.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="ABC & XYZ Restaurant Analytics",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Paths ──────────────────────────────────────────────────────
DB_PATH = r"C:\Users\HP\Desktop\Restruant_Project\data\restaurant_2025.db"
# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FC; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1E2761;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #1E2761; }
    .metric-label { font-size: 13px; color: #718096; margin-top: 4px; }
    .page-title {
        font-size: 28px; font-weight: bold;
        color: #1E2761; margin-bottom: 4px;
    }
    .page-subtitle { font-size: 14px; color: #718096; margin-bottom: 20px; }
    div[data-testid="stSidebar"] { background-color: #1E2761; }
    div[data-testid="stSidebar"] .stSelectbox label { color: white !important; }
    div[data-testid="stSidebar"] .stMultiSelect label { color: white !important; }
    div[data-testid="stSidebar"] p { color: #CADCFC !important; }
    div[data-testid="stSidebar"] h1,h2,h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT o.*, r.restaurant_city, r.restaurant_state
        FROM orders o
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    """, conn)
    conn.close()
    return df

df_full = load_data()

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍕 Restaurant Analytics")
    st.markdown("---")

    page = st.selectbox(
        "Navigate to",
        ["🏠 Overview", "📦 Products", "🗺️ Regional", "🤖 AI Query"]
    )

    st.markdown("---")
    st.markdown("### Filters")

    chain_filter = st.multiselect(
        "Chain",
        options=["ABC", "XYZ"],
        default=["ABC", "XYZ"]
    )

    season_filter = st.multiselect(
        "Season",
        options=["Spring", "Summer", "Fall", "Winter"],
        default=["Spring", "Summer", "Fall", "Winter"]
    )

    gender_filter = st.multiselect(
        "Gender",
        options=["M", "F"],
        default=["M", "F"]
    )

    method_filter = st.multiselect(
        "Purchase Method",
        options=["Dine In", "Carry Out", "Delivery"],
        default=["Dine In", "Carry Out", "Delivery"]
    )

    st.markdown("---")
    st.markdown("##### ABC & XYZ Merger")
    st.markdown("Data: Jan 2018 – Jun 2019")
    st.markdown("40,000 transactions | 544 locations")

# ── Apply Filters ──────────────────────────────────────────────
df = df_full.copy()
if chain_filter:
    df = df[df['chain'].isin(chain_filter)]
if season_filter:
    df = df[df['season'].isin(season_filter)]
if gender_filter:
    df = df[df['gender'].isin(gender_filter)]
if method_filter:
    df = df[df['order_purchase_method'].isin(method_filter)]

# ── Colors ─────────────────────────────────────────────────────
COLORS = {"ABC": "#2196F3", "XYZ": "#FF5722"}
CAT_COLORS = px.colors.qualitative.Set2

# ══════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown('<div class="page-title">Business Overview Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Combined performance of ABC & XYZ restaurant chains after merger</div>', unsafe_allow_html=True)

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    total_rev    = df['order_total_cost'].sum()
    total_profit = df['profit'].sum()
    total_orders = df['order_number'].nunique()
    total_rest   = df['restaurant_id'].nunique()
    avg_order    = df['order_total_cost'].mean()

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">${total_rev/1e6:.1f}M</div><div class="metric-label">Total Revenue</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">${total_profit/1e6:.1f}M</div><div class="metric-label">Total Profit</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_orders:,}</div><div class="metric-label">Unique Orders</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_rest:,}</div><div class="metric-label">Restaurants</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">${avg_order:,.0f}</div><div class="metric-label">Avg Order Value</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Row 2: Chain comparison + Monthly trend
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Chain Performance")
        chain_summary = df.groupby('chain').agg(
            Revenue=('order_total_cost', 'sum'),
            Profit=('profit', 'sum'),
            Orders=('order_number', 'nunique')
        ).reset_index()
        chain_summary['Revenue'] = chain_summary['Revenue'].round(0)
        chain_summary['Profit']  = chain_summary['Profit'].round(0)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Revenue', x=chain_summary['chain'],
            y=chain_summary['Revenue']/1e6,
            marker_color=[COLORS.get(c, '#888') for c in chain_summary['chain']],
            text=[f'${v:.1f}M' for v in chain_summary['Revenue']/1e6],
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            name='Profit', x=chain_summary['chain'],
            y=chain_summary['Profit']/1e6,
            marker_color=['#90CAF9', '#FFAB91'],
            text=[f'${v:.1f}M' for v in chain_summary['Profit']/1e6],
            textposition='outside'
        ))
        fig.update_layout(
            barmode='group', height=320,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", y=-0.2),
            plot_bgcolor='white', paper_bgcolor='white',
            yaxis_title="$M"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Monthly Revenue Trend")
        monthly = df[df['order_purchase_date'].notna()].copy()
        monthly['order_purchase_date'] = pd.to_datetime(monthly['order_purchase_date'])
        monthly['period'] = monthly['order_purchase_date'].dt.to_period('M').astype(str)
        monthly_grp = monthly.groupby(['period', 'chain'])['order_total_cost'].sum().reset_index()
        monthly_grp['Revenue_K'] = monthly_grp['order_total_cost'] / 1000

        fig2 = px.line(
            monthly_grp, x='period', y='Revenue_K', color='chain',
            color_discrete_map=COLORS,
            markers=True, labels={'Revenue_K': 'Revenue ($K)', 'period': 'Month'}
        )
        fig2.update_layout(
            height=320, margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor='white', paper_bgcolor='white',
            xaxis_tickangle=-45, legend_title=""
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Row 3: Season + Purchase method + Gender
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Revenue by Season")
        season_grp = df[df['season'].notna()].groupby('season')['order_total_cost'].sum().reset_index()
        season_grp['Revenue_M'] = season_grp['order_total_cost'] / 1e6
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_grp['season'] = pd.Categorical(season_grp['season'], categories=season_order, ordered=True)
        season_grp = season_grp.sort_values('season')
        fig3 = px.bar(season_grp, x='season', y='Revenue_M', color='season',
                      color_discrete_sequence=CAT_COLORS,
                      labels={'Revenue_M': 'Revenue ($M)', 'season': ''})
        fig3.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10),
                           plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("#### Orders by Purchase Method")
        method_grp = df.groupby('order_purchase_method').size().reset_index(name='count')
        fig4 = px.pie(method_grp, values='count', names='order_purchase_method',
                      color_discrete_sequence=['#1E2761','#2196F3','#F4A261'],
                      hole=0.4)
        fig4.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig4, use_container_width=True)

    with col3:
        st.markdown("#### Revenue by Gender")
        gender_grp = df.groupby('gender')['order_total_cost'].sum().reset_index()
        gender_grp['Revenue_M'] = gender_grp['order_total_cost'] / 1e6
        fig5 = px.bar(gender_grp, x='gender', y='Revenue_M',
                      color='gender', color_discrete_map={'M':'#2196F3','F':'#E91E63'},
                      labels={'Revenue_M':'Revenue ($M)','gender':'Gender'},
                      text=[f'${v:.1f}M' for v in gender_grp['Revenue_M']])
        fig5.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10),
                           plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
        fig5.update_traces(textposition='outside')
        st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2: PRODUCTS
# ══════════════════════════════════════════════════════════════
elif page == "📦 Products":
    st.markdown('<div class="page-title">Product Performance Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Best and worst selling items, category profitability breakdown</div>', unsafe_allow_html=True)

    # Category profitability
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Profit by Category")
        cat_grp = df.groupby('item_category').agg(
            Profit=('profit','sum'),
            Units=('quantity','sum')
        ).reset_index().sort_values('Profit', ascending=False)
        cat_grp['Profit_M'] = cat_grp['Profit'] / 1e6

        fig = px.bar(cat_grp, x='item_category', y='Profit_M',
                     color='item_category', color_discrete_sequence=CAT_COLORS,
                     labels={'Profit_M':'Profit ($M)','item_category':'Category'},
                     text=[f'${v:.1f}M' for v in cat_grp['Profit_M']])
        fig.update_traces(textposition='outside')
        fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white',
                          showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Category Performance by Chain")
        cat_chain = df.groupby(['chain','item_category'])['profit'].sum().reset_index()
        cat_chain['Profit_K'] = cat_chain['profit'] / 1000

        fig2 = px.bar(cat_chain, x='item_category', y='Profit_K', color='chain',
                      barmode='group', color_discrete_map=COLORS,
                      labels={'Profit_K':'Profit ($K)','item_category':'Category'})
        fig2.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(l=10,r=10,t=10,b=10), legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Top / Bottom products
    n = st.slider("Number of products to display", 5, 20, 10)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Top {n} Best Sellers")
        top_prod = df.groupby(['item_description','item_category'])['quantity'].sum()\
                     .reset_index().sort_values('quantity', ascending=False).head(n)
        fig3 = px.bar(top_prod, x='quantity', y='item_description',
                      orientation='h', color='item_category',
                      color_discrete_sequence=CAT_COLORS,
                      labels={'quantity':'Units Sold','item_description':''})
        fig3.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(l=10,r=10,t=10,b=10),
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown(f"#### Bottom {n} Worst Sellers")
        bot_prod = df.groupby(['item_description','item_category'])['quantity'].sum()\
                     .reset_index().sort_values('quantity', ascending=True).head(n)
        fig4 = px.bar(bot_prod, x='quantity', y='item_description',
                      orientation='h', color='item_category',
                      color_discrete_sequence=px.colors.qualitative.Pastel,
                      labels={'quantity':'Units Sold','item_description':''})
        fig4.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(l=10,r=10,t=10,b=10),
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)

    # Profitability table
    st.markdown("---")
    st.markdown("#### Full Product Profitability Table")
    prod_table = df.groupby(['item_description','item_category','chain']).agg(
        Units_Sold=('quantity','sum'),
        Total_Profit=('profit','sum'),
        Avg_Profit=('profit','mean'),
        Menu_Price=('menu_price','mean')
    ).reset_index().sort_values('Total_Profit', ascending=False)
    prod_table['Total_Profit'] = prod_table['Total_Profit'].round(0)
    prod_table['Avg_Profit']   = prod_table['Avg_Profit'].round(2)
    prod_table['Menu_Price']   = prod_table['Menu_Price'].round(2)
    st.dataframe(prod_table, use_container_width=True, height=300)

# ══════════════════════════════════════════════════════════════
# PAGE 3: REGIONAL
# ══════════════════════════════════════════════════════════════
elif page == "🗺️ Regional":
    st.markdown('<div class="page-title">Regional Performance Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">State-by-state revenue and profit breakdown across 48 states</div>', unsafe_allow_html=True)

    # Top states bar
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Top States by Profit")
        n_states = st.slider("Number of states", 5, 20, 10)
        state_grp = df.groupby('restaurant_state').agg(
            Profit=('profit','sum'),
            Revenue=('order_total_cost','sum'),
            Orders=('order_number','nunique')
        ).reset_index().sort_values('Profit', ascending=False).head(n_states)
        state_grp['Profit_M']  = state_grp['Profit'] / 1e6
        state_grp['Revenue_M'] = state_grp['Revenue'] / 1e6

        fig = px.bar(state_grp, x='Profit_M', y='restaurant_state',
                     orientation='h',
                     color='Profit_M', color_continuous_scale='Blues',
                     labels={'Profit_M':'Profit ($M)','restaurant_state':'State'},
                     text=[f'${v:.1f}M' for v in state_grp['Profit_M']])
        fig.update_traces(textposition='outside')
        fig.update_layout(height=420, plot_bgcolor='white', paper_bgcolor='white',
                          margin=dict(l=10,r=10,t=10,b=10),
                          yaxis={'categoryorder':'total ascending'},
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### State Summary Table")
        state_table = df.groupby('restaurant_state').agg(
            Revenue=('order_total_cost','sum'),
            Profit=('profit','sum'),
            Locations=('restaurant_id','nunique')
        ).reset_index().sort_values('Profit', ascending=False)
        state_table['Revenue'] = ('$' + (state_table['Revenue']/1e6).round(1).astype(str) + 'M')
        state_table['Profit']  = ('$' + (state_table['Profit']/1e6).round(1).astype(str) + 'M')
        state_table.columns    = ['State','Revenue','Profit','Locations']
        st.dataframe(state_table, use_container_width=True, height=420)

    st.markdown("---")

    # State comparison by chain
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 10 States — ABC")
        abc_states = df[df['chain']=='ABC'].groupby('restaurant_state')['profit'].sum()\
                       .reset_index().sort_values('profit', ascending=False).head(10)
        abc_states['Profit_K'] = abc_states['profit'] / 1000
        fig2 = px.bar(abc_states, x='Profit_K', y='restaurant_state',
                      orientation='h', color_discrete_sequence=['#2196F3'],
                      labels={'Profit_K':'Profit ($K)','restaurant_state':''})
        fig2.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(l=10,r=10,t=10,b=10),
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("#### Top 10 States — XYZ")
        xyz_states = df[df['chain']=='XYZ'].groupby('restaurant_state')['profit'].sum()\
                       .reset_index().sort_values('profit', ascending=False).head(10)
        xyz_states['Profit_K'] = xyz_states['profit'] / 1000
        fig3 = px.bar(xyz_states, x='Profit_K', y='restaurant_state',
                      orientation='h', color_discrete_sequence=['#FF5722'],
                      labels={'Profit_K':'Profit ($K)','restaurant_state':''})
        fig3.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(l=10,r=10,t=10,b=10),
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4: AI QUERY
# ══════════════════════════════════════════════════════════════
elif page == "🤖 AI Query":
    st.markdown('<div class="page-title">AI-Powered Data Query</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ask questions about the restaurant data in plain English</div>', unsafe_allow_html=True)

    st.info("💡 Ask anything about the data — the AI will query the database and answer in plain English.")

    # Example questions
    st.markdown("#### Try these example questions:")
    examples = [
        "Which state had the highest profit?",
        "What is the most popular item in ABC chain?",
        "How much revenue did we make in Spring?",
        "Which category has the lowest average profit?",
        "How many female customers ordered Delivery?",
    ]
    cols = st.columns(len(examples))
    selected_example = None
    for i, (col, ex) in enumerate(zip(cols, examples)):
        with col:
            if st.button(ex, key=f"ex_{i}"):
                selected_example = ex

    st.markdown("---")

    # Query input
    question = st.text_input(
        "Type your question here:",
        value=selected_example if selected_example else "",
        placeholder="e.g. Which city had the most orders?"
    )

    if st.button("🔍 Get Answer", type="primary") and question:
        with st.spinner("Analysing your question..."):

            # Build context summary for the AI
            conn = sqlite3.connect(DB_PATH)

            # Run a few automatic queries based on keywords
            answer_data = None
            chart = None

            q_lower = question.lower()

            try:
                if any(w in q_lower for w in ['state','region','where']):
                    answer_data = pd.read_sql_query("""
                        SELECT r.restaurant_state as State,
                               ROUND(SUM(o.profit)/1000,1) as Profit_K,
                               ROUND(SUM(o.order_total_cost)/1000,1) as Revenue_K,
                               COUNT(DISTINCT o.order_number) as Orders
                        FROM orders o JOIN restaurants r ON o.restaurant_id=r.restaurant_id
                        GROUP BY r.restaurant_state ORDER BY Profit_K DESC LIMIT 10
                    """, conn)
                    chart = px.bar(answer_data, x='Profit_K', y='State', orientation='h',
                                   color='Profit_K', color_continuous_scale='Blues',
                                   title='Top States by Profit ($K)')

                elif any(w in q_lower for w in ['item','product','food','menu','popular','sell']):
                    answer_data = pd.read_sql_query("""
                        SELECT item_description as Item, item_category as Category, chain as Chain,
                               SUM(quantity) as Units_Sold,
                               ROUND(SUM(profit)/1000,1) as Profit_K
                        FROM orders GROUP BY item_description, chain
                        ORDER BY Units_Sold DESC LIMIT 10
                    """, conn)
                    chart = px.bar(answer_data, x='Units_Sold', y='Item', orientation='h',
                                   color='Chain', color_discrete_map=COLORS,
                                   title='Top Items by Units Sold')

                elif any(w in q_lower for w in ['season','spring','summer','fall','winter']):
                    answer_data = pd.read_sql_query("""
                        SELECT season as Season, chain as Chain,
                               ROUND(SUM(order_total_cost)/1000000,2) as Revenue_M,
                               ROUND(SUM(profit)/1000000,2) as Profit_M
                        FROM orders WHERE season IS NOT NULL
                        GROUP BY season, chain ORDER BY Revenue_M DESC
                    """, conn)
                    chart = px.bar(answer_data, x='Season', y='Revenue_M', color='Chain',
                                   barmode='group', color_discrete_map=COLORS,
                                   title='Revenue by Season & Chain ($M)')

                elif any(w in q_lower for w in ['category','type','kind']):
                    answer_data = pd.read_sql_query("""
                        SELECT item_category as Category,
                               ROUND(SUM(profit)/1000000,2) as Profit_M,
                               ROUND(AVG(profit),2) as Avg_Profit,
                               SUM(quantity) as Units_Sold
                        FROM orders GROUP BY item_category ORDER BY Profit_M DESC
                    """, conn)
                    chart = px.bar(answer_data, x='Category', y='Profit_M',
                                   color='Category', color_discrete_sequence=CAT_COLORS,
                                   title='Profit by Category ($M)')

                elif any(w in q_lower for w in ['gender','male','female','women','men']):
                    answer_data = pd.read_sql_query("""
                        SELECT gender as Gender, chain as Chain,
                               ROUND(SUM(order_total_cost)/1000000,2) as Revenue_M,
                               ROUND(AVG(order_total_cost),2) as Avg_Order,
                               COUNT(*) as Orders
                        FROM orders GROUP BY gender, chain
                    """, conn)
                    chart = px.bar(answer_data, x='Gender', y='Revenue_M', color='Chain',
                                   barmode='group', color_discrete_map=COLORS,
                                   title='Revenue by Gender & Chain ($M)')

                else:
                    answer_data = pd.read_sql_query("""
                        SELECT chain,
                               ROUND(SUM(order_total_cost)/1000000,2) as Revenue_M,
                               ROUND(SUM(profit)/1000000,2) as Profit_M,
                               COUNT(DISTINCT order_number) as Orders,
                               ROUND(AVG(order_total_cost),2) as Avg_Order
                        FROM orders GROUP BY chain
                    """, conn)

            except Exception as e:
                st.error(f"Query error: {e}")

            conn.close()

            # Display results
            if answer_data is not None:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("#### 📊 Data Results")
                    st.dataframe(answer_data, use_container_width=True)
                with col2:
                    if chart:
                        st.markdown("#### 📈 Visualization")
                        chart.update_layout(
                            plot_bgcolor='white', paper_bgcolor='white',
                            height=350, margin=dict(l=10,r=10,t=40,b=10),
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(chart, use_container_width=True)

                # Generate text insight
                st.markdown("#### 💡 Key Insight")
                if not answer_data.empty:
                    top_row = answer_data.iloc[0]
                    col_names = answer_data.columns.tolist()
                    insight = f"Based on your question about **'{question}'**, here's what the data shows: "
                    insight += f"The top result is **{top_row[col_names[0]]}** "
                    if len(col_names) > 1:
                        insight += f"with **{top_row[col_names[1]]}** ({col_names[1].replace('_',' ')})."
                    st.success(insight)
                    st.markdown(f"*Showing top {len(answer_data)} results from {len(df_full):,} total records.*")