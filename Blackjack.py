import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}
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

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.image_path = f"C:/Users/zacba/PycharmProjects/Blackjack/Blackjack_Proj/cards/{rank_to_filename[rank]}_of_{suit}.png"
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
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # Load background image
        self.background_image = Image.open(f"cards/blackjack.jpg")
        self.background_image = self.background_image.resize((1920, 1080), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create card and chip placeholders
        self.player_cards_frame = tk.Frame(self, bg="green")
        self.player_cards_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        self.dealer_cards_frame = tk.Frame(self, bg="green")
        self.dealer_cards_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.chips_frame = tk.Frame(self, bg="green")
        self.chips_frame.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        # Load chip images
        self.chip_images = {}
        for chip_value in [10, 25, 100]:
            chip_image = Image.open(f"cards/{chip_value}.png")
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
        self.chips_label = tk.Label(self, text=f"Chips: {self.player_chips.total}", font=("Arial", 14), bg="green", fg="white")
        self.chips_label.place(relx=0.8, rely=0.35, anchor=tk.CENTER)

        # Control Buttons
        self.hit_button = tk.Button(self, text="Hit", command=self.hit, state=tk.DISABLED, font=("Arial", 12))
        self.hit_button.place(relx=0.41, rely=0.8, anchor=tk.CENTER)

        self.stand_button = tk.Button(self, text="Stand", command=self.stand, state=tk.DISABLED, font=("Arial", 12))
        self.stand_button.place(relx=0.46, rely=0.8, anchor=tk.CENTER)

        self.double_button = tk.Button(self, text="Double Down", command=self.double_down, state=tk.DISABLED, font=("Arial", 12))
        self.double_button.place(relx=0.52, rely=0.8, anchor=tk.CENTER)

        self.split_button = tk.Button(self, text="Split", command=self.split, state=tk.DISABLED, font=("Arial", 12))
        self.split_button.place(relx=0.58, rely=0.8, anchor=tk.CENTER)

        # Recommendation Label
        self.recommendation_label = tk.Label(self, text="", font=("Arial", 14), bg="green", fg="white")
        self.recommendation_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

    def update_display(self):
        self.chips_label.config(text=f"Chips: {self.player_chips.total}")
        self.bet_button.config(state=tk.NORMAL if not self.playing else tk.DISABLED)

        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()

        for card in self.player_hand.cards:
            card_label = tk.Label(self.player_cards_frame, image=card.tk_image)
            card_label.pack(side=tk.LEFT, padx=5)

        for card in self.dealer_hand.cards:
            if self.show_dealer_card or card == self.dealer_hand.cards[0]:
                card_label = tk.Label(self.dealer_cards_frame, image=card.tk_image)
            else:
                back_image = Image.open("cards/back.png")
                back_image = back_image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
                back_photo = ImageTk.PhotoImage(back_image)
                card_label = tk.Label(self.dealer_cards_frame, image=back_photo)
                card_label.image = back_photo  # Keep a reference
            card_label.pack(side=tk.LEFT, padx=5)

        self.hit_button.config(state=tk.NORMAL if self.playing else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if self.playing else tk.DISABLED)
        self.double_button.config(
            state=tk.NORMAL if self.playing and self.player_chips.bet <= self.player_chips.total // 2 else tk.DISABLED)
        self.split_button.config(state=tk.NORMAL if self.playing and self.can_split() else tk.DISABLED)

        self.recommendation_label.config(text=self.get_recommendation())

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

    def add_bet(self, amount):
        current_bet = int(self.bet_entry.get() or 0)
        new_bet = current_bet + amount
        self.bet_entry.delete(0, tk.END)
        self.bet_entry.insert(0, str(new_bet))

    def place_bet(self):
        try:
            bet = int(self.bet_entry.get())
            if bet < MIN_BET or bet > self.player_chips.total:
                messagebox.showerror("Error", f"Invalid bet! Bet must be between {MIN_BET} and {self.player_chips.total}.")
            else:
                self.player_chips.bet = bet
                self.playing = True
                self.start_game()
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter an integer.")

    def start_game(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.show_dealer_card = False

        self.player_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

        self.update_display()

        if self.player_hand.get_value() == 21:
            self.player_wins_blackjack()

    def hit(self):
        self.player_hand.add_card(self.deck.deal())
        self.update_display()
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
            messagebox.showerror("Error", "You can only split with two cards of the same rank.")

    def can_split(self):
        return len(self.player_hand.cards) == 2 and self.player_hand.cards[0].rank == self.player_hand.cards[1].rank

    def play_split_hands(self):
        for hand in self.split_hands:
            self.player_hand = hand
            self.update_display()
            while self.player_hand.get_value() < 21:
                if self.player_hand.get_value() < 17:
                    self.player_hand.add_card(self.deck.deal())
                else:
                    break
            if self.player_hand.get_value() > 21:
                self.player_busts()
        self.stand()

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
        messagebox.showinfo("Game Over", "Player wins with Blackjack_Proj!")
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def player_busts(self):
        self.show_all()
        messagebox.showinfo("Game Over", "Player busts!")
        self.player_chips.lose_bet()
        self.playing = False
        self.update_display()

    def player_wins(self):
        messagebox.showinfo("Game Over", "Player wins!")
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def dealer_busts(self):
        messagebox.showinfo("Game Over", "Dealer busts!")
        self.player_chips.win_bet()
        self.playing = False
        self.update_display()

    def dealer_wins(self):
        messagebox.showinfo("Game Over", "Dealer wins!")
        self.player_chips.lose_bet()
        self.playing = False
        self.update_display()

    def push(self):
        messagebox.showinfo("Game Over", "It's a tie! Push.")
        self.playing = False
        self.update_display()

    def new_game(self):
        self.player_chips = Chips()
        self.update_display()
        self.bet_entry.delete(0, tk.END)

if __name__ == '__main__':
    game = BlackjackGame()
    game.mainloop()
