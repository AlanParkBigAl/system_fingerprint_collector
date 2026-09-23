# Midtown IT Computer Fingerprint Collector

A small command line tool that collects basic system and network information from a computer and saves it to a CSV file. Built for Midtown IT to keep a simple inventory of the machines it manages.

## What it collects

- Computer name
- IP address
- MAC address
- Processor model
- Operating system
- Current system time
- Internet speed (download, upload, ping)
- List of open ports from a common set (20, 21, 22, 80, 443, 3306, 8000, 8080)

## Requirements

- Python 3.x
- The speedtest-cli package (imported in the code as "speedtest")

Install the dependency with:

pip install speedtest-cli

Or use the included requirements.txt:

pip install -r requirements.txt

## Usage

Run the script from a terminal:

python fingerprint_collector.py

You will see a menu with these options:

1. Full scan (all information, saved to CSV)
2. Computer name only
3. IP address only
4. MAC address only
5. Processor model only
6. Operating system only
7. System time only
8. Internet speed only
9. Open ports only
10. Exit program

Options 2 through 9 print a single piece of information to the screen. Option 1 runs the full scan and appends the result as a new row in midtown_computers.csv. If the file does not exist yet, it is created with a header row.

## Notes on behavior

- The script never overwrites old rows. Every full scan adds a new row, even if the same computer was scanned before.
- If a computer has been scanned before and the new data differs from the last scan, a warning is printed to the console, but the row is still added rather than replacing the old one.
- If the CSV file is open in another program or the folder is read only, saving fails with a permission error and the script prints a message instead of crashing.
- If there is no internet connection, the speed test step fails on its own and records an error message in that field instead of stopping the whole scan.
- Open port scanning only checks a fixed list of common ports on the machine's own IP address, not a full sweep of every port.

## Project files

- fingerprint_collector.py, the main script
- requirements.txt, the one external dependency
- .gitignore, excludes the generated CSV and other local files from version control
- screenshots, a folder for example output images referenced below

## Screenshots

Add your own screenshots to the screenshots folder and link them here, for example:

![Menu](screenshots/menu.png)
![Full scan output](screenshots/csv_output.png)
![Error handling example](screenshots/permission_error.png)

Before adding any screenshot that shows real IP addresses or MAC addresses, blur or crop that information out first, or capture the screenshot on a test machine instead.

## License

No license has been added yet. Add one such as MIT if you want to make the terms of reuse clear to others.
