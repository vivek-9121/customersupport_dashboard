import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Data Analysis App", layout="wide")

# Upload CSV
st.sidebar.header("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Display Raw Data
    st.header("📊 Raw Data")
    st.dataframe(df)

    # Filtering
    st.sidebar.header("Filter Data")
    min_salary = st.sidebar.slider("Minimum Salary", int(df['Salary'].min()), int(df['Salary'].max()), int(df['Salary'].min()))
    max_salary = st.sidebar.slider("Maximum Salary", int(df['Salary'].min()), int(df['Salary'].max()), int(df['Salary'].max()))

    filtered_df = df[(df['Salary'] >= min_salary) & (df['Salary'] <= max_salary)]

    # Display Filtered Data
    st.subheader("🔍 Filtered Data")
    st.dataframe(filtered_df)

    # Grouping and Aggregation
    st.subheader("📈 Salary by Department")
    group_df = df.groupby('Department')['Salary'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(group_df['Department'], group_df['Salary'], color='green')
    plt.xlabel("Department")
    plt.ylabel("Average Salary")
    plt.title("Average Salary by Department")
    st.pyplot(fig)

    # Sorting
    st.subheader("🔢 Sorted Data")
    sorted_df = df.sort_values(by='Salary', ascending=False)
    st.dataframe(sorted_df)

    # Exporting
    st.sidebar.header("Export Data")
    export_format = st.sidebar.selectbox("Export Format", ["CSV", "Excel"])

    if st.sidebar.button("Export"):
        if export_format == "CSV":
            filtered_df.to_csv("exported_data.csv", index=False)
            st.success("✅ Data exported as CSV!")
        elif export_format == "Excel":
            filtered_df.to_excel("exported_data.xlsx", index=False)
            st.success("✅ Data exported as Excel!")

else:
    st.info("📥 Upload a CSV file to get started.")
