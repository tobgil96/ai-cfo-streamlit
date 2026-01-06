import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# -----------------------------------
# Page setup
# -----------------------------------
st.set_page_config(
    page_title="AI CFO Dashboard",
    layout="wide"
)

st.title("AI CFO – Cashflow & Entscheidungen")

# -----------------------------------
# Load data
# -----------------------------------
try:
    df = pd.read_csv("finance_data.csv")
except Exception as e:
    st.error("finance_data.csv konnte nicht geladen werden.")
    st.stop()

st.subheader("Finanzdaten")
st.dataframe(df, use_container_width=True)

# -----------------------------------
# KPI calculations
# -----------------------------------
df["profit"] = df["revenue"] - df["fixed_costs"] - df["variable_costs"]

avg_profit = float(df["profit"].mean())
cash = float(df["cash"].iloc[0])
runway = cash / avg_profit if avg_profit > 0 else None

c1, c2, c3 = st.columns(3)
c1.metric("Ø Monatsgewinn", f"{avg_profit:,.0f} €")
c2.metric("Cash (Start)", f"{cash:,.0f} €")
c3.metric("Runway (Monate)", f"{runway:,.1f}" if runway else "n/a")

st.divider()

# -----------------------------------
# AI CFO decision engine
# -----------------------------------
st.subheader("KI-Entscheidung (AI CFO)")

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

if st.button("Empfehlung berechnen"):
    if not api_key:
        st.error("Kein OpenAI API Key gefunden. Bitte als Secret setzen.")
    else:
        client = OpenAI(api_key=api_key)

        prompt = f"""
Du bist CFO eines Unternehmens.
Analysiere die folgenden Finanzdaten (Monat, Umsatz, Fixkosten, variable Kosten, Cash).

Gib:
1) eine kurze Executive Summary (max. 5 Sätze),
2) eine Einschätzung zur Runway,
3) 3 klare Management-Entscheidungen,
4) 2 kritische Risiken.

Antworte präzise, sachlich und entscheidungsorientiert.

Daten:
{df.to_string(index=False)}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            st.success("Analyse abgeschlossen")
            st.write(response.choices[0].message.content)

        except Exception:
            st.warning("KI aktuell nicht verfügbar – Demo-Fallback wird angezeigt.")

            st.subheader("Demo-Empfehlung (Fallback)")
            st.write(
                f"""
**Executive Summary**  
Der durchschnittliche Monatsgewinn liegt bei ca. {avg_profit:,.0f} €.
Bei einem Cashbestand von {cash:,.0f} € ergibt sich eine Runway von rund {runway:,.1f} Monaten.

**Management-Entscheidungen**
1) Neueinstellungen nur bei stabiler Umsatzentwicklung.
2) Variable Kosten kurzfristig überprüfen und senken.
3) Fokus auf margenstarke Bestandskunden.

**Risiken**
- Umsatzrückgang bei gleichbleibenden Fixkosten.
- Eingeschränkte Flexibilität durch hohe Fixkosten.
"""
            )
