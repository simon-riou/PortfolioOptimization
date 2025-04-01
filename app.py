import streamlit as st
from optimizer import optimize_portfolio
from data import get_data_sources, get_combined_data
import pandas as pd

st.set_page_config(page_title="Optimiseur de Portefeuille", layout="wide")
st.title("📈 Optimisation de Portefeuille")

# Sidebar
st.sidebar.header("Paramètres")
data_sources = get_data_sources()
selected_sources = st.sidebar.multiselect("Choisissez les sources de données :", options=list(data_sources.keys()), default=["CAC 40"])

selected_tickers = []

def toggle_selection(source):
    key = f"selection_{source}"
    tickers = data_sources[source]
    if key in st.session_state and set(st.session_state[key]) == set(tickers):
        st.session_state[key] = []
    else:
        st.session_state[key] = tickers.copy()

show_selection_panel = st.sidebar.checkbox("Afficher la sélection des actions", value=True)

# Process each data source
for source in selected_sources:
    tickers = data_sources[source]
    key = f"selection_{source}"

    # First init
    if key not in st.session_state:
        st.session_state[key] = tickers[:5]

    if show_selection_panel:
        all_selected = key in st.session_state and set(st.session_state[key]) == set(tickers)
        btn_label = "Tout désélectionner" if all_selected else "Tout sélectionner"

        if st.sidebar.button(f"{btn_label} ({source})", key=f"btn_{source}"):
            toggle_selection(source)

        # Use multiselect with a DIFFERENT key than the session state key
        # The widget key needs to be unique but different from the session state key
        widget_key = f"multiselect_{source}"
        selection = st.sidebar.multiselect(
            f"Actions de {source} :",
            options=tickers,
            default=st.session_state[key],  # Use session state as default
            key=widget_key  # Use a different key for the widget
        )
        
        st.session_state[key] = selection
    
    if key in st.session_state:
        selected_tickers.extend(st.session_state[key])

# Remove duplicates (in case same ticker appears in multiple sources)
selected_tickers = list(dict.fromkeys(selected_tickers))

date_start = st.sidebar.date_input("Date de début", value=pd.to_datetime("2023-01-01"))
date_end = st.sidebar.date_input("Date de fin", value=pd.to_datetime("2024-01-01"))

use_bounds = st.sidebar.checkbox("Activer les contraintes de poids par action", value=False)

min_weight, max_weight = 0.0, 1.0
if use_bounds:
    st.sidebar.markdown("### Contraintes de poids")
    min_weight = st.sidebar.slider("Poids minimum par action", 0.0, 1.0, 0.0, 0.01)
    max_weight = st.sidebar.slider("Poids maximum par action", 0.0, 1.0, 1.0, 0.01)

target_return = st.sidebar.slider("Rendement cible (%/jour)", min_value=0.0, max_value=1.0, step=0.01, value=0.1) / 100

# Debug info
st.sidebar.markdown("### Débogage")
st.sidebar.write(f"Actions sélectionnées: {len(selected_tickers)}")
if st.sidebar.checkbox("Afficher les actions sélectionnées"):
    st.sidebar.write(selected_tickers)

# Data processing
if selected_tickers:
    data = get_combined_data(selected_tickers, date_start, date_end)
    
    if data is None or data.empty:
        st.warning("Pas de données disponibles pour les actions sélectionnées.")
    else:
        returns = data.pct_change().dropna()
        result = optimize_portfolio(returns, target_return, min_weight, max_weight, use_bounds)

        if result is None:
            st.error("⚠️ Aucun portefeuille trouvé pour ce rendement cible. Essayez un rendement plus faible.")
        else:
            weights, expected_return, risk = result
            
            st.subheader("Poids optimaux :")
            st.bar_chart(weights)

            st.markdown(f"**Rendement attendu :** {expected_return:.2%}")
            st.markdown(f"**Volatilité (écart-type) :** {risk:.2%}")
else:
    st.warning("Veuillez sélectionner au moins une action pour optimiser le portefeuille.")