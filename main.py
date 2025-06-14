
from playwright.sync_api import sync_playwright
import time, re, numpy as np, requests, os, json, pytz
import scipy.stats as st
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


URLS = [
    "https://maps.app.goo.gl/kKeL7nBAjbzNE2Zq6",
    "https://maps.app.goo.gl/Z8wkjniiEQcR3GHG7",
    "https://maps.app.goo.gl/XNddMiLXiH1x8Uxb6",
    "https://maps.app.goo.gl/S8CxP5Z8wNXpD1bf7",
    "https://maps.app.goo.gl/pqhATKVwytaWhJMh9",
    "https://maps.app.goo.gl/vRWE5DjtRcSD2Dzs5",
    "https://maps.app.goo.gl/defV5kJAkUSpv2DE7",
    "https://maps.app.goo.gl/1vKarATSeAkBBk5u8",
    "https://maps.app.goo.gl/QAJDsLxxurCdgrBh8",
    "https://maps.app.goo.gl/WKyXwt3XYF3g2v6LA",
    "https://maps.app.goo.gl/Wb3Arspg8G81ceYr5",
    "https://maps.app.goo.gl/3TmEumFsQPT5yuNn8",
    "https://maps.app.goo.gl/FweHVWMD3UkZDD386",
    "https://maps.app.goo.gl/HLtADMWqJNUYMrVCA",
    "https://maps.app.goo.gl/KRFzxWrPFjQZ2k6u9",
    "https://maps.app.goo.gl/bB2D8DPqHHePZEo8A",
    "https://maps.app.goo.gl/1USxasGA7dxo3jGt7",
    "https://maps.app.goo.gl/hHqVuyqWuiCxmXRt6",
    "https://maps.app.goo.gl/H5StMDKmGtLaWi9F8",
    "https://maps.app.goo.gl/CwRvKzfEhNEC2PDbA",
    "https://maps.app.goo.gl/jj67D7XhazAJUWBR6",
    "https://maps.app.goo.gl/xP3BpXo3pTYFTAua8",
    "https://maps.app.goo.gl/BJPrQNR3m4mvdQGRA",
    "https://maps.app.goo.gl/bSTkxsu9CLvJjciUA",
    "https://maps.app.goo.gl/gs1GK95vYbuMHGgh7",
    "https://maps.app.goo.gl/CTaqSGqm35H2w3B2A",
    "https://maps.app.goo.gl/q2eGVDHvfmbxRKodA",
    "https://maps.app.goo.gl/uH6VSbaEBMKXSAn49",
    "https://maps.app.goo.gl/iGbgkAmVpzeLEYEX6",
    "https://maps.app.goo.gl/jCCajz7N3X7Pqexx5",
    "https://maps.app.goo.gl/24dM71bTWS5bwUCA7",
]

class History:
    def __init__(self):
        self.values = self.read()

    def push(self, value):
        self.values.append([int(time.time()), value])
        self.values = self.values[-100:]
        self.write()

    def reset(self):
        self.values = []
        self.write()

    def read(self):
        if os.path.exists("history.json"):
            with open("history.json", "r") as f:
                return json.load(f)

        return []

    def write(self):
        with open("history.json", "w") as f:
            json.dump(self.values, f)
    

class Main:
    def __init__(self, 
            p, 
            sensitivity=100 # Lower numbers means score tends towards 100
        ):

        self.h = History()
        self.sensitivity = sensitivity

        self.browser = p.chromium.launch_persistent_context(
            user_data_dir="profile",
            channel='chrome',
            headless=True
        )
        self.page = self.browser.new_page()
    
    def start(self):
        while True:

            if self.is_closed():
                self.set("latest", {"score": None, "closed":True, "epoch": int(time.time())})
                self.h.reset()

            else:
                score = self.__call__()
                if not score is None:
                    self.h.push(score)
                    score = np.mean([i[1] for i in self.h.values[-3:]])
                    self.set("latest", {"closed":False, "score": score, "epoch": int(time.time())})
                    self.set("history", {"scores": self.h.values})    

            time.sleep(60 * 5)

    def is_closed(self):
        dc_tz = pytz.timezone('America/New_York')
        dc_time = datetime.now(dc_tz)
        return 3 <= dc_time.hour < 6
    
    def get_times(self, url:str):
        
        self.page.goto(url)
        time.sleep(1)
        
        element = self.page.locator('[aria-label*="Currently"][aria-label*="busy, usually"][aria-label*="busy."]')
        
        if element.count() > 0:
            aria_label = element.get_attribute('aria-label')
            match = re.match(r'Currently (\d+)% busy, usually (\d+)% busy\.', aria_label)
            
            if match:
                return (
                    int(match.group(1)), # [0, 100] 
                    int(match.group(2))  # [0, 100]
                )
        
        return None

    def __call__(self):
        numbers = []
        
        for url in tqdm(URLS):
            numbers.append(self.get_times(url))
            
        numbers = [i for i in numbers if not i is None]

        if len(numbers) < 3:
            print("Could not compute score, might be bot detected or too early.")
            self.h.reset()
            return -1

        delta = [abs(i[0] - i[1]) / self.sensitivity for i in numbers]
        score = np.mean(delta)
        return round((st.norm.cdf(score)-0.5) * 200, 2)

    def set(self, key:str, data:dict):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        response = requests.patch(
            f"{supabase_url}?key=eq.{key}",
            json={"value": json.dumps(data)},
            headers=headers
        )

        return response.status_code == 200
            

if __name__ == "__main__":
    with sync_playwright() as p:
        print(Main(p).start())

