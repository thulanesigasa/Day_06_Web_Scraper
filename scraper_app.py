import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import threading

# Theme Constants
BG_COLOR = "#1F1C2C"
FG_COLOR = "#928DAB"
ACCENT_COLOR = "#928DAB"
FONT_FAMILY = "Arial"

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Day 6: Web Scraper")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)

        self.setup_ui()

    def setup_ui(self):
        # Title Label
        self.title_label = tk.Label(
            self.root,
            text="Quote Scraper",
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
            font=(FONT_FAMILY, 24, "bold"),
            pady=10
        )
        self.title_label.pack()

        # Target Info
        self.target_label = tk.Label(
            self.root,
            text="Target: http://quotes.toscrape.com",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=(FONT_FAMILY, 10, "italic"),
            pady=5
        )
        self.target_label.pack()

        # Scrape Button
        self.scrape_button = tk.Button(
            self.root,
            text="Scrape Quotes",
            command=self.start_scraping_thread,
            bg=ACCENT_COLOR,
            fg=BG_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground=BG_COLOR,
            font=(FONT_FAMILY, 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.scrape_button.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(
            self.root,
            text="",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=(FONT_FAMILY, 10)
        )
        self.status_label.pack()

        # Listbox Frame with Scrollbars
        list_frame = tk.Frame(self.root, bg=BG_COLOR)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.scrollbar_y = tk.Scrollbar(list_frame)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.results_listbox = tk.Listbox(
            list_frame,
            font=(FONT_FAMILY, 11),
            bg=BG_COLOR,
            fg=FG_COLOR,
            selectbackground=FG_COLOR,
            selectforeground=BG_COLOR,
            bd=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar_y.config(command=self.results_listbox.yview)
        self.scrollbar_x.config(command=self.results_listbox.xview)

    def start_scraping_thread(self):
        self.scrape_button.config(state="disabled")
        self.status_label.config(text="Scraping...")
        self.results_listbox.delete(0, tk.END)
        # Run scraping in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.scrape_data)
        thread.start()

    def scrape_data(self):
        url = "http://quotes.toscrape.com"
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            quotes = soup.find_all('div', class_='quote')

            if not quotes:
                self.root.after(0, self.update_gui_error, "No quotes found on the page.")
                return

            scraped_items = []
            for quote in quotes:
                textElement = quote.find('span', class_='text')
                authorElement = quote.find('small', class_='author')
                
                if textElement and authorElement:
                    text = textElement.text
                    author = authorElement.text
                    scraped_items.append(f"{text} - {author}")

            self.root.after(0, self.update_gui_success, scraped_items)

        except requests.exceptions.RequestException as e:
            self.root.after(0, self.update_gui_error, f"Network error: {e}")
        except Exception as e:
            self.root.after(0, self.update_gui_error, f"An error occurred: {e}")

    def update_gui_success(self, items):
        for item in items:
            self.results_listbox.insert(tk.END, item)
        self.status_label.config(text=f"Successfully scraped {len(items)} quotes.")
        self.scrape_button.config(state="normal")

    def update_gui_error(self, error_msg):
        self.status_label.config(text="Scraping failed.")
        messagebox.showerror("Error", error_msg)
        self.scrape_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()
