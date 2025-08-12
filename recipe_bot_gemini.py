import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key ="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"

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
    ["Home", "About", "How It Works", "Contact"]
)

# ----------------- Home Page -----------------
if page == "Home":
    st.title("🍽️ OpenRecipeBot")
    st.subheader("AI-powered recipe creator")
    st.caption("Powered by Mistral via OpenRouter")

    if api_key is None:
        st.error("❌ API Key not found. Please check your .env file.")
    else:
        query = st.text_input("🔍 What do you want a recipe for?", placeholder="e.g., high protein vegan lunch")
        diet = st.selectbox("🥗 Choose a diet type", ["None", "Vegan", "Keto", "Low Carb", "Diabetic", "High Protein"])
        generate = st.button("🚀 Generate Recipe")

        if generate and query:
            prompt = f"""
You are a professional chef and dietician. Generate a recipe for: {query}
Diet type: {diet if diet != "None" else "general"}

Include:
- 🍎 Ingredients
- 🍳 Cooking instructions
- 🔢 Nutritional info
- 💡 Serving tips
"""
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
1️⃣ **Describe your meal** using simple text (e.g., 'low-carb vegan dinner').

2️⃣ **Select a diet type** from the dropdown (optional).

3️⃣ Click **Generate Recipe**, and the bot will:
- Generate ingredients based on dietary needs.
- Provide step-by-step instructions.
- Estimate nutritional information.
- Share serving & preparation tips.

🏗️ The app uses **Mistral 7B via OpenRouter** for generation and **Streamlit** for a seamless interface.
    """)

# ----------------- Contact Page -----------------
elif page == "Contact":
    st.title("📬 Contact")
    st.markdown("""
For feedback, collaboration, or issues:

- 📧 Email: [likkithas68@gmail.com](mailto:youremail@example.com)

- 🌐 LinkedIn: [Likkitha S ](https://www.linkedin.com/in/yourname)

🛠️ Built with ❤️ using open-source AI.
    """)
