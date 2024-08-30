import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    # Replace 'df_train.csv' with your data file
    return pd.read_csv('df_train.csv')

def remove_outliers(df, column):
    """ Remove outliers from a DataFrame based on the IQR method. """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

def main():
    st.markdown("""
        <style>
        .title {
            text-align: center;
            font-family: 'Arial', sans-serif;
            font-size: 3em;
            font-weight: bold;
            color: #a8d4f6;  /* Modern green color */
            margin-bottom: 20px;
        }
        </style>
        <div class="title">Bank Marketing Campaign</div>
    """, unsafe_allow_html=True)


    # Define color palette
    color_palette = {
        'yes': '#ff7f0e',  # Default blue color
        'no': '#65bcff'   # Default orange color
    }

    # Load data
    data = load_data()

    # Sidebar for user input
    st.sidebar.header("Adjust the details accordingly")

    # Filter by month if 'month' column exists
    if 'month' in data.columns:
        selected_month = st.sidebar.selectbox("Select a Month", data['month'].unique())
        data = data[data['month'] == selected_month]

    # Filter by prev_contacted if 'prev_contacted' column exists
    if 'prev_contacted' in data.columns:
        selected_prev_contacted = st.sidebar.selectbox("Is customer previously contacted", data['prev_contacted'].unique())
        data = data[data['prev_contacted'] == selected_prev_contacted]

    # Age range slider
    if 'age' in data.columns:
        min_age = int(data['age'].min())
        max_age = int(data['age'].max())
        age_range = st.sidebar.slider(
            "Age of the customer",
            min_value=min_age,
            max_value=max_age,
            value=(min_age, max_age)
        )
        data = data[(data['age'] >= age_range[0]) & (data['age'] <= age_range[1])]

    # Calculate the percentage of subscribed customers after filtering
    if 'subscribed' in data.columns:
        total_customers = len(data)
        subscribed_customers = data['subscribed'].value_counts().get('yes', 0)  # Count 'yes' values
        percentage_subscribed = (subscribed_customers / total_customers) * 100
    

    # Calculate mean values for duration, campaign, pdays, and previous
    mean_duration_subscribed = data[data['subscribed'] == 'yes']['duration'].mean() if 'duration' in data.columns else 'N/A'
    mean_duration_not_subscribed = data[data['subscribed'] == 'no']['duration'].mean() if 'duration' in data.columns else 'N/A'
    mean_campaign_subscribed = data[data['subscribed'] == 'yes']['campaign'].mean() if 'campaign' in data.columns else 'N/A'
    mean_campaign_not_subscribed = data[data['subscribed'] == 'no']['campaign'].mean() if 'campaign' in data.columns else 'N/A'
    mean_pdays = data['pdays'].mean() if 'pdays' in data.columns else 'N/A'
    mean_previous = data['previous'].mean() if 'previous' in data.columns else 'N/A'


    # Display mean values in cards
    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 20px;">
        <div style="background-color: #ff01cc; border-radius: 40px; padding: 20px; text-align: center; width: 500px;">
            <h4>Percentage of Term Deposite Subscribed Customers</h4>
            <h2>{percentage_subscribed:.2f} %</h2>
        </div>
        
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .subheader {
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 2.0em;
            font-weight: 700;
            color: white;  /* Gold color for a gaming look */
            margin-bottom: 6px;
            margin-top: 15px;
            letter-spacing: 2px;
            text-shadow: 2px 2px #000000;
        }
        </style>
        <div class="subheader">Demographic Profiles</div>
    """, unsafe_allow_html=True)

    # Create two columns for demographic profiles
    col1, col2 = st.columns(2)

    with col1:
        if 'age' in data.columns:


            # Age histogram
            fig_hist = px.histogram(data, x='age', nbins=30, title='Age Distribution')
            fig_hist.update_traces(marker_line_color='black', marker_line_width=1)  # Add black lines to bins
            fig_hist.update_layout(
                title={
                'text': 'Age Distribution',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                 },
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Age',
                yaxis_title='Count'
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            # Age side-by-side box plot
            fig_box = px.box(data, x='subscribed', y='age', title='Age Distribution by Subscription Status')
            fig_box.update_layout(
                 title={
                'text': 'Age Distribution by Subscription Status',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                 },
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Subscription Status',
                yaxis_title='Age'
            )
            st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        if 'job' in data.columns:
            job_counts = data.groupby(['job', 'subscribed']).size().unstack().fillna(0)
            job_percentage = job_counts.div(job_counts.sum(axis=1), axis=0) * 100
            fig_job = go.Figure()
            for col in job_percentage.columns:
                fig_job.add_trace(go.Bar(
                    x=job_percentage.index,
                    y=job_percentage[col],
                    name=col,
                    marker_color=color_palette[col]  # Use color palette
                ))
            fig_job.update_layout(
                title={
                'text': 'Job vs Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                },
                barmode='stack',
                xaxis_title='Job',
                yaxis_title='Percentage',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_job, use_container_width=True)

        if 'education' in data.columns:
            education_counts = data.groupby(['education', 'subscribed']).size().unstack().fillna(0)
            education_percentage = education_counts.div(education_counts.sum(axis=1), axis=0) * 100
            fig_education = go.Figure()
            for col in education_percentage.columns:
                fig_education.add_trace(go.Bar(
                    x=education_percentage.index,
                    y=education_percentage[col],
                    name=col,
                    marker_color=color_palette[col]  # Use color palette
                ))
            fig_education.update_layout(
                title={
                'text': 'Education Level vs Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                },
                barmode='stack',
                xaxis_title='Education Level',
                yaxis_title='Percentage',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_education, use_container_width=True)

    st.markdown("""
        <style>
        .subheader {
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 2.0em;
            font-weight: 700;
            color: white;  /* Gold color for a gaming look */
            margin-bottom: 6px;
            margin-top: 15px;
            letter-spacing: 2px;
            text-shadow: 2px 2px #000000;
        }
        </style>
        <div class="subheader">Financial Profiles</div>
    """, unsafe_allow_html=True)

    # Create two rows and two columns for financial profiles
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        if 'loan' in data.columns:
            loan_counts = data.groupby(['loan', 'subscribed']).size().unstack().fillna(0)
            loan_percentage = loan_counts.div(loan_counts.sum(axis=1), axis=0) * 100
            fig_loan = go.Figure()
            for col in loan_percentage.columns:
                fig_loan.add_trace(go.Bar(
                    x=loan_percentage.index,
                    y=loan_percentage[col],
                    name=col,
                    marker_color=color_palette[col]  # Use color palette
                ))
            fig_loan.update_layout(
                title={
                'text': 'Loan Status vs Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                },
                barmode='stack',
                xaxis_title='Loan Status',
                yaxis_title='Percentage',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_loan, use_container_width=True)

    with row1_col2:
        if 'housing' in data.columns:
            loan_counts = data.groupby(['housing', 'subscribed']).size().unstack().fillna(0)
            loan_percentage = loan_counts.div(loan_counts.sum(axis=1), axis=0) * 100
            fig_loan = go.Figure()
            for col in loan_percentage.columns:
                fig_loan.add_trace(go.Bar(
                    x=loan_percentage.index,
                    y=loan_percentage[col],
                    name=col,
                    marker_color=color_palette[col]  # Use color palette
                ))
            fig_loan.update_layout(
                title={
                'text': 'Housing Loan Status vs Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                },
                barmode='stack',
                xaxis_title='Housing Loan Status',
                yaxis_title='Percentage',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_loan, use_container_width=True)

    with row2_col1:
        if 'default' in data.columns:
            default_counts = data['default'].value_counts()
            fig_default_pie = px.pie(default_counts, names=default_counts.index, values=default_counts.values, title='Credit Card Default Status')
            color_sequence = ['#1f77b4', '#ff7f0e']  # Orange and Blue

            fig_default_pie.update_traces(
            marker=dict(colors=color_sequence)
            )
            fig_default_pie.update_layout(
                title={
                'text': 'Credit Card Default Status',
                'x': 0.4,  # Center the title
                'xanchor': 'center'
                 },
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_default_pie, use_container_width=True)

    with row2_col2:
       if 'balance' in data.columns:
            # Remove outliers from balance column
            data_cleaned = remove_outliers(data, 'balance')

            # Balance side-by-side box plot
            fig_balance = px.box(data_cleaned, x='subscribed', y='balance', title='Account Balance by Subscription')
            fig_balance.update_layout(
                title={
                'text': 'ccount Balance by Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                 },
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Subscription Status',
                yaxis_title='Balance'
            )
            st.plotly_chart(fig_balance, use_container_width=True)

    st.markdown("""
        <style>
        .subheader {
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 2.0em;
            font-weight: 700;
            color: white;  /* Gold color for a gaming look */
            margin-bottom: 6px;
            margin-top: 15px;
            letter-spacing: 2px;
            text-shadow: 2px 2px #000000;
        }
        </style>
        <div class="subheader">Campaign Details</div>
    """, unsafe_allow_html=True)


    # Create two columns for campaign details
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        if 'contact' in data.columns:
            contact_counts = data.groupby(['contact', 'subscribed']).size().unstack().fillna(0)
            contact_percentage = contact_counts.div(contact_counts.sum(axis=1), axis=0) * 100
            fig_contact = go.Figure()
            for col in contact_percentage.columns:
                fig_contact.add_trace(go.Bar(
                    x=contact_percentage.index,
                    y=contact_percentage[col],
                    name=col,
                    marker_color=color_palette[col]  # Use color palette
                ))
            fig_contact.update_layout(
                title={
                'text': 'Contacted Method vs Subscription',
                'x': 0.5,  # Center the title
                'xanchor': 'center'
                },
                barmode='stack',
                xaxis_title='Contacted Method',
                yaxis_title='Percentage',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_contact, use_container_width=True)

    with row1_col2:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 20px;margin-top: 40px;">
            <div style="background-color: #1f77b4; border-radius: 20px; padding: 20px; text-align: center; width: 200px;">
                <h4>Average Last Call Duration </h4>
                <p><strong>Subscribed:</strong></p>
                <p>{mean_duration_subscribed:.2f} minutes</p>
                <p><strong>Not Subscribed:</strong></p>
                <p>{mean_duration_not_subscribed:.2f} minutes</p>
            </div>
            <div style="background-color: #1f77b4; border-radius: 20px; padding: 20px; text-align: center; width: 200px;">
                <h4>Average Times Contacted</h4>
                <p><strong>Subscribed:</strong></p>
                <p>{mean_campaign_subscribed:.2f} times</p>
                <p><strong>Not Subscribed:</strong></p>
               <p>{mean_campaign_not_subscribed:.2f} times</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
        

    if selected_prev_contacted == 'yes':
        st.markdown("""
        <style>
        .subheader {
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 2.0em;
            font-weight: 700;
            color: white;  /* Gold color for a gaming look */
            margin-bottom: 6px;
            margin-top: 15px;
            letter-spacing: 2px;
            text-shadow: 2px 2px #000000;
        }
        </style>
        <div class="subheader">Previous Campaign Details</div>
    """, unsafe_allow_html=True)

        # Create two columns for campaign details
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            if 'poutcome' in data.columns:
                contact_counts = data.groupby(['poutcome', 'subscribed']).size().unstack().fillna(0)
                contact_percentage = contact_counts.div(contact_counts.sum(axis=1), axis=0) * 100
                fig_contact = go.Figure()
                for col in contact_percentage.columns:
                    fig_contact.add_trace(go.Bar(
                        x=contact_percentage.index,
                        y=contact_percentage[col],
                        name=col,
                        marker_color=color_palette[col]  # Use color palette
                    ))
                fig_contact.update_layout(
                    title={
                    'text': 'Result of Previous Campaign vs Subscription',
                    'x': 0.5,  # Center the title
                    'xanchor': 'center'
                    },
                    barmode='stack',
                    xaxis_title='Result of Previous Campaign',
                    yaxis_title='Percentage',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_contact, use_container_width=True)

        with row1_col2:
         st.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 20px;margin-top: 40px;">
                <div style="background-color: #1f77b4; border-radius: 20px; padding: 20px; text-align: center; width: 200px;">
                    <h4>Average Times Previously Contacted</h4>
                    <h2>{mean_previous:.2f} days</h2>
                </div>
                <div style="background-color: #1f77b4; border-radius: 20px; padding: 20px; text-align: center; width: 200px;">
                    <h4>Average Days form Lastly Contacted</h4>
                    <h2>{mean_pdays:.2f} times</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
