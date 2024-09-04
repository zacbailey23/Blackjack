import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10,
          'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']

CARD_WIDTH = 100
CARD_HEIGHT = 145

MIN_BET = 10
MAX_BET = 100000

rank_to_filename = {
    'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5', 'Six': '6',
    'Seven': '7', 'Eight': '8', 'Nine': '9', 'Ten': '10',
    'Jack': 'jack', 'Queen': 'queen', 'King': 'king', 'Ace': 'ace'
}


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # This is where PyInstaller stores temporary files
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.image_path = resource_path(f"cards/{rank_to_filename[rank]}_of_{suit}.png")
        self.image = Image.open(self.image_path)
        self.image = self.image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.image)

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop()


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'Ace':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def get_value(self):
        return self.value


class Chips:
    def __init__(self):
        self.total = 1000
        self.bet = 0

    def win_bet(self):
        self.total += self.bet

    def lose_bet(self):
        self.total -= self.bet


class BlackjackGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack_Proj")
        self.geometry("1920x1080")

        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_chips = Chips()
        self.playing = False
        self.show_dealer_card = False

        # Initialize the list to store image references
        self.card_images = []  # This ensures images are not garbage collected

        self.create_widgets()
        self.update_display()

    def deal_card_face_down_with_animation(self, card, target_frame, start_x, start_y, end_x, end_y, duration=500):
        """Animate the card moving from the deck to the target position, face down."""
        frames = int(duration / 10)
        delta_x = (end_x - start_x) / frames
        delta_y = (end_y - start_y) / frames

        # Load the card back image
        back_image = Image.open(resource_path("cards/back.png"))
        back_image = back_image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
        back_photo = ImageTk.PhotoImage(back_image)

        # Create a label to animate the face-down card
        card_label = tk.Label(self, image=back_photo)
        card_label.place(x=start_x, y=start_y)

        # Store the reference to prevent garbage collection
        self.card_images.append(back_photo)

        def animate(step=0):
            if step < frames:
                new_x = start_x + delta_x * step
                new_y = start_y + delta_y * step
                card_label.place(x=new_x, y=new_y)
                self.after(10, animate, step + 1)
            else:
                card_label.place_forget()  # Remove the temporary animation card

                # Place the card face down in the target frame
                final_card_label = tk.Label(target_frame, image=back_photo, width=CARD_WIDTH, height=CARD_HEIGHT)
                final_card_label.pack(side=tk.LEFT, padx=5)

                # Ensure the image reference persists
                final_card_label.image = back_photo
                self.card_images.append(back_photo)

                # Debugging output to confirm placement
                print(f"Face-down card placed at {end_x}, {end_y}")

        animate()

    def deal_card_with_animation(self, card, target_frame, start_x, start_y, end_x, end_y, duration=500):
        """Animate the card moving from the deck to the target position."""
        frames = int(duration / 10)
        delta_x = (end_x - start_x) / frames
        delta_y = (end_y - start_y) / frames

        # Create a label to animate the card
        card_label = tk.Label(self, image=card.tk_image)
        card_label.place(x=start_x, y=start_y)

        # Ensure the image reference is stored to prevent garbage collection
        self.card_images.append(card.tk_image)

        def animate(step=0):
            if step < frames:
                new_x = start_x + delta_x * step
                new_y = start_y + delta_y * step
                card_label.place(x=new_x, y=new_y)
                self.after(10, animate, step + 1)
            else:
                card_label.place_forget()  # Remove the temporary animation card

                # Create the final card label in the target frame
                final_card_label = tk.Label(target_frame, image=card.tk_image, width=CARD_WIDTH, height=CARD_HEIGHT)
                final_card_label.pack(side=tk.LEFT, padx=5)

                # Ensure the image reference persists
                final_card_label.image = card.tk_image
                self.card_images.append(card.tk_image)

                # Debugging output to confirm placement
                print(f"Card {card} placed at {end_x}, {end_y}")

        animate()

    def create_widgets(self):
        # Load background image
        self.background_image = Image.open(resource_path("cards/blackjack.jpg"))
        self.background_image = self.background_image.resize((1920, 1080), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create card and chip placeholders
        self.player_cards_frame = tk.Frame(self, bg=None)
        self.player_cards_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        self.dealer_cards_frame = tk.Frame(self, bg=None)
        self.dealer_cards_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.chips_frame = tk.Frame(self, bg="green")
        self.chips_frame.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        # Load chip images
        self.chip_images = {}
        for chip_value in [10, 25, 100]:
            chip_image = Image.open(resource_path(f"cards/{chip_value}.png"))
            chip_image = chip_image.resize((50, 50), Image.LANCZOS)
            self.chip_images[chip_value] = ImageTk.PhotoImage(chip_image)

        # Create chip buttons
        self.chip_buttons = {}
        for chip_value in [10, 25, 100]:
            chip_button = tk.Label(self.chips_frame, image=self.chip_images[chip_value])
            chip_button.pack(side=tk.LEFT, padx=10)
            chip_button.bind("<Button-1>", lambda e, value=chip_value: self.add_bet(value))
            self.chip_buttons[chip_value] = chip_button

        # Bet Entry
        self.bet_entry = tk.Entry(self, font=("Arial", 14))
        self.bet_entry.place(relx=0.8, rely=0.45, anchor=tk.CENTER)

        # Bet Button
        self.bet_button = tk.Button(self, text="Place Bet", command=self.place_bet, font=("Arial", 12))
        self.bet_button.place(relx=0.8, rely=0.55, anchor=tk.CENTER)

        # Player Chips
        self.chips_label = tk.Label(self, text=f"Chips: {self.player_chips.total}", font=("Arial", 14), bg="green",
                                    fg="white")
        self.chips_label.place(relx=0.8, rely=0.35, anchor=tk.CENTER)

        # Control Buttons
        self.hit_button = tk.Button(self, text="Hit", command=self.hit, state=tk.DISABLED, font=("Arial", 12))
        self.hit_button.place(relx=0.41, rely=0.8, anchor=tk.CENTER)

        self.stand_button = tk.Button(self, text="Stand", command=self.stand, state=tk.DISABLED, font=("Arial", 12))
        self.stand_button.place(relx=0.46, rely=0.8, anchor=tk.CENTER)

        self.double_button = tk.Button(self, text="Double Down", command=self.double_down, state=tk.DISABLED,
                                       font=("Arial", 12))
        self.double_button.place(relx=0.52, rely=0.8, anchor=tk.CENTER)

        self.split_button = tk.Button(self, text="Split", command=self.split, state=tk.DISABLED, font=("Arial", 12))
        self.split_button.place(relx=0.58, rely=0.8, anchor=tk.CENTER)

        # Recommendation Label
        self.recommendation_label = tk.Label(self, text="", font=("Arial", 14), bg="green", fg="white")
        self.recommendation_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        self.recommendation_button = tk.Button(self, text="?", command=self.show_recommendation_explanation,
                                               font=("Arial", 10), bg="green", fg="white")
        self.recommendation_button.place(relx=0.57, rely=0.85, anchor=tk.CENTER)

    def update_display(self):
        self.chips_label.config(text=f"Chips: {self.player_chips.total}")
        self.bet_button.config(state=tk.NORMAL if not self.playing else tk.DISABLED)

        # Clear the existing cards from the frames
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

        # Display player's cards
        for card in self.player_hand.cards:
            card_label = tk.Label(self.player_cards_frame, image=card.tk_image)
            card_label.pack(side=tk.LEFT, padx=5)

        # Display dealer's cards
        for i, card in enumerate(self.dealer_hand.cards):
            if i == 0 and not self.show_dealer_card:
                # Show the first card face down if dealer's card is hidden
                back_image = Image.open(resource_path("cards/back.png"))
                back_image = back_image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
                back_photo = ImageTk.PhotoImage(back_image)
                card_label = tk.Label(self.dealer_cards_frame, image=back_photo)
                card_label.image = back_photo  # Keep a reference to avoid garbage collection
            elif i == 1 and not self.show_dealer_card:
                # The second dealer card should not be displayed until the dealer's turn
                continue
            else:
                card_label = tk.Label(self.dealer_cards_frame, image=card.tk_image)
            card_label.pack(side=tk.LEFT, padx=5)

        self.hit_button.config(state=tk.NORMAL if self.playing else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if self.playing else tk.DISABLED)
        self.double_button.config(
            state=tk.NORMAL if self.playing and self.player_chips.bet <= self.player_chips.total // 2 else tk.DISABLED)
        self.split_button.config(state=tk.NORMAL if self.playing and self.can_split() else tk.DISABLED)

        self.recommendation_label.config(text=self.get_recommendation())

    def custom_popup(self, title, message, button_text="OK", command=None):
        # Create a new dialog window that looks like part of the game
        popup_window = tk.Toplevel(self)
        popup_window.title(title)

        # Make the window look like part of the game
        popup_window.configure(bg="green")
        popup_window.geometry("400x200")
        popup_window.transient(self)
        popup_window.grab_set()
        popup_window.resizable(False, False)

        # Add a border to the window to make it more integrated
        popup_frame = tk.Frame(popup_window, bg="darkgreen", bd=10, relief=tk.RAISED)
        popup_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Label with the message, styled like the rest of the game
        label = tk.Label(popup_frame, text=message, font=("Arial", 16), bg="green", fg="white", wraplength=350)
        label.pack(pady=20)

        # Style for the button
        button_style = {
            "font": ("Arial", 14),
            "bg": "white",
            "fg": "black",
            "activebackground": "darkgreen",
            "activeforeground": "white",
            "relief": tk.RAISED,
            "bd": 5,
            "width": 10
        }

        # OK button or custom action button
        action_button = tk.Button(popup_frame, text=button_text,
                                  command=lambda: [popup_window.destroy(), command() if command else None],
                                  **button_style)
        action_button.pack(pady=20)

        # Center the popup window on the screen
        self.center_popup_window(popup_window)

    def center_popup_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def get_recommendation(self):
        if not self.dealer_hand.cards:
            return ""

        player_total = self.player_hand.get_value()
        dealer_card = self.dealer_hand.cards[0]
        dealer_value = values[dealer_card.rank]

        # Determine if the hand is soft (contains an Ace counted as 11)
        has_ace = any(card.rank == 'A' for card in self.player_hand.cards)
        is_soft = has_ace and player_total + 10 <= 21

        # Basic strategy for splitting
        if self.can_split():
            if self.player_hand.cards[0].rank in ['A', '8']:
                return "Recommendation: Split"
            elif self.player_hand.cards[0].rank in ['2', '3', '7']:
                if dealer_value in [2, 3, 4, 5, 6, 7]:
                    return "Recommendation: Split"
            elif self.player_hand.cards[0].rank == '6':
                if dealer_value in [2, 3, 4, 5, 6]:
                    return "Recommendation: Split"
            elif self.player_hand.cards[0].rank == '9':
                if dealer_value not in [7, 10, 'A']:
                    return "Recommendation: Split"
            elif self.player_hand.cards[0].rank == '4':
                if dealer_value in [5, 6]:
                    return "Recommendation: Split"

        # Basic strategy for doubling down
        if (player_total == 11) or (player_total == 10 and dealer_value < 10) or (
                player_total == 9 and dealer_value in [3, 4, 5, 6]):
            return "Recommendation: Double Down"

        # Basic strategy for hitting or standing
        if is_soft:
            if player_total == 18:
                if dealer_value in [9, 10, 'A']:
                    return "Recommendation: Hit"
                else:
                    return "Recommendation: Stand"
            elif player_total in [15, 16, 17]:
                if dealer_value in [4, 5, 6]:
                    return "Recommendation: Double Down"
                else:
                    return "Recommendation: Hit"
            elif player_total == 13 or player_total == 14:
                if dealer_value in [5, 6]:
                    return "Recommendation: Double Down"
                else:
                    return "Recommendation: Hit"
        else:
            if player_total >= 17:
                return "Recommendation: Stand"
            elif player_total >= 13 and player_total <= 16:
                if dealer_value >= 7:
                    return "Recommendation: Hit"
                else:
                    return "Recommendation: Stand"
            elif player_total == 12:
                if dealer_value in [4, 5, 6]:
                    return "Recommendation: Stand"
                else:
                    return "Recommendation: Hit"
            else:
                return "Recommendation: Hit"

    def get_recommendation_explanation(self):
        if not self.dealer_hand.cards:
            return "No recommendation available."

        player_total = self.player_hand.get_value()
        dealer_card = self.dealer_hand.cards[0]
        dealer_value = values[dealer_card.rank]

        # Determine if the hand is soft (contains an Ace counted as 11)
        has_ace = any(card.rank == 'A' for card in self.player_hand.cards)
        is_soft = has_ace and player_total + 10 <= 21

        # Explanation for splitting
        if self.can_split():
            if self.player_hand.cards[0].rank == 'Ace':
                return (
                    "Splitting aces is recommended because it increases your chances of making 21 and forming two strong hands. "
                    "Note that after splitting aces, you'll only receive one additional card per hand."
                )
            elif self.player_hand.cards[0].rank in ['2', '3', '7']:
                return (
                    f"Splitting {self.player_hand.cards[0].rank}s is a good idea because the dealer's {dealer_card.rank} is a low card. "
                    "This gives you a potential advantage, as the dealer is more likely to bust with a weak up card."
                )
            elif self.player_hand.cards[0].rank == '8':
                return (
                    "Splitting 8s is recommended because a total of 16 is difficult to play. Splitting gives you a better chance "
                    "to improve both hands."
                )
            elif dealer_value in [4, 5, 6]:
                return (
                    f"Splitting your pair is recommended because the dealer's {dealer_card.rank} is weak. However, be cautious, "
                    "as this can be a risky move."
                )

        # Explanation for doubling down
        if (player_total == 11) or (player_total == 10 and dealer_value < 10) or (
                player_total == 9 and dealer_value in [3, 4, 5, 6]):
            return f"Recommendation is to Double Down because your total is {player_total}, which is favorable against the dealer's {dealer_card.rank}."

        # Explanation for hitting or standing
        if is_soft:
            if player_total == 18:
                if dealer_value in [9, 10, 'A']:
                    return "Recommendation is to Hit because your soft 18 is weak against the dealer's high card."
                else:
                    return "Recommendation is to Stand because your soft 18 is strong against the dealer's low card."
            elif player_total in [15, 16, 17]:
                return "Recommendation is to Double Down if allowed; otherwise, Hit, because your hand can improve."
            elif player_total == 13 or player_total == 14:
                return "Recommendation is to Double Down if allowed; otherwise, Hit, because you have a soft hand with potential."
        else:
            if player_total >= 17:
                return "Recommendation is to Stand because your hand is strong enough."
            elif player_total >= 13 and player_total <= 16:
                if dealer_value >= 7:
                    return "Recommendation is to Hit because the dealer's up card is strong."
                else:
                    return "Recommendation is to Stand because the dealer's up card is weak."
            elif player_total == 12:
                if dealer_value in [4, 5, 6]:
                    return "Recommendation is to Stand because the dealer's up card is weak."
                else:
                    return "Recommendation is to Hit because the dealer's up card is strong."
            else:
                return "Recommendation is to Hit because your hand is too weak."

        return "No specific recommendation."

    def show_recommendation_explanation(self):
        explanation = self.get_recommendation_explanation()
        self.custom_popup("Recommendation Explanation", explanation, button_text="Continue",
                          command=self.update_display)

    def add_bet(self, amount):
        current_bet = int(self.bet_entry.get() or 0)
        new_bet = current_bet + amount
        self.bet_entry.delete(0, tk.END)
        self.bet_entry.insert(0, str(new_bet))

    def place_bet(self):
        try:
            bet = int(self.bet_entry.get())
            if bet < MIN_BET or bet > self.player_chips.total:
                self.custom_popup("Error", f"Invalid bet! Bet must be between {MIN_BET} and {self.player_chips.total}.")
            else:
                self.player_chips.bet = bet
                self.playing = True
                self.start_game()
        except ValueError:
            self.custom_popup("Error", "Invalid input! Please enter an integer.")

    def start_game(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.show_dealer_card = False  # Dealer's first card is face down initially

        # Clear previous cards from display
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

        # Coordinates for animation
        deck_x, deck_y = 960, 100  # Assuming the deck is centered at the top of the screen
        player_end_x, player_end_y = 860, 600  # Example final position for player cards
        dealer_end_x, dealer_end_y = 860, 200  # Example final position for dealer cards

        # Deal initial cards (only to the hand, not to the display)
        player_card1 = self.deck.deal()
        player_card2 = self.deck.deal()
        dealer_card1 = self.deck.deal()
        dealer_card2 = self.deck.deal()

        # Add cards to hands
        self.player_hand.add_card(player_card1)
        self.player_hand.add_card(player_card2)
        self.dealer_hand.add_card(dealer_card1)
        self.dealer_hand.add_card(dealer_card2)

        # Debugging output
        print(f"Player cards dealt: {player_card1}, {player_card2}")
        print(f"Dealer cards dealt: {dealer_card1}, {dealer_card2} (one face down)")

        # Animate and display the player's cards
        self.deal_card_with_animation(player_card1, self.player_cards_frame, deck_x, deck_y, player_end_x, player_end_y)
        self.after(600, lambda: self.deal_card_with_animation(player_card2, self.player_cards_frame, deck_x, deck_y,
                                                              player_end_x + 120, player_end_y))

        # Animate and display the dealer's first card face down
        self.after(1200, lambda: self.deal_card_face_down_with_animation(dealer_card1, self.dealer_cards_frame, deck_x,
                                                                         deck_y, dealer_end_x, dealer_end_y))

        # Animate and display the dealer's second card face up
        self.after(1800, lambda: self.deal_card_with_animation(dealer_card2, self.dealer_cards_frame, deck_x, deck_y,
                                                               dealer_end_x + 120, dealer_end_y))

        # After all animations are complete, update the display to ensure everything is correct
        self.after(2400, self.update_display)

        # Check for Blackjack after all animations are done
        self.after(2400, self.check_blackjack)

    def check_blackjack(self):
        if self.player_hand.get_value() == 21:
            self.player_wins_blackjack()

    def hit(self):
        if self.playing:
            self.player_hand.add_card(self.deck.deal())
            self.update_display()
            if self.player_hand.get_value() > 21:
                self.show_all()
                self.player_busts()
            elif self.player_hand.get_value() == 21:
                self.stand()

    def check_player_bust(self):
        if self.player_hand.get_value() > 21:
            self.show_all()
            self.player_busts()
        elif self.player_hand.get_value() == 21:
            self.stand()

    def stand(self):
        self.playing = False
        self.show_dealer_card = True
        self.update_display()
        self.dealer_turn()

    def dealer_turn(self):
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
        self.show_all()
        self.check_winner()

    def double_down(self):
        self.player_chips.bet *= 2
        self.player_hand.add_card(self.deck.deal())
        self.playing = False
        self.show_dealer_card = True
        self.update_display()
        self.dealer_turn()

    def split(self):
        if self.can_split():
            self.split_hands = [Hand(), Hand()]
            self.split_hands[0].add_card(self.player_hand.cards[0])
            self.split_hands[1].add_card(self.player_hand.cards[1])
            self.split_hands[0].add_card(self.deck.deal())
            self.split_hands[1].add_card(self.deck.deal())
            self.playing = False
            self.play_split_hands()
        else:
            self.custom_popup("Error", "You can only split cards of the same rank!", button_text="Continue",
                              command=self.update_display)

    def can_split(self):
        return len(self.player_hand.cards) == 2 and self.player_hand.cards[0].rank == self.player_hand.cards[1].rank

    def play_split_hands(self):
        split_results = []
        for i, hand in enumerate(self.split_hands):
            self.player_hand = hand
            self.update_display()

            while self.player_hand.get_value() < 21:
                action = self.ask_player_action_for_split_hand(
                    i + 1)  # Ask the player for action on the current split hand
                if action == "Hit":
                    self.player_hand.add_card(self.deck.deal())
                    self.update_display()
                elif action == "Stand":
                    break

            if self.player_hand.get_value() > 21:
                split_results.append("Bust")
                self.player_busts()
            else:
                split_results.append(f"Stand with {self.player_hand.get_value()}")

        self.show_dealer_card = True
        self.update_display()
        self.dealer_turn()

        # Check results for both hands
        final_results = []
        for result in split_results:
            if result == "Bust":
                final_results.append("Lost")
            else:
                dealer_value = self.dealer_hand.get_value()
                player_value = int(result.split(" ")[-1])

                if dealer_value > 21:
                    final_results.append("Won")
                elif player_value > dealer_value:
                    final_results.append("Won")
                elif player_value < dealer_value:
                    final_results.append("Lost")
                else:
                    final_results.append("Push")

        # Display the results for both hands
        for i, result in enumerate(final_results):
            if result == "Won":
                self.player_chips.win_bet()
            elif result == "Lost":
                self.player_chips.lose_bet()

            self.custom_popup("Game Over", f"Result for hand {i + 1}: {result}", button_text="Continue",
                              command=self.update_display)

        self.playing = False
        self.update_display()

    def ask_player_action_for_split_hand(self, hand_number):
        # Create a new dialog window
        action_window = tk.Toplevel(self)
        action_window.title("Choose Action")

        # Set the size and position of the window
        action_window.geometry("300x150")
        action_window.transient(self)
        action_window.grab_set()

        # Label with the question
        label = tk.Label(action_window,
                         text=f"What would you like to do with Hand {hand_number}?\nChoose Hit or Stand.")
        label.pack(pady=20)

        # Create a variable to store the player's choice
        player_action = tk.StringVar()

        # Hit button
        hit_button = tk.Button(action_window, text="Hit", command=lambda: player_action.set("Hit"))
        hit_button.pack(side=tk.LEFT, padx=20, pady=20)

        # Stand button
        stand_button = tk.Button(action_window, text="Stand", command=lambda: player_action.set("Stand"))
        stand_button.pack(side=tk.RIGHT, padx=20, pady=20)

        # Wait for the player to choose
        self.wait_variable(player_action)

        # Close the dialog window
        action_window.destroy()

        return player_action.get()

    def show_all(self):
        self.show_dealer_card = True
        self.update_display()

    def check_winner(self):
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()

        if player_value > 21:
            self.player_busts()
        elif dealer_value > 21:
            self.dealer_busts()
        elif dealer_value > player_value:
            self.dealer_wins()
        elif dealer_value < player_value:
            self.player_wins()
        else:
            self.push()

    def player_wins_blackjack(self):
        self.show_all()
        self.custom_popup("Game Over", "BLACKJACKKKKKK BABYYYYYY!", button_text="Continue", command=self.update_display)
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def player_busts(self):
        self.show_all()
        self.custom_popup("Game Over", "You busted and lost!", button_text="Continue", command=self.update_display)
        self.player_chips.lose_bet()
        self.playing = False
        self.update_display()

    def player_wins(self):
        self.custom_popup("Game Over", "Player wins!", button_text="Continue", command=self.update_display)
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def dealer_busts(self):
        self.custom_popup("Game Over", "Dealer Busts!", button_text="Continue", command=self.update_display)
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def dealer_wins(self):
        self.custom_popup("Game Over", "Dealer wins!", button_text="Continue", command=self.update_display)
        self.player_chips.lose_bet()
        self.playing = False
        self.update_display()

    def push(self):
        self.custom_popup("Game Over", "Its a Tie (Push)!", button_text="Continue", command=self.update_display)
        self.playing = False
        self.update_display()

    def new_game(self):
        self.player_chips = Chips()
        self.update_display()
        self.bet_entry.delete(0, tk.END)




if __name__ == '__main__':
    game = BlackjackGame()
    game.mainloop()
