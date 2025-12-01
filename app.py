import streamlit as st
import pandas as pd
import os
from groq import Groq

# Load API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --------------------------
#  SALES ANALYSIS FUNCTIONS
# --------------------------

def process_sales(df):
    result = {}

    # Total sales
    result["Total Sales"] = df["Sales"].sum()

    # Average sales
    result["Average Sales"] = df["Sales"].mean()

    # Sales by product
    result["Sales by Product"] = df.groupby("Product")["Sales"].sum()

    # Sales per month
    df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M")
    result["Sales per Month"] = df.groupby("Month")["Sales"].sum()

    # Growth %
    monthly = result["Sales per Month"]
    if len(monthly) > 1:
        result["Growth (%)"] = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
    else:
        result["Growth (%)"] = "Not enough data"

    return result


# --------------------------
#        AI ANALYSIS
# --------------------------

def ai_sales_analysis(summary):
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert sales analyst."},
            {"role": "user", "content": f"Berikan analisis menyeluruh dari data penjualan berikut:\n{summary}"}
        ]
    )
    return response.choices[0].message["content"]


# --------------------------
#          UI
# --------------------------

st.title("📈 Sales Analysis AI Agent")
st.write("Upload file penjualan Anda untuk mendapatkan analisis otomatis + insight AI")

upload = st.file_uploader("Upload Excel", type=["xlsx"])

if upload:
    df = pd.read_excel(upload)

    st.subheader("Raw Sales Data")
    st.dataframe(df)

    analysis = process_sales(df)

    st.subheader("📊 Ringkasan Analisis")
    st.write(f"**Total Sales:** {analysis['Total Sales']}")
    st.write(f"**Average Sales:** {analysis['Average Sales']}")

    st.write("### Sales by Product")
    st.dataframe(analysis["Sales by Product"])

    st.write("### Sales per Month")
    st.dataframe(analysis["Sales per Month"])

    st.write(f"### Growth (%): {analysis['Growth (%)']}")

    # Prepare text for AI
    summary_text = f"""
    Total Sales: {analysis['Total Sales']}
    Average Sales: {analysis['Average Sales']}
    Sales by Product: {analysis['Sales by Product'].to_string()}
    Sales per Month: {analysis['Sales per Month'].to_string()}
    Growth: {analysis['Growth (%)']}
    """

    if st.button("🔍 Analisis AI"):
        with st.spinner("AI sedang menganalisis data..."):
            ai_result = ai_sales_analysis(summary_text)

        st.subheader("📘 Insight AI")
        st.write(ai_result)
