import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

FILE_NAME = "loans.xlsx"

# -------------------- Initialization --------------------
def initialize_file():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "Date", "Name", "Amount", "Interest Rate (%)", "Duration (Months)",
            "Start Month", "End Month", "Total Interest", "Total Payable",
            "Documents", "Installments Received", "Remaining Balance"
        ])
        df.to_excel(FILE_NAME, index=False)

def load_data():
    return pd.read_excel(FILE_NAME)

def save_data(df):
    df.to_excel(FILE_NAME, index=False)

def calculate_interest(principal, rate, months):
    time_in_years = months / 12
    interest = (principal * rate * time_in_years) / 100
    return round(interest, 2), round(principal + interest, 2)

# -------------------- App Setup --------------------
initialize_file()
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "➕ Add Loan Record", "📚 View Records"])
st.title("💼 Finance Lending Manager")

# -------------------- Home Page --------------------
if page == "🏠 Home":
    st.header("Loan Calculator (Not Saved)")
    with st.form("calc_form"):
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Loan Duration (in Months)", min_value=1, step=1)

        calculate = st.form_submit_button("Estimate Loan")
        if calculate:
            interest, total = calculate_interest(principal, rate, months)
            st.success(f"Estimated Interest: ₹{interest}")
            st.success(f"Total Payable Amount: ₹{total}")

# -------------------- Add Loan Record Page --------------------
elif page == "➕ Add Loan Record":
    st.header("Add New Loan Record")
    with st.form("add_loan_form"):
        name = st.text_input("Borrower's Name")
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Duration (Months)", min_value=1, step=1)
        start_month = st.date_input("Loan Start Date (Month)", min_value=datetime.today())
        documents = st.text_area("Documents Submitted (e.g., Aadhaar, PAN)")

        save = st.form_submit_button("Calculate & Save Loan")

        if save:
            interest, total = calculate_interest(principal, rate, months)
            end_month = start_month + timedelta(days=30 * months)

            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name,
                "Amount": principal,
                "Interest Rate (%)": rate,
                "Duration (Months)": months,
                "Start Month": start_month.strftime("%Y-%m-%d"),
                "End Month": end_month.strftime("%Y-%m-%d"),
                "Total Interest": interest,
                "Total Payable": total,
                "Documents": documents,
                "Installments Received": 0.0,
                "Remaining Balance": total
            }

            df = load_data()
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)

            st.success("Loan record saved successfully.")
            st.info(f"Interest: ₹{interest} | Total Payable: ₹{total}")

# -------------------- View Records Page --------------------
elif page == "📚 View Records":
    st.header("All Loan Records")
    df = load_data()

    st.dataframe(df, use_container_width=True)

    st.subheader("Update Installments")
    selected_name = st.selectbox("Select Borrower", df["Name"].unique())

    borrower_df = df[df["Name"] == selected_name]
    index = borrower_df.index[0]  # Assuming one loan per person for now

    st.write(f"**Outstanding Balance:** ₹{df.loc[index, 'Remaining Balance']}")
    installment = st.number_input("Installment Received (₹)", min_value=0.0, step=100.0)

    if st.button("Record Installment"):
        df.loc[index, "Installments Received"] += installment
        df.loc[index, "Remaining Balance"] -= installment
        df.loc[index, "Remaining Balance"] = max(0.0, df.loc[index, "Remaining Balance"])  # no negative balances
        save_data(df)
        st.success("Installment recorded.")
        st.experimental_rerun()

    with st.expander("📥 Download as Excel"):
        st.download_button(
            "Download Excel",
            data=open(FILE_NAME, "rb").read(),
            file_name="loan_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
