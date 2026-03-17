import streamlit as st
import random

# title at top of app
st.title("Blackjack")

# this makes a random card
def draw_card():
    card = random.randint(1, 13)

    # 1 will be ace
    if card == 1:
        return "Ace"

    # these are face cards so just count them as 10
    elif card in [11, 12, 13]:
        return 10

    # everything else stays the same
    return card

# this adds up the hand
def calculate_total(hand):
    total = 0
    aces = 0

    # go through every card in the hand
    for card in hand:
        if card == "Ace":
            # start by pretending ace is 11
            total += 11
            aces += 1
        else:
            total += card

    # if total is too high and we have aces
    # turn an ace from 11 into 1 by taking away 10
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total

# making the saved variables so streamlit doesnt forget everything every click
if "player_hand" not in st.session_state:
    st.session_state.player_hand = []

if "dealer" not in st.session_state:
    st.session_state.dealer = 0

if "started" not in st.session_state:
    st.session_state.started = False

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "message" not in st.session_state:
    st.session_state.message = ""

# this saves the most recent card drawn so we can show it
if "last_card" not in st.session_state:
    st.session_state.last_card = None

# when this button is pressed start fresh
if st.button("Start New Game"):
    # give player 2 cards
    st.session_state.player_hand = [draw_card(), draw_card()]

    # dealer just gets a random final value for now
    st.session_state.dealer = random.randint(17, 24)

    # now the game is active again
    st.session_state.started = True
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.last_card = None

# only show the game stuff after starting
if st.session_state.started:
    st.subheader("Your Cards")

    # show every card the player has
    for i, card in enumerate(st.session_state.player_hand, start=1):
        st.write(f"Card {i}: {card}")

    # work out total from whole hand
    total = calculate_total(st.session_state.player_hand)
    st.write(f"Current total: {total}")

    # check if game should already end
    if total > 21:
        st.session_state.message = "Game over - Bust!"
        st.session_state.game_over = True
    elif total == 21:
        st.session_state.message = "You Win -- Perfect Score!"
        st.session_state.game_over = True

    # only let them keep playing if game not over yet
    if not st.session_state.game_over:
        col1, col2 = st.columns(2)

        with col1:
            # if hit gets pressed add 1 more card
            if st.button("Hit"):
                new_card = draw_card()
                st.session_state.player_hand.append(new_card)
                st.session_state.last_card = new_card
                st.rerun()

        with col2:
            # if stand gets pressed compare against dealer
            if st.button("Stand"):
                dealer = st.session_state.dealer
                total = calculate_total(st.session_state.player_hand)

                # now compare player and dealer
                if dealer > 21:
                    st.session_state.message = f"You Win -- Dealer Busted with {dealer}!"
                elif total > dealer:
                    st.session_state.message = f"You Win! Dealer had {dealer}"
                elif total < dealer:
                    st.session_state.message = f"Game over - You Lost! Dealer had {dealer}"
                else:
                    st.session_state.message = f"Push. Dealer had {dealer}"

                st.session_state.game_over = True

    # show result message if there is one
    if st.session_state.message:
        if "You Win" in st.session_state.message or "Push" in st.session_state.message:
            st.success(st.session_state.message)
        else:
            st.error(st.session_state.message)

    # once game is over show dealer number
    if st.session_state.game_over:
        st.write(f"Dealer's number: {st.session_state.dealer}")