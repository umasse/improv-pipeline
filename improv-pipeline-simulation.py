import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🎭 Improv School Course Pipeline Simulation")

st.sidebar.header("Simulation Parameters")

# User inputs
num_L1_courses = st.sidebar.slider("L1 Courses per Quarter", 1, 10, 4)
L1_capacity = st.sidebar.slider("L1 Course Capacity", 8, 20, 14)
L2_capacity = st.sidebar.slider("L2 Course Capacity", 8, 20, 12)
L3_capacity = st.sidebar.slider("L3 Course Capacity", 8, 20, 12)

retention_L1 = st.sidebar.slider("Retention: 1st to 2nd L1", 0.0, 1.0, 0.7)
retention_L1toL2 = st.sidebar.slider("Retention: L1 to L2", 0.0, 1.0, 0.7)
retention_L2 = st.sidebar.slider("Retention through L2", 0.0, 1.0, 0.8)
retention_L2toL3 = st.sidebar.slider("Retention: L2 to L3", 0.0, 1.0, 0.6)

num_quarters = st.sidebar.slider("Number of Quarters to Simulate", 1, 12, 6)
viable_min = 8
iterations = 200

# Data tracking
def simulate_pipeline():
    quarter_data = []

    for iteration in range(iterations):
        cohorts = {
            'L1_1x': [],
            'L1_2x': [],
            'L2_1x': [],
            'L2_2x': [],
            'L2_3x': [],
            'L3': []
        }
        quarter_results = []

        for q in range(1, num_quarters + 1):
            # New L1 students
            new_L1_students = num_L1_courses * L1_capacity
            L1_repeaters = np.random.binomial(new_L1_students, retention_L1)
            L1_to_L2 = np.random.binomial(L1_repeaters, retention_L1toL2)

            # L2 simulations
            L2_1x = L1_to_L2
            L2_2x = np.random.binomial(L2_1x, retention_L2)
            L2_3x = np.random.binomial(L2_2x, retention_L2)
            L3_candidates = np.random.binomial(L2_3x, retention_L2toL3)

            cohorts['L1_1x'].append(new_L1_students)
            cohorts['L1_2x'].append(L1_repeaters)
            cohorts['L2_1x'].append(L1_to_L2)
            cohorts['L2_2x'].append(L2_2x)
            cohorts['L2_3x'].append(L2_3x)
            cohorts['L3'].append(L3_candidates)

            quarter_results.append({
                'Quarter': q,
                'L1_students': new_L1_students,
                'L2_students': L1_to_L2,
                'L3_students': L3_candidates
            })

        quarter_data.append(pd.DataFrame(quarter_results))

    return pd.concat(quarter_data).groupby("Quarter").mean().reset_index(), cohorts

# Run simulation
summary_df, cohorts = simulate_pipeline()

# Display flow chart
st.subheader("📊 Average Student Flow per Quarter")
fig = px.bar(summary_df.melt(id_vars=["Quarter"], var_name="Level", value_name="Students"),
             x="Quarter", y="Students", color="Level", barmode="group",
             labels={"Quarter": "Quarter", "Students": "# of Students"},
             title="Average Number of Students per Level per Quarter")
st.plotly_chart(fig, use_container_width=True)

# Show flow table
st.subheader("📈 Detailed Average Flow Table")
st.dataframe(summary_df.style.format("{:.1f}"))

# Visualize pipeline as Sankey diagram (simplified view)
sankey_labels = ["L1 Start", "L1 Repeat", "L2 Entry", "L2 Mid", "L2 Final", "L3"]
sankey_sources = [0, 1, 2, 3, 4]
sankey_targets = [1, 2, 3, 4, 5]
sankey_values = [
    np.mean(cohorts['L1_1x']),
    np.mean(cohorts['L1_2x']),
    np.mean(cohorts['L2_1x']),
    np.mean(cohorts['L2_2x']),
    np.mean(cohorts['L3'])
]

sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=sankey_labels,
    ),
    link=dict(
        source=sankey_sources,
        target=sankey_targets,
        value=sankey_values
    ))])

sankey_fig.update_layout(title_text="Student Pipeline Flow", font_size=12)
st.subheader("🔀 Pipeline Flow Overview")
st.plotly_chart(sankey_fig, use_container_width=True)

# Recommendation
st.subheader("🧭 Recommendation")
avg_viable_L2 = summary_df['L2_students'].mean() / L2_capacity
if avg_viable_L2 >= 3:
    st.success(f"This setup supports approximately {avg_viable_L2:.1f} viable L2 courses per quarter.")
else:
    st.warning(f"Only about {avg_viable_L2:.1f} viable L2 courses per quarter. Consider increasing L1 intake or retention.")
