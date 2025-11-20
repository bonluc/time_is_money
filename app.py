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

if "category" not in st.session_state:
    st.session_state.category = None  # quiz category


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
# QUESTION CATEGORIES
# -------------------------
question_categories = {
    "Balance Sheet": [
        {
            "question": "What is a balance sheet?",
            "options": [
                "A statement of a company’s assets, liabilities, and equity",
                "A record of cash inflows and outflows",
                "A forecast of future earnings"
            ],
            "answer": 0,
            "value": 600,
            "explanation": "A balance sheet shows assets, liabilities, and equity at a specific point in time."
        },
        {
            "question": "What is an asset?",
            "options": [
                "Something the company owes",
                "Something the company owns",
                "The company’s profit"
            ],
            "answer": 1,
            "value": 500,
            "explanation": "Assets are resources the company owns that have economic value."
        },
    ],
    "Cash Flow Management": [
        {
            "question": "What does operating cash flow measure?",
            "options": [
                "Profit including non-cash expenses",
                "Cash generated from core business activities",
                "Cash spent on new investments"
            ],
            "answer": 1,
            "value": 700,
            "explanation": "Operating cash flow measures the cash produced by a company’s normal operations."
        },
        {
            "question": "Why is cash flow important?",
            "options": [
                "It shows long-term profitability",
                "It determines short-term liquidity",
                "It measures tax efficiency"
            ],
            "answer": 1,
            "value": 600,
            "explanation": "Healthy cash flow ensures the company can pay its bills and survive."
        },
    ],
}

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
# HELPERS
# -------------------------
def get_avatar_emoji():
    """Return the emoji representing the currently equipped outfit, or default avatar."""
    if st.session_state.equipped:
        for category_items in store_items.values():
            for item in category_items:
                if item["name"] == st.session_state.equipped:
                    return item["emoji"]
    return "🧍"


def get_active_questions():
    """Return the list of questions for the currently selected category."""
    if st.session_state.category is None:
        return []
    return question_categories[st.session_state.category]


# -------------------------
# GAME LOGIC FUNCTIONS
# -------------------------
def check_answer(choice):
    """Evaluate the answer, update money, and show result."""
    questions = get_active_questions()
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
    questions = get_active_questions()
    st.session_state.index += 1
    st.session_state.show_result = False
    st.session_state.has_answered = False
    st.session_state.question_start_time = None

    if st.session_state.index >= len(questions):
        st.session_state.index = len(questions)
        st.session_state.show_result = True


def reset_category():
    """Reset category selection and question progress."""
    st.session_state.category = None
    st.session_state.index = 0
    st.session_state.show_result = False
    st.session_state.question_start_time = None
    st.session_state.has_answered = False


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
                    st.info("Premium active ✅ (effect to be defined)")
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
        st.write("Basic outfit equipped. Visit the store to buy hustler clothing!")

    premium_names = [p["name"] for p in store_items["Premium"]]
    if any(item in st.session_state.inventory for item in premium_names):
        st.write("Premium status: ✅ (effects coming soon)")
    else:
        st.write("Premium status: ❌")

    st.stop()


# -------------------------
# QUIZ PAGE
# -------------------------
if st.session_state.page == "quiz":

    # -------- CATEGORY SELECTION --------
    if st.session_state.category is None:
        st.title("💰 Entrepreneurial Finance Quiz")
        st.subheader("📚 Choose a Category")

        chosen = st.radio("Select a topic to begin:", list(question_categories.keys()))

        if st.button("Start Category"):
            st.session_state.category = chosen
            st.session_state.index = 0
            st.session_state.show_result = False
            st.session_state.has_answered = False
            st.session_state.question_start_time = None

        st.stop()

    # We have a category selected from here on
    active_questions = get_active_questions()

    # Auto-refresh for live countdown (only while a question is active and no result yet)
    if st.session_state.index < len(active_questions) and not st.session_state.show_result:
        st_autorefresh(interval=200, key="quiz_refresh")

    st.title("💰 Entrepreneurial Finance Quiz")
    st.write(f"Category: **{st.session_state.category}**")
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

    if st.session_state.index < len(active_questions):

        q = active_questions[st.session_state.index]

        # Start the timer ONLY when the question appears
        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()

        st.subheader(f"Question {st.session_state.index + 1} / {len(active_questions)}")
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
        choice_key = f"q_{st.session_state.category}_{st.session_state.index}"
        choice = st.radio("Choose an answer:", q["options"], key=choice_key)

        # Manual submit
        if st.button("Submit Answer"):
            if not st.session_state.has_answered:
                check_answer(choice)

        # Auto-submit on timeout (Option A)
        if time_left <= 0 and not st.session_state.has_answered:
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
        # No more questions in this category
        st.header("🎉 Category Complete!")
        st.subheader(f"Category: **{st.session_state.category}**")
        st.subheader(f"Total capital: **${st.session_state.money}**")

        if st.button("Play This Category Again"):
            st.session_state.index = 0
            st.session_state.show_result = False
            st.session_state.question_start_time = None
            st.session_state.has_answered = False

        if st.button("Choose Another Category"):
            reset_category()
