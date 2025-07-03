from extract_all_itineraries import itinerary
from ventusky_weather_scraper import weather_scraper
import os
import re
from PyQt5.QtWidgets import QApplication, QFileDialog

class Executive:
    def __init__(self):
        print("Welcome to the AEP DUB automator!".center(80, "="))

        while True:
            try:
                u_in = input("Would you like to extract Itineraries (I), Weather (W), or Exit (E): ").strip().upper()

                if u_in == "I":
                    app = QApplication([])
                    folder_dialog = QFileDialog()
                    folder_dialog.setFileMode(QFileDialog.Directory)
                    folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
                    folder_path = folder_dialog.getExistingDirectory(None, "Select Session Folder")

                    if not folder_path:
                        print("No folder selected. Exiting.")
                        return

                    session_match = re.search(r"Session[_\s]*(\d+)", folder_path, re.IGNORECASE)
                    session_number = session_match.group(1) if session_match else "S1"
                    my_itinerary = itinerary(folder_path, session_number)
                    my_itinerary.run_itinerary_extraction()

                elif u_in == "W":
                    day_delta = int(input("Enter the number of days in the future you would like the weather to be forecast?: ").strip())
                    my_weather = weather_scraper(day_delta)
                    my_weather.run_weather_scraper()
                elif u_in == "E":
                    print("Exiting the program.")
                    break

                else:
                    Exception("Invalid input. Please enter 'I' for Itineraries or 'W' for Weather.")

            except Exception as e:
                print(f"Error: {e}. Please try again.")
