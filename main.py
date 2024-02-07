from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.lang import Builder

import requests
from colorama import init, Fore

init(autoreset=True)  # Initialize colorama

Builder.load_string("""
<MyLayout>:
    orientation: 'vertical'
    Label:
        id: status_label
        text: 'Program Running'
        font_size: '20sp'
        color: 0, 1, 0, 1  # Green color
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(48)  # Adjust the height as needed
        spacing: dp(10)  # Adjust the spacing as needed
        pos_hint: {'center_x': 0.5, 'center_y': 0.1}  # Adjust the position as needed
        ToggleButton:
            id: toggle_button
            text: 'Pause/Resume'
            on_press: root.toggle_program()
""")

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.status_label = Label(text='Program Running', font_size='20sp', color=(0, 1, 0, 1))
        self.add_widget(self.status_label)

        self.toggle_button = self.ids.toggle_button  # Reference the ToggleButton by its id
        self.paused = False
        self.previous_data = None  # Declare previous_data as an attribute

        Clock.schedule_interval(self.update_data, 5)  # Fetch data every 5 seconds

    def toggle_program(self, *args):
        self.paused = not self.paused
        self.status_label.text = 'Program Paused' if self.paused else 'Program Running'
        self.status_label.color = (1, 0, 0, 1) if self.paused else (0, 1, 0, 1)

    def update_data(self, dt):
        if not self.paused:
            current_data = fetch_stock_data()
            compared_data = compare_stock_data(current_data, self.previous_data)
            display_stock_data(compared_data)
            self.previous_data = current_data  # Update previous_data



def fetch_stock_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch.")
            return None
    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching data:", e)
        return None  # Your existing fetch_stock_data function...

def compare_stock_data(current_data, previous_data):
    if current_data is None or previous_data is None:
        return []  # Return an empty list if any data is missing

    compared_data = []
    for current_stock in current_data.get("data", []):
        current_symbol = current_stock["symbol"]
        current_price = float(current_stock["lastPrice"])
        previous_price = None
        day_high = float(current_stock["dayHigh"])
        day_low = float(current_stock["dayLow"])

        for previous_stock in previous_data.get("data", []):
            if previous_stock["symbol"] == current_symbol:
                previous_price = float(previous_stock["lastPrice"])
                break

        if previous_price is not None:
            change_percent = (current_price - previous_price) / previous_price * 100

            # Check if the stock is at day high or day low
            stock_status = ""
            if current_price == day_high:
                stock_status = " (Day High)"
            elif current_price == day_low:
                stock_status = " (Day Low)"

            compared_data.append((current_symbol, change_percent, stock_status, current_price))
    return compared_data  # Your existing compare_stock_data function...

def display_stock_data(compared_data):
    compared_data.sort(key=lambda x: x[1], reverse=True)  # Sort by percentage change in descending order

    print("")
    for stock, change_percent, stock_status, last_price in compared_data[:10]:
        if change_percent > 0:
            color = Fore.LIGHTGREEN_EX
            print(f"{stock}\t: {color}{change_percent:.2f}%{stock_status} - {last_price}")

    print("")
    for stock, change_percent, stock_status, last_price in compared_data[-5:]:
        if change_percent < 0:
            color = Fore.LIGHTRED_EX
            print(f"{stock}\t: {color}{change_percent:.2f}%{stock_status} - {last_price}")

    print("-" * 5)
previous_data = fetch_stock_data()

class MyApp(App):
    def build(self):
        return MyLayout()

if __name__ == '__main__':
    MyApp().run()
