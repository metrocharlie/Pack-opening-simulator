import tkinter as tk
import random
import pickle
from tkinter import messagebox, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk
import re

# Updated card packs including Easter Egg packs
CARD_PACKS = {
    "Bronze Pack": {"cost": 100, "currency": "coins", "rarity_distribution": {"common": 70, "uncommon": 20, "rare": 10}, "icon_path": "assets/packs/images/bronze_pack_animation.png"},
    "Silver Pack": {"cost": 200, "currency": "coins", "rarity_distribution": {"common": 10, "uncommon": 30, "rare": 35, "super rare": 25}, "icon_path": "assets/packs/images/silver_pack_animation.png"},
    "Gold Pack": {"cost": 500, "currency": "coins", "rarity_distribution": {"uncommon": 10, "rare": 40, "super rare": 35, "epic": 15}, "icon_path": "assets/packs/images/gold_pack_animation.png"},
    "Ruby Pack": {"cost": 1000, "currency": "coins", "rarity_distribution": {"rare": 30, "super rare": 40, "epic": 20, "mythic": 10}, "icon_path": "assets/packs/images/ruby_pack_animation.png"},
    "Emerald Pack": {"cost": 2000, "currency": "coins", "rarity_distribution": {"super rare": 20, "epic": 40, "mythic": 30, "legendary": 10}, "icon_path": "assets/packs/images/emerald_pack_animation.png"},
    "Diamond Pack": {"cost": 3000, "currency": "coins", "rarity_distribution": {"epic": 45, "mythic": 25, "legendary": 25, "godlike": 5}, "icon_path": "assets/packs/images/diamond_pack_animation.png"},
    "Stardust Pack": {"cost": 5000, "currency": "coins", "rarity_distribution": {"legendary": 70, "godlike": 25, "star": 5}, "icon_path": "assets/packs/images/stardust_pack_animation.png"},
    "Cold Pack": {"cost": 1, "currency": "snow", "rarity_distribution": {"cold common": 70, "cold uncommon": 20, "cold rare": 10}, "icon_path": "assets/packs/images/cold_pack_animation.png"},
    "Frost Pack": {"cost": 10, "currency": "snow", "rarity_distribution": {"cold uncommon": 40, "cold rare": 40, "cold super rare": 20}, "icon_path": "assets/packs/images/frost_pack_animation.png"},
    "Ice Pack": {"cost": 25, "currency": "snow", "rarity_distribution": {"cold rare": 30, "cold super rare": 40, "cold epic": 30}, "icon_path": "assets/packs/images/ice_pack_animation.png"},
    "Snow Pack": {"cost": 75, "currency": "snow", "rarity_distribution": {"cold super rare": 30, "cold epic": 50, "cold mythic": 20}, "icon_path": "assets/packs/images/snow_pack_animation.png"},
    "Blizzard Pack": {"cost": 150, "currency": "snow", "rarity_distribution": {"cold epic": 40, "cold mythic": 40, "cold legendary": 20}, "icon_path": "assets/packs/images/blizzard_pack_animation.png"},
    
    # Easter Egg Packs (hidden packs)
    "Ollie Pack": {"cost": 0, "currency": "special", "rarity_distribution": {"ollie rare": 50, "ollie epic": 30, "ollie legendary": 20}, "icon_path": "assets/packs/images/ollie_pack_animation.png", "purchasable": False},
    "Plasma Pack": {"cost": 0, "currency": "special", "rarity_distribution": {"plasma common": 40, "plasma rare": 40, "plasma epic": 20}, "icon_path": "assets/packs/images/plasma_pack_animation.png", "purchasable": False},
    "Hacker Pack": {"cost": 0, "currency": "special", "rarity_distribution": {"hacker uncommon": 40, "hacker rare": 30, "hacker epic": 20, "hacker mythic": 10}, "icon_path": "assets/packs/images/hacker_pack_animation.png", "purchasable": False},
}

# Chances for shiny, shadow, and cold cards
SHINY_CHANCE = 0.10
SHADOW_CHANCE = 0.01
COLD_CHANCE = 0.01  # 1% chance from normal packs
REFUND_CHANCE = 0.05  # 5% chance to get twice the money you spent back

# Easter Egg Chance
EASTER_EGG_CHANCE = 0.005  # 0.5% chance
EASTER_EGG_OPTIONS = {
    "Ollie Pack": 33,
    "Plasma Pack": 33,
    "Hacker Pack": 33,
    "Million Coins": 1,
}

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
        self.root.attributes('-fullscreen', True)

        self.player_currency = 180
        self.player_snow = 0  # New Snow currency
        self.player_inventory = []
        self.player_cards = []
        self.currency_label = None
        self.snow_label = None  # Label for Snow currency

        self.icons = {}
        self.load_icons()

        saved_data = load_game()
        if saved_data:
            self.player_currency, self.player_snow, self.player_inventory, self.player_cards = saved_data

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
        # Remove the old labels if they exist
        if self.currency_label:
            self.currency_label.destroy()
        if self.snow_label:
            self.snow_label.destroy()

        # Create new labels to display the current currency
        self.currency_label = tk.Label(self.root, text=f"Coins: {self.player_currency}", font=("Helvetica", 14))
        self.currency_label.place(relx=0.98, rely=0.02, anchor='ne')

        self.snow_label = tk.Label(self.root, text=f"Snow: {self.player_snow}", font=("Helvetica", 14))
        self.snow_label.place(relx=0.98, rely=0.07, anchor='ne')

    def main_menu(self):
        """Main menu setup."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Card Pack Opening Game", font=("Helvetica", 24)).pack(pady=20)

        tk.Button(self.root, text="Shop", width=20, command=self.shop_menu).pack(pady=10)
        tk.Button(self.root, text="Inventory", width=20, command=self.inventory_menu).pack(pady=10)
        tk.Button(self.root, text="Market", width=20, command=self.market_menu).pack(pady=10)
        tk.Button(self.root, text="Convert Currency", width=20, command=self.convert_currency_menu).pack(pady=10)
        tk.Button(self.root, text="Save Progress", width=20, command=self.save_progress).pack(pady=10)
        tk.Button(self.root, text="Exit", width=20, command=self.root.quit).pack(pady=10)

    def convert_currency_menu(self):
        """Menu to convert between Coins and Snow."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_currency_display()

        tk.Label(self.root, text="Convert Currency", font=("Helvetica", 18)).pack(pady=20)

        # Conversion from Coins to Snow
        tk.Button(self.root, text="Convert 250 Coins to 1 Snow",
                  width=30, command=self.convert_coins_to_snow).pack(pady=5)

        # Conversion from Snow to Coins
        tk.Button(self.root, text="Convert 1 Snow to 250 Coins",
                  width=30, command=self.convert_snow_to_coins).pack(pady=5)

        tk.Button(self.root, text="Back", width=20, command=self.main_menu).pack(pady=20)

    def convert_coins_to_snow(self):
        """Converts 250 Coins to 1 Snow."""
        if self.player_currency >= 250:
            self.player_currency -= 250
            self.player_snow += 1
            self.update_currency_display()
            messagebox.showinfo("Conversion Successful", "Converted 250 Coins to 1 Snow!")
        else:
            messagebox.showerror("Error", "Not enough coins to convert!")
        self.convert_currency_menu()

    def convert_snow_to_coins(self):
        """Converts 1 Snow to 250 Coins."""
        if self.player_snow >= 1:
            self.player_snow -= 1
            self.player_currency += 250
            self.update_currency_display()
            messagebox.showinfo("Conversion Successful", "Converted 1 Snow to 250 Coins!")
        else:
            messagebox.showerror("Error", "Not enough Snow to convert!")
        self.convert_currency_menu()

    def shop_menu(self):
        """Display the shop menu where players can buy packs."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a canvas and a frame that will hold all the pack buttons
        canvas = tk.Canvas(self.root)
        scroll_y = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_y.pack(anchor="center")

        # This frame will be where the actual widgets (buttons, labels) are placed
        scrollable_frame = tk.Frame(canvas)

        # Function to configure scroll region
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Add a binding to the mouse scroll wheel
        def _on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        # Create a window inside the canvas to hold the scrollable frame
        new_window_with = 800
        window_width = self.root.winfo_width()
        canvas.create_window(((window_width - new_window_with) // 2, 0), window=scrollable_frame, anchor="nw", width=new_window_with)
        canvas.configure(yscrollcommand=scroll_y.set)

        # Title
        tk.Label(scrollable_frame, text="Shop", font=("Helvetica", 18)).pack(pady=20)

        # Outer frame to help with centering
        outer_frame = tk.Frame(scrollable_frame)
        outer_frame.pack(anchor="center")

        # Pack frame that will hold the pack options
        pack_frame = tk.Frame(outer_frame)
        pack_frame.pack(anchor="center", pady=20)

        # Add pack options inside pack_frame
        for pack_name, pack_info in CARD_PACKS.items():
            if not pack_info.get("purchasable", True):
                continue  # Skip Easter Egg packs (not purchasable)

            icon = self.icons.get(pack_name)

            frame = tk.Frame(pack_frame)
            frame.pack(pady=5)

            # Determine the currency to display
            currency_type = "Coins" if pack_info["currency"] == "coins" else "Snow"
            cost_text = f"{pack_info['cost']} {currency_type}"

            tk.Label(frame, image=icon).pack(side='left', padx=10)
            tk.Button(frame, text=f"{pack_name} - {cost_text}",
                    width=30,
                    command=lambda name=pack_name: self.select_pack_quantity(name)).pack(side='left')

        # Position the back button at the bottom of the scrollable_frame, centered
        tk.Button(scrollable_frame, text="Back", width=20, command=self.main_menu).pack(pady=20)

        # Pack everything in the main root window
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Ensure currency display is updated after everything is set up
        self.update_currency_display()

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
        pack_info = CARD_PACKS[pack_name]
        total_cost = pack_info["cost"] * quantity

        if pack_info["currency"] == "coins":
            if self.player_currency >= total_cost:
                self.player_currency -= total_cost
                self.player_inventory.extend([pack_name] * quantity)
                messagebox.showinfo("Pack Purchased", f"You bought {quantity} {pack_name}(s)!")
                self.inventory_menu()  # Go to inventory to reflect the purchase
            else:
                messagebox.showerror("Error", "Not enough currency!")
                self.shop_menu()
        elif pack_info["currency"] == "snow":
            if self.player_snow >= total_cost:
                self.player_snow -= total_cost
                self.player_inventory.extend([pack_name] * quantity)
                messagebox.showinfo("Pack Purchased", f"You bought {quantity} {pack_name}(s)!")
                self.inventory_menu()  # Go to inventory to reflect the purchase
            else:
                messagebox.showerror("Error", "Not enough Snow!")
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
                try:
                    price = self.get_card_price(card)
                    tk.Button(self.root, text=f"Sell {card} for {price} Coins",
                            width=40,
                            command=lambda idx=i, price=price: self.sell_card(idx, price)).pack(pady=5)
                except Exception as e:
                    # Print the exception in the console for debugging
                    print(f"Error displaying card {card}: {e}")
                    # Show an error messagebox for feedback
                    messagebox.showerror("Error", f"Could not display card: {card}")
        else:
            tk.Label(self.root, text="No Cards to Sell", font=("Helvetica", 14)).pack(pady=10)

        tk.Button(self.root, text="Back", width=20, command=self.main_menu).pack(pady=20)

    def sell_card(self, index, price):
        """Handles selling a card from the inventory."""
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
            "super rare": 500,  # Make sure this is correctly identified
            "epic": 1000,
            "mythic": 1600,
            "legendary": 3200,
            "godlike": 6400,
            "star": 30000,
            "cold common": 220,
            "cold uncommon": 350,
            "cold rare": 500,
            "cold super rare": 800,
            "cold epic": 1600,
            "cold mythic": 3200,
            "cold legendary": 6400,
        }

        # Debugging output to see the exact card name
        print(f"Processing card: {card}")

        card_lower = card.lower().strip()
        price = 0

        # Match rarity, handling potential errors or unusual formats
        matched = False

        # Check for more specific rarities first
        rarity_order = sorted(base_prices.keys(), key=lambda r: len(r), reverse=True)

        for rarity in rarity_order:
            base_price = base_prices[rarity]
            # Debugging output for matching attempt
            print(f"Trying to match rarity '{rarity}' with card '{card_lower}'")
            
            if re.search(r'\b' + re.escape(rarity) + r'\b', card_lower):
                price = base_price
                matched = True
                print(f"Match found: {rarity}, base price: {base_price}")
                break

        if not matched:
            # If no rarity is matched, output an error with more details
            error_message = f"Could not determine the rarity for card: '{card}' (processed as '{card_lower}')"
            print(error_message)
            messagebox.showerror("Error", error_message)
            return 0

        # Adjust the price based on card variants
        if "shiny" in card_lower:
            print(f"Card '{card_lower}' is shiny. Doubling price.")
            price *= 2
        elif "shadow" in card_lower:
            print(f"Card '{card_lower}' is shadow. Tripling price.")
            price *= 3
        elif "cold" in card_lower and "cold" not in rarity:
            print(f"Card '{card_lower}' has cold variant. Doubling price.")
            price *= 2

        # Final debugging output for the determined price
        print(f"Final price for '{card}': {price}")
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

        # Easter Egg logic: 0.5% chance to trigger an Easter Egg
        if random.random() <= EASTER_EGG_CHANCE:
            easter_egg_choice = random.choices(
                list(EASTER_EGG_OPTIONS.keys()), 
                list(EASTER_EGG_OPTIONS.values()), 
                k=1
            )[0]
            
            if easter_egg_choice == "Million Coins":
                self.player_currency += 1_000_000
                return "Easter Egg! You received 1 Million Coins!"
            else:
                self.player_inventory.append(easter_egg_choice)
                return f"Easter Egg! You found a hidden {easter_egg_choice}!"

        # Normal card generation logic based on pack's rarity distribution
        pack_info = CARD_PACKS[pack_name]
        rarity_distribution = pack_info["rarity_distribution"]

        rarities = list(rarity_distribution.keys())
        probabilities = list(rarity_distribution.values())

        selected_rarity = random.choices(rarities, probabilities, k=1)[0]

        # Determine if the card is a variant (Shiny, Shadow, Cold)
        card_variant = ""
        variant_roll = random.random()

        if "cold" not in selected_rarity.lower():  # Cold cards from normal packs
            if variant_roll <= SHADOW_CHANCE:
                card_variant = "Shadow "
            elif variant_roll <= SHINY_CHANCE + SHADOW_CHANCE:
                card_variant = "Shiny "
            elif variant_roll <= COLD_CHANCE + SHINY_CHANCE + SHADOW_CHANCE:
                card_variant = "Cold "

        # Cold packs always give a cold variant
        if "cold" in selected_rarity.lower():
            card_variant = ""  # Avoid adding "Cold" again

        card_name = f"{card_variant}{selected_rarity.capitalize()} Card"

        self.player_cards.append(card_name)
        return card_name

    def save_progress(self):
        """Saves the current game progress."""
        data = (self.player_currency, self.player_snow, self.player_inventory, self.player_cards)
        save_game(data)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")  # Set the window size
    app = CardGameApp(root)
    root.mainloop()