import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="CHLOE AI | Enterprise Suite", layout="wide", page_icon="🧬")

# --- 1. INITIALIZARE DATABASE (Session State) ---
if 'db' not in st.session_state:
    # Simulăm data curentă ca fiind 31 Ianuarie 2026
    today = datetime(2026, 1, 31)
    st.session_state.db = pd.DataFrame([
        {"id": "PX-101", "nume": "Mme. Dupont", "med": "Levothyrox 75µg", "cat": "Tiroidă", "ultima_vizita": today - timedelta(days=26), "qty": 1, "daily_dose": 1, "mpr": 0.98, "marja_euro": 12.5, "sms_trimis": False},
        {"id": "PX-102", "nume": "M. Ionescu", "med": "Metformine 500mg", "cat": "Diabet", "ultima_vizita": today - timedelta(days=32), "qty": 3, "daily_dose": 3, "mpr": 0.85, "marja_euro": 8.2, "sms_trimis": False},
        {"id": "PX-103", "nume": "Mme. Curie", "med": "Eliquis 5mg", "cat": "Cardio", "ultima_vizita": today - timedelta(days=12), "qty": 1, "daily_dose": 2, "mpr": 0.95, "marja_euro": 45.0, "sms_trimis": False},
        {"id": "PX-104", "nume": "M. Arnault", "med": "Lipanthyl 160mg", "cat": "Colesterol", "ultima_vizita": today - timedelta(days=29), "qty": 1, "daily_dose": 1, "mpr": 0.70, "marja_euro": 15.8, "sms_trimis": False},
        {"id": "PX-105", "nume": "Mme. Bovary", "med": "Januvia 100mg", "cat": "Diabet", "ultima_vizita": today - timedelta(days=25), "qty": 1, "daily_dose": 1, "mpr": 0.92, "marja_euro": 38.0, "sms_trimis": False},
        {"id": "PX-106", "nume": "M. Proust", "med": "Aerius 5mg", "cat": "Alergii", "ultima_vizita": today - timedelta(days=10), "qty": 1, "daily_dose": 1, "mpr": 0.99, "marja_euro": 5.5, "sms_trimis": False},
    ])

# --- 2. ENGINE CHLOE (LOGICA DE CALCUL) ---
def run_chloe_logic(df):
    temp_df = df.copy()
    today = datetime(2026, 1, 31)
    
    # Formula de predicție: t_next = t_last + (Qty * Units / Dose) * MPR
    temp_df['zile_teoretice'] = (temp_df['qty'] * 30) / temp_df['daily_dose']
    temp_df['zile_ajustate'] = temp_df['zile_teoretice'] * temp_df['mpr']
    temp_df['data_predictie'] = temp_df.apply(lambda x: x['ultima_vizita'] + timedelta(days=int(x['zile_ajustate'])), axis=1)
    temp_df['zile_ramase'] = temp_df['data_predictie'].apply(lambda x: (x - today).days)
    
    # Clasificare RISC (Fix pentru eroarea anterioară)
    def classify_risk(row):
        if row['zile_ramase'] < 0: return "CRITIC"
        if row['zile_ramase'] <= 5: return "RIDICAT"
        return "SCĂZUT"
    
    temp_df['risc'] = temp_df.apply(classify_risk, axis=1)
    return temp_df

# --- 3. UI SIDEBAR (SIMULATOR & NETWORK) ---
st.sidebar.title("🎮 CHLOE Control Center")
st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ Simulator Business")
marja_boost = st.sidebar.slider("Ajustare Marjă Globală (%)", -20, 50, 0)
target_profit_daily = st.sidebar.number_input("Target Profit Zilnic (€)", value=500)

st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Network Intelligence")
spike_factor = st.sidebar.slider("Regional Allergy Spike", 1.0, 2.5, 1.4)
if spike_factor > 1.3:
    st.sidebar.error(f"🚨 Spike regional detectat: {int((spike_factor-1)*100)}%")

# --- 4. DASHBOARD PRINCIPAL (BI & PROFIT) ---
st.title("🛡️ CHLOE AI | Proactive Pharmacy Management")
processed_db = run_chloe_logic(st.session_state.db)

# TOP ROW: Barometru și Radar Chart
col_baro, col_radar = st.columns([1, 1])

with col_baro:
    # Barometru de Profitabilitate
    total_margin = (processed_db['marja_euro'] * (1 + marja_boost/100)).sum()
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_margin,
        title = {'text': "Profitabilitate Curentă (€)", 'font': {'size': 20}},
        delta = {'reference': target_profit_daily, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, target_profit_daily * 1.5]},
            'bar': {'color': "#14b8a6"},
            'steps': [
                {'range': [0, target_profit_daily*0.6], 'color': "#fee2e2"},
                {'range': [target_profit_daily*0.6, target_profit_daily], 'color': "#fef3c7"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': target_profit_daily}
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_radar:
    # Radar Chart: Pharmacy Health Score
    categories = ['Stoc', 'Aderență', 'Retenție', 'Marjă', 'Digitalizare']
    # Scoruri simulate bazate pe MPR-ul mediu și alte date
    health_scores = [80, int(processed_db['mpr'].mean()*100), 75, 90, 85]
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=health_scores, theta=categories, fill='toself', line_color='#0d9488'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
                          title="Radarul Sănătății Farmaciei", height=300, margin=dict(l=50, r=50, t=50, b=20))
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- 5. TABS FUNCTIONALE ---
tab_ops, tab_stats, tab_inv = st.tabs(["⚡ Operațiuni Zilnice", "📊 Statistici & Profit", "📦 Supply Chain"])

with tab_ops:
    st.subheader("📋 Intervenții Pacienți")
    # Prioritizăm după risc
    ops_df = processed_db.sort_values(by=['zile_ramase'])
    
    for idx, row in ops_df.iterrows():
        color = "red" if row['risc'] == "CRITIC" else ("orange" if row['risc'] == "RIDICAT" else "green")
        with st.expander(f"Status: {row['risc']} | {row['nume']} - {row['med']}"):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"📅 **Data Refill:** {row['data_predictie'].strftime('%d %b %Y')}")
            c1.write(f"💵 **Marjă în Risc:** {row['marja_euro']:.2f} €")
            
            c2.progress(row['mpr'], text=f"Scor Aderență (MPR): {int(row['mpr']*100)}%")
            
            status_text = "✅ Mesaj Trimis" if st.session_state.db.at[idx, 'sms_trimis'] else "⏳ Necunoscut"
            c3.write(status_text)
            if c3.button("Engagement SMS", key=f"sms_{row['id']}"):
                st.session_state.db.at[idx, 'sms_trimis'] = True
                st.rerun()

with tab_stats:
    st.subheader("Analiza Financiară a Portofoliului")
    s1, s2 = st.columns(2)
    
    with s1:
        # Scatter: Adherence vs Profit (Fix pentru eroarea 'risc')
        fig_scatter = px.scatter(processed_db, x="mpr", y="marja_euro", size="qty", color="risc",
                                hover_name="nume", title="Aderență vs Marjă (per Pacient)",
                                color_discrete_map={"CRITIC": "red", "RIDICAT": "orange", "SCĂZUT": "green"})
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with s2:
        # Bar: Top Medicamente după Profitabilitate
        top_meds = processed_db.groupby('med')['marja_euro'].sum().sort_values(ascending=False).reset_index()
        fig_bar = px.bar(top_meds, x='marja_euro', y='med', orientation='h', 
                         title="Top Medicamente (Marjă Totală)", color='marja_euro', color_continuous_scale='Teal')
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_inv:
    st.subheader("Supply Chain Intelligence")
    # Factor Network Intel aplicat pe stocul necesar (7 zile)
    st.info(f"💡 Factorul Network Intel ({spike_factor}x) este aplicat automat pentru prognoza stocului.")
    
    inventory_needed = processed_db[processed_db['zile_ramase'] <= 7].copy()
    if inventory_needed.empty:
        st.success("Stocul actual acoperă cererea prognozată pentru următoarele 7 zile.")
    else:
        inventory_needed['qty_sugerata'] = (inventory_needed['qty'] * spike_factor).apply(np.ceil)
        summary = inventory_needed.groupby('med')['qty_sugerata'].sum().reset_index()
        st.table(summary)
        if st.button("🚀 Trimite Comandă către Depozit"):
            st.balloons()
            st.success("Comanda a fost transmisă via API către wholesaler!")

# --- FOOTER ---
st.divider()
st.caption(f"CHLOE AI Enterprise | Logged in: Pharmacist Admin | {datetime.now().strftime('%Y-%m-%d %H:%M')}")