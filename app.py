import streamlit as st
import random

# set up app page first so browser tab and layout ready before anything else run
# make it look like blackjack app from very beginning
st.set_page_config(page_title="Blackjack", page_icon="🃏", layout="centered")

# push in all table styling now
# idea here build casino mood before game pieces render
# background dark outside
# table green and oval
# cards white and readable
# all visual rules grouped together so later code just uses class names and not think about style again
st.markdown("""
<style>
/* Page background */
[data-testid="stAppViewContainer"] {
    background: #1a1a2e;
}
[data-testid="stHeader"] { background: transparent; }

/* Felt table */
.table {
    background: #1a5c2e;
    border-radius: 50% / 18%;
    border: 8px solid #7a4f2a;
    outline: 3px solid #c9a84c;
    padding: 32px 40px;
    min-height: 580px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0px;
    position: relative;
    box-shadow: 0 0 60px rgba(0,0,0,0.7);
}
.table::before {
    content: '';
    position: absolute;
    inset: 10px;
    border-radius: 50% / 16%;
    border: 1px solid rgba(201,168,76,0.25);
    pointer-events: none;
}

/* Zone labels */
.zone-label {
    font-size: 11px;
    letter-spacing: 3px;
    color: rgba(201,168,76,0.5);
    text-transform: uppercase;
    text-align: center;
    margin: 4px 0;
    font-family: Georgia, serif;
}

/* Card row */
.hand-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    min-height: 110px;
    align-items: center;
    padding: 8px 0;
}

/* Individual card */
.card {
    width: 64px;
    height: 90px;
    background: #fff;
    border-radius: 8px;
    border: 1px solid #ccc;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    position: relative;
    box-shadow: 2px 3px 6px rgba(0,0,0,0.5);
    font-family: Georgia, serif;
}
.card.red { color: #c0392b; }
.card-corner {
    position: absolute;
    font-size: 11px;
    font-weight: 700;
    line-height: 1.2;
    text-align: center;
}
.card-corner.tl { top: 4px; left: 5px; }
.card-corner.br { bottom: 4px; right: 5px; transform: rotate(180deg); }
.card-suit { font-size: 26px; line-height: 1; }
.card-back {
    width: 64px;
    height: 90px;
    border-radius: 8px;
    border: 1px solid #0d2460;
    background: repeating-linear-gradient(
        135deg,
        #1a3a8a,
        #1a3a8a 5px,
        #2255cc 5px,
        #2255cc 10px
    );
    display: inline-block;
    box-shadow: 2px 3px 6px rgba(0,0,0,0.5);
}

/* Total badge */
.total-badge {
    background: rgba(0,0,0,0.4);
    color: #c9a84c;
    font-size: 13px;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 20px;
    border: 1px solid rgba(201,168,76,0.4);
    text-align: center;
    font-family: Georgia, serif;
    letter-spacing: 0.5px;
    margin: 2px 0;
}

/* Message box */
.msg-box {
    font-size: 15px;
    font-weight: 600;
    padding: 10px 28px;
    border-radius: 24px;
    text-align: center;
    font-family: Georgia, serif;
    letter-spacing: 0.5px;
    border: 1px solid rgba(201,168,76,0.5);
    background: rgba(0,0,0,0.45);
    color: #fff;
    min-width: 220px;
}
.msg-box.win  { color: #ffd700; border-color: #ffd700; }
.msg-box.lose { color: #ff7070; border-color: #ff6060; }
.msg-box.push { color: #aaddff; border-color: #aaddff; }

/* Divider */
.divider {
    width: 55%;
    height: 1px;
    background: rgba(201,168,76,0.2);
    margin: 6px 0;
}

/* Score strip */
.score-strip {
    display: flex;
    gap: 24px;
    font-size: 12px;
    color: rgba(201,168,76,0.55);
    letter-spacing: 1px;
    font-family: Georgia, serif;
    text-transform: uppercase;
}
.score-strip b { color: #c9a84c; font-weight: 600; }

/* Hide streamlit button styling — use custom ones */
[data-testid="stButton"] button {
    background: rgba(201,168,76,0.15) !important;
    color: #c9a84c !important;
    border: 1px solid #c9a84c !important;
    border-radius: 20px !important;
    font-family: Georgia, serif !important;
    letter-spacing: 0.5px !important;
    font-weight: 500 !important;
    padding: 8px 24px !important;
    transition: background 0.15s !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(201,168,76,0.3) !important;
}
[data-testid="stButton"] button:disabled {
    opacity: 0.35 !important;
}
</style>
""", unsafe_allow_html=True)

# make deck ingredients simple and global
# keep suit and rank choices in one place so draw function stay tiny
# also keep red suits separate because card html need color choice later
SUITS = ["♠", "♥", "♦", "♣"]
RED_SUITS = {"♥", "♦"}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


# when game need a card just grab random rank and random suit
# not realistic deck with removals
# but fast and enough for simple blackjack toy
def draw_card():
    return {"rank": random.choice(RANKS), "suit": random.choice(SUITS)}


# convert visible card into value idea
# ace handled special on purpose
# return word ace first so total logic can decide 11 or 1 later
# face cards all become 10
def card_value(card):
    r = card["rank"]
    if r == "A":
        return "Ace"
    if r in ("J", "Q", "K"):
        return 10
    return int(r)


# walk through whole hand and build best blackjack total
# first act like every ace is 11 because that gives strongest hand
# then if total too high keep downgrading aces from 11 to 1
# this is main scoring brain for both player and dealer
def calculate_total(hand):
    total, aces = 0, 0
    for card in hand:
        v = card_value(card)
        if v == "Ace":
            total += 11
            aces += 1
        else:
            total += v
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


# session state is memory between reruns
# streamlit rerun all script after button click
# so put every game variable here or round disappears
# loop keeps setup compact instead of many repeated if blocks
for key, default in [
    ("player_hand", []),
    ("dealer_hand", []),
    ("started", False),
    ("game_over", False),
    ("message", "Press 'New Game' to play"),
    ("msg_cls", ""),
    ("wins", 0),
    ("losses", 0),
    ("pushes", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# start fresh round here
# deal two cards each side
# mark game active
# reset message and style
# after deal check instant blackjack so round can finish immediately
def new_game():
    st.session_state.player_hand = [draw_card(), draw_card()]
    st.session_state.dealer_hand = [draw_card(), draw_card()]
    st.session_state.started = True
    st.session_state.game_over = False
    st.session_state.message = "Hit or Stand?"
    st.session_state.msg_cls = ""
    pt = calculate_total(st.session_state.player_hand)
    if pt == 21:
        end_round()


# resolve whole round here
# dealer must keep drawing until at least 17
# then compare both totals and decide result text and score counters
# also catch blackjack bust win lose push all in one place
# final step lock board by marking game over
def end_round():
    while calculate_total(st.session_state.dealer_hand) < 17:
        st.session_state.dealer_hand.append(draw_card())

    pt = calculate_total(st.session_state.player_hand)
    dt = calculate_total(st.session_state.dealer_hand)

    if pt == 21 and len(st.session_state.player_hand) == 2:
        st.session_state.message = "Blackjack! You win!"
        st.session_state.msg_cls = "win"
        st.session_state.wins += 1
    elif pt > 21:
        st.session_state.message = "Bust! You lose."
        st.session_state.msg_cls = "lose"
        st.session_state.losses += 1
    elif dt > 21:
        st.session_state.message = f"Dealer busts ({dt})! You win!"
        st.session_state.msg_cls = "win"
        st.session_state.wins += 1
    elif pt > dt:
        st.session_state.message = f"You win! {pt} vs {dt}"
        st.session_state.msg_cls = "win"
        st.session_state.wins += 1
    elif pt < dt:
        st.session_state.message = f"Dealer wins. {dt} vs {pt}"
        st.session_state.msg_cls = "lose"
        st.session_state.losses += 1
    else:
        st.session_state.message = f"Push — both had {pt}"
        st.session_state.msg_cls = "push"
        st.session_state.pushes += 1

    st.session_state.game_over = True


# build one visible card as html block
# choose red class only for hearts and diamonds
# then place rank and suit in corners plus big suit in center
# this keeps render function later very dumb and easy
def card_html(card):
    cls = "card red" if card["suit"] in RED_SUITS else "card"
    r, s = card["rank"], card["suit"]
    return f"""
    <div class="{cls}">
      <div class="card-corner tl">{r}<br>{s}</div>
      <div class="card-suit">{s}</div>
      <div class="card-corner br">{r}<br>{s}</div>
    </div>"""


# hidden dealer card uses a different fake back
# return just one reusable html snippet
def back_html():
    return '<div class="card-back"></div>'


# turn whole hand into row of card html
# second card can be hidden during active round for dealer suspense
# collect html pieces then wrap in row container
def render_hand(hand, hide_second=False):
    cards_html = ""
    for i, card in enumerate(hand):
        if hide_second and i == 1:
            cards_html += back_html()
        else:
            cards_html += card_html(card)
    return f'<div class="hand-row">{cards_html}</div>'


# decide when dealer second card should stay hidden
# active started game and not finished means keep it hidden
hide_dealer = st.session_state.started and not st.session_state.game_over

# prebuild both rows of cards before final page html
# render functions do markup work so layout block later stays clean
dealer_hand_html = render_hand(st.session_state.dealer_hand, hide_second=hide_dealer)
player_hand_html = render_hand(st.session_state.player_hand)

# totals prepared separately because table wants badges in specific spots
# empty string when hand missing so layout not explode
dealer_total = calculate_total(st.session_state.dealer_hand) if st.session_state.dealer_hand else ""
player_total = calculate_total(st.session_state.player_hand) if st.session_state.player_hand else ""

# dealer total logic has two display modes
# full total after round over
# partial clue during round showing first card plus mystery
dealer_total_html = f'<div class="total-badge">Total: {dealer_total}</div>' if (
    st.session_state.dealer_hand and not hide_dealer) else (
    f'<div class="total-badge">{card_value(st.session_state.dealer_hand[0])} + ?</div>'
    if st.session_state.dealer_hand else ""
)

# player total can always show because no hidden info there
player_total_html = f'<div class="total-badge">Total: {player_total}</div>' if st.session_state.player_hand else ""

# message class picks win lose push colors
# scoreboard html prepared here so final table markup just drops it in place
msg_cls = st.session_state.msg_cls
score_html = f"""
<div class="score-strip">
  <span>Wins <b>{st.session_state.wins}</b></span>
  <span>Losses <b>{st.session_state.losses}</b></span>
  <span>Pushes <b>{st.session_state.pushes}</b></span>
</div>"""

# now assemble main table face
# everything already computed above
# this section mostly placement and not logic
st.markdown(f"""
<div class="table">
  <div class="zone-label">Dealer</div>
  {dealer_hand_html}
  {dealer_total_html}
  <div class="divider"></div>
  <div class="msg-box {msg_cls}">{st.session_state.message}</div>
  {score_html}
  <div class="divider"></div>
  {player_total_html}
  {player_hand_html}
  <div class="zone-label">You</div>
</div>
""", unsafe_allow_html=True)

# leave little space before controls
st.write("")

# make three button lanes
# keep actions separate so each button logic easy to scan
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # first button always available for reset and new deal
    # after state update force rerun so ui refresh immediately
    if st.button("🂠  New Game", use_container_width=True):
        new_game()
        st.rerun()

with col2:
    # hit only allowed during active unfinished round
    # on hit add one card then recheck player total
    # bust ends round right here
    # 21 sends control to end round so dealer can finish too
    hit_disabled = not st.session_state.started or st.session_state.game_over
    if st.button("Hit", disabled=hit_disabled, use_container_width=True):
        st.session_state.player_hand.append(draw_card())
        pt = calculate_total(st.session_state.player_hand)

        if pt > 21:
            st.session_state.message = "Bust! You lose."
            st.session_state.msg_cls = "lose"
            st.session_state.losses += 1
            st.session_state.game_over = True
        elif pt == 21:
            end_round()

        st.rerun()

with col3:
    # stand means player done and dealer must finish round
    # call end round and rerun so revealed cards and result show up
    stand_disabled = not st.session_state.started or st.session_state.game_over
    if st.button("Stand", disabled=stand_disabled, use_container_width=True):
        end_round()
        st.rerun()
