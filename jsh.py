
import streamlit as st
import pandas as pd
from datetime import datetime
import os

FILE_NAME = "loans.xlsx"

# Initialize storage
def initialize_file():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "Date", "Name", "Amount", "Interest Rate (%)", "Duration (Months)",
            "Total Interest", "Total Payable", "Documents"
        ])
        df.to_excel(FILE_NAME, index=False)

def load_data():
    return pd.read_excel(FILE_NAME)

def save_data(df):
    df.to_excel(FILE_NAME, index=False)

def calculate_interest(principal, rate, months):
    interest = (principal * rate * months) / 100
    return round(interest, 2), round(principal + interest, 2), round((principal + interest) / months, 2)

# Initialize file
initialize_file()

# Sidebar Navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "➕ Add Loan Record", "📚 View Records"])

st.title("💼 J.S.H. Finance Co.")

# Home Page
if page == "🏠 Home":
    st.header("Loan Calculator (Not Saved)")

    with st.form("calc_form"):
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Loan Duration (in Months)", min_value=1, step=1)

        calculate = st.form_submit_button("Estimate Loan")

        if calculate:
            interest, total, installment = calculate_interest(principal, rate, months)
            st.success(f"Estimated Interest: ₹{interest}")
            st.success(f"Total Payable Amount: ₹{total}")
            st.success(f"MOnthly Payable: ₹{installment}")

# Add Loan Page
elif page == "➕ Add Loan Record":
    st.header("Add New Loan Record")

    with st.form("add_loan_form"):
        name = st.text_input("Borrower's Name")
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Duration (Months)", min_value=1, step=1)
        documents = st.text_area("Documents Submitted (e.g., Aadhaar, PAN)")

        save = st.form_submit_button("Calculate & Save Loan")

        if save:
            interest, total, installment = calculate_interest(principal, rate, months)

            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name,
                "Amount": principal,
                "Interest Rate (%)": rate,
                "Duration (Months)": months,
                "Total Interest": interest,
                "Total Payable": total,
                "Installment": installment,
                "Documents": documents
            }

            df = load_data()
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)

            st.success("Loan record saved successfully.")
            st.info(f"Interest: ₹{interest} | Total Payable: ₹{total} | Monthly Payable: ₹{installment}")

# View Records Page
elif page == "📚 View Records":
    st.header("All Loan Records")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    with st.expander("📥 Download as Excel"):
        st.download_button(
            "Download Excel",
            data=open(FILE_NAME, "rb").read(),
            file_name="loan_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
