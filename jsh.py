import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

LOANS_FILE = "loans1.xlsx"
PAYMENTS_FILE = "payments.xlsx"

# -------------------- Setup --------------------
def initialize_files():
    if not os.path.exists(LOANS_FILE):
        df_loans1 = pd.DataFrame(columns=[
            "Loan ID", "Date", "Name", "Amount", "Interest Rate (%)", "Duration (Months)",
            "Start Date", "End Date", "Total Interest", "Total Payable", "Monthly Installment", "Documents"
        ])
        df_loans1.to_excel(LOANS_FILE, index=False)

    if not os.path.exists(PAYMENTS_FILE):
        df_payments = pd.DataFrame(columns=[
            "Loan ID", "Payment Date", "Amount Paid"
        ])
        df_payments.to_excel(PAYMENTS_FILE, index=False)

def load_loans():
    return pd.read_excel(LOANS_FILE)

def load_payments():
    return pd.read_excel(PAYMENTS_FILE)

def save_loans(df):
    df.to_excel(LOANS_FILE, index=False)

def save_payments(df):
    df.to_excel(PAYMENTS_FILE, index=False)

def calculate_interest(principal, rate, months):
    time_in_years = months
    interest = (principal * rate * time_in_years) / 100
    total_payable = principal + interest
    monthly_installment = total_payable / months
    return round(interest, 2), round(total_payable, 2), round(monthly_installment, 2)

initialize_files()

# -------------------- Streamlit Setup --------------------
st.set_page_config(page_title="Finance Lending App", layout="centered")
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "➕ Add Loan", "📚 View Loans"])

# -------------------- Home Page --------------------
if page == "🏠 Home":
    st.title("💼 Finance Lending Manager")
    st.subheader("Loan Estimator")
    with st.form("calc_form"):
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Loan Duration (Months)", min_value=1, step=1)
        calc = st.form_submit_button("Estimate")
        if calc:
            interest, total, emi = calculate_interest(principal, rate, months)
            st.success(f"Monthly Installment: ₹{emi}")
            st.success(f"Interest: ₹{interest}")
            st.success(f"Total Payable: ₹{total}")
        

# -------------------- Add Loan --------------------
elif page == "➕ Add Loan":
    st.title("Add New Loan Record")
    with st.form("add_loan_form"):
        name = st.text_input("Borrower's Name")
        principal = st.number_input("Loan Amount (₹)", min_value=0.0, step=100.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.number_input("Duration (Months)", min_value=1, step=1)
        start_date = st.date_input("Start Date", min_value=datetime.today())
        documents = st.text_area("Documents Submitted")

        interest, total, emi = calculate_interest(principal, rate, months)

        st.markdown(f"**Monthly Installment:** ₹{emi}")

        submit = st.form_submit_button("Save Loan")

        if submit:
            end_date = start_date + timedelta(days=30 * months)

            df_loans1 = load_loans()
            loan_id = f"L{len(df_loans1)+1:04d}"

            new_loan = {
                "Loan ID": loan_id,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name,
                "Amount": principal,
                "Interest Rate (%)": rate,
                "Duration (Months)": months,
                "Start Date": start_date.strftime("%Y-%m-%d"),
                "End Date": end_date.strftime("%Y-%m-%d"),
                "Total Interest": interest,
                "Total Payable": total,
                "Monthly Installment": emi,
                "Documents": documents
            }

            df_loans1 = pd.concat([df_loans1, pd.DataFrame([new_loan])], ignore_index=True)
            save_loans(df_loans1)
            st.success(f"Loan saved! Loan ID: {loan_id}")

# -------------------- View Loans --------------------
elif page == "📚 View Loans":
    st.title("Loan Records")
    df_loans1 = load_loans()
    df_payments = load_payments()

    if df_loans1.empty:
        st.warning("No loans available.")
    else:
        name_filter = st.text_input("Search by Borrower's Name")
        filtered = df_loans1[df_loans1["Name"].str.contains(name_filter, case=False, na=False)]

        if filtered.empty:
            st.info("No matching records found.")
        else:
            selected_id = st.selectbox("Select Loan ID", filtered["Loan ID"].tolist())
            selected_loan = filtered[filtered["Loan ID"] == selected_id].iloc[0]

            st.markdown(f"### Loan for {selected_loan['Name']}")
            st.write(f"**Loan ID:** {selected_loan['Loan ID']}")
            st.write(f"**Amount:** ₹{selected_loan['Amount']}")
            st.write(f"**Total Payable:** ₹{selected_loan['Total Payable']}")
            st.write(f"**Monthly Installment:** ₹{selected_loan['Monthly Installment']}")
            st.write(f"**Start:** {selected_loan['Start Date']} → **End:** {selected_loan['End Date']}")
            st.write(f"**Documents:** {selected_loan['Documents']}")

            # Payments Summary
            loan_payments = df_payments[df_payments["Loan ID"] == selected_id]
            total_paid = loan_payments["Amount Paid"].sum()
            remaining = selected_loan["Total Payable"] - total_paid

            st.subheader("💳 Payment Summary")
            st.metric("Total Paid", f"₹{total_paid}")
            st.metric("Remaining Balance", f"₹{remaining}")

            st.subheader("➕ Add Payment")
            with st.form("add_payment_form"):
                amount_paid = st.number_input("Payment Amount (₹)", min_value=0.0, step=100.0)
                pay_now = st.form_submit_button("Record Payment")
                if pay_now:
                    new_payment = {
                        "Loan ID": selected_id,
                        "Payment Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Amount Paid": amount_paid
                    }
                    df_payments = pd.concat([df_payments, pd.DataFrame([new_payment])], ignore_index=True)
                    save_payments(df_payments)
                    st.success("Payment recorded! Please refresh manually to see updated balance.")

            with st.expander("📜 Payment History"):
                st.dataframe(loan_payments, use_container_width=True)
