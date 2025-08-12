import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Page config
st.set_page_config(page_title="🍽️ OpenRecipeBot", layout="centered")

# Custom CSS for Dark Theme Styling
st.markdown("""
    <style>
    .reportview-container {
        background-color: #121212;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
        border: 1px solid #444444;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF4B4B;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF1F1F;
        transform: scale(1.02);
    }
    .sidebar .sidebar-content {
        background-color: #212121;
        color: white;
    }
    .sidebar .sidebar-content a {
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🍽️ OpenRecipeBot")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Knowledge Base", "About", "How It Works", "Contact"]
)

# Create or load history CSV
history_file = "history.csv"
if not os.path.exists(history_file):
    df_history = pd.DataFrame(columns=["Timestamp", "Query", "Diet"])
    df_history.to_csv(history_file, index=False)
else:
    df_history = pd.read_csv(history_file)

# ----------------- Home Page -----------------
if page == "Home":
    st.title("🍽️ OpenRecipeBot")
    st.subheader("AI-powered recipe creator")
    st.caption("Powered by Mistral via OpenRouter")

    if api_key is None:
        st.error("❌ API Key not found. Please check your .env file.")
    else:
        query = st.text_input("🔍 What do you want a recipe for?", placeholder="e.g., South Indian full meal")
        diet = st.selectbox("🥗 Choose a diet type", ["None", "Vegan", "Keto", "Low Carb", "Diabetic", "High Protein"])
        generate = st.button("🚀 Generate Recipe")

        if generate and query:
            # Save to knowledge base
            new_entry = pd.DataFrame({
                "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Query": [query],
                "Diet": [diet]
            })
            new_entry.to_csv(history_file, mode='a', header=False, index=False)

            # Custom prompt adjustment based on Indian meal detection
            query_lower = query.lower()
            if "south indian" in query_lower or "north indian" in query_lower or "thali" in query_lower or "full meal" in query_lower:
                prompt = f"""
You are a professional Indian chef. Create a full Indian thali for this request: "{query}"

Include:
- Starter
- 2 Main dishes (e.g., rice, chapati, curry)
- 2 Side dishes (e.g., dal, sabzi, sambar, rasam)
- 1 Chutney or pickle
- 1 Dessert
- Short description of each item
- 🍎 Ingredients
- 🍳 Cooking Instructions
- 🔢 Nutritional Information
- 💡 Serving Suggestions

Only suggest authentic regional dishes relevant to the type of thali (South or North Indian).
"""
            else:
                # General-purpose recipe generation
                prompt = f"""
You are a professional chef and dietician. Generate a recipe for: {query}
Diet type: {diet if diet != "None" else "general"}

Include:
- 🍎 Ingredients
- 🍳 Cooking instructions
- 🔢 Nutritional info
- 💡 Serving tips
"""

            # API request
            with st.spinner("Cooking up something delicious... 🍳"):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                }
                try:
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            recipe_text = result["choices"][0]["message"]["content"]
                            st.markdown("### 🧾 Here's your recipe!")
                            st.markdown(recipe_text)
                        else:
                            st.error("❌ Invalid response from the API.")
                    else:
                        st.error(f"❌ API call failed with status code {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ----------------- Knowledge Base Page -----------------
elif page == "Knowledge Base":
    st.title("📚 Knowledge Base - Search History")
    st.markdown("Filter your past recipe searches by date, diet type, or keyword.")

    df_history = pd.read_csv(history_file)
    if not df_history.empty:
        df_history["Timestamp"] = pd.to_datetime(df_history["Timestamp"])

        with st.expander("🔎 Filter your search history", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                date_min = df_history["Timestamp"].min().date()
                date_max = df_history["Timestamp"].max().date()
                start_date = st.date_input("Start Date", value=date_min, min_value=date_min, max_value=date_max)
                end_date = st.date_input("End Date", value=date_max, min_value=date_min, max_value=date_max)

            with col2:
                diet_options = ["All"] + sorted(df_history["Diet"].dropna().unique().tolist())
                selected_diet = st.selectbox("Diet Type", options=diet_options)

            with col3:
                keyword = st.text_input("Keyword in Query", placeholder="e.g., vegan")

        mask = (df_history["Timestamp"].dt.date >= start_date) & (df_history["Timestamp"].dt.date <= end_date)

        if selected_diet != "All":
            mask &= df_history["Diet"] == selected_diet

        if keyword:
            mask &= df_history["Query"].str.contains(keyword, case=False, na=False)

        filtered_df = df_history.loc[mask].sort_values(by="Timestamp", ascending=False)

        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

        csv_download = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered History as CSV",
            data=csv_download,
            file_name='filtered_recipe_history.csv',
            mime='text/csv'
        )
    else:
        st.info("Your Knowledge Base is empty. Generate some recipes to see your search history here!")

# ----------------- About Page -----------------
elif page == "About":
    st.title("📌 About OpenRecipeBot")
    st.markdown("""
**OpenRecipeBot** is your personal AI-powered recipe generator using open-source models via OpenRouter.

✨ **Features:**
- Generate recipes based on your dietary preferences.
- Get detailed nutritional information.
- AI-powered cooking instructions & serving tips.
- Uses **Mistral 7B** open-source LLM via OpenRouter API.

👩‍💻 Created and maintained by **Likkitha**.
""")

# ----------------- How It Works -----------------
elif page == "How It Works":
    st.title("🛠️ How It Works")
    st.markdown("""
1️⃣ **Describe your meal** using simple text (e.g., 'South Indian full meal').

2️⃣ **Select a diet type** from the dropdown (optional).

3️⃣ Click **Generate Recipe**, and the bot will:
- Generate multiple dishes for thalis or full meals
- Provide ingredients and cooking instructions
- Estimate nutritional information
- Share serving tips

🏗️ The app uses **Mistral 7B via OpenRouter** for generation and **Streamlit** for a seamless UI.
""")

# ----------------- Contact Page -----------------
elif page == "Contact":
    st.title("📬 Contact")
    st.markdown("""
For feedback, collaboration, or issues:

- 📧 Email: [likkithas68@gmail.com](mailto:likkithas68@gmail.com)

- 🌐 LinkedIn: [Likkitha S](https://www.linkedin.com/in/yourname)

🛠️ Built with ❤️ using open-source AI.
""")
