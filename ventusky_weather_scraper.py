import re
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from PIL import Image
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

# Utility function to select itinerary folder
def get_itinerary_folder():
    app = QApplication(sys.argv)
    folder = QFileDialog.getExistingDirectory(None, "Select Folder Containing Itineraries")
    app.exit()
    if not folder:
        print("No folder selected. Exiting program.")
        sys.exit(0)
    return folder

class weather_scraper:
    def __init__(self, day_delta):
        self.day_delta = day_delta

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        return webdriver.Chrome(options=chrome_options)
    
    def search_location(self, driver, location, layer="feel", zoom=7):
        wait = WebDriverWait(driver, 15)
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=self.day_delta)
        
        time_param = tomorrow.strftime("?t=%Y%m%d/2100")
        driver.get("https://www.ventusky.com" + time_param)

        city_map = {
            "Anchorage": "Anchorage Alaska",
            "Little Rock": "Little Rock Arkansas",
            "Albany": "Albany California",
            "Los Angeles": "Los Angeles California",
            "Palo Alto": "Palo Alto California",
            "Denver": "Denver Colorado",
            "Arvada": "Arvada Colorado",
            "Clinton": "Clinton Connecticut",
            "Wilmington": "Wilmington Delaware",
            "Babcock Ranch": "Babcock Ranch Florida",
            "Naples": "Naples Florida",
            "Jackson": "Jackson Georgia",
            "Riggins": "Riggins Idaho",
            "Galena": "Galena Illinois",
            "Lawrence": "Lawrence Kansas",
            "Dodge City": "Dodge City Kansas",
            "Kenner": "Kenner Louisiana",
            "Dover-Foxcroft": "Dover-Foxcroft Maine",
            "Portland": "Portland Maine",
            "Gloucester": "Gloucester Massachusetts",
            "Kingston": "Kingston Massachusetts",
            "Blue Earth": "Blue Earth Minnesota",
            "Willmar": "Willmar Minnesota",
            "Flowood": "Flowood Mississippi",
            "Saint Ignatius": "Saint Ignatius Montana",
            "Lincoln": "Lincoln Nebraska",
            "Las Vegas": "Las Vegas Nevada",
            "Orford": "Orford New Hampshire",
            "Sussex": "Sussex New Jersey",
            "Toms River": "Toms River New Jersey",
            "Albuquerque": "Albuquerque New Mexico",
            "Croton-on-Hudson": "Croton-on-Hudson New York",
            "New York": "New York New York",
            "Bellefontaine": "Bellefontaine Ohio",
            "Cleveland": "Cleveland Ohio",
            "Grants Pass": "Grants Pass Oregon",
            "North Powder": "North Powder Oregon",
            "Tulsa": "Tulsa Oklahoma",
            "Gettysburg": "Gettysburg Pennsylvania",
            "Scranton": "Scranton Pennsylvania",
            "Nashville": "Nashville Tennessee",
            "Kingsport": "Kingsport Tennessee",
            "Jasper": "Jasper Texas",
            "Kilgore": "Kilgore Texas",
            "Dallas": "Dallas Texas",
            "West Jordan": "West Jordan Utah",
            "American Fork": "American Fork Utah",
            "Montpelier": "Montpelier Vermont",
            "Washington": "Washington District of Columbia",
            "Verona": "Verona Wisconsin",
            "Sheridan": "Sheridan Wyoming"
        }
        location = city_map.get(location, location)

        search_box = wait.until(EC.presence_of_element_located((By.ID, "search-q")))
        search_box.clear()
        search_box.send_keys(location)
        search_box.send_keys(Keys.ENTER)

        try:
            suggestions = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "lat=") and contains(@href, "lon=")]')))
            non_county_suggestion = None
            county_suggestion = None

            for s in suggestions:
                if "county" in s.text.lower():
                    if not county_suggestion:
                        county_suggestion = s
                else:
                    non_county_suggestion = s
                    break

            if non_county_suggestion:
                non_county_suggestion.click()
            elif county_suggestion:
                county_suggestion.click()
            else:
                print(f"No valid clickable suggestion found for {location}")
        except Exception as e:
            print(f"Could not click suggestion for {location}: {e}")

        time.sleep(5)

    def zoom_in(self, driver, times=2):
        wait = WebDriverWait(driver, 15)

        for _ in range(times):
            zoom_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Zoom in"]')))
            zoom_btn.click()
            time.sleep(1)
    
    def zoom_out(self, driver, times=1):
                wait = WebDriverWait(driver, 15)

                for _ in range(times):
                    zoom_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Zoom out"]')))
                    zoom_btn.click()
                    time.sleep(1)

    def switch_layer(self, driver, layer_name):
        wait = WebDriverWait(driver, 10)
        # Wait for the button with the text "Feels like temperature" to appear
        
        if layer_name == "feel":
            text = '//a[contains(text(), "Feels like temperature")]'
        else:
            text = f'//a[contains(text(), "Precipitation")]'

        
        wait.until(EC.presence_of_element_located((By.XPATH, text)))

        layers = driver.find_elements(By.XPATH, text)
        for item in layers:
            if layer_name.lower() in item.text.lower():
                item.click()
                break
        time.sleep(3)

    def capture_centered_screenshot(self, driver, output_path, crop_size=(1040, 780)):
        current_url = driver.current_url
        timestamp = ""
        if "t=" in current_url:
            raw_time = current_url.split("t=")[-1].split("&")[0]
            try:
                dt = datetime.datetime.strptime(raw_time, "%Y%m%d/%H%M")
                timestamp = dt.strftime("%m-%d")
            except:
                timestamp = raw_time.replace("/", "")[4:8] if len(raw_time) >= 8 else "unknown"
        output_path = output_path.replace(".png", f"_{timestamp}.png")
        screenshot_path = output_path.replace(".png", "_full.png")
        driver.save_screenshot(screenshot_path)

        image = Image.open(screenshot_path)
        w, h = image.size
        cx, cy = w // 2, h // 2 
        cw, ch = crop_size
        left = max(cx - cw // 2, 0)
        upper = max(cy - ch // 2, 0)
        right = left + cw
        lower = upper + ch

        cropped = image.crop((left, upper, right, lower))
        cropped.save(output_path)
        os.remove(screenshot_path)

    def get_weather_screenshots(self, location, output_dir):
        driver = self.setup_driver()
        try:
            self.search_location(driver, location)
            self.zoom_in(driver)
            # No folder creation/clearing here; output_dir is the city folder
            # Feels-like temperature
            self.switch_layer(driver, "feel")
            self.capture_centered_screenshot(driver, os.path.join(output_dir, "feels_like.png"))
            # Precipitation
            self.switch_layer(driver, "Precipitation")
            self.capture_centered_screenshot(driver, os.path.join(output_dir, "precipitation.png"))
            print(f"Saved screenshots for {location} in {output_dir}")
        finally:
            driver.quit()

    def get_national_weather_map(self, output_dir):
        driver = self.setup_driver()
        try:
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=self.day_delta)
            time_param = tomorrow.strftime("%Y%m%d/2100")
            url = f"https://www.ventusky.com/?p=55;-101;5&t={time_param}"
            driver.get(url)
            WebDriverWait(driver, 10).until(lambda d: "t=" in d.current_url)
            time.sleep(3)  # Allow time for timestamp to populate in URL
            self.zoom_out(driver, times=3)

            # Make sure Individual/National exists
            national_folder = os.path.join(output_dir, "Individual", "National")
            os.makedirs(national_folder, exist_ok=True)
            # Clear folder
            for file in os.listdir(national_folder):
                file_path = os.path.join(national_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Feels-like temperature
            self.switch_layer(driver, "feel")
            self.capture_centered_screenshot(
                driver,
                os.path.join(national_folder, "feels_like.png"),
                crop_size=(1632, 918)
            )

            # Precipitation
            self.switch_layer(driver, "Precipitation")
            self.capture_centered_screenshot(
                driver,
                os.path.join(national_folder, "precipitation.png"),
                crop_size=(1632, 918)
            )

            # Combine the two images vertically if both exist
            feels_path = next((os.path.join(national_folder, f) for f in os.listdir(national_folder) if f.startswith("feels_like")), None)
            precip_path = next((os.path.join(national_folder, f) for f in os.listdir(national_folder) if f.startswith("precipitation")), None)
            if feels_path and os.path.exists(feels_path) and precip_path and os.path.exists(precip_path):
                img1 = Image.open(feels_path)
                img2 = Image.open(precip_path)
                w = max(img1.width, img2.width)
                h = img1.height + img2.height
                combined = Image.new("RGB", (w, h))
                combined.paste(img1, (0, 0))
                combined.paste(img2, (0, img1.height))
                combined_dir = os.path.join(output_dir, "Combined")
                current_url = driver.current_url
                timestamp = ""
                if "t=" in current_url:
                    raw_time = current_url.split("t=")[-1].split("&")[0]
                    try:
                        dt = datetime.datetime.strptime(raw_time, "%Y%m%d/%H%M")
                        timestamp = dt.strftime("%m-%d")
                    except:
                        timestamp = raw_time.replace("/", "")[4:8]
                else:
                    timestamp = datetime.datetime.now().strftime("%m-%d")  # fallback
                os.makedirs(combined_dir, exist_ok=True)
                combined.save(os.path.join(combined_dir, f"National_{timestamp}.png"))

            print("Saved national weather screenshots")
        finally:
            driver.quit()


    # Extract cities from folder names in a directory
    def extract_cities_from_directory(self, root_dir):
        cities = set()
        folder_pattern = re.compile(r"\d{4} - S\d - [A-Z]{2} ([^-]+) -")
        for entry in os.listdir(root_dir):
            entry_path = os.path.join(root_dir, entry)
            print(f"Inspecting entry: {entry}")
            if not os.path.isdir(entry_path):
                print(f"Skipping non-directory: {entry}")
                continue

            match = folder_pattern.match(entry)
            if match:
                city = match.group(1).strip()
                print(f"Matched city: {city} from folder: {entry}")
                print(f"Extracted city: {city} from: {entry}")
                cities.add(city)
            else:
                print(f"Warning: Folder name format unrecognized - {entry}")

        return sorted(cities)

    def stack_weather_images(self, city_folder, city_name, main_output_dir=None):
        feels_path = next((os.path.join(city_folder, f) for f in os.listdir(city_folder) if f.startswith("feels_like")), None)
        precip_path = next((os.path.join(city_folder, f) for f in os.listdir(city_folder) if f.startswith("precipitation")), None)

        if feels_path and os.path.exists(feels_path) and precip_path and os.path.exists(precip_path):
            img1 = Image.open(feels_path)
            img2 = Image.open(precip_path)
            w = max(img1.width, img2.width)
            h = img1.height + img2.height
            combined = Image.new("RGB", (w, h))
            combined.paste(img1, (0, 0))
            combined.paste(img2, (0, img1.height))
            # Store in Combined under main output dir
            if main_output_dir is None:
                combined_dir = os.path.join(os.path.dirname(city_folder), "Combined")
            else:
                combined_dir = os.path.join(main_output_dir, "Combined")
            os.makedirs(combined_dir, exist_ok=True)
            # Robust timestamp extraction and fallback
            timestamp = ""
            if "_" in os.path.basename(feels_path):
                raw = os.path.basename(feels_path).rsplit("_", 1)[-1].replace(".png", "")
                try:
                    dt = datetime.datetime.strptime(raw, "%m-%d")
                    timestamp = dt.strftime("%m-%d")
                except:
                    timestamp = raw[4:8] if len(raw) >= 8 else raw
            if not timestamp:
                timestamp = datetime.datetime.now().strftime("%m-%d")
            combined.save(os.path.join(combined_dir, f"{city_name}_{timestamp}.png"))

    def run_weather_scraper(self):
        session_map = {
            "4": "Session 4_ July 2 - July 9, 2025",
            "5": "Session 5_ July 9 - 16, 2025",
            "6": "Session 6_ July 16 - 23, 2025",
            "7": "Session 7_ July 23 - 30, 2025"
        }

        print("Available sessions:")
        for key, val in session_map.items():
            print(f"{key}: {val}")

        selected = input("Select a session (4, 5, 6, or 7): ").strip()
        while selected not in session_map:
            selected = input("Invalid selection. Please choose 4, 5, 6, or 7: ").strip()

        # Hardcoded city lists for each session
        s4_cities = ["Little Rock", "Albany", "Hollywood", "Denver", "Clinton", "Galena", "Las Vegas", "Grants Pass", "Nashville"]
        s5_cities = ["Los Angeles", "Palo Alto", "Washington", "Wilmington", "Gloucester", "Wilmar", "Croton-on-Hudson", "North Powder", "Scranton", "Kilgore", "Oak Cliff", "Sheridan"]
        s6_cities = ["Little Rock", "Babcock Ranch", "Lawrence", "St Ignatius", "New York", "Gettysburg", "Kingsport", "American Fork", "Montpelier"]
        s7_cities = ["Riggins", "Dodge City", "Blue Earth"]

        # Use PyQt5 QFileDialog to select save location
        app = QApplication(sys.argv)
        from PyQt5.QtWidgets import QWidget
        window = QWidget()
        window.setWindowTitle('Folder Picker')
        window.setFixedSize(1, 1)
        window.move(0, 0)
        window.show()

        import os
        start_dir = os.path.expanduser("~/Downloads")
        QFileDialog.DontUseNativeDialog
        output_dir = QFileDialog.getExistingDirectory(window, "Select Folder to Save Weather Screenshots", start_dir)
        # Handle cancellation
        if not output_dir:
            print("No folder selected. Exiting program.")
            sys.exit(0)
        window.close()
        app.exit()

        output_dir.replace("chrome-mac-arm64/Google Chrome for Testing.app/Contents/Frameworks/Google Chrome for Testing Framework.framework/Versions/Current", "/")

        # Create a folder named "Weather Screenshots for [date]" using the forecast date in MM-DD format
        today_str = (datetime.datetime.now() + datetime.timedelta(days=self.day_delta)).strftime("%m-%d")
        output_dir = os.path.join(output_dir, f"Weather Screenshots for {today_str}")
        os.makedirs(output_dir, exist_ok=True)

        # Create Individual and Combined folders
        individual_dir = os.path.join(output_dir, "Individual")
        combined_dir = os.path.join(output_dir, "Combined")
        os.makedirs(individual_dir, exist_ok=True)
        os.makedirs(combined_dir, exist_ok=True)

        cities = {
            "4": s4_cities,
            "5": s5_cities,
            "6": s6_cities,
            "7": s7_cities
        }[selected]

        # National/Regional map always goes to Individual/National
        if any("Anchorage" in city for city in cities):
            self.get_national_weather_map(output_dir)
        else:
            self.get_regional_weather_map(output_dir)

        print(cities[0], end="")  # Print the first city without a leading comma
        [print(", " + city, end="") for city in cities[1:]]  # Print the rest of the cities with a leading comma

        for city in cities:
            print(f"\nProcessing weather for city: {city}")
            city_folder = os.path.join(individual_dir, city.replace(" ", "_"))
            # Create/clear city_folder
            os.makedirs(city_folder, exist_ok=True)
            for file in os.listdir(city_folder):
                file_path = os.path.join(city_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            # Pass city_folder as output_dir to get_weather_screenshots
            self.get_weather_screenshots(city, city_folder)
            # Stack and store combined image in Combined under main output_dir
            self.stack_weather_images(city_folder, city, main_output_dir=output_dir)

        print("Weather Scraper Finished")

    def get_regional_weather_map(self, output_dir):
        driver = self.setup_driver()
        screen_scalar = 0.73
        try:
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=self.day_delta)
            time_param = tomorrow.strftime("%Y%m%d/2100")
            url = f"https://www.ventusky.com/?p=39.0;-98.0;5&t={time_param}"
            driver.get(url)
            time.sleep(5)
            self.zoom_out(driver, times=2)

            # Make sure Individual/National exists
            national_folder = os.path.join(output_dir, "Individual", "National")
            os.makedirs(national_folder, exist_ok=True)
            # Clear folder
            for file in os.listdir(national_folder):
                file_path = os.path.join(national_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Feels-like temperature
            self.switch_layer(driver, "feel")
            self.capture_centered_screenshot(
                driver,
                os.path.join(national_folder, "feels_like.png"),
                crop_size=(int(1920 * screen_scalar), int(1080 * screen_scalar))
            )

            # Precipitation
            self.switch_layer(driver, "Precipitation")
            self.capture_centered_screenshot(
                driver,
                os.path.join(national_folder, "precipitation.png"),
                crop_size=(int(1920 * screen_scalar), int(1080 * screen_scalar))
            )

            # Combine the two images vertically if both exist
            feels_path = next((os.path.join(national_folder, f) for f in os.listdir(national_folder) if f.startswith("feels_like")), None)
            precip_path = next((os.path.join(national_folder, f) for f in os.listdir(national_folder) if f.startswith("precipitation")), None)
            if feels_path and os.path.exists(feels_path) and precip_path and os.path.exists(precip_path):
                img1 = Image.open(feels_path)
                img2 = Image.open(precip_path)
                w = max(img1.width, img2.width)
                h = img1.height + img2.height
                combined = Image.new("RGB", (w, h))
                combined.paste(img1, (0, 0))
                combined.paste(img2, (0, img1.height))
                combined_dir = os.path.join(output_dir, "Combined")
                current_url = driver.current_url
                timestamp = ""
                if "t=" in current_url:
                    raw_time = current_url.split("t=")[-1]
                    try:
                        dt = datetime.datetime.strptime(raw_time, "%Y%m%d/%H%M")
                        timestamp = dt.strftime("%m-%d")
                    except:
                        timestamp = raw_time.replace("/", "")[4:8]
                os.makedirs(combined_dir, exist_ok=True)
                combined.save(os.path.join(combined_dir, f"National_{timestamp}.png"))

            print("Saved regional weather screenshots")
        finally:
            driver.quit()