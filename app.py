import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import calendar

st.set_page_config(page_title="KPI Planner", layout="wide")

DATA_FILE = "data.csv"

# =====================
# LOAD / INIT DATA
# =====================
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=[
            "KPI", "Activity", "Deadline", "PIC", "Status", "Last Updated"
        ])
        df.to_csv(DATA_FILE, index=False)

    # SAFE datetime parsing (FIX ERROR KAMU)
    df["Deadline"] = pd.to_datetime(
        df["Deadline"],
        format="mixed",
        errors="coerce"
    ).dt.date

    df["Last Updated"] = pd.to_datetime(
        df["Last Updated"],
        format="mixed",
        errors="coerce"
    )

    return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


df = load_data()

# =====================
# SIDEBAR
# =====================
page = st.sidebar.radio("Menu", ["➕ Input Activity", "📅 Calendar View"])

PIC_LIST = ["Andi", "Windy", "Eta", "Intern"]

# =====================
# PAGE 1 — INPUT
# =====================
if page == "➕ Input Activity":
    st.title("➕ Input KPI & Activity")

    with st.form("input_form"):
        kpi = st.text_input("KPI")
        activity = st.text_input("Activity / Sub-KPI")
        deadline = st.date_input("Deadline", min_value=date.today())
        pic = st.selectbox("PIC", PIC_LIST)

        submitted = st.form_submit_button("Save")

        if submitted:
            new_row = {
                "KPI": kpi,
                "Activity": activity,
                "Deadline": deadline,
                "PIC": pic,
                "Status": "Open",
                "Last Updated": None
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Activity berhasil disimpan ✅")

    st.divider()
    st.subheader("📋 Data Saat Ini")
    st.dataframe(df, use_container_width=True)


# =====================
# PAGE 2 — CALENDAR
# =====================
elif page == "📅 Calendar View":
    st.title("📅 Calendar View")

    today = date.today()
    year = st.selectbox("Year", range(today.year - 1, today.year + 2), index=1)
    month = st.selectbox("Month", range(1, 13), index=today.month - 1)

    cal = calendar.monthcalendar(year, month)

    st.markdown(
        """
        <style>
        .day-box {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 8px;
            height: 180px;
            overflow-y: auto;
        }
        .activity {
            background-color: #f4f6f8;
            padding: 6px;
            border-radius: 6px;
            margin-top: 6px;
            font-size: 13px;
        }
        .done {
            background-color: #d4f8d4;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, d in enumerate(days):
        cols[i].markdown(f"**{d}**")

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    current_date = date(year, month, day)
                    st.markdown(f"<div class='day-box'><b>{day}</b>", unsafe_allow_html=True)

                    day_tasks = df[df["Deadline"] == current_date]

                    for idx, row in day_tasks.iterrows():
                        is_done = row["Status"] == "Done"
                        css_class = "activity done" if is_done else "activity"

                        st.markdown(
                            f"""
                            <div class="{css_class}">
                                <b>{row['Activity']}</b><br>
                                {row['PIC']} | {row['Status']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if not is_done:
                            if st.button("Mark Done", key=f"done_{idx}"):
                                df.loc[idx, "Status"] = "Done"
                                df.loc[idx, "Last Updated"] = datetime.now()
                                save_data(df)
                                st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)
