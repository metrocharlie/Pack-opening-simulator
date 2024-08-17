import tkinter as tk
import random
import pickle
from tkinter import messagebox
from PIL import Image, ImageTk

# Define the card packs with costs and rarity distributions
CARD_PACKS = {
    "Bronze Pack": {"cost": 100, "rarity_distribution": {"common": 70, "uncommon": 20, "rare": 10}, "icon_path": "assets/packs/images/bronze_pack_animation.png"},
    "Silver Pack": {"cost": 200, "rarity_distribution": {"common": 40, "uncommon": 45, "rare": 10, "super rare": 5}, "icon_path": "assets/packs/images/silver_pack_animation.png"},
    "Gold Pack": {"cost": 500, "rarity_distribution": {"uncommon": 10, "rare": 40, "super rare": 35, "epic": 15}, "icon_path": "assets/packs/images/gold_pack_animation.png"},
    "Ruby Pack": {"cost": 1000, "rarity_distribution": {"rare": 30, "super rare": 40, "epic": 20, "mythic": 10}, "icon_path": "assets/packs/images/ruby_pack_animation.png"},
    "Emerald Pack": {"cost": 2000, "rarity_distribution": {"super rare": 20, "epic": 40, "mythic": 30, "legendary": 10}, "icon_path": "assets/packs/images/emerald_pack_animation.png"},
    "Diamond Pack": {"cost": 3000, "rarity_distribution": {"epic": 45, "mythic": 25, "legendary": 25, "godlike": 5}, "icon_path": "assets/packs/images/diamond_pack_animation.png"},
    "Stardust Pack": {"cost": 5000, "rarity_distribution": {"legendary": 70, "godlike": 25, "star": 5}, "icon_path": "assets/packs/images/stardust_pack_animation.png"},
}

# Chances for shiny and shadow cards
SHINY_CHANCE = 0.10
SHADOW_CHANCE = 0.01
REFUND_CHANCE = 0.05  # 5% chance to get twice the money you spent back

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

        self.player_currency = 180
        self.player_inventory = []
        self.player_cards = []
        self.currency_label = None

        self.icons = {}
        self.load_icons()

        saved_data = load_game()
        if saved_data:
            self.player_currency, self.player_inventory, self.player_cards = saved_data

        self.start_coin_reward_system()
        self.main_menu()

    def load_icons(self):
        """Load all the icons required for the game."""
        for pack_name, pack_info in CARD_PACKS.items():
            try:
                image = Image.open(pack_info["icon_path"])
                image = image.resize((50, 50), Image.LANCZOS)
                self.icons[pack_name] = ImageTk.PhotoImage(image)
            except FileNotFoundError:
                messagebox.showerror("Error", f"Image for {pack_name} not found at {pack_info['icon_path']}")

        # Load animation images for each pack type
        self.pack_animation_images = {}
        for pack_name in CARD_PACKS.keys():
            try:
                animation_image = Image.open(f"assets/packs/images/{pack_name.lower().replace(' ', '_')}_animation.png")
                animation_image = animation_image.resize((200, 200), Image.LANCZOS)
                self.pack_animation_images[pack_name] = ImageTk.PhotoImage(animation_image)
            except FileNotFoundError:
                messagebox.showerror("Error", f"Animation image for {pack_name} not found.")

    def start_coin_reward_system(self):
        """Awards the player 20 coins every 2 minutes."""
        self.player_currency += 20
        self.update_currency_display()
        self.root.after(2 * 60 * 1000, self.start_coin_reward_system)

    def update_currency_display(self):
        """Updates the currency display in the top right corner of the window."""
        # Remove the old label if it exists
        if self.currency_label:
            self.currency_label.destroy()

        # Create a new label to display the current currency
        self.currency_label = tk.Label(self.root, text=f"Coins: {self.player_currency}", font=("Helvetica", 14))
        self.currency_label.place(relx=0.98, rely=0.02, anchor='ne')

    def main_menu(self):
        """Main menu setup."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Card Pack Opening Game", font=("Helvetica", 24)).pack(pady=20)

        tk.Button(self.root, text="Shop", width=20, command=self.shop_menu).pack(pady=10)
        tk.Button(self.root, text="Inventory", width=20, command=self.inventory_menu).pack(pady=10)
        tk.Button(self.root, text="Market", width=20, command=self.market_menu).pack(pady=10)
        tk.Button(self.root, text="Save Progress", width=20, command=self.save_progress).pack(pady=10)
        tk.Button(self.root, text="Exit", width=20, command=self.root.quit).pack(pady=10)

    def shop_menu(self):
        """Display the shop menu where players can buy packs."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Shop", font=("Helvetica", 18)).pack(pady=20)

        for pack_name, pack_info in CARD_PACKS.items():
            icon = self.icons.get(pack_name)
            frame = tk.Frame(self.root)
            frame.pack(pady=5)

            tk.Label(frame, image=icon).pack(side='left', padx=10)
            tk.Button(frame, text=f"{pack_name} - {pack_info['cost']} Coins",
                      width=30,
                      command=lambda name=pack_name: self.select_pack_quantity(name)).pack(side='left')

        tk.Button(self.root, text="Back", width=20, command=self.main_menu).pack(pady=20)

    def select_pack_quantity(self, pack_name):
        """Display a menu to select the quantity of packs to buy."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text=f"Buy {pack_name}", font=("Helvetica", 18)).pack(pady=20)

        def purchase(quantity):
            self.buy_pack(pack_name, quantity)

        for i in range(1, 6):  # Allows selection of 1 to 5 packs
            tk.Button(self.root, text=f"Buy {i} {pack_name}(s)",
                      width=30,
                      command=lambda quantity=i: purchase(quantity)).pack(pady=5)

        tk.Button(self.root, text="Back", width=20, command=self.shop_menu).pack(pady=20)

    def buy_pack(self, pack_name, quantity=1):
        total_cost = CARD_PACKS[pack_name]["cost"] * quantity
        if self.player_currency >= total_cost:
            self.player_currency -= total_cost
            self.player_inventory.extend([pack_name] * quantity)
            messagebox.showinfo("Pack Purchased", f"You bought {quantity} {pack_name}(s)!")
            self.inventory_menu()  # Go to inventory to reflect the purchase
        else:
            messagebox.showerror("Error", "Not enough currency!")
            self.shop_menu()


    def inventory_menu(self):
        """Displays the inventory menu."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Inventory", font=("Helvetica", 18)).pack(pady=20)

        tk.Button(self.root, text="Open Packs", width=20, command=self.open_pack_inventory).pack(pady=10)
        tk.Button(self.root, text="View Cards", width=20, command=self.card_inventory_menu).pack(pady=10)
        tk.Button(self.root, text="Back", width=20, command=self.main_menu).pack(pady=20)

    def open_pack_inventory(self):
        """Displays the list of packs available to open."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Your Packs", font=("Helvetica", 18)).pack(pady=20)

        if self.player_inventory:
            for i, pack in enumerate(self.player_inventory):
                icon = self.icons.get(pack)
                frame = tk.Frame(self.root)
                frame.pack(pady=5)

                tk.Label(frame, image=icon).pack(side='left', padx=10)
                tk.Button(frame, text=f"Open {pack}",
                          width=30,
                          command=lambda idx=i: self.open_pack_animation(idx)).pack(side='left')
        else:
            tk.Label(self.root, text="No Packs in Inventory").pack(pady=10)

        tk.Button(self.root, text="Back", width=20, command=self.inventory_menu).pack(pady=20)

    def card_inventory_menu(self):
        """Displays the player's card collection."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Your Cards", font=("Helvetica", 18)).pack(pady=20)

        if self.player_cards:
            for card in self.player_cards:
                tk.Label(self.root, text=card, font=("Helvetica", 14)).pack(pady=2)
        else:
            tk.Label(self.root, text="No Cards in Inventory").pack(pady=10)

        tk.Button(self.root, text="Back", width=20, command=self.inventory_menu).pack(pady=20)

    def market_menu(self):
        """Displays the market where players can sell their cards."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Market", font=("Helvetica", 18)).pack(pady=20)

        if self.player_cards:
            for i, card in enumerate(self.player_cards):
                price = self.get_card_price(card)
                tk.Button(self.root, text=f"Sell {card} for {price} Coins",
                          width=40,
                          command=lambda idx=i, price=price: self.sell_card(idx, price)).pack(pady=5)
        else:
            tk.Label(self.root, text="No Cards to Sell").pack(pady=10)

        tk.Button(self.root, text="Back", width=20, command=self.main_menu).pack(pady=20)

    def sell_card(self, index, price):
        card = self.player_cards.pop(index)
        self.player_currency += price
        messagebox.showinfo("Card Sold", f"You sold {card} for {price} coins!")
        self.market_menu()

    def get_card_price(self, card):
        """Determines the selling price of a card based on its rarity and variant."""
        base_prices = {
            "common": 110,
            "uncommon": 175,
            "rare": 250,
            "super rare": 400,
            "epic": 800,
            "mythic": 1600,
            "legendary": 3200,
            "godlike": 6400,
            "star": 30000
        }

        price = 0
        for rarity in base_prices:
            if rarity in card.lower():
                price = base_prices[rarity]
                break

        # Adjust price for shiny or shadow variants
        if "shiny" in card.lower():
            price *= 2
        elif "shadow" in card.lower():
            price *= 3

        return price

    def open_pack_animation(self, index):
        """Animates the card pack opening with the correct animation based on the pack."""
        pack_name = self.player_inventory.pop(index)  # Remove the pack from inventory
        result = self.generate_card(pack_name)        # Generate the card based on the pack

        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        # Get the correct animation image for the pack
        pack_animation_image = self.pack_animation_images.get(pack_name, None)
        
        if pack_animation_image:
            pack_img = tk.Label(self.root, image=pack_animation_image)
            pack_img.pack(pady=20)
            self.root.after(2000, lambda: self.reveal_card(result))
        else:
            self.reveal_card(result)


    def reveal_card(self, card_obtained):
        """Displays the obtained card after opening a pack."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="You obtained:", font=("Helvetica", 18)).pack(pady=20)
        tk.Label(self.root, text=card_obtained, font=("Helvetica", 16)).pack(pady=10)

        tk.Button(self.root, text="Back to Inventory", width=20, command=self.inventory_menu).pack(pady=20)

    def generate_card(self, pack_name):
        """Generates a card from a given pack based on its rarity distribution or provides a refund."""
        if random.random() <= REFUND_CHANCE:
            refund_amount = CARD_PACKS[pack_name]["cost"] * 2
            self.player_currency += refund_amount
            return f"Refund! You received {refund_amount} Coins."

        pack_info = CARD_PACKS[pack_name]
        rarity_distribution = pack_info["rarity_distribution"]

        rarities = list(rarity_distribution.keys())
        probabilities = list(rarity_distribution.values())

        selected_rarity = random.choices(rarities, probabilities, k=1)[0]

        # Determine if the card is shiny or shadow variant
        card_variant = ""
        variant_roll = random.random()
        if variant_roll <= SHADOW_CHANCE:
            card_variant = "Shadow "
        elif variant_roll <= SHINY_CHANCE + SHADOW_CHANCE:
            card_variant = "Shiny "

        card_name = f"{card_variant}{selected_rarity.capitalize()} Card"

        self.player_cards.append(card_name)
        return card_name

    def save_progress(self):
        """Saves the current game progress."""
        data = (self.player_currency, self.player_inventory, self.player_cards)
        save_game(data)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")  # Set the window size
    app = CardGameApp(root)
    root.mainloop()