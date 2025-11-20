import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Entrepreneurial Finance Quiz", page_icon="💰")

# -------------------------
# CONSTANTS
# -------------------------
MAX_TIME = 20  # seconds per question
WRONG_PENALTY_FACTOR = 0.5  # lose 50% of base value on wrong answer


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

if "last_reward" not in st.session_state:
    st.session_state.last_reward = 0

if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None

if "has_answered" not in st.session_state:
    st.session_state.has_answered = False

# -------------------------
# SIDEBAR MENU
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
# STORE ITEMS (with Premium)
# -------------------------
store_items = {
    "Outfits": [
        {"name": "Classic Suit", "price": 800, "emoji": "🤵"},
        {"name": "Blue Business Suit", "price": 1200, "emoji": "🕴️"},
        {"name": "Fancy Investor Suit", "price": 2000, "emoji": "💼"},
        {"name": "Silicon Valley Hoodie", "price": 500, "emoji": "🧑‍💻"},
    ],
    "Premium": [
        {"name": "Linked Premium Badge", "price": 5000, "emoji": "🔗"},
        {"name": "Premium Investor Access", "price": 10000, "emoji": "🏛️"},
    ],
}


# -------------------------
# HELPER: Get avatar emoji
# -------------------------
def get_avatar_emoji():
    if st.session_state.equipped:
        for category_items in store_items.values():
            for item in category_items:
                if item["name"] == st.session_state.equipped:
                    return item["emoji"]
    return "🧍"


# -------------------------
# GAME LOGIC FUNCTIONS
# -------------------------
def check_answer(choice):
    """Evaluate the answer, update money, and show result."""
    q = questions[st.session_state.index]
    options = q["options"]

    # Determine correctness safely
    if choice is None or choice not in options:
        correct = False
    else:
        correct = (options.index(choice) == q["answer"])

    st.session_state.last_correct = correct

    # Time-based reward
    if st.session_state.question_start_time is None:
        time_left = 0
    else:
        time_passed = time.time() - st.session_state.question_start_time
        time_left = max(0, MAX_TIME - time_passed)

    base_value = q["value"]
    reward_if_correct = int(base_value * (time_left / MAX_TIME))

    if correct:
        # Gain time-scaled reward
        st.session_state.money += reward_if_correct
        st.session_state.last_reward = reward_if_correct
    else:
        # Lose money on wrong answer (fixed fraction of base value)
        penalty = int(base_value * WRONG_PENALTY_FACTOR)
        st.session_state.money -= penalty
        st.session_state.last_reward = -penalty

    st.session_state.show_result = True
    st.session_state.has_answered = True


def next_question():
    """Move to the next question and reset per-question state."""
    st.session_state.index += 1
    st.session_state.show_result = False
    st.session_state.has_answered = False
    st.session_state.question_start_time = None

    if st.session_state.index >= len(questions):
        st.session_state.index = len(questions)
        st.session_state.show_result = True


# -------------------------
# STORE PAGE
# -------------------------
if st.session_state.page == "store":
    st.header("🛒 Store — Buy Items for Your Avatar & Premium")

    st.write(f"Your capital: **${st.session_state.money}**")

    for category, items in store_items.items():
        st.subheader(f"📂 {category}")
        for i, item in enumerate(items):
            st.markdown(f"**{item['emoji']} {item['name']}**")
            st.write(f"Price: ${item['price']}")

            owned = item["name"] in st.session_state.inventory

            if owned:
                st.success("Owned ✔")
                if category == "Outfits":
                    if st.button(f"Equip {item['name']}", key=f"equip_{category}_{i}"):
                        st.session_state.equipped = item["name"]
                        st.success(f"You equipped: {item['name']}")
                else:
                    st.info("Premium active ✅")
            else:
                if st.button(f"Buy {item['name']}", key=f"buy_{category}_{i}"):
                    if st.session_state.money >= item["price"]:
                        st.session_state.money -= item["price"]
                        st.session_state.inventory.append(item["name"])
                        st.success(f"Purchased {item['name']}!")
                    else:
                        st.error("Not enough capital to buy this.")

    st.stop()


# -------------------------
# AVATAR PAGE
# -------------------------
if st.session_state.page == "avatar":
    st.header("🧍 Your Avatar")

    avatar_emoji = get_avatar_emoji()
    st.markdown(
        f"""
        <h1 style="text-align:center; font-size:90px;">
            {avatar_emoji}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.subheader(f"Total capital: ${st.session_state.money}")

    if st.session_state.equipped:
        st.write(f"Currently wearing: **{st.session_state.equipped}**")
    else:
        st.write("No outfit equipped yet. Visit the store to buy one!")

    if any(item in st.session_state.inventory for item in [p["name"] for p in store_items["Premium"]]):
        st.write("Premium status: ✅ (effect to be defined)")
    else:
        st.write("Premium status: ❌")

    st.stop()


# -------------------------
# QUIZ PAGE
# -------------------------
if st.session_state.page == "quiz":

    # Auto-refresh for live countdown (only while question is active and not answered)
    if st.session_state.index < len(questions) and not st.session_state.show_result:
        st_autorefresh(interval=200, key="quiz_refresh")

    st.title("💰 Entrepreneurial Finance Quiz")
    st.write("Answer questions before time runs out. Correct answers earn money, wrong answers lose money!")

    # Status bar: avatar + capital
    avatar_emoji = get_avatar_emoji()
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
            <span style="font-size:40px;">{avatar_emoji}</span>
            <span style="font-size:20px;">Capital: <b>${st.session_state.money}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize timer storage (already in session init, but safe)
    if "question_start_time" not in st.session_state:
        st.session_state.question_start_time = None

    if st.session_state.index < len(questions):

        q = questions[st.session_state.index]

        # Start the timer ONLY when the question appears
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()

        st.subheader(f"Question {st.session_state.index + 1}")
        st.write(q["question"])

        # TIMER
        time_passed = time.time() - st.session_state.question_start_time
        time_left = max(0, MAX_TIME - time_passed)

        st.progress(time_left / MAX_TIME)
        st.write(f"⏱️ Time left: {time_left:.1f} seconds")

        # Decreasing reward for *correct* answer (preview)
        base_value = q["value"]
        time_factor = time_left / MAX_TIME
        current_value = int(base_value * time_factor)
        st.write(f"💸 Current reward for a correct answer (if you answer now): **${current_value}**")
        st.write(f"❌ Wrong answer penalty: **-${int(base_value * WRONG_PENALTY_FACTOR)}**")

        # Answer options
        choice_key = f"q_{st.session_state.index}"
        choice = st.radio("Choose an answer:", q["options"], key=choice_key)

        # Manual submit
        if st.button("Submit Answer"):
            if not st.session_state.has_answered:
                check_answer(choice)

        # Auto-submit on timeout (Option A)
        if time_left <= 0 and not st.session_state.has_answered:
            # Use whatever is currently selected; if nothing, treated as incorrect
            current_choice = st.session_state.get(choice_key, None)
            check_answer(current_choice)

        # Show result
        if st.session_state.show_result:
            if st.session_state.last_correct:
                st.success(f"Correct! You earned ${st.session_state.last_reward}.")
            else:
                st.error(f"Incorrect. You lost ${-st.session_state.last_reward}.")

            st.info(f"📘 Explanation: {q['explanation']}")

            st.button("Next Question", on_click=next_question)

    else:
        st.header("🎉 Game Over!")
        st.subheader(f"Total capital: **${st.session_state.money}**")

        if st.button("Play Again"):
            st.session_state.index = 0
            st.session_state.money = 0
            st.session_state.show_result = False
            st.session_state.question_start_time = None
            st.session_state.has_answered = False
