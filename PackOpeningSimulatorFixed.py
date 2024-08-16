import tkinter as tk
import random
import pickle
from tkinter import messagebox

# Define the card packs with costs and rarity distributions
CARD_PACKS = {
    "Bronze Pack": {"cost": 100, "rarity_distribution": {"common": 70, "uncommon": 20, "rare": 10}},
    "Silver Pack": {"cost": 200, "rarity_distribution": {"common": 60, "uncommon": 25, "rare": 10, "super rare": 5}},
    "Gold Pack": {"cost": 500, "rarity_distribution": {"uncommon": 20, "rare": 40, "super rare": 30, "epic": 10}},  # Reduced uncommon chance
    "Ruby Pack": {"cost": 1000, "rarity_distribution": {"rare": 40, "super rare": 30, "epic": 20, "mythic": 10}},
    "Emerald Pack": {"cost": 2000, "rarity_distribution": {"super rare": 40, "epic": 30, "mythic": 20, "legendary": 10}},
    "Diamond Pack": {"cost": 3000, "rarity_distribution": {"epic": 50, "mythic": 30, "legendary": 15, "godlike": 5}},
    "Stardust Pack": {"cost": 5000, "rarity_distribution": {"legendary": 70, "godlike": 25, "star": 5}},
}

# Chances for shiny and shadow cards
SHINY_CHANCE = 0.10
SHADOW_CHANCE = 0.01
REFUND_CHANCE = 0.05  # 5% chance to get twice the money back

def save_game(data, filename="savegame.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    messagebox.showinfo("Save Game", "Game progress saved successfully!")

def load_game(filename="savegame.pkl"):
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        messagebox.showinfo("Load Game", "Game progress loaded successfully!")
        return data
    except FileNotFoundError:
        messagebox.showwarning("Load Game", "No saved game found.")
        return None

class CardGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Pack Opening Game")

        self.player_currency = 180  # Starting with 180 coins
        self.player_inventory = []
        self.player_cards = []
        self.currency_label = None

        # Load the game data if available
        saved_data = load_game()
        if saved_data:
            self.player_currency, self.player_inventory, self.player_cards = saved_data

        # Initialize the coin reward system
        self.start_coin_reward_system()

        self.main_menu()

    def start_coin_reward_system(self):
        """Awards the player 20 coins every 2 minutes."""
        self.player_currency += 20
        self.update_currency_display()
        self.root.after(2 * 60 * 1000, self.start_coin_reward_system)  # Repeat every 2 minutes

    def update_currency_display(self):
        """ Updates the currency display in the top right corner of the window. """
        if self.currency_label:
            self.currency_label.destroy()

        self.currency_label = tk.Label(self.root, text=f"Coins: {self.player_currency}", font=("Helvetica", 14))
        self.currency_label.place(relx=1.0, rely=0.0, anchor='ne')

    def save_progress(self):
        data = (self.player_currency, self.player_inventory, self.player_cards)
        save_game(data)

    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Card Pack Opening Game", font=("Helvetica", 24)).pack(pady=20)

        tk.Button(self.root, text="Shop", command=self.shop_menu).pack(pady=10)
        tk.Button(self.root, text="Inventory", command=self.inventory_menu).pack(pady=10)
        tk.Button(self.root, text="Market", command=self.market_menu).pack(pady=10)  # Market button moved to main menu
        tk.Button(self.root, text="Save Progress", command=self.save_progress).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=10)

    def shop_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Shop", font=("Helvetica", 18)).pack(pady=20)

        for pack_name, pack_info in CARD_PACKS.items():
            tk.Button(self.root, text=f"{pack_name} - {pack_info['cost']} Coins", 
                      command=lambda name=pack_name: self.buy_pack(name)).pack(pady=5)
        
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=20)

    def buy_pack(self, pack_name):
        if self.player_currency >= CARD_PACKS[pack_name]["cost"]:
            self.player_currency -= CARD_PACKS[pack_name]["cost"]
            self.player_inventory.append(pack_name)
            messagebox.showinfo("Pack Purchased", f"You bought a {pack_name}!")
            self.inventory_menu()  # Go back to inventory to reflect the purchase
        else:
            messagebox.showerror("Error", "Not enough currency!")
        self.shop_menu()

    def inventory_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Inventory", font=("Helvetica", 18)).pack(pady=20)

        tk.Button(self.root, text="Card Packs", command=self.open_pack_inventory).pack(pady=10)
        tk.Button(self.root, text="View Cards", command=self.card_inventory_menu).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=20)

    def open_pack_inventory(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Card Packs", font=("Helvetica", 18)).pack(pady=20)

        if self.player_inventory:
            for i, pack in enumerate(self.player_inventory):
                tk.Button(self.root, text=f"Open {pack}", 
                          command=lambda idx=i: self.open_pack_animation(idx)).pack(pady=5)
        else:
            tk.Label(self.root, text="No Packs in Inventory").pack(pady=10)

        tk.Button(self.root, text="Back", command=self.inventory_menu).pack(pady=20)

    def card_inventory_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Card Inventory", font=("Helvetica", 18)).pack(pady=20)

        if self.player_cards:
            for card in self.player_cards:
                tk.Label(self.root, text=card, font=("Helvetica", 14)).pack(pady=5)
        else:
            tk.Label(self.root, text="No Cards in Inventory").pack(pady=10)

        tk.Button(self.root, text="Back", command=self.inventory_menu).pack(pady=20)

    def market_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Market", font=("Helvetica", 18)).pack(pady=20)

        if self.player_cards:
            for i, card in enumerate(self.player_cards):
                price = self.get_card_price(card)
                tk.Button(self.root, text=f"Sell {card} for {price} Coins",
                          command=lambda idx=i, price=price: self.sell_card(idx, price)).pack(pady=5)
        else:
            tk.Label(self.root, text="No Cards to Sell").pack(pady=10)

        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=20)

    def sell_card(self, index, price):
        card = self.player_cards.pop(index)
        self.player_currency += price
        messagebox.showinfo("Card Sold", f"You sold {card} for {price} coins!")
        self.market_menu()

    def get_card_price(self, card):
        """ Determines the selling price of a card based on its rarity and variant. """
        base_prices = {
            "common": 120,         # 4x boost for common cards
            "uncommon": 300,       # 5x boost for uncommon cards
            "rare": 300,           # 2x boost for rare cards
            "super rare": 450,     # 1.5x boost for super rare cards
            "epic": 600,
            "mythic": 1500,
            "mythic": 1500,
            "legendary": 3000,
            "godlike": 6000,
            "star": 15000
        }
        
        for rarity in base_prices:
            if rarity in card.lower():
                price = base_prices[rarity]
                break
        else:
            price = 0

        # Adjust price for shiny or shadow variants
        if "shiny" in card.lower():
            price *= 1.5
        elif "shadow" in card.lower():
            price *= 2.5

        # Random fluctuation in price
        price = int(price * (random.uniform(0.9, 1.1)))

        return price

    def open_pack_animation(self, index):
        """Animates the card pack sliding upwards into the middle and fading out to reveal the card."""
        pack_name = self.player_inventory.pop(index)
        result = self.generate_cards(pack_name)

        if isinstance(result, list):  # If a card was generated
            self.player_cards.extend(result)
            card_obtained = result[0]
        else:  # If a refund was given
            card_obtained = result

        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        # Create the "Back to Inventory" button first
        back_button = tk.Button(self.root, text="Back to Inventory", command=self.inventory_menu)
        back_button.pack(pady=20)

        # Pack image placeholder, centered under the back button
        pack_img = tk.Label(self.root, text="[Pack Image]", font=("Helvetica", 18), bg="brown", fg="white")
        pack_img.place(relx=0.5, rely=0.5, anchor='center')

        # Start the animation of the pack sliding upwards
        self.slide_pack_up(pack_img, card_obtained)

    def slide_pack_up(self, pack_img, card_obtained):
        """Animate the card pack sliding upwards into the middle of the screen."""
        def animate_slide(step=10):
            # Move the pack up by `step` pixels
            x, y = pack_img.winfo_x(), pack_img.winfo_y()
            if y > 200:  # Slide to a position under the "Back to Inventory" button
                pack_img.place(x=x, y=y-step)
                self.root.after(50, animate_slide)
            else:
                # Once the pack is in place, start fading it out
                self.fade_pack(pack_img, card_obtained)

        animate_slide()

    def fade_pack(self, pack_img, card_obtained):
        """Fades out the card pack image and reveals the card or refund."""
        def animate_fade(alpha=1.0, step=0.1):
            # Reduce the transparency by step
            if alpha > 0:
                pack_img.config(fg=f'#{int(alpha*255):02x}0000')  # Fade out effect
                self.root.after(50, animate_fade, alpha-step)
            else:
                # Pack has faded out, reveal the card or refund
                pack_img.destroy()
                self.reveal_card(card_obtained)

        animate_fade()

    def reveal_card(self, card_obtained):
        """Reveal the card or refund after the pack has faded away."""
        if isinstance(card_obtained, str) and card_obtained.startswith("Refund"):
            card_label = tk.Label(self.root, text=card_obtained, font=("Helvetica", 18), bg="green", fg="white")
        else:
            card_label = tk.Label(self.root, text=card_obtained, font=("Helvetica", 18), bg="gold", fg="black")
        
        card_label.place(relx=0.5, rely=0.5, anchor='center')  # Centered under the "Back to Inventory" button

    def generate_cards(self, pack_name):
        """Generates cards from a given pack based on its rarity distribution or refunds twice the pack cost."""
        if random.random() <= REFUND_CHANCE:
            refund_amount = CARD_PACKS[pack_name]["cost"] * 2
            self.player_currency += refund_amount
            return f"Refund! You got {refund_amount} Coins"

        pack_info = CARD_PACKS[pack_name]
        rarity_distribution = pack_info["rarity_distribution"]

        # Select the card rarity based on the distribution probabilities
        rarities = list(rarity_distribution.keys())
        probabilities = list(rarity_distribution.values())

        selected_rarity = random.choices(rarities, probabilities, k=1)[0]
        
        # Determine if the card is shiny or shadow variant
        card_variant = ""
        if random.random() <= SHINY_CHANCE:
            card_variant = "Shiny "
        elif random.random() <= SHADOW_CHANCE:
            card_variant = "Shadow "

        card_name = f"{card_variant}{selected_rarity.capitalize()} Card"

        return [card_name]

if __name__ == "__main__":
    root = tk.Tk()
    app = CardGameApp(root)
    root.mainloop()