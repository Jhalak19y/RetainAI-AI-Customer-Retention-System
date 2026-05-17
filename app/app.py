import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import os

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RetainAI",
    page_icon="🚀",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    font-size: 17px;
    font-weight: bold;
    background-color: #2563eb;
    color: white;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<h1 style='text-align:center; color:#2563eb;'>
🚀 RetainAI
</h1>

<h4 style='text-align:center;'>
AI-Powered Customer Retention Intelligence Platform
</h4>
""", unsafe_allow_html=True)

# =====================================================
# LOAD FILES
# =====================================================

model = joblib.load('models/churn_prediction_model.pkl')

feature_columns = joblib.load(
    'models/feature_columns.pkl'
)

df = pd.read_csv('data/customer_churn.csv')

# =====================================================
# FIX CHURN COLUMN
# =====================================================

df['Churn_Numeric'] = df['Churn'].map({
    'Yes': 1,
    'No': 0
})

# =====================================================
# CREATE USERS FOLDER
# =====================================================

if not os.path.exists("users"):
    os.makedirs("users")

USER_FILE = "users/users.csv"
HISTORY_FILE = "users/history.csv"

# =====================================================
# CREATE USER FILE
# =====================================================

if not os.path.exists(USER_FILE):

    users_df = pd.DataFrame(
        columns=['username', 'password']
    )

    users_df.to_csv(USER_FILE, index=False)

# =====================================================
# CREATE HISTORY FILE
# =====================================================

if not os.path.exists(HISTORY_FILE):

    history_df = pd.DataFrame(
        columns=[
            'username',
            'tenure',
            'monthly_charges',
            'contract',
            'risk_score',
            'prediction'
        ]
    )

    history_df.to_csv(HISTORY_FILE, index=False)

# =====================================================
# SESSION STATE
# =====================================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# =====================================================
# SIDEBAR BRANDING
# =====================================================

st.sidebar.title("🚀 RetainAI")

# =====================================================
# LOGIN / SIGNUP MENU
# =====================================================

menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Signup"]
)

# =====================================================
# SIGNUP
# =====================================================

if not st.session_state.logged_in:

    if menu == "Signup":

        st.title("📝 Create Account")

        new_user = st.text_input("Username")

        new_password = st.text_input(
            "Password",
            type='password'
        )

        if st.button("Create Account"):

            users_df = pd.read_csv(USER_FILE)

            if new_user in users_df['username'].values:

                st.error("Username already exists")

            elif new_user == "" or new_password == "":

                st.warning("Please fill all fields")

            else:

                new_data = pd.DataFrame({
                    'username': [new_user],
                    'password': [new_password]
                })

                users_df = pd.concat(
                    [users_df, new_data],
                    ignore_index=True
                )

                users_df.to_csv(
                    USER_FILE,
                    index=False
                )

                st.success(
                    "Account created successfully"
                )

# =====================================================
# LOGIN
# =====================================================

    elif menu == "Login":

        st.title("🔐 Login")

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type='password'
        )

        if st.button("Login"):

            users_df = pd.read_csv(USER_FILE)

            valid_user = users_df[
                (users_df['username'] == username)
                &
                (users_df['password'] == password)
            ]

            if len(valid_user) > 0:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

# =====================================================
# MAIN DASHBOARD
# =====================================================

else:

    # =================================================
    # SIDEBAR
    # =================================================

    st.sidebar.success(
        f"Logged in as {st.session_state.username}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()

    st.sidebar.header("📌 Customer Details")

    tenure = st.sidebar.slider(
        "Tenure",
        0,
        72,
        12
    )

    monthly_charges = st.sidebar.number_input(
        "Monthly Charges",
        0.0,
        1000.0,
        70.0
    )

    total_charges = st.sidebar.number_input(
        "Total Charges",
        0.0,
        100000.0,
        1000.0
    )

    contract = st.sidebar.selectbox(
        "Contract",
        [
            "Month-to-month",
            "One year",
            "Two year"
        ]
    )

    internet_service = st.sidebar.selectbox(
        "Internet Service",
        [
            "DSL",
            "Fiber optic",
            "No"
        ]
    )

    partner = st.sidebar.selectbox(
        "Partner",
        ["Yes", "No"]
    )

    paperless_billing = st.sidebar.selectbox(
        "Paperless Billing",
        ["Yes", "No"]
    )

    # =================================================
    # KPI SECTION
    # =================================================

    st.header("📊 Business KPIs")

    total_customers = len(df)

    churned_customers = int(
        df['Churn_Numeric'].sum()
    )

    retention_rate = round(
        (1 - df['Churn_Numeric'].mean()) * 100,
        2
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Customers",
            total_customers
        )

    with col2:
        st.metric(
            "Churned Customers",
            churned_customers
        )

    with col3:
        st.metric(
            "Retention Rate",
            f"{retention_rate}%"
        )

    st.divider()

    # =================================================
    # CHARTS
    # =================================================

    st.header("📈 Analytics Dashboard")

    chart1, chart2 = st.columns(2)

    with chart1:

        pie_chart = px.pie(
            df,
            names='Churn',
            title='Customer Churn Distribution'
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True
        )

    with chart2:

        bar_chart = px.histogram(
            df,
            x='Contract',
            color='Churn',
            barmode='group',
            title='Contract Type vs Churn'
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True
        )

    box_chart = px.box(
        df,
        x='Churn',
        y='MonthlyCharges',
        color='Churn',
        title='Monthly Charges vs Churn'
    )

    st.plotly_chart(
        box_chart,
        use_container_width=True
    )

    st.divider()

    # =================================================
    # CUSTOMER PROFILE SUMMARY
    # =================================================

    st.header("📋 Customer Profile")

    p1, p2, p3 = st.columns(3)

    with p1:
        st.info(f"📅 Tenure: {tenure} Months")
        st.info(f"💳 Monthly Charges: ₹{monthly_charges}")

    with p2:
        st.info(f"📄 Contract: {contract}")
        st.info(f"🌐 Internet Service: {internet_service}")

    with p3:
        st.info(f"👥 Partner: {partner}")
        st.info(f"🧾 Paperless Billing: {paperless_billing}")

    st.divider()

    # =================================================
    # PREPARE INPUT DATA
    # =================================================

    input_data = pd.DataFrame(
        columns=feature_columns
    )

    input_data.loc[0] = 0

    # NUMERIC FEATURES

    if 'tenure' in input_data.columns:
        input_data.at[0, 'tenure'] = tenure

    if 'MonthlyCharges' in input_data.columns:
        input_data.at[
            0,
            'MonthlyCharges'
        ] = monthly_charges

    if 'TotalCharges' in input_data.columns:
        input_data.at[
            0,
            'TotalCharges'
        ] = total_charges

    # PARTNER

    if 'Partner_Yes' in input_data.columns:

        input_data.at[
            0,
            'Partner_Yes'
        ] = 1 if partner == "Yes" else 0

    # PAPERLESS BILLING

    if 'PaperlessBilling_Yes' in input_data.columns:

        input_data.at[
            0,
            'PaperlessBilling_Yes'
        ] = 1 if paperless_billing == "Yes" else 0

    # CONTRACT

    if contract == "One year":

        if 'Contract_One year' in input_data.columns:

            input_data.at[
                0,
                'Contract_One year'
            ] = 1

    elif contract == "Two year":

        if 'Contract_Two year' in input_data.columns:

            input_data.at[
                0,
                'Contract_Two year'
            ] = 1

    # INTERNET SERVICE

    if internet_service == "Fiber optic":

        if 'InternetService_Fiber optic' in input_data.columns:

            input_data.at[
                0,
                'InternetService_Fiber optic'
            ] = 1

    elif internet_service == "No":

        if 'InternetService_No' in input_data.columns:

            input_data.at[
                0,
                'InternetService_No'
            ] = 1

    # =================================================
    # AI PREDICTION
    # =================================================

    st.header("🤖 AI Churn Prediction")

    if st.button("Predict Customer Churn"):

        prediction = model.predict(
            input_data
        )

        probability = model.predict_proba(
            input_data
        )[0][1]

        risk_score = round(
            probability * 100,
            2
        )

        # =============================================
        # RISK METER
        # =============================================

        st.subheader("📊 Churn Risk Meter")

        st.progress(int(risk_score))

        st.write(
            f"## Risk Score: {risk_score}%"
        )

        # =============================================
        # RESULT
        # =============================================

        if prediction[0] == 1:

            prediction_text = "Likely to Churn"

            st.error(
                f"⚠️ Customer is likely to churn"
            )

        else:

            prediction_text = "Likely to Stay"

            st.success(
                f"✅ Customer is likely to stay"
            )

        # =============================================
        # CUSTOMER SEGMENT
        # =============================================

        if risk_score >= 75:

            st.error(
                "🔴 Critical Risk Customer"
            )

        elif risk_score >= 40:

            st.warning(
                "🟠 Medium Risk Customer"
            )

        else:

            st.success(
                "🟢 Loyal Customer"
            )

        # =============================================
        # METRICS
        # =============================================

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "Risk %",
                f"{risk_score}%"
            )

        with m2:
            st.metric(
                "Tenure",
                f"{tenure} Months"
            )

        with m3:
            st.metric(
                "Revenue",
                f"₹{monthly_charges}"
            )

        st.divider()

        # =============================================
        # AI INSIGHTS
        # =============================================

        st.subheader("🧠 AI Insights")

        insights = []

        if monthly_charges > 80:

            insights.append(
                "Customer is paying high monthly charges."
            )

        if tenure < 12:

            insights.append(
                "Customer relationship is still new."
            )

        if contract == "Month-to-month":

            insights.append(
                "Flexible contracts have higher churn."
            )

        if internet_service == "Fiber optic":

            insights.append(
                "Fiber users often churn because of competition."
            )

        if len(insights) == 0:

            insights.append(
                "Customer profile appears stable."
            )

        for item in insights:

            st.info(item)

        # =============================================
        # RECOMMENDATIONS
        # =============================================

        st.subheader("🎯 Retention Recommendations")

        if risk_score > 70:

            st.success(
                "🎁 Offer discount or loyalty rewards."
            )

            st.success(
                "📞 Customer success team should contact customer."
            )

            st.success(
                "⭐ Recommend annual subscription plan."
            )

        elif risk_score > 40:

            st.success(
                "📧 Send engagement emails."
            )

            st.success(
                "🎯 Improve customer engagement."
            )

        else:

            st.success(
                "✅ Customer retention level is healthy."
            )

        # =============================================
        # SAVE HISTORY
        # =============================================

        history_df = pd.read_csv(HISTORY_FILE)

        new_history = pd.DataFrame({

            'username': [
                st.session_state.username
            ],

            'tenure': [tenure],

            'monthly_charges': [
                monthly_charges
            ],

            'contract': [contract],

            'risk_score': [risk_score],

            'prediction': [
                prediction_text
            ]
        })

        history_df = pd.concat(
            [history_df, new_history],
            ignore_index=True
        )

        history_df.to_csv(
            HISTORY_FILE,
            index=False
        )

    st.divider()

    # =================================================
    # HISTORY SECTION
    # =================================================

    st.header("🕒 Prediction History")

    history_df = pd.read_csv(HISTORY_FILE)

    user_history = history_df[
        history_df['username']
        ==
        st.session_state.username
    ]

    if len(user_history) > 0:

        st.dataframe(
            user_history,
            use_container_width=True
        )

    else:

        st.info("No prediction history found.")

    st.divider()

    st.caption(
        "Built with ❤️ by Jhalak Yadav"
    )