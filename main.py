import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from prophet import Prophet
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# NEUE IMPORT für Exponential Smoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# --- Dark Mode Umschalter ---
dark_mode = st.toggle("Dark Mode ", value=False)

# --- Farben definieren ---
if dark_mode:
    background_color = "#0E1117"
    text_color = "#FAFAFA"
    table_bg = "#1e1e1e"
    table_text = "#FAFAFA"
    plotly_template_global = "plotly_dark"
else:
    background_color = "#FAFAFA"
    text_color = "#000000"
    table_bg = "#FFFFFF"
    table_text = "#000000"
    plotly_template_global = "plotly_white"

# --- Globales CSS anwenden ---
st.markdown(f"""
    <style>
        /* NEU: Überschriften und Markdown-Text linksbündig ausrichten */
        h1, h2, h3, h4, h5, h6, .stMarkdown {{
            text-align: left !important; /* !important, um sicherzustellen, dass es Vorrang hat */
            width: 100%;
        }}

        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        .css-1v3fvcr, .css-1dp5vir, .css-1d391kg, .css-1e5imcs {{ /* Anpassen für Streamlit-Widgets */
            background-color: {background_color} !important;
            color: {text_color} !important;
        }}
        .orange-text {{
            color: #FF6600;
            font-weight: bold;
            font-size: 36px;
        }}
        /* Für Tabellen-Styling */
        table {{
            background-color: {table_bg};
            color: {table_text};
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid {text_color};
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: {table_bg};
            color: {text_color};
        }}
        /* Streamlit info, warning, error boxen anpassen */
        .stAlert {{
            color: {text_color}; /* Textfarbe für Alerts */
        }}
        .stAlert.info {{
            background-color: rgba(0, 123, 255, 0.2); /* Hellblau */
            border-color: #007bff;
        }}
        .stAlert.warning {{
            background-color: rgba(255, 193, 7, 0.2); /* Hellorange/Gelb */
            border-color: #ffc107;
        }}
        .stAlert.error {{
            background-color: rgba(220, 53, 69, 0.2); /* Hellrot */
            border-color: #dc3545;
        }}
        section[data-testid="stSidebar"] > div {{
            background-color: {background_color};
        }}
        div[data-baseweb="select"] > div {{
            background-color: {background_color} !important;
            color: {text_color} !important;
        }}
        div[data-baseweb="select"] * {{
            color: {text_color} !important;
        }}
        input, textarea {{
            background-color: {background_color} !important;
            color: {text_color} !important;
            border: 1px solid {text_color} !important;
        }}
        label, .stTextInput, .stSelectbox, .stMultiSelect {{
            color: {text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Layout & Design ---
st.set_page_config(page_title="DZI Aktien Analyst", layout="wide")

# --- Titel und Logo ---
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div class='orange-text'>DZI Aktien Analyst</div>", unsafe_allow_html=True)
with col2:
    # Stelle sicher, dass logo.png im selben Verzeichnis wie main.py ist
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

# --- Benchmark-Auswahl korrekt ---
benchmark_options = {
    "Keine Benchmark": None,
    "S&P 500 (USA)": "SPY",
    "NASDAQ 100": "QQQ",
    "MSCI World (ETF)": "URTH",  # Alternativen: EUNL.DE, IWDA, etc.
    "DAX (Deutschland)": "^GDAXI"
}

selected_benchmark_label = st.selectbox(
    "Benchmark zum Vergleich auswählen:",
    options=list(benchmark_options.keys()),
    index=1,
    key="benchmark_select_perf"
)

benchmark_symbol = benchmark_options.get(selected_benchmark_label)

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
period_comparison = st.selectbox("Zeitraum für Vergleich", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# --- Kursdaten abrufen (für Vergleich) ---
all_data = {}

# Aktiendaten abrufen
for symbol in symbols:
    try:
        df = yf.download(symbol, period=period_comparison, auto_adjust=True)[["Close"]]
        df = df.pct_change().add(1).cumprod().multiply(100)
        df.rename(columns={"Close": symbol}, inplace=True)
        all_data[symbol] = df
    except Exception as e:
        st.error(f"Fehler beim Laden von {symbol}: {e}")

# Benchmark-Daten hinzufügen
if benchmark_symbol:
    try:
        df_benchmark = yf.download(benchmark_symbol, period=period_comparison, auto_adjust=True)[["Close"]]
        df_benchmark = df_benchmark.pct_change().add(1).cumprod().multiply(100)
        df_benchmark.rename(columns={"Close": "Benchmark"}, inplace=True)
        all_data["Benchmark"] = df_benchmark
    except Exception as e:
        st.warning(f"Benchmark konnte nicht geladen werden: {e}")

# --- Chart anzeigen (Vergleich) ---
if all_data:
    combined_df = pd.concat(all_data.values(), axis=1, join='inner')
    st.markdown("### Kursvergleich")

    fig = go.Figure()
    for symbol_col in combined_df.columns:  # Umbenannt, um Konflikt mit der globalen 'symbol' Variable zu vermeiden
        is_benchmark = symbol_col == "Benchmark"
        label = f"{selected_benchmark_label} (Benchmark)" if is_benchmark else symbol_col
        fig.add_trace(go.Scatter(
            x=combined_df.index,
            y=combined_df[symbol_col],
            mode='lines',
            name=str(label),
            line=dict(
                width=2,
                dash="dot" if is_benchmark else "solid",
                color="gray" if is_benchmark else None
            )
        ))

    fig.update_layout(
        xaxis_title="Datum",
        yaxis_title="Indexiert (%)",
        height=500,
        template=plotly_template_global,
        legend_title="Symbol",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(color=text_color)
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
            "Div.-Rendite [%]": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0.0
        })
    except Exception as e:
        st.warning(f"Daten für {symbol} konnten nicht geladen werden: {e}")

if rows:
    df_info = pd.DataFrame(rows)

    # Transponieren
    df_info_transposed = df_info.set_index("Symbol").transpose()

    # HTML-Tabelle mit gestyltem Output
    html_info = df_info_transposed.to_html(escape=False)
    st.markdown(html_info, unsafe_allow_html=True)
else:
    st.info("Keine Unternehmensinformationen verfügbar.")

# --- Fundamentaldaten ---
st.markdown("### Fundamentaldaten")

fundamentals = []

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

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
            "Eigenkapitalrendite (ROE) [%]": round(roe * 100, 2) if roe is not None else "n/a",
            "Schuldenquote [%]": round(debt_to_equity, 2) if debt_to_equity is not None else "n/a",
            "Cash-Reserven [Mrd $]": total_cash_mrd if total_cash_mrd is not None else "n/a"
        })

    except Exception as e:
        st.warning(f"Fehler bei Zusatzkennzahlen für {symbol}: {e}")

# --- Transponierte kombinierte Fundamentaldaten ---
combined_data = []
min_len = min(len(fundamentals), len(extra_fundamentals))
for i in range(min_len):
    base = fundamentals[i].copy()
    extra = extra_fundamentals[i]
    base.update({
        "Eigenkapitalrendite (ROE) [%]": extra.get("Eigenkapitalrendite (ROE) [%]", "n/a"),
        "Schuldenquote [%]": extra.get("Schuldenquote [%]", "n/a"),
        "Cash-Reserven [Mrd $]": extra.get("Cash-Reserven [Mrd $]", "n/a")
    })
    combined_data.append(base)

if combined_data:
    df_combined = pd.DataFrame(combined_data).set_index("Symbol")


    def format_badge(rating):
        rating = str(rating).lower()
        if "strong buy" in rating:
            return "<span style='background-color:#006400;color:white;padding:4px 8px;border-radius:6px;'>Strong Buy</span>"
        elif "buy" in rating:
            return "<span style='background-color:#28a745;color:white;padding:4px 8px;border-radius:6px;'>Buy</span>"
        elif "hold" in rating or "neutral" in rating:
            return "<span style='background-color:#ffc107;color:white;padding:4px 8px;border-radius:6px;'>Hold</span>"
        elif "sell" in rating:
            return "<span style='background-color:#dc3545;color:white;padding:4px 8px;border-radius:6px;'>Sell</span>"
        return f"<span style='background-color:#6c757d;color:white;padding:4px 8px;border-radius:6px;'>{rating.capitalize()}</span>"


    if "Analysten-Rating" in df_combined.columns:
        df_combined["Analysten-Rating"] = df_combined["Analysten-Rating"].apply(format_badge)

    df_transposed_fund = df_combined.transpose()
    st.markdown(df_transposed_fund.to_html(escape=False), unsafe_allow_html=True)
else:
    st.info("Keine Fundamentaldaten verfügbar.")

# --- Wertentwicklung berechnen ---
st.markdown("### Wertentwicklung (Performance in %)")

today = datetime.date.today()
perf_periods = {
    "Heute (%)": today - datetime.timedelta(days=1),
    "1 Woche (%)": today - datetime.timedelta(days=7),
    "1 Monat (%)": today - datetime.timedelta(days=30),
    "6 Monate (%)": today - datetime.timedelta(days=182),
    "1 Jahr (%)": today - datetime.timedelta(days=365),
    "3 Jahre (%)": today - datetime.timedelta(days=3 * 365),
    "5 Jahre (%)": today - datetime.timedelta(days=5 * 365)
}

perf_data = []

for symbol in symbols:
    try:
        df_perf = yf.download(symbol, start=min(perf_periods.values()), end=today + datetime.timedelta(days=1),
                              auto_adjust=True)

        if df_perf.empty or "Close" not in df_perf:
            raise ValueError("Keine gültigen Preisdaten erhalten für Performance-Berechnung")

        row = {"Symbol": symbol}
        for label, start_date in perf_periods.items():
            start_price_series = df_perf[df_perf.index >= pd.Timestamp(start_date, tz=df_perf.index.tz)]['Close']
            end_price = df_perf["Close"].iloc[-1]

            if not start_price_series.empty:
                start_price_val = float(start_price_series.iloc[0])
                end_price_val = float(end_price)

                if start_price_val != 0:
                    change = ((end_price_val - start_price_val) / start_price_val) * 100
                    row[label] = round(change, 2)
                else:
                    row[label] = None
            else:
                row[label] = None

        perf_data.append(row)

    except Exception as e:
        st.warning(f"Fehler bei der Performance-Berechnung für {symbol}: {e}")

if perf_data:
    perf_df = pd.DataFrame(perf_data)
    perf_df.set_index("Symbol", inplace=True)

    perf_df_transposed = perf_df.transpose()


    def format_percent(val):
        try:
            if val is None:
                return "N/A"
            return f"{val:.2f} %"
        except:
            return val


    perf_html = perf_df_transposed.map(format_percent).to_html(escape=False)

    st.markdown(perf_html, unsafe_allow_html=True)
else:
    st.info("Keine Performance-Daten verfügbar.")

# Risikoanalyse
periods_risk = {
    "1 Monat": today - datetime.timedelta(days=30),
    "6 Monate": today - datetime.timedelta(days=182),
    "1 Jahr": today - datetime.timedelta(days=365),
    "3 Jahre": today - datetime.timedelta(days=3 * 365),
    "5 Jahre": today - datetime.timedelta(days=5 * 365)
}

risk_data = {}

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=min(periods_risk.values()), end=today + datetime.timedelta(days=1))

        risk_data[symbol] = {}
        for label, start_date in periods_risk.items():
            start_ts = pd.Timestamp(start_date)
            if hist.index.tz is None:
                start_ts = start_ts.tz_localize('UTC')
                df_risk = hist[hist.index >= start_ts].copy()
            else:
                start_ts = start_ts.tz_localize(hist.index.tz)
                df_risk = hist[hist.index >= start_ts].copy()

            if len(df_risk) > 1:
                df_risk["Return"] = df_risk["Close"].pct_change()
                clean_returns = df_risk["Return"].dropna()
                if len(clean_returns) > 0:
                    volatility = clean_returns.std() * (252 ** 0.5)
                    sharpe_ratio = clean_returns.mean() / clean_returns.std() * (
                            252 ** 0.5) if clean_returns.std() != 0 else 0.0

                    cumulative = (1 + clean_returns).cumprod()
                    if not cumulative.empty:
                        peak = cumulative.cummax()
                        drawdown = (cumulative - peak) / peak
                        max_drawdown = drawdown.min()
                    else:
                        max_drawdown = 0.0

                    risk_data[symbol][f"Volatilität {label} (%)"] = round(volatility * 100, 2)
                    risk_data[symbol][f"Sharpe Ratio {label}"] = round(sharpe_ratio, 2)
                    risk_data[symbol][f"Max. Drawdown {label} (%)"] = round(max_drawdown * 100, 2)
                else:
                    risk_data[symbol][f"Volatilität {label} (%)"] = None
                    risk_data[symbol][f"Sharpe Ratio {label} (%)"] = None
                    risk_data[symbol][f"Max. Drawdown {label} (%)"] = None
            else:
                risk_data[symbol][f"Volatilität {label} (%)"] = None
                risk_data[symbol][f"Sharpe Ratio {label} (%)"] = None
                risk_data[symbol][f"Max. Drawdown {label} (%)"] = None
    except Exception as e:
        st.warning(f"Fehler bei Risikoanalyse für {symbol}: {e}")

df_risk = pd.DataFrame(risk_data).T

st.markdown("### Risiko")

if not df_risk.empty:
    df_transposed_risk = df_risk.T
    sort_order = []
    for metric in ["Volatilität", "Sharpe Ratio", "Max. Drawdown"]:
        for period_label in periods_risk.keys():
            # Anpassung für Sharpe Ratio, da es keine Prozentangabe hat
            if "Sharpe Ratio" in metric:
                sort_order.append(f"{metric} {period_label}")
            else:
                sort_order.append(f"{metric} {period_label} (%)")

    valid_sort_order = [idx for idx in sort_order if idx in df_transposed_risk.index]
    df_sorted_risk = df_transposed_risk.reindex(valid_sort_order)

    formatted_data = {}
    for col in df_sorted_risk.columns:
        formatted_data[col] = []
        for idx in df_sorted_risk.index:
            val = df_sorted_risk.loc[idx, col]
            if "Volatilität" in idx or "Drawdown" in idx:
                formatted_data[col].append(f"{val:.2f} %" if isinstance(val, (int, float)) else "N/A")
            elif "Sharpe Ratio" in idx:
                formatted_data[col].append(f"{val:.2f}" if isinstance(val, (int, float)) else "N/A")
            else:
                formatted_data[col].append(val if val is not None else "N/A")

    df_formatted_risk = pd.DataFrame(formatted_data, index=df_sorted_risk.index)

    risk_html_sorted = df_formatted_risk.to_html(escape=False)
    st.markdown(risk_html_sorted, unsafe_allow_html=True)
else:
    st.info("Keine Risikoanalyse-Daten verfügbar.")

# --- Detailanalyse mit Candlestick-Chart ---
st.markdown("## Detailanalyse einzelner Aktien")

if symbols:
    detail_symbol = st.selectbox("Wähle eine Aktie zur Detailanalyse", options=symbols, key="detail_symbol_select")
else:
    detail_symbol = None
    st.info("Bitte wähle zuerst eine Aktie für die Detailanalyse aus den oberen Auswahlfeldern.")

if detail_symbol:
    # Update der Selectbox Optionen, um 1mo und 3mo wieder zu enthalten
    interval_options = ["15m", "1h", "1d", "1wk", "1mo", "3mo"]
    interval = st.selectbox(
        "Intervall auswählen",
        options=interval_options,
        index=2,  # Setzt "1d" als Standardauswahl
        key="detail_interval_select"
    )

    # Die Prognose-Methoden sind nur für "1d" und "1wk" sinnvoll aufgrund der Datenmenge
    if interval in ["1d", "1wk", "1mo", "3mo"]:  # Prophet/ETS für längere Intervalle erlauben
        forecast_method = st.radio(
            "Prognosemethode wählen:",
            options=["Keine", "Exponential Smoothing", "Prophet"],
            horizontal=True
        )
    else:
        forecast_method = "Keine"  # Keine Prognose für 15m/1h

    if forecast_method in ["Exponential Smoothing", "Prophet"]:
        forecast_horizon = st.slider(
            "Prognosezeitraum auswählen (3-30)",
            min_value=3,
            max_value=30,
            value=7
        )
    else:
        forecast_horizon = 0

    show_sma50 = st.checkbox("SMA 50 anzeigen", key="show_sma50_check")
    show_sma200 = st.checkbox("SMA 200 anzeigen", key="show_sma200_check")
    show_volume = st.checkbox("Volumen anzeigen", key="show_volume_check")
    show_rsi = st.checkbox("RSI anzeigen", key="show_rsi_check")

    # Aktualisierte interval_period_map für die neuen Optionen
    interval_period_map = {
        "15m": "15d",
        "1h": "60d",  # Angepasst: 40d ist evtl. zu kurz für 1h Daten
        "1d": "1y",  # 1 Jahr Daten für täglichen Chart
        "1wk": "5y",  # 5 Jahre Daten für wöchentlichen Chart
        "1mo": "10y",  # 10 Jahre Daten für monatlichen Chart
        "3mo": "max"  # Maximal verfügbare Daten für vierteljährlichen Chart (oder z.B. "20y")
    }

    period_detail = interval_period_map.get(interval)

    if period_detail is None:
        st.error(
            f"Fehler: Das ausgewählte Intervall '{interval}' wird derzeit nicht unterstützt. Bitte wählen Sie ein anderes Intervall.")
        st.stop()

    # --- Kursdaten laden ---
    df_detail = yf.download(detail_symbol, period=period_detail, interval=interval, auto_adjust=True)
    df_detail.index = pd.to_datetime(df_detail.index)
    df_detail.sort_index(inplace=True)

    if isinstance(df_detail.columns, pd.MultiIndex):
        df_detail.columns = df_detail.columns.get_level_values(0)

    df_detail = df_detail.copy()

    # --- Candlestick-Plot ---
    if not df_detail.empty and all(col in df_detail.columns for col in ["Open", "High", "Low", "Close", "Volume"]):
        rows = 1
        row_heights = [0.6]
        subplot_titles = [f"Candlestick-Chart für {detail_symbol}"]

        if show_volume:
            rows += 1
            row_heights.append(0.2)
            subplot_titles.append("Volumen")
        if show_rsi:
            rows += 1
            row_heights.append(0.2)
            subplot_titles.append("RSI (14)")

        fig_detail = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )

        fig_detail.add_trace(go.Candlestick(
            x=df_detail.index,
            open=df_detail["Open"],
            high=df_detail["High"],
            low=df_detail["Low"],
            close=df_detail["Close"],
            name="Kurs",
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=True
        ), row=1, col=1)

        if show_sma50:
            df_detail["SMA50"] = df_detail["Close"].rolling(window=50, min_periods=1).mean()
            fig_detail.add_trace(go.Scatter(
                x=df_detail.index, y=df_detail["SMA50"], mode="lines",
                name="SMA 50", line=dict(color='orange', width=2)
            ), row=1, col=1)

        if show_sma200:
            df_detail["SMA200"] = df_detail["Close"].rolling(window=200, min_periods=1).mean()
            fig_detail.add_trace(go.Scatter(
                x=df_detail.index, y=df_detail["SMA200"], mode="lines",
                name="SMA 200", line=dict(color='teal', width=2)
            ), row=1, col=1)

        row_idx_current = 2
        if show_volume:
            fig_detail.add_trace(go.Bar(
                x=df_detail.index, y=df_detail["Volume"],
                name="Volumen", marker_color="lightgray"
            ), row=row_idx_current, col=1)
            row_idx_current += 1

        if show_rsi:
            delta = df_detail["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(com=13, adjust=False).mean()
            avg_loss = loss.ewm(com=13, adjust=False).mean()
            rs = avg_gain / avg_loss
            df_detail["RSI"] = 100 - (100 / (1 + rs))

            fig_detail.add_trace(go.Scatter(
                x=df_detail.index, y=df_detail["RSI"],
                mode="lines", name="RSI",
                line=dict(color="purple")
            ), row=row_idx_current, col=1)
            fig_detail.add_hline(y=70, line_dash="dot", line_color="red", row=row_idx_current, col=1)
            fig_detail.add_hline(y=30, line_dash="dot", line_color="green", row=row_idx_current, col=1)

        # Layout finalisieren
        fig_detail.update_layout(
            height=250 * rows + 150,
            showlegend=True,
            template=plotly_template_global,
            xaxis_rangeslider_visible=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            font=dict(color=text_color)
        )
        for i in range(1, rows + 1):
            fig_detail.update_xaxes(rangeslider_visible=False, row=i, col=1)

        st.plotly_chart(fig_detail, use_container_width=True)
    else:
        st.warning(
            f"Für {detail_symbol} konnten im Intervall {interval} keine ausreichenden Kursdaten geladen oder der Chart nicht erstellt werden. Bitte wähle ein anderes Intervall oder eine andere Aktie.")

    # --- HIER BEGINNT DER NEUE FORECAST-BEREICH ---
    # Prognose nur anzeigen, wenn eine Methode ausgewählt ist
    if forecast_method != "Keine" and not df_detail.empty and "Close" in df_detail.columns:
        st.markdown(f"### Kursprognose ({forecast_method})")

        try:
            # NEUE MAPPING FÜR RESAMPLING FREQUENZEN
            # Diese Map ist spezifisch für Pandas resample()
            resample_frequency_map = {
                "15m": "15min",  # 15 Minuten
                "1h": "H",  # Stündlich
                "1d": "D",  # Täglich
                "1wk": "W",  # Wöchentlich (Wochenende)
                "1mo": "M",  # Monatlich (Monatsende)
                "3mo": "Q"  # Quartalsweise (Quartalsende)
            }

            # Hole die passende Resampling-Frequenz für Pandas
            # Fallback ist der ursprüngliche Interval-String, falls kein Mapping existiert (sollte aber nicht passieren)
            resample_freq = resample_frequency_map.get(interval, interval)

            # Stelle sicher, dass die Daten für Prophet/ETS geeignet sind (keine Lücken im Index für Resampling)
            # resample().last() nimmt den letzten Wert in jedem Intervall
            df_resampled = df_detail['Close'].resample(resample_freq).last().ffill().bfill()

            # Sicherstellen, dass der Index den richtigen Typ hat für Prophet
            df_prophet_input = df_resampled.reset_index()
            df_prophet_input.columns = ["ds", "y"]

            if len(df_resampled) < 2:
                st.info("Nicht genügend Datenpunkte für eine sinnvolle Prognose (mindestens 2 benötigt).")
            else:
                fig_forecast = go.Figure()

                # Historische Daten immer anzeigen
                fig_forecast.add_trace(go.Scatter(
                    x=df_resampled.index,
                    y=df_resampled,
                    mode='lines',
                    name='Historische Kurse',
                    line=dict(color='blue')
                ))

                if forecast_method == "Exponential Smoothing":
                    # Hier wird das Modell direkt auf die resampelten Daten angewendet
                    fit = ExponentialSmoothing(
                        df_resampled,
                        trend='add',
                        seasonal=None,  # Keine Saisonalität angenommen, um Komplexität zu vermeiden
                        initialization_method="estimated"
                    ).fit()

                    # Erzeuge zukünftige Zeitstempel basierend auf der Resampling-Frequenz
                    last_date = df_resampled.index[-1]
                    future_dates = pd.date_range(start=last_date, periods=forecast_horizon + 1, freq=resample_freq)[1:]

                    forecast = fit.forecast(forecast_horizon)
                    forecast_df = pd.DataFrame({'ds': future_dates, 'yhat': forecast.values})

                    fig_forecast.add_trace(go.Scatter(
                        x=forecast_df['ds'],
                        y=forecast_df['yhat'],
                        mode='lines',
                        name='Prognose (Exponential Smoothing)',
                        line=dict(color='green', dash='dot')
                    ))

                elif forecast_method == "Prophet":
                    model = Prophet(
                        yearly_seasonality=True,
                        weekly_seasonality=True if interval not in ["1mo", "3mo"] else False,
                        # Wochen-Saison nur für tägliche/wöchentliche Daten
                        daily_seasonality=False  # Tägliche Saisonalität bei stündlichen/minütlichen Daten
                    )
                    model.fit(df_prophet_input)

                    # Erstelle zukünftige Dataframes für die Prognose
                    # Abhängig vom Intervall, entsprechende Frequenz für future_dates
                    freq_map_prophet = {
                        "15m": "15min",
                        "1h": "H",
                        "1d": "D",
                        "1wk": "W",
                        "1mo": "M",
                        "3mo": "Q"
                    }
                    future = model.make_future_dataframe(periods=forecast_horizon,
                                                         freq=freq_map_prophet.get(interval, 'D'))
                    forecast = model.predict(future)

                    fig_forecast.add_trace(go.Scatter(
                        x=forecast['ds'],
                        y=forecast['yhat'],
                        mode='lines',
                        name='Prognose (Prophet)',
                        line=dict(color='green', dash='dot')
                    ))
                    fig_forecast.add_trace(go.Scatter(
                        x=forecast['ds'],
                        y=forecast['yhat_lower'],
                        fill='tonexty',
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        name='Untergrenze'
                    ))
                    fig_forecast.add_trace(go.Scatter(
                        x=forecast['ds'],
                        y=forecast['yhat_upper'],
                        fill='tonexty',
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        name='Obergrenze'
                    ))

                fig_forecast.update_layout(
                    xaxis_title="Datum",
                    yaxis_title="Kurs",
                    height=500,
                    template=plotly_template_global,
                    legend_title="Legende",
                    plot_bgcolor=background_color,
                    paper_bgcolor=background_color,
                    font=dict(color=text_color),
                    hovermode="x unified"
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

        except Exception as e:
            st.error(f"Fehler bei der Prognose: {e}")
            st.info(
                "Bitte überprüfe, ob ausreichend historische Daten für das gewählte Intervall und den Prognosezeitraum vorhanden sind. Bei sehr kurzen Intervallen oder langen Prognosezeiträumen kann es zu Problemen kommen.")