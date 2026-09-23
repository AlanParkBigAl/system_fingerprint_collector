"""
Midtown IT - Computer Fingerprint Collector
Author: Alan Park
Purpose: Collect system information and store in CSV file
"""

import platform
import socket
import uuid
import time
import speedtest
import csv
import os

CSV_FILE = "midtown_computers.csv"


# --- SYSTEM INFORMATION FUNCTIONS --- #

def get_host_name():
    # get computer name
    return socket.gethostname()


def get_ip_address():
    # gethostbyname can return 127.0.0.1 on some computers which is not the real network IP
    # instead open a temporary UDP connection to an outside address (google)
    # it doesn't actually send any data but forces the OS to pick the real network IP
    # then read that IP back from the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # AF_INET to use IPv4, SOCK_DGRAM specifies UDP
    s.connect(("8.8.8.8", 80))  # It attempts to connect to Google's public DNS (always on) on port. 
    ip = s.getsockname()[0]    # getsocketname() returns a "tuple" with local IP and the port, [0] grabs first item which is actual Network IP address. 
    s.close()
    return ip


def get_mac_address():
    # uuid.getnode() gives the MAC address as integer
    # So, need to convert it manually to a format like A4-B5-C6-D7-E8-F9

    mac = uuid.getnode()

    # step 1 - build a 12-character hex string from the integer manually
    # each loop, take the last hex digit using remainder (% 16)
    # then add it to the front of the string because we are building it right to left
    # then chop off that digit with integer division (// 16)
    hex_characters = "0123456789abcdef"     # reference string to convert numbers into hexadecimals. 
    hex_string = ""      # empty string to store hexadecimals
    temp = mac         # temporary copy of MAC integer

    for i in range(12):
        remainder = temp % 16    # this gets the last digit of hex value
        hex_string = hex_characters[remainder] + hex_string   # look up the reference string and add it to the front.(right-to-left)
        temp = temp // 16      # use integer to chop off the digit processed, moving to next

    # hex_string now looks like "a4b5c6d7e8f9"

    # step 2 - split into pairs of 2 characters
    # i goes 0, 2, 4, 6, 8, 10 so we grab 2 characters each time
    pairs = []     #intialise an empty list
    for i in range(0, 12, 2):    #loop 12-character string in steps of 2
        pairs.append(hex_string[i:i+2])   #grab 2 characters at a time and add them to list

    # step 3 - join with "-" and convert to uppercase
    # result looks like "A4-B5-C6-D7-E8-F9"
    mac_formatted = "-".join(pairs)   #All pairs now join with"-"
    return mac_formatted.upper()     #convert them to uppercase


def get_processor():
    # platform.processor() works fine on Windows but returns blank on Linux
    # so if it comes back empty, read it directly from /proc/cpuinfo instead
    processor = platform.processor()

    if processor == "":
        # /proc/cpuinfo is a Linux system file that has all the CPU details
        # look for the line "model name" and grab the value
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:     #loops through cpuinfo line by line
                    if "model name" in line:
                        processor = line.split(":")[1].strip()    #only need Part[1]=2nd part=CPU name
                        break  # found it, no need to keep reading
        except:
            processor = "Unknown"

    return processor


def get_os():
    # get operating system
    return platform.system() + " " + platform.release()


def get_system_time():
    # get current date and time in DD/MM/YYYY HH:MM:SS format
    return time.strftime("%d/%m/%Y %H:%M:%S")


def get_internet_speed():
    # Get download & upload speed in Mbps + ping
    # if it fails for any reason (no internet, timeout etc) return an error message instead of crashing
    try:
        st = speedtest.Speedtest()
        st.get_best_server()    # Choose closest/fastest server
        download = st.download() / 1000000   # convert bytes/sec to Mbps
        upload = st.upload() / 1000000   # Mbps
        ping = st.results.ping     # latency in ms
        return f"{download:.1f} Mbps down / {upload:.1f} Mbps up (ping {ping:.0f} ms)"   # results rounded to 1 decimal place
    except Exception as e:
        return f"Speed test failed: {str(e)}"     # str= showing error messegae as string (readable words)


def get_open_ports():
    # check a list of common ports to see which ones are open
    # using the real IP address so results reflect actual network
    ip = get_ip_address()
    common_ports = [20, 21, 22, 80, 443, 3306, 8000, 8080]
    open_ports = []

    for port in common_ports:    # check each port 1 by 1
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)    #wait 0.5s 
            result = s.connect_ex((ip, port))     #ex (extended) = returns an error code instead of crashing
            if result == 0:      # 0 means connection succeeded so the port is open
                open_ports.append(str(port))
            s.close()
        except:
            continue

    return ";".join(open_ports) if open_ports else "None"


# ---------------- CSV FILE FUNCTIONS ---------------- #

def save_to_csv(data):
    # append the scanned data as a new row to the CSV file
    # if the file is new, write the header row first
    # never update or overwrite existing rows - only append
    try:
        file_exists = os.path.isfile(CSV_FILE)  #looks at specific filename and returns True if it finds or Fasle if not.

        # step 1 - check if this computer was scanned before and if data has changed
        if file_exists:
            with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            # with= file closes automally when finished. "r" opens the file in Read mode
            # newline="" to make sure not to add extra blank rows. "utf-8" to make every text look same (CSV, PC, MAC.etc..)   
                reader = csv.reader(f)   #Python to see the file as rows & colums instead of a long string of text
                next(reader)  # skip header row
                for row in reader:
                    if row[0] == data[0]:    #row[0] = "computer name" already saved, data[0] = just scanned
                        # found a previous scan for this computer
                        if row != data:   #after finding same computer, now compare whole lists
                            print("WARNING: Computer information has changed!")
                        break  # only need to find the first match
 
        # step 2 - if file is new, write the header row first
        # step 3 - always append the new scan as a new row
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Computer Name", "IP Address", "MAC Address",
                    "Processor Model", "Operating System",
                    "System Time", "Internet Speed", "Open Ports"
                ])
            writer.writerow(data)

        print("Data saved successfully.")

    except Exception as e:
        print(f"Error saving to CSV: {e}")


# ---------------- MAIN MENU FUNCTION ---------------- #

def main_menu():
    # keep showing the menu until the user chooses to exit
    while True:
        print("\n--- Midtown IT Computer Fingerprint Collector ---")
        print("1. Full scan (all information)")
        print("2. Computer Name only")
        print("3. IP Address only")
        print("4. MAC Address only")
        print("5. Processor Model only")
        print("6. Operating System only")
        print("7. System Time only")
        print("8. Internet Speed only")
        print("9. Open Ports only")
        print("10. Exit program")

        # catch non-number input so the program doesn't crash
        try:
            choice = int(input("\nEnter your choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        # Selection control structure
        if choice == 1:
            computer_name = get_host_name()
            ip = get_ip_address()
            mac = get_mac_address()
            processor = get_processor()
            os_info = get_os()
            system_time = get_system_time()
            speed = get_internet_speed()
            ports = get_open_ports()

            data = [computer_name, ip, mac, processor, os_info, system_time, speed, ports]
            save_to_csv(data)
        elif choice == 2:
            print("Computer Name:", get_host_name())
        elif choice == 3:
            print("IP Address:", get_ip_address())
        elif choice == 4:
            print("MAC Address:", get_mac_address())
        elif choice == 5:
            print("Processor:", get_processor())
        elif choice == 6:
            print("Operating System:", get_os())
        elif choice == 7:
            print("System Time:", get_system_time())
        elif choice == 8:
            print("Internet Speed:", get_internet_speed())
        elif choice == 9:
            print("Open Ports:", get_open_ports())
        elif choice == 10:
            print("Exiting the program")
            break
        else:
            print("Invalid option, Try again")


# ---------------- PROGRAM START ---------------- #

if __name__ == "__main__":
    main_menu()
