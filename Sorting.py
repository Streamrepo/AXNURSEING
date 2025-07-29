import streamlit as st
import pandas as pd

st.title("Dynamic Multi-Sheet Excel Filter & Analysis Tool")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file with yearly or partial sheets", type=["xlsx"])

if uploaded_file:
    # Load all sheets
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)

    # Combine all sheets into one DataFrame, with sheet name as 'Period'
    df_list = []
    for sheet_name, df in all_sheets.items():
        df["Period"] = str(sheet_name)
        df_list.append(df)

    full_df = pd.concat(df_list, ignore_index=True)

    # Check for required columns
    required_cols = [
        "NameDimensiontype",
        "NameReportingstructuregroup2",
        "NameReportingstructuregroup4",
        "NameReportingstructuregroup6",
        "NameGeneralledgeraccount"
    ]
    missing_cols = [col for col in required_cols if col not in full_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        for col in required_cols:
            if col not in full_df.columns:
                full_df[col] = None 

        st.success(f"✅ Loaded data from {len(all_sheets)} sheets: {list(all_sheets.keys())}")

        # === HIERARCHICAL FILTERS (Auto-adapt to data) ===
        st.subheader("Apply Filters (Hierarchical)")

        filter_df = full_df.copy()

       def cascading_filter(df, col, label):
           options = sorted(df[col].dropna().unique())
           if not options:
               return df
           choice = st.selectbox(label, ["All"] + options)
           return df if choice == "All" else df[df[col] == choice]

        filter_df = cascading_filter(filter_df, "NameDimensiontype", "Select NameDimensiontype")
        filter_df = cascading_filter(filter_df, "NameReportingstructuregroup2", "Select NameReportingstructuregroup2")
        filter_df = cascading_filter(filter_df, "NameReportingstructuregroup4", "Select NameReportingstructuregroup4")
        filter_df = cascading_filter(filter_df, "NameReportingstructuregroup6", "Select NameReportingstructuregroup6")
        filter_df = cascading_filter(filter_df, "NameGeneralledgeraccount", "Select NameGeneralledgeraccount")

        # === Show Filtered Data ===
        st.write("### Filtered Data (All Periods)")
        st.dataframe(filter_df)

        # === Summary Section ===
        if "Value" in filter_df.columns:
            st.subheader("Period Summary of 'Value'")
            summary_df = (
                filter_df.groupby("Period")["Value"]
                .sum()
                .reset_index()
                .sort_values("Period")
            )
            st.dataframe(summary_df)
            st.line_chart(summary_df.set_index("Period"))

