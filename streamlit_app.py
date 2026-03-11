
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="פרויקט מחקר אנליטי - יהלומים", layout="wide")

@st.cache_data
def load_data():
    file_options = [
        "diamonds_clean.csv",
        "diamonds.csv",
        "B_student_diamonds.csv",
        "diamonds_for_jasp.csv"
    ]
    for file_name in file_options:
        try:
            loaded_df = pd.read_csv(file_name)
            return loaded_df, file_name
        except Exception:
            continue
    fallback_df = px.data.diamonds()
    return fallback_df, "plotly_sample_diamonds"

data_df, source_name = load_data()
data_df = data_df.copy()

for numeric_col in ["price", "carat", "depth", "table", "x", "y", "z"]:
    if numeric_col in data_df.columns:
        data_df[numeric_col] = pd.to_numeric(data_df[numeric_col], errors="coerce")

st.sidebar.header("סינון הנתונים")
cut_vals = sorted([val for val in data_df["cut"].dropna().unique()]) if "cut" in data_df.columns else []
color_vals = sorted([val for val in data_df["color"].dropna().unique()]) if "color" in data_df.columns else []
clarity_vals = sorted([val for val in data_df["clarity"].dropna().unique()]) if "clarity" in data_df.columns else []

selected_cuts = st.sidebar.multiselect("בחרי חיתוך", cut_vals, default=cut_vals)
selected_colors = st.sidebar.multiselect("בחרי צבע", color_vals, default=color_vals)
selected_clarity = st.sidebar.multiselect("בחרי ניקיון", clarity_vals, default=clarity_vals)

filtered_df = data_df.copy()
if len(selected_cuts) > 0 and "cut" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["cut"].isin(selected_cuts)]
if len(selected_colors) > 0 and "color" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["color"].isin(selected_colors)]
if len(selected_clarity) > 0 and "clarity" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["clarity"].isin(selected_clarity)]

st.title("פרויקט מחקר אנליטי - שוק היהלומים")
st.markdown("### שאלת המחקר")
st.markdown("עד כמה משקל היהלום ומדדי האיכות שלו מסבירים את המחיר, ואילו משתנים משפיעים עליו יותר")
st.markdown("### השערת המחקר")
st.markdown("ככל שמשקל היהלום גבוה יותר וככל שמדדי האיכות טובים יותר, כך המחיר צפוי להיות גבוה יותר")

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("מספר תצפיות לאחר סינון", int(len(filtered_df)))
metric_b.metric("מחיר ממוצע", round(float(filtered_df["price"].dropna().mean()), 2) if "price" in filtered_df.columns and filtered_df["price"].dropna().shape[0] > 0 else 0)
metric_c.metric("קראט ממוצע", round(float(filtered_df["carat"].dropna().mean()), 2) if "carat" in filtered_df.columns and filtered_df["carat"].dropna().shape[0] > 0 else 0)

st.markdown("### תובנות מרכזיות")
st.markdown("יהלומים כבדים יותר נוטים להיות יקרים יותר, אך גם לצבע, לניקיון ולחיתוך יש השפעה חשובה")
st.markdown("השוואה בין קבוצות מאפשרת לזהות אם יש דפוסים עקביים במחיר לפי איכות")
st.markdown("זהו בסיס טוב לניתוח תיאורי ולהסקת מסקנות במסגרת עבודת חקר")

if "carat" in filtered_df.columns and "price" in filtered_df.columns:
    scatter_df = filtered_df[["carat", "price", "cut", "color", "clarity"]].dropna()
    scatter_df = scatter_df.sample(min(4000, len(scatter_df)), random_state=42) if len(scatter_df) > 0 else scatter_df
    fig_scatter = px.scatter(scatter_df, x="carat", y="price", color="cut" if "cut" in scatter_df.columns else None, hover_data=[col for col in ["color", "clarity"] if col in scatter_df.columns], title="הקשר בין קראט למחיר")
    st.plotly_chart(fig_scatter, use_container_width=True)

left_col, right_col = st.columns(2)
with left_col:
    if "cut" in filtered_df.columns and "price" in filtered_df.columns:
        cut_df = filtered_df[["cut", "price"]].dropna().groupby("cut", as_index=False)["price"].mean()
        fig_cut = px.bar(cut_df, x="cut", y="price", title="מחיר ממוצע לפי חיתוך")
        st.plotly_chart(fig_cut, use_container_width=True)
with right_col:
    if "color" in filtered_df.columns and "price" in filtered_df.columns:
        color_df = filtered_df[["color", "price"]].dropna().groupby("color", as_index=False)["price"].mean()
        fig_color = px.line(color_df.sort_values("color"), x="color", y="price", markers=True, title="מחיר ממוצע לפי צבע")
        st.plotly_chart(fig_color, use_container_width=True)

if "clarity" in filtered_df.columns and "price" in filtered_df.columns:
    clarity_df = filtered_df[["clarity", "price"]].dropna().groupby("clarity", as_index=False)["price"].mean()
    fig_clarity = px.bar(clarity_df, x="clarity", y="price", title="מחיר ממוצע לפי ניקיון")
    st.plotly_chart(fig_clarity, use_container_width=True)

st.markdown("### פרשנות")
st.markdown("מן הנתונים עולה כי למחיר היהלום יש קשר חיובי עם משקל בקראט. עם זאת, גם למדדי האיכות יש השפעה ניכרת על המחיר ולכן חשוב לבחון יותר ממשתנה אחד")
st.markdown("הצגה של תרשימי השוואה מסייעת להבין האם קיימים הבדלים עקביים בין קבוצות שונות של יהלומים")

st.markdown("### מגבלות המחקר")
st.markdown("הניתוח מבוסס על הדאטהסט הקיים בלבד ולכן אינו כולל בהכרח את כל הגורמים האפשריים המשפיעים על מחיר יהלומים בשוק האמיתי")
st.markdown("בנוסף, קשר בין משתנים אינו מוכיח בהכרח סיבתיות")

summary_text = """
פרויקט מחקר אנליטי - יהלומים

שאלת המחקר:
עד כמה משקל היהלום ומדדי האיכות שלו מסבירים את המחיר

ממצאים עיקריים:
1. קיים קשר חיובי בין קראט למחיר.
2. גם לחיתוך, לצבע ולניקיון יש השפעה על המחיר.
3. נדרש ניתוח רב משתני כדי לקבל תמונה מלאה יותר.

מסקנה:
מחיר היהלום מושפע ממספר משתנים במקביל ולא ממשתנה יחיד בלבד.

מקור הנתונים:
""" + str(source_name)

buffer_obj = BytesIO(summary_text.encode("utf-8"))
st.download_button("הורדת תקציר הממצאים", data=buffer_obj, file_name="diamond_research_summary.txt", mime="text/plain")
