import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- Dark Mode Umschalter ---
dark_mode = st.toggle(" Dark Mode ", value=False)

# --- Farben definieren ---
if dark_mode:
    background_color = "#0E1117"
    text_color = "#FAFAFA"
    table_bg = "#1e1e1e"
    table_text = "#FAFAFA"
    plotly_template = "plotly_dark"
else:
    background_color = "#FAFAFA"
    text_color = "#000000"
    table_bg = "#FFFFFF"
    table_text = "#000000"
    plotly_template = "plotly_white"

# --- Globales CSS anwenden ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        .css-1v3fvcr, .css-1dp5vir, .css-1d391kg, .css-1e5imcs {{
            background-color: {background_color} !important;
            color: {text_color} !important;
        }}
        .orange-text {{
            color: #FF6600;
            font-weight: bold;
            font-size: 36px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Layout & Design ---
st.set_page_config(page_title="DZI Aktien Analyst", layout="wide")

st.markdown("""
    <style>
        .orange-text { color: #FF6600; font-weight: bold; font-size: 36px; }
        .stApp { background-color: #FAFAFA; }
    </style>
""", unsafe_allow_html=True)

# --- Titel und Logo ---
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='orange-text'>DZI Aktien Analyst</div>", unsafe_allow_html=True)
with col2:
    st.image("logo.png", width=250)

st.markdown("## Aktienauswahl")

# --- Aktienlisten mit ISIN & WKN ---
us_stocks = {
    "Apple": {"symbol": "AAPL", "isin": "US0378331005", "wkn": "865985"},
    "Microsoft": {"symbol": "MSFT", "isin": "US5949181045", "wkn": "870747"},
    "Amazon": {"symbol": "AMZN", "isin": "US0231351067", "wkn": "906866"},
    "NVIDIA": {"symbol": "NVDA", "isin": "US67066G1040", "wkn": "918422"},
    "Alphabet (GOOGL)": {"symbol": "GOOGL", "isin": "US02079K3059", "wkn": "A14Y6F"},
    "Meta": {"symbol": "META", "isin": "US30303M1027", "wkn": "A1JWVX"},
    "Berkshire Hathaway": {"symbol": "BRK-B", "isin": "US0846707026", "wkn": "A0YJQ2"},
    "Tesla": {"symbol": "TSLA", "isin": "US88160R1014", "wkn": "A1CX3T"},
    "Visa": {"symbol": "V", "isin": "US92826C8394", "wkn": "A0NC7B"},
    "Johnson & Johnson": {"symbol": "JNJ", "isin": "US4781601046", "wkn": "853260"},
    "UnitedHealth": {"symbol": "UNH", "isin": "US91324P1021", "wkn": "869561"},
    "Exxon Mobil": {"symbol": "XOM", "isin": "US30231G1022", "wkn": "852549"},
    "JPMorgan": {"symbol": "JPM", "isin": "US46625H1005", "wkn": "850628"},
    "Procter & Gamble": {"symbol": "PG", "isin": "US7427181091", "wkn": "852062"},
    "Mastercard": {"symbol": "MA", "isin": "US57636Q1040", "wkn": "A0F602"},
    "Pfizer": {"symbol": "PFE", "isin": "US7170811035", "wkn": "852009"},
    "Chevron": {"symbol": "CVX", "isin": "US1667641005", "wkn": "852552"},
    "Coca-Cola": {"symbol": "KO", "isin": "US1912161007", "wkn": "850663"},
    "PepsiCo": {"symbol": "PEP", "isin": "US7134481081", "wkn": "851995"},
    "Intel": {"symbol": "INTC", "isin": "US4581401001", "wkn": "855681"},
    "Cisco": {"symbol": "CSCO", "isin": "US17275R1023", "wkn": "878841"},
    "AbbVie": {"symbol": "ABBV", "isin": "US00287Y1091", "wkn": "A1J84E"},
    "Walmart": {"symbol": "WMT", "isin": "US9311421039", "wkn": "860853"},
    "Merck & Co": {"symbol": "MRK", "isin": "US58933Y1055", "wkn": "A0YD8Q"},
    "Oracle": {"symbol": "ORCL", "isin": "US68389X1054", "wkn": "871460"},
    "Comcast": {"symbol": "CMCSA", "isin": "US20030N1019", "wkn": "157484"},
    "Adobe": {"symbol": "ADBE", "isin": "US00724F1012", "wkn": "871981"},
    "Salesforce": {"symbol": "CRM", "isin": "US79466L3024", "wkn": "A0B87V"},
    "Netflix": {"symbol": "NFLX", "isin": "US64110L1061", "wkn": "552484"},
    "McDonald's": {"symbol": "MCD", "isin": "US5801351017", "wkn": "856958"}
}

dax_stocks = {
    "Adidas": {"symbol": "ADS.DE", "isin": "DE000A1EWWW0", "wkn": "A1EWWW"},
    "Allianz": {"symbol": "ALV.DE", "isin": "DE0008404005", "wkn": "840400"},
    "BASF": {"symbol": "BAS.DE", "isin": "DE000BASF111", "wkn": "BASF11"},
    "Bayer": {"symbol": "BAYN.DE", "isin": "DE000BAY0017", "wkn": "BAY001"},
    "BMW": {"symbol": "BMW.DE", "isin": "DE0005190003", "wkn": "519000"},
    "Continental": {"symbol": "CON.DE", "isin": "DE0005439004", "wkn": "543900"},
    "Covestro": {"symbol": "1COV.DE", "isin": "DE0006062144", "wkn": "606214"},
    "Daimler Truck": {"symbol": "DTG.DE", "isin": "DE000DTR0CK8", "wkn": "DTR0CK"},
    "Deutsche Bank": {"symbol": "DBK.DE", "isin": "DE0005140008", "wkn": "514000"},
    "Deutsche Börse": {"symbol": "DB1.DE", "isin": "DE0005810055", "wkn": "581005"},
    "Deutsche Post": {"symbol": "DHL.DE", "isin": "DE0005552004", "wkn": "555200"},
    "Deutsche Telekom": {"symbol": "DTE.DE", "isin": "DE0005557508", "wkn": "555750"},
    "E.ON": {"symbol": "EOAN.DE", "isin": "DE000ENAG999", "wkn": "ENAG99"},
    "Fresenius": {"symbol": "FRE.DE", "isin": "DE0005785604", "wkn": "578560"},
    "Fresenius Medical Care": {"symbol": "FME.DE", "isin": "DE0005785802", "wkn": "578580"},
    "Hannover Rück": {"symbol": "HNR1.DE", "isin": "DE0008402215", "wkn": "840221"},
    "Heidelberg Materials": {"symbol": "HEI.DE", "isin": "DE0006047004", "wkn": "604700"},
    "Henkel": {"symbol": "HEN3.DE", "isin": "DE0006048432", "wkn": "604843"},
    "Infineon": {"symbol": "IFX.DE", "isin": "DE0006231004", "wkn": "623100"},
    "Linde": {"symbol": "LIN.DE", "isin": "IE00BZ12WP82", "wkn": "A2DSYC"},
    "Mercedes-Benz": {"symbol": "MBG.DE", "isin": "DE0007100000", "wkn": "710000"},
    "MTU Aero Engines": {"symbol": "MTX.DE", "isin": "DE000A0D9PT0", "wkn": "A0D9PT"},
    "Münchener Rück": {"symbol": "MUV2.DE", "isin": "DE0008430026", "wkn": "843002"},
    "Porsche AG": {"symbol": "P911.DE", "isin": "DE000PAG9113", "wkn": "PAG911"},
    "Qiagen": {"symbol": "QIA.DE", "isin": "NL0012169213", "wkn": "A2DKCH"},
    "RWE": {"symbol": "RWE.DE", "isin": "DE0007037129", "wkn": "703712"},
    "SAP": {"symbol": "SAP.DE", "isin": "DE0007164600", "wkn": "716460"},
    "Siemens": {"symbol": "SIE.DE", "isin": "DE0007236101", "wkn": "723610"},
    "Volkswagen VZ": {"symbol": "VOW3.DE", "isin": "DE0007664039", "wkn": "766403"},
    "Zalando": {"symbol": "ZAL.DE", "isin": "DE000ZAL1111", "wkn": "ZAL111"}
}

# --- Auswahlfelder ---
col_dropdown, col_manual = st.columns([3, 2])
with col_dropdown:
    selected_names = st.multiselect(
        "Wähle bis zu 3 bekannte Aktien",
        options=list(us_stocks.keys()) + list(dax_stocks.keys()),
        default=["Apple", "Amazon", "NVIDIA"],
        max_selections=3
    )
with col_manual:
    input_symbols = st.text_input("Oder gib bis zu 3 Symbole durch Komma getrennt ein (z. B. AAPL,MSFT)")

# --- Symbolauswahl & Mapping ---
symbols = []
meta_info = {}

if input_symbols:
    symbols = [sym.strip().upper() for sym in input_symbols.split(",")[:3]]
    for sym in symbols:
        meta_info[sym] = {"name": sym, "isin": "", "wkn": ""}
elif selected_names:
    for name in selected_names:
        stock = us_stocks.get(name) or dax_stocks.get(name)
        if stock:
            symbols.append(stock["symbol"])
            meta_info[stock["symbol"]] = {
                "name": name,
                "isin": stock["isin"],
                "wkn": stock["wkn"]
            }

# --- Zeitraum auswählen ---
period = st.selectbox("Zeitraum für Vergleich", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# --- Daten abrufen ---
all_data = {}
for symbol in symbols:
    try:
        df = yf.download(symbol, period=period, auto_adjust=True)
        df = df[['Close']].copy()
        df.rename(columns={'Close': symbol}, inplace=True)
        df = df.pct_change().add(1).cumprod().multiply(100)
        all_data[symbol] = df
    except Exception as e:
        st.error(f"Fehler beim Laden von {symbol}: {e}")
# --- Chart anzeigen ---
if all_data:
    combined_df = pd.concat(all_data.values(), axis=1, join='inner')
    st.markdown("### Kursvergleich ")
    fig = go.Figure()
    for symbol in combined_df.columns:
        fig.add_trace(go.Scatter(
            x=combined_df.index,
            y=combined_df[symbol],
            mode='lines',
            name=str(symbol)  # wichtig: explizit in String umwandeln
        ))
    fig.update_layout(
        xaxis_title="Datum", yaxis_title="Indexiert (%)", height=500,
        template="plotly_white", legend_title="Symbol"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Keine Daten konnten geladen werden.")

# --- Unternehmensinfos ---
st.markdown("### Unternehmensdaten")

rows = []
for symbol in symbols:
    try:
        info = yf.Ticker(symbol).info
        meta = meta_info.get(symbol, {})
        rows.append({
            "Symbol": symbol,
            "Name": meta.get("name", info.get("longName", "N/A")),
            "ISIN": meta.get("isin", ""),
            "WKN": meta.get("wkn", ""),
            "Branche": info.get("industry", "N/A"),
            "Sektor": info.get("sector", "N/A"),
            "Marktkap. [Mrd $]": round(info.get("marketCap", 0) / 1e9, 2),
            "Div.-Rendite [%]": round(info.get("dividendYield", 0) / 1, 2) if info.get("dividendYield") else 0.0
        })
    except Exception as e:
        st.warning(f"Daten für {symbol} konnten nicht geladen werden: {e}")

if rows:
    df_info = pd.DataFrame(rows)

    # Transponieren
    df_info_transposed = df_info.set_index("Symbol").transpose()


    # Prozentformatierung für Div.-Rendite
    def format_mixed(val):
        if isinstance(val, float):
            return f"{val:.2f} %" if "Rendite" in df_info_transposed.index else f"{val}"
        return val


    # HTML-Tabelle mit gestyltem Output
    html_info = df_info_transposed.applymap(format_mixed).to_html(escape=False)

    st.markdown(html_info, unsafe_allow_html=True)
else:
    st.info("Keine Unternehmensinformationen verfügbar.")

# --- Fundamentaldaten ---
st.markdown("### Fundamentaldaten")

fundamentals = []

for symbol in symbols:
    try:
        info = yf.Ticker(symbol).info
        fundamentals.append({
            "Symbol": symbol,
            "KGV (PE)": round(info.get("trailingPE", 0), 2),
            "EPS": round(info.get("trailingEps", 0), 2),
            "Umsatz [Mrd $]": round(info.get("totalRevenue", 0) / 1e9, 2),
            "Gewinn [Mrd $]": round(info.get("netIncomeToCommon", 0) / 1e9, 2),
            "Mitarbeiter": info.get("fullTimeEmployees", "N/A"),
            "Beta": round(info.get("beta", 0), 2),
            "Analysten-Rating": f'{info.get("recommendationMean", "N/A")} ({info.get("recommendationKey", "N/A")})'
        })
    except Exception as e:
        st.warning(f"Fehler beim Abruf der Fundamentaldaten für {symbol}: {e}")

#if fundamentals:
#    df_fund = pd.DataFrame(fundamentals)
#    st.dataframe(df_fund, use_container_width=True)
#else:
#    st.info("Keine Fundamentaldaten verfügbar.")

# --- Erweiterung: Dynamische Fundamentaldaten ---
extra_fundamentals = []

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        roe = info.get("returnOnEquity", None)
        debt_to_equity = info.get("debtToEquity", None)
        total_cash = info.get("totalCash", None)
        total_cash_mrd = round(total_cash / 1e9, 2) if total_cash else None

        extra_fundamentals.append({
            "Symbol": symbol,
            "Name": meta_info.get(symbol, {}).get("name", symbol),
            "Eigenkapitalrendite (ROE) [%]": round(roe * 100, 2) if roe else "n/a",
            "Schuldenquote [%]": round(debt_to_equity, 2) if debt_to_equity else "n/a",
            "Cash-Reserven [Mrd $]": total_cash_mrd if total_cash_mrd else "n/a"
        })

    except Exception as e:
        st.warning(f"Fehler bei Zusatzkennzahlen für {symbol}: {e}")

#if extra_fundamentals:
#    df_extra = pd.DataFrame(extra_fundamentals)
#    st.markdown("### 🧾 Erweiterte Kennzahlen")
#    st.dataframe(df_extra, use_container_width=True)
#else:
#    st.info("Keine erweiterten Fundamentaldaten verfügbar.")

# --- Transponierte kombinierte Fundamentaldaten ---
#st.markdown("### 🧮 Transponierte Fundamentaldaten (inkl. erweiterten Kennzahlen)")

# Kombinieren von Basis- und erweiterten Daten
combined_data = []
for base, extra in zip(fundamentals, extra_fundamentals):
    base.update({
        "Eigenkapitalrendite (ROE) [%]": extra.get("Eigenkapitalrendite (ROE) [%]", "n/a"),
        "Schuldenquote [%]": extra.get("Schuldenquote [%]", "n/a"),
        "Cash-Reserven [Mrd $]": extra.get("Cash-Reserven [Mrd $]", "n/a")
    })
    combined_data.append(base)

# In DataFrame umwandeln
df_combined = pd.DataFrame(combined_data).set_index("Symbol")

# Analysten-Rating als Badge formatieren
def format_badge(rating):
    rating = rating.lower()
    if "strong" in rating and "buy" in rating:
        return "<span style='background-color:#006400;color:white;padding:4px 8px;border-radius:6px;'>Strong Buy</span>"
    elif "buy" in rating:
        return "<span style='background-color:#28a745;color:white;padding:4px 8px;border-radius:6px;'>Buy</span>"
    elif "hold" in rating:
        return "<span style='background-color:#ffc107;color:white;padding:4px 8px;border-radius:6px;'>Hold</span>"
    elif "sell" in rating:
        return "<span style='background-color:#dc3545;color:white;padding:4px 8px;border-radius:6px;'>Sell</span>"
    return f"<span style='background-color:#6c757d;color:white;padding:4px 8px;border-radius:6px;'>{rating}</span>"

df_combined["Analysten-Rating"] = df_combined["Analysten-Rating"].apply(format_badge)

# Transponieren und anzeigen
df_transposed = df_combined.transpose()
st.markdown(df_transposed.to_html(escape=False), unsafe_allow_html=True)

import datetime

# --- Wertentwicklung berechnen ---
st.markdown("### Wertentwicklung (Performance in %)")

today = datetime.date.today()
perf_periods = {
    "Heute (%)": today - datetime.timedelta(days=1),
    "1 Woche (%)": today - datetime.timedelta(days=7),
    "1 Monat (%)": today - datetime.timedelta(days=30),
    "6 Monate (%)": today - datetime.timedelta(days=182),
    "1 Jahr (%)": today - datetime.timedelta(days=365),
    "3 Jahre (%)": today - datetime.timedelta(days=3*365),
    "5 Jahre (%)": today - datetime.timedelta(days=5*365)
}

perf_data = []

for symbol in symbols:
    try:
        df = yf.download(symbol, start=min(perf_periods.values()), end=today + datetime.timedelta(days=1), auto_adjust=True)

        if df.empty or "Close" not in df:
            raise ValueError("Keine gültigen Preisdaten erhalten")

        row = {"Symbol": symbol}
        for label, start_date in perf_periods.items():
            start_price = df[df.index >= pd.Timestamp(start_date)]["Close"]
            end_price = df["Close"].iloc[-1]  # Nur den letzten float-Wert

            if not start_price.empty:
                change = ((float(end_price) - float(start_price.iloc[0])) / float(start_price.iloc[0])) * 100
                row[label] = round(change, 2)
            else:
                row[label] = None

        perf_data.append(row)

    except Exception as e:
        except Exception as e:
        st.error(f"Ein Problem ist bei der Prognose-Erstellung aufgetreten: {e}")
        st.error("Dies kann an fehlenden Daten, Netzwerkproblemen oder einem ungültigen Aktiensymbol liegen.")

# --- Tabelle anzeigen ---
if perf_data:
    perf_df = pd.DataFrame(perf_data)
    perf_df.set_index("Symbol", inplace=True)

    # Transponieren
    perf_df_transposed = perf_df.transpose()

    # HTML-Tabelle mit Prozentformatierung
    def format_percent(val):
        try:
            return f"{val:.2f} %"
        except:
            return val

    perf_html = perf_df_transposed.map(format_percent).to_html(escape=False)

    st.markdown(perf_html, unsafe_allow_html=True)
else:
    st.info("Keine Performance-Daten verfügbar.")

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Risikoanalyse
periods = {
    "1 Monat": today - datetime.timedelta(days=30),
    "6 Monate": today - datetime.timedelta(days=182),
    "1 Jahr": today - datetime.timedelta(days=365),
    "3 Jahre": today - datetime.timedelta(days=3 * 365),
    "5 Jahre": today - datetime.timedelta(days=5 * 365)
}

risk_data = {}

for symbol in symbols:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=min(periods.values()), end=today + datetime.timedelta(days=1))

    risk_data[symbol] = {}
    for label, start_date in periods.items():
        start_ts = pd.Timestamp(start_date).tz_localize(hist.index.tz)  # z. B. tz='America/New_York'
        df = hist[hist.index >= start_ts].copy()
        if len(df) > 1:
            df["Return"] = df["Close"].pct_change()
            volatility = df["Return"].std() * (252 ** 0.5)
            sharpe_ratio = df["Return"].mean() / df["Return"].std() * (252 ** 0.5)
            cumulative = (1 + df["Return"]).cumprod()
            peak = cumulative.cummax()
            drawdown = (cumulative - peak) / peak
            max_drawdown = drawdown.min()

            risk_data[symbol][f"Volatilität {label} (%)"] = round(volatility * 100, 2)
            risk_data[symbol][f"Sharpe Ratio {label}"] = round(sharpe_ratio, 2)
            risk_data[symbol][f"Max. Drawdown {label} (%)"] = round(max_drawdown * 100, 2)
        else:
            risk_data[symbol][f"Volatilität {label} (%)"] = None
            risk_data[symbol][f"Sharpe Ratio {label}"] = None
            risk_data[symbol][f"Max. Drawdown {label} (%)"] = None

df = pd.DataFrame(risk_data).T
df_transposed = df.T
print(df_transposed.to_markdown())
# --- Risikoanalyse als HTML-Tabelle anzeigen ---
st.markdown("### Risiko")

## Index umsortieren: zuerst Volatilität, dann Sharpe, dann Drawdown
sort_order = []
for metric in ["Volatilität", "Sharpe Ratio", "Max. Drawdown"]:
    for period in ["1 Monat", "6 Monate", "1 Jahr", "3 Jahre", "5 Jahre"]:
        sort_order.append(f"{metric} {period} (%)" if "Drawdown" in metric or "Volatilität" in metric else f"{metric} {period}")

# Index sortieren
df_sorted = df_transposed.reindex(sort_order)

# Formatierung anwenden
def format_metric(val):
    try:
        return f"{val:.2f} %" if isinstance(val, float) else "-"
    except:
        return "-"

risk_html_sorted = df_sorted.applymap(format_metric).to_html(escape=False)
st.markdown(risk_html_sorted, unsafe_allow_html=True)

# --- Detailanalyse mit Candlestick-Chart ---
st.markdown("## Detailanalyse einzelner Aktien")

detail_symbol = st.selectbox("Wähle eine Aktie zur Detailanalyse", options=symbols)

interval = st.selectbox(
    "Intervall auswählen",
    options=["15m", "1h", "1d", "1wk"],
    index=2
)

show_sma50 = st.checkbox("SMA 50 anzeigen")
show_sma200 = st.checkbox("SMA 200 anzeigen")
show_volume = st.checkbox("Volumen anzeigen")
show_rsi = st.checkbox("RSI anzeigen")

interval_period_map = {
    "15m": "15d",
    "1h": "40d",
    "1d": "1y",
    "1wk": "5y"
}
period = interval_period_map.get(interval)

# --- Kursdaten laden ---
df = yf.download(detail_symbol, period=period, interval=interval, auto_adjust=True)
df.index = pd.to_datetime(df.index)
df.sort_index(inplace=True)

# --- MultiIndex fixen (z. B. durch group_by='ticker') ---
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.copy()

# Debug-Ansicht zur Kontrolle
#st.write(df[["Open", "High", "Low", "Close"]].tail(10))

# --- Candlestick-Plot ---
if not df.empty and all(col in df.columns for col in ["Open", "High", "Low", "Close"]):
    # Subplots vorbereiten
    rows = 1 + int(show_volume) + int(show_rsi)
    row_heights = [0.6] + [0.2] * (rows - 1)
    fig = make_subplots(
    rows=rows, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=row_heights,
    subplot_titles=[f"Candlestick-Chart für {detail_symbol}"] +
                   (["Volumen"] if show_volume else []) +
                   (["RSI (14)"] if show_rsi else [])
    )


    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Kurs",
        increasing_line_color='green',
        decreasing_line_color='red',
        showlegend=True
    ))

    # --- SMA 50 ---
    if show_sma50:
        df["SMA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA50"], mode="lines",
            name="SMA 50", line=dict(color='orange', width=2)
        ))

    # --- SMA 200 ---
    if show_sma200:
        df["SMA200"] = df["Close"].rolling(window=200, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA200"], mode="lines",
            name="SMA 200", line=dict(color='teal', width=2)
        ))

    if show_rsi:
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

    row_idx = 2
    if show_volume:
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            name="Volumen", marker_color="lightgray"
        ), row=row_idx, col=1)
    row_idx += 1

    if show_rsi:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"],
            mode="lines", name="RSI",
            line=dict(color="purple")
        ), row=row_idx, col=1)

    # Layout finalisieren
    fig.update_layout(
        height=250 * rows + 300,
        showlegend=True,
        template="plotly_white",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Für dieses Intervall konnten keine Kursdaten geladen werden.")
import datetime
import pandas as pd  # Sicherstellen, dass pandas importiert ist
import plotly.graph_objects as go  # Sicherstellen, dass plotly.graph_objects importiert ist

# NEUE IMPORT für Exponential Smoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# --- Prognose (Forecast) Abschnitt ---
st.markdown("## 📈 Aktienprognose")

# Sicherstellen, dass ein Symbol für die Prognose ausgewählt ist
if symbols:
    forecast_symbol = st.selectbox(
        "Wähle eine Aktie für die Prognose",
        options=symbols,
        key="forecast_stock_select"  # unique key to avoid duplicate widget error
    )
else:
    st.info("Bitte wähle zuerst eine Aktie aus den oberen Auswahlfeldern, um eine Prognose zu erstellen.")
    forecast_symbol = None

if forecast_symbol:
    forecast_period_days = st.slider(
        "Anzahl der Tage für die Prognose",
        min_value=7, max_value=180, value=30, step=7  # Max 180 Tage, da länger sehr unsicher wird
    )

    st.markdown(f"### Prognose für {forecast_symbol}")
    st.info(
        "ℹ️ Die Prognose basiert auf einem Exponential Smoothing Modell und sollte nur als Indikator dienen, nicht als Finanzberatung. Historische Daten bis heute werden verwendet.")

    try:
        # Lade historische Daten (Tagesdaten sind am besten für ETS)
        forecast_df = yf.download(forecast_symbol, period="5y", interval="1d",
                                  auto_adjust=True)  # 5 Jahre für gute Basis
        forecast_df = forecast_df[['Close']]  # Nur den Schlusskurs verwenden

        # Überprüfen, ob genügend Daten vorhanden sind
        # Exponential Smoothing benötigt eine ausreichende Datenmenge, hier mindestens 60 Punkte für eine solide Basis
    else:
    # --- HIER DIE DEBUGGING-ZEILEN EINFÜGEN ---
    st.write("DEBUG: forecast_df Kopf (erste 5 Zeilen):")
    st.write(forecast_df.head())
    st.write("DEBUG: forecast_df Ende (letzte 5 Zeilen):")
    st.write(forecast_df.tail())
    st.write("DEBUG: forecast_df Fehlende Werte pro Spalte:")
    st.write(forecast_df.isnull().sum())

    # Exponential Smoothing Modell trainieren
    # `trend='add'` für einen additiven Trend (z.B. Kurs steigt konstant)
    # `seasonal='add'` für additive Saisonalität (z.B. gleiche saisonale Schwankungen über die Zeit)
    # `seasonal_periods=5` für wöchentliche Saisonalität bei täglichen Handelsdaten (5 Handelstage pro Woche)
    model_fit = ExponentialSmoothing(
        forecast_df['Close'],
        trend='add',
        seasonal='add',
        seasonal_periods=5
    ).fit()

    # Zukünftige Datenpunkte für die Prognose erstellen (nur Handelstage)
    last_date = forecast_df.index[-1]
    future_dates = []
    current_date = last_date + pd.Timedelta(days=1)
    while len(future_dates) < forecast_period_days:
        if current_date.dayofweek < 5:  # Montag=0, Sonntag=6 (nur Werktage)
            future_dates.append(current_date)
        current_date += pd.Timedelta(days=1)

    # Prognose erstellen
    forecast_values = model_fit.forecast(len(future_dates))

    # Kombiniere historische und prognostizierte Daten für den Plot
    # Erstelle eine Series aus den Prognosewerten mit den zukünftigen Daten als Index
    forecast_series = pd.Series(forecast_values.values, index=future_dates)

    # --- WEITERE DEBUGGING-ZEILEN HIER EINFÜGEN ---
    st.write("DEBUG: forecast_series Kopf (erste 5 Prognosen):")
    st.write(forecast_series.head())
    st.write("DEBUG: forecast_series Ende (letzte 5 Prognosen):")
    st.write(forecast_series.tail())
    st.write("DEBUG: forecast_series Fehlende Werte pro Prognose:")
    st.write(forecast_series.isnull().sum())
    st.write("DEBUG: forecast_series Länge:", len(forecast_series))

    # Plotly Figur erstellen
    fig_forecast = go.Figure()

    # Historische Daten hinzufügen
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['Close'],
        mode='lines',
        name='Historischer Kurs',
        line=dict(color='blue')
    ))

    # Prognose hinzufügen
    fig_forecast.add_trace(go.Scatter(
        x=forecast_series.index,
        y=forecast_series.values,
        mode='lines',
        name='Prognose',
        line=dict(color='red', dash='dash')
    ))

    # Layout anpassen (behalte das hardcodierte Template vorerst bei)
    fig_forecast.update_layout(
        title=f'Prognose für {forecast_symbol} mit Exponential Smoothing',
        xaxis_title="Datum",
        yaxis_title="Schlusskurs",
        template="plotly_white",  # <-- Diese Zeile so lassen, bis der Plot funktioniert
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # --- DEBUGGING: Plotly Figure Objekt selbst anzeigen ---
    st.write("DEBUG: Plotly Figure Objekt (dies zeigt seine interne Struktur):")
    st.write(fig_forecast)

    st.plotly_chart(fig_forecast, use_container_width=True)