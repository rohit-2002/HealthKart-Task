import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HealthKart Influencer Dashboard", layout="wide")
st.title("📈 HealthKart Influencer Campaign Dashboard")

# Sample fallback data
def sample_data():
    influencer_data = pd.DataFrame({
        "id": ["IK_01", "IK_02", "IK_03", "IK_04", "IK_05"],
        "influencer_name": ["Riya", "Aman", "Tara", "Kunal", "Neha"],
        "platform": ["Instagram", "YouTube", "Instagram", "Instagram", "YouTube"],
        "niche": ["Nutrition", "Fitness", "Lifestyle", "Nutrition", "Fitness"],
        "followers": [15000, 50000, 25000, 30000, 40000],
        "gender": ["F", "M", "F", "M", "F"]
    })

    posts_data = pd.DataFrame({
        "influencer_id": ["IK_01", "IK_02", "IK_03", "IK_04", "IK_05"] * 2,
        "platform": ["Instagram", "YouTube", "Instagram", "Instagram", "YouTube"] * 2,
        "date": pd.date_range("2024-01-01", periods=10),
        "url": [f"https://post/{i}" for i in range(10)],
        "caption": ["Great product!" for _ in range(10)],
        "reach": [13000, 21000, 15000, 20000, 18000, 14500, 22000, 16000, 24000, 17500],
        "likes": [1200, 1800, 1400, 2000, 1600, 1250, 1900, 1500, 2100, 1650],
        "comments": [75, 120, 90, 150, 100, 80, 130, 95, 160, 110]
    })

    tracking_data = pd.DataFrame({
        "source": ["Instagram", "YouTube", "Instagram", "Instagram", "YouTube"],
        "campaign": ["MB01", "GZ01", "HK01", "GZ02", "MB02"],
        "influencer_id": ["IK_01", "IK_02", "IK_03", "IK_04", "IK_05"],
        "user_id": [101, 102, 103, 104, 105],
        "product": ["Whey", "Shake", "Zinc", "Gainer", "Whey"],
        "date": pd.date_range("2024-03-01", periods=5),
        "orders": [40, 10, 15, 30, 31],
        "revenue": [25000, 1890, 7200, 37800, 42000]
    })

    campaign_data = tracking_data.copy()
    campaign_data["brand"] = ["MuscleBlaze", "Gritzo", "HK Vitals", "Gritzo", "MuscleBlaze"]
    campaign_data["cost"] = [6500, 5000, 3000, 5200, 8000]

    payouts_data = pd.DataFrame({
        "influencer_id": ["IK_01", "IK_02", "IK_03", "IK_04", "IK_05"],
        "basis": ["order", "post", "order", "order", "post"],
        "rate": [500, 2000, 400, 300, 1800],
        "orders": [40, 2, 15, 30, 2]
    })
    payouts_data["total_payout"] = payouts_data.apply(
        lambda row: row["rate"] * (row["orders"] if row["basis"] == "order" else 1), axis=1
    )

    return influencer_data, posts_data, campaign_data, payouts_data

# Load from uploads or use sample data
def load_uploaded_or_sample_data():
    st.sidebar.header("📁 Upload CSV Data (Optional)")
    up_inf = st.sidebar.file_uploader("Influencers CSV", type="csv")
    up_post = st.sidebar.file_uploader("Posts CSV", type="csv")
    up_camp = st.sidebar.file_uploader("Campaigns CSV", type="csv")
    up_pay = st.sidebar.file_uploader("Payouts CSV", type="csv")

    if all([up_inf, up_post, up_camp, up_pay]):
        try:
            df_influencers = pd.read_csv(up_inf)
            df_posts = pd.read_csv(up_post, parse_dates=["date"])
            df_campaigns = pd.read_csv(up_camp, parse_dates=["date"])
            df_payouts = pd.read_csv(up_pay)
            df_campaigns["roi"] = df_campaigns["revenue"] / df_campaigns["cost"]
            df_campaigns["roas"] = df_campaigns["revenue"] / (df_campaigns["cost"] + 1)
            df_payouts["total_payout"] = df_payouts.apply(
                lambda row: row["rate"] * (row["orders"] if row["basis"] == "order" else 1), axis=1
            )
            return df_influencers, df_posts, df_campaigns, df_payouts
        except Exception as e:
            st.sidebar.error(f"Upload error: {e}. Loading sample data instead.")
            return sample_data()
    else:
        return sample_data()

# Load data
df_influencers, df_posts, df_campaigns, df_payouts = load_uploaded_or_sample_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Data")
    selected_platforms = st.multiselect("Select Platform(s)", df_influencers["platform"].unique(), default=df_influencers["platform"].unique())
    selected_niches = st.multiselect("Select Niche(s)", df_influencers["niche"].unique(), default=df_influencers["niche"].unique())

filtered_influencers = df_influencers[
    df_influencers["platform"].isin(selected_platforms) & df_influencers["niche"].isin(selected_niches)
]

# Merge for campaign-level analysis
merged = df_campaigns.merge(filtered_influencers, left_on="influencer_id", right_on="id")
merged["roi"] = merged["revenue"] / merged["cost"]
merged["roas"] = merged["revenue"] / (merged["cost"] + 1)

# Extra filters for brand/product
st.sidebar.markdown("---")
selected_brands = st.sidebar.multiselect("Brand", merged["brand"].unique(), merged["brand"].unique())
selected_products = st.sidebar.multiselect("Product", merged["product"].unique(), merged["product"].unique())
merged = merged[merged["brand"].isin(selected_brands) & merged["product"].isin(selected_products)]

# KPIs
st.subheader("🔢 Campaign KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", int(merged["orders"].sum()))
col2.metric("Total Revenue", f"₹{merged['revenue'].sum():,}")
col3.metric("Avg ROI", f"{merged['roi'].mean():.2f}x")

# Leaderboard
st.subheader("🏆 Influencer Leaderboard")
leaderboard = merged.groupby(["influencer_id", "influencer_name", "platform"]).agg(
    total_orders=("orders", "sum"),
    total_revenue=("revenue", "sum"),
    total_cost=("cost", "sum"),
    avg_roi=("roi", "mean")
).reset_index().sort_values(by="avg_roi", ascending=False)
st.dataframe(leaderboard)

# Brand Summary
st.subheader("📦 Brand Summary")
brand_summary = merged.groupby("brand").agg(
    total_orders=("orders", "sum"),
    total_revenue=("revenue", "sum"),
    avg_revenue_per_order=("revenue", lambda x: x.sum() / x.count())
).reset_index()
st.dataframe(brand_summary)

# Post Performance
st.subheader("📸 Post Performance")
if not filtered_influencers.empty:
    post_perf = df_posts[df_posts["influencer_id"].isin(filtered_influencers["id"])].groupby("influencer_id").agg(
        avg_reach=("reach", "mean"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean")
    ).reset_index().merge(filtered_influencers, left_on="influencer_id", right_on="id")
    st.dataframe(post_perf[["influencer_name", "platform", "avg_reach", "avg_likes", "avg_comments"]])
else:
    st.warning("No influencers match the selected filters.")

# ROAS Chart
st.subheader("📊 ROAS vs Followers")
fig = px.scatter(
    merged, x="followers", y="roas", size="roas", color="platform",
    hover_name="influencer_name", title="Influencer Size vs ROAS", size_max=25
)
st.plotly_chart(fig, use_container_width=True)

# Payouts
st.subheader("💰 Payout Tracking")
payout_merged = df_payouts.merge(df_influencers, left_on="influencer_id", right_on="id")
st.dataframe(payout_merged[["influencer_name", "platform", "basis", "rate", "orders", "total_payout"]])

# Export Buttons
st.subheader("📤 Export CSV")
col1, col2 = st.columns(2)
col1.download_button("Download Leaderboard CSV", leaderboard.to_csv(index=False), "leaderboard.csv", "text/csv")
col2.download_button("Download Payouts CSV", payout_merged.to_csv(index=False), "payouts.csv", "text/csv")

# Insights
st.markdown("### 📄 Insights Summary")
st.markdown("""
- **Top ROI Influencer**: Based on the leaderboard  
- **Lowest Performing Brand**: Check brand summary avg revenue  
- **Instagram** shows stronger ROAS trend  
- **Nutrition influencers** show better average results  
""")

st.markdown("---")
st.markdown("🚀 Built for HealthKart | 📂 [GitHub Repo](https://github.com/rohit-2002/HealthKart-Task.git)")
