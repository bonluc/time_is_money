import time
import os
import csv
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Entrepreneurial Finance Quiz", page_icon="💰")

# -------------------------
# CONSTANTS
# -------------------------
MAX_TIME = 20  # seconds per question
WRONG_PENALTY_FACTOR = 0.3  # lose 30% of base value on wrong answer
LEADERBOARD_FILE = "leaderboard.csv"


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

if "username" not in st.session_state:
    st.session_state.username = None

if "saved_this_round" not in st.session_state:
    st.session_state.saved_this_round = False


# -------------------------
# SIDEBAR MENU
# -------------------------
st.sidebar.title("Menu")
st.session_state.page = st.sidebar.radio(
    "Go to:",
    ("quiz", "store", "avatar", "leaderboard"),
    format_func=lambda x: x.capitalize()
)

# ---------------------------
# USERNAME LOGIN SCREEN
# ---------------------------
if st.session_state.username is None:
    st.title("🎮 Welcome to Time is Money!")
    st.subheader("Please enter your player name to begin")

    name_input = st.text_input("Your player name:")

    if st.button("Continue"):
        if name_input.strip() != "":
            chosen_name = name_input.strip()

            # Ensure unique name by checking leaderboard.csv
            if os.path.exists(LEADERBOARD_FILE):
                df = pd.read_csv(LEADERBOARD_FILE)
                existing = df["username"].tolist()
            else:
                existing = []

            # Generate increment if necessary
            base = chosen_name
            suffix = 1
            while chosen_name in existing:
                chosen_name = f"{base} ({suffix})"
                suffix += 1

            st.session_state.username = chosen_name
            st.success(f"Welcome, {chosen_name}!")
            #st.experimental_rerun()
            st.rerun()


    st.stop()

# -------------------------
# QUESTION CATEGORIES
# -------------------------
question_categories = {
    "Balance Sheet": [
        {
            "question": "What is the accounting equation?",
            "options": [
                "Assets = Revenue + Expenses",
                "Assets = Liabilities + Equity",
                "Liabilities = Assets + Equity",
                "Equity = Assets * Liabilities",
            ],
            # Correct: Assets = Liabilities + Equity -> index 1
            "answer": 1,
            "value": 600,
            "explanation": (
                "The accounting equation is Assets = Liabilities + Equity. "
                "Assets are what the business owns, funded by liabilities (what it owes) "
                "and equity (the owners' claim on the assets)."
            ),
        },
        {
            "question": "What are the main sections of a balance sheet?",
            "options": [
                "Revenue, Expenses, Profit",
                "Assets, Liabilities, Equity",
                "Cash Flow, Income, Expenses",
                "Investments, Dividends, Retained Earnings",
            ],
            # Correct: Assets, Liabilities, Equity -> index 1
            "answer": 1,
            "value": 500,
            "explanation": (
                "A balance sheet is split into Assets, Liabilities, and Equity, "
                "reflecting the accounting equation."
            ),
        },
        {
            "question": "Given total assets of 500.000 and total liabilities of 350.000, what is owner's equity?",
            "options": [
                "850.000",
                "350.000",
                "150.000",
                "500.000",
            ],
            # Equity = Assets - Liabilities = 150.000 -> index 2
            "answer": 2,
            "value": 500,
            "explanation": (
                "Using Assets = Liabilities + Equity, rearrange to Equity = Assets − Liabilities: "
                "500.000 − 350.000 = 150.000."
            ),
        },
    ],
    "Cash Flow Management": [
        {
            "question": "What is the primary purpose of a cash flow statement?",
            "options": [
                "To determine employee productivity",
                "To monitor the inflow and outflow of cash",
                "To track inventory levels",
                "To calculate net profit",
            ],
            # Correct: monitor inflow/outflow of cash -> index 1
            "answer": 1,
            "value": 700,
            "explanation": "A cash flow statement tracks how cash moves in and out of the business.",
        },
        {
            "question": "Which financial metric helps assess a startup’s ability to meet short-term obligations?",
            "options": [
                "Current Ratio",
                "Debt-to-equity ratio",
                "Gross margin",
                "Return on investment (ROI)",
            ],
            # Correct: Current Ratio -> index 0
            "answer": 0,
            "value": 600,
            "explanation": "The current ratio compares current assets to current liabilities.",
        },
        {
            "question": "Operating cash flow differs from free cash flow because free cash flow:",
            "options": [
                "Excludes depreciation",
                "Includes capital expenditures deducted",
                "Does not account for working capital changes",
                "Measures revenue only",
            ],
            # Correct: includes capex deducted -> index 1
            "answer": 1,
            "value": 600,
            "explanation": (
                "Free cash flow = Operating cash flow − Capital expenditures, "
                "showing cash available to grow the business or return to investors."
            ),
        },
    ],
    "Startup Finance": [
        {
            "question": "Which of the following is a common source of early-stage funding for startups?",
            "options": [
                "Corporate bonds",
                "Angel investors",
                "Initial Public Offering (IPO)",
                "Venture capital",
            ],
            # Early stage: Angel investors -> index 1
            "answer": 1,
            "value": 800,
            "explanation": "Angel investors often fund very early-stage startups before VCs enter.",
        },
        {
            "question": "What is the role of equity financing in a startup?",
            "options": [
                "To repay existing loans",
                "To reduce operating expenses",
                "To raise capital in exchange for ownership",
                "To increase product prices",
            ],
            # Correct: raise capital for ownership -> index 2
            "answer": 2,
            "value": 500,
            "explanation": "Equity financing gives investors shares in exchange for capital.",
        },
    ],
    "Venture Capital and Equity Dilution": [
        {
            "question": (
                "A startup founder owns 100 pct. of 1,000,000 shares. They take a Series A investment that values "
                "the company at $10 million post-money and gives the investor 20 pct. of the company. "
                "How many new shares were issued in this round?"
            ),
            "options": [
                "250.000 new shares",
                "200.000 new shares",
                "125.000 new shares",
                "500.000 new shares",
            ],
            # Solve 0.2 = x / (1,000,000 + x) => x = 250,000 -> index 0
            "answer": 0,
            "value": 700,
            "explanation": (
                "0.2 = x / (1,000,000 + x) leads to x = 250,000 new shares, which is 20% post-money."
            ),
        },
        {
            "question": (
                "A founder owns 60 pct. of the company before a funding round. "
                "The new investor purchases 25 pct. of the company in the round. "
                "What is the founder's ownership percentage immediately after this funding round?"
            ),
            "options": [
                "48%",
                "50%",
                "35%",
                "45%",
            ],
            # Founder keeps 60% of remaining 75%: 0.6 * 0.75 = 0.45 -> 45% -> index 3
            "answer": 3,
            "value": 800,
            "explanation": "The founder owns 60 pct. of the remaining 75 pct., so 0.6 × 0.75 = 45 pct.",
        },
        {
            "question": (
                "A VC firm invests $10 million for 20 pct. of a company with a 2x Non-Participating "
                "Liquidation Preference. If the company is acquired for $15 million, "
                "how much does the investor receive?"
            ),
            "options": [
                "$20 million",
                "$3 million",
                "$10 million",
                "$15 million",
            ],
            # 2x preference is $20m but capped by exit value: $15m -> index 3
            "answer": 3,
            "value": 800,
            "explanation": (
                "The 2x non-participating preference entitles them to up to $20m, "
                "but the exit is only $15m, so they get $15m."
            ),
        },
    ],
    "Income Statement": [
        {
            "question": "What does the income statement primarily show?",
            "options": [
                "A company's cash inflows and outflows",
                "A company’s financial position at a specific point in time",
                "A company’s revenue, expenses, and profit over a period",
                "How much equity owners have invested in the company"
            ],
            "answer": 2,
            "value": 600,
            "explanation": "The income statement summarizes revenues and expenses over a period, showing the company’s profit or loss."
        },
        {
            "question": "Gross profit is calculated as:",
            "options": [
                "Revenue − Operating Expenses",
                "Revenue − Cost of Goods Sold",
                "Net Income − Taxes",
                "Revenue − Depreciation"
            ],
            "answer": 1,
            "value": 700,
            "explanation": "Gross profit is revenue minus the direct costs of producing goods (COGS)."
        },
        {
            "question": "Which of the following is considered an operating expense?",
            "options": [
                "Interest expense",
                "Cost of raw materials",
                "Marketing and administrative expenses",
                "Income tax expense"
            ],
            "answer": 2,
            "value": 700,
            "explanation": "Operating expenses include marketing, admin, salaries, rent—costs needed to run daily operations."
        },
        {
            "question": "Net income is best defined as:",
            "options": [
                "Revenue minus COGS",
                "Gross profit minus taxes only",
                "Revenue minus all expenses including taxes and interest",
                "Cash received minus cash paid"
            ],
            "answer": 2,
            "value": 800,
            "explanation": "Net income is revenue minus ALL expenses: COGS, operating expenses, interest, and taxes."
        }
    ]
}

# -------------------------
# STORE ITEMS (with Premium)
# -------------------------
store_items = {
    "Outfits": [
        {"name": "Classic Suit", "price": 800, "emoji": "🤵"},
        {"name": "Blue Business Suit", "price": 1200, "emoji": "🕴️"},
        {"name": "Fancy Investor", "price": 2000, "emoji": "💼"},
        {"name": "Silicon Valley Hoodie", "price": 500, "emoji": "🧑‍💻"},
    ],
    "Premium": [
        {"name": "LinkedIn Premium Badge", "price": 5000, "emoji": "🔗"},
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


def save_to_leaderboard():
    """Append current user result to leaderboard.csv once per category completion."""
    if st.session_state.saved_this_round:
        return

    row = [
        st.session_state.username,
        st.session_state.money,
    ]

    file_exists = os.path.exists(LEADERBOARD_FILE)

    with open(LEADERBOARD_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header if file is new/empty
        if not file_exists:
            writer.writerow(["username", "capital"])
        writer.writerow(row)

    st.session_state.saved_this_round = True



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
    st.session_state.saved_this_round = False


# -------------------------
# STORE PAGE
# -------------------------
if st.session_state.page == "store":
    st.header("🛒 Store — Buy Items for Your Avatar")

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
        unsafe_allow_html=True,
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
# LEADERBOARD PAGE
# -------------------------
if st.session_state.page == "leaderboard":
    st.title("🏆 Leaderboard")

    if os.path.exists(LEADERBOARD_FILE):
        df = pd.read_csv(LEADERBOARD_FILE)
        # Sort by highest capital
        df = df.sort_values(by="capital", ascending=False)

        st.write("### Top Players (All Time)")
        st.dataframe(df)
    else:
        st.info("No leaderboard data yet. Complete a quiz category to add your score!")

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
            st.session_state.saved_this_round = False

        st.stop()

    # We have a category selected from here on
    active_questions = get_active_questions()

    # Auto-refresh for live countdown (only while a question is active and no result yet)
    if st.session_state.index < len(active_questions) and not st.session_state.show_result:
        st_autorefresh(interval=200, key="quiz_refresh")

    st.title("💰 Entrepreneurial Finance Quiz")
    st.write(f"Player: **{st.session_state.username}**")
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

        # Auto-save to leaderboard (only once per round)
        save_to_leaderboard()
        st.success("Your score has been saved to the leaderboard ✅")

        if st.button("Play This Category Again"):
            st.session_state.index = 0
            st.session_state.show_result = False
            st.session_state.question_start_time = None
            st.session_state.has_answered = False
            st.session_state.saved_this_round = False

        if st.button("Choose Another Category"):
            reset_category()
