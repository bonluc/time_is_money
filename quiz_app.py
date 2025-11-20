import streamlit as st

st.set_page_config(page_title="Entrepreneurial Finance Quiz", page_icon="💰")

# -------------------------
# SESSION STATE INIT
# -------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = []

if "equipped" not in st.session_state:
    st.session_state.equipped = None

if "page" not in st.session_state:
    st.session_state.page = "quiz"

if "index" not in st.session_state:
    st.session_state.index = 0

if "money" not in st.session_state:
    st.session_state.money = 0

if "show_result" not in st.session_state:
    st.session_state.show_result = False

if "last_correct" not in st.session_state:
    st.session_state.last_correct = False

# -------------------------
# SIDEBAR MENU (PLACE HERE!)
# -------------------------
st.sidebar.title("Menu")
st.session_state.page = st.sidebar.radio(
    "Go to:",
    ("quiz", "store", "avatar"),
    format_func=lambda x: x.capitalize()
)

# -------------------------
# QUESTIONS
# -------------------------
questions = [
    {
        "question": "What is equity financing?",
        "options": [
            "Borrowing money you must repay",
            "Selling ownership in the company",
            "A type of short-term loan"
        ],
        "answer": 1,
        "value": 500,
        "explanation": "Equity financing means selling shares of your company to raise money."
    },
    {
        "question": "What does 'burn rate' refer to?",
        "options": [
            "The rate at which the startup spends cash",
            "The valuation of the startup",
            "The growth rate of customers"
        ],
        "answer": 0,
        "value": 700,
        "explanation": "Burn rate is how quickly a startup spends cash reserves each month."
    },
    {
        "question": "What is a term sheet?",
        "options": [
            "A legal requirement for hiring employees",
            "A non-binding outline of investment terms",
            "A startup's financial statement"
        ],
        "answer": 1,
        "value": 900,
        "explanation": "A term sheet outlines the key terms of an investment deal."
    }
]

# -------------------------
# STORE ITEMS
# -------------------------
store_items = [
    {"name": "Classic Suit", "price": 800, "emoji": "🤵"},
    {"name": "Blue Business Suit", "price": 1200, "emoji": "🕴️"},
    {"name": "Fancy Investor Suit", "price": 2000, "emoji": "💼"},
    {"name": "Silicon Valley Hoodie", "price": 500, "emoji": "🧑‍💻"}
]

# -------------------------
# GAME LOGIC FUNCTIONS
# -------------------------
def check_answer(choice):
    q = questions[st.session_state.index]
    correct = q["options"].index(choice) == q["answer"]
    st.session_state.last_correct = correct

    # Calculate decreasing reward
    import time
    MAX_TIME = 20
    time_passed = time.time() - st.session_state.question_start_time
    time_left = max(0, MAX_TIME - time_passed)
    reward = int(q["value"] * (time_left / MAX_TIME))

    if correct:
        st.session_state.money += reward
        st.session_state.last_reward = reward
    else:
        st.session_state.last_reward = 0

    st.session_state.show_result = True



def next_question():
    st.session_state.index += 1
    st.session_state.show_result = False
    st.session_state.question_start_time = None   # <-- Reset timer here

    if st.session_state.index >= len(questions):
        st.session_state.index = len(questions)
        st.session_state.show_result = True



# -------------------------
# STORE PAGE (FIXED)
# -------------------------
if st.session_state.page == "store":
    st.header("🛒 Store — Buy Items for Your Avatar")

    st.write(f"Your money: **${st.session_state.money}**")

    for i, item in enumerate(store_items):
        st.subheader(f"{item['emoji']} {item['name']}")
        st.write(f"Price: ${item['price']}")

        # Already own it?
        if item["name"] in st.session_state.inventory:
            st.success("Owned ✔")

            # EQUIP button with UNIQUE KEY
            if st.button(f"Equip {item['name']}", key=f"equip_{i}"):
                st.session_state.equipped = item["name"]
                st.success(f"You equipped: {item['name']}")

        else:
            # BUY button with UNIQUE KEY
            if st.button(f"Buy {item['name']}", key=f"buy_{i}"):
                if st.session_state.money >= item["price"]:
                    st.session_state.money -= item["price"]
                    st.session_state.inventory.append(item["name"])
                    st.success(f"Purchased {item['name']}!")
                else:
                    st.error("Not enough money.")

    st.stop()

# -------------------------
# AVATAR PAGE (FIXED)
# -------------------------
if st.session_state.page == "avatar":
    st.header("🧍 Your Avatar")

    if st.session_state.equipped:
        outfit = next((i for i in store_items if i["name"] == st.session_state.equipped), None)
        st.subheader(f"Currently wearing: {st.session_state.equipped}")

        st.markdown(
            f"""
            <h1 style="text-align:center; font-size:90px;">
                {outfit['emoji']}
            </h1>
            """,
            unsafe_allow_html=True
        )
    else:
        st.subheader("You have no outfit equipped!")
        st.markdown(
            """
            <h1 style="text-align:center; font-size:90px;">
                🧍
            </h1>
            """,
            unsafe_allow_html=True
        )

    st.stop()

# -------------------------
# QUIZ PAGE
# -------------------------
if st.session_state.page == "quiz":

    import time

    st.title("💰 Entrepreneurial Finance Quiz")
    st.write("Answer questions and earn money for each correct answer!")

    # Initialize timer storage
    if "question_start_time" not in st.session_state:
        st.session_state.question_start_time = None

    if st.session_state.index < len(questions):

        q = questions[st.session_state.index]

        # Start the timer ONLY when the question appears
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()

        st.subheader(f"Question {st.session_state.index + 1}")
        st.write(q["question"])

        # TIMER CONFIG
        MAX_TIME = 20  # seconds
        time_passed = time.time() - st.session_state.question_start_time
        time_left = max(0, MAX_TIME - time_passed)

        st.progress(time_left / MAX_TIME)
        st.write(f"⏱️ Time left: {time_left:.1f} seconds")

        # Decreasing reward
        base_value = q["value"]
        time_factor = time_left / MAX_TIME
        current_value = int(base_value * time_factor)

        st.write(f"💸 Current reward: **${current_value}**")

        # Answer options
        choice = st.radio("Choose an answer:", q["options"], key=f"q_{st.session_state.index}")

        if st.button("Submit Answer"):
            check_answer(choice)

        # Show result
        if st.session_state.show_result:

            if st.session_state.last_correct:
                st.success(f"Correct! You earned ${st.session_state.last_reward}.")
            else:
                st.error("Incorrect.")

            st.info(f"📘 Explanation: {q['explanation']}")

            st.button("Next Question", on_click=next_question)

    else:
        st.header("🎉 Game Over!")
        st.subheader(f"Total money earned: **${st.session_state.money}**")

        if st.button("Play Again"):
            st.session_state.index = 0
            st.session_state.money = 0
            st.session_state.show_result = False
            st.session_state.question_start_time = None
