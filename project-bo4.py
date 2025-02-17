#this was made by @sirchico
#this was based on @bodnjenie14's code
#this is open source so don't pmo by selling it

import os
import sys
import json
import re
import shutil
import subprocess
import zipfile
from colorama import init, Fore, Style
print(Fore.CYAN + f"            this tool is free and made by @sirchico and I appreciate giving credits\n                {Fore.LIGHTMAGENTA_EX}             this was based on @bodnjenie14's code\n\n")
import socket
import os
import time

# Initialize colorama for colored output (and to support Windows)
init(autoreset=True)

# Regular expression to validate IPv4 addresses
IP_REGEX = r"^((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$"
JSON_FILE = "project-bo4.json"
cwd = os.getcwd()
resources_dir = os.path.join(cwd, "project-bo4", "files")
settings_file = os.path.join(cwd, resources_dir, "settings.ini")
server_ip_file = os.path.join(cwd, resources_dir, "Ip_address.txt")

# Files that will be removed after game execution
FILES_TO_REMOVE = ["d3d11.dll", "UMPDC.dll"]

def load_config():
    """Loads or creates the configuration file."""
    if not os.path.exists(JSON_FILE):
        try:
            default_name = os.getlogin()
        except Exception:
            default_name = "Unknown Soldier"
        config = {
            "demonware": {"ipv4": "78.157.42.107"},
            "identity": {"name": default_name},
            "mode": "offline",
            "reshade": False
        }
        save_config(config)
        return config
    else:
        with open(JSON_FILE, "r") as f:
            return json.load(f)

def save_config(config):
    """Saves the configuration file."""
    with open(JSON_FILE, "w") as f:
        json.dump(config, f, indent=4)

def validate_ip(ip):
    """Validates the provided IP address."""
    return re.match(IP_REGEX, ip) is not None

def read_ip_addresses(file_path):
    """Reads IP addresses from Ip_address.txt."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def is_server_online(ip, port=3074, timeout=2):
    """Checks if a server is reachable at the given IP and port."""
    try:
        with socket.create_connection((ip, port), timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_ip_and_prompt():
    """Checks available IPs and gives the user options based on connectivity."""
    ip_file = "Ip_address.txt"
    ip_list = read_ip_addresses(ip_file)
    valid_ip = None
    
    for ip in ip_list:
        if ip == "127.0.0.1":
            continue  # Skip localhost
        if is_server_online(ip):
            valid_ip = ip
            break
    
    if valid_ip:
        print(f"✅ Server found at {valid_ip}. Play online? (Y/N)")
        choice = input().strip().lower()
        if choice == 'y':
            run_online(valid_ip)
        else:
            print("Exiting...")
            exit()
    else:
        print("❌ No valid servers found. Play offline? (Y/N)")
        choice = input().strip().lower()
        if choice == 'y':
            run_offline()
        else:
            print("Exiting script...")
            exit()

def run_online():
    cwd = os.getcwd()
    resources_dir = os.path.join(cwd, "project-bo4", "files")
    copy_players_cfg(cwd, resources_dir)
    copy_lpc_folder(cwd, resources_dir)
    config = load_config()
    ip = config.get("demonware", {}).get("ipv4", "")
    if not ip:
        print(Fore.RED + "No IP address set. Please update the IP.")
        input("Press Enter to resume the script...")
        clear_screen()
        main()
    extract_dll_zip(cwd, resources_dir, "online", config.get("reshade", False))
    print(Fore.GREEN + f"Launching game in Online mode with IP {ip}...")
    run_game()

def run_offline():
    cwd = os.getcwd()
    resources_dir = os.path.join(cwd, "project-bo4", "files")
    copy_players_cfg(cwd, resources_dir)
    copy_lpc_folder(cwd, resources_dir)
    config = load_config()
    extract_dll_zip(cwd, resources_dir, "offline", config.get("reshade", False))
    print(Fore.BLUE + "Launching game in Offline mode...")
    run_game()

def run_game():
    try:
        print("Launching BlackOps4.exe ...")
        process = subprocess.Popen("BlackOps4.exe")
        process.wait()
        remove_dll_files(os.getcwd())
        sys.exit(0)
    except Exception as e:
        print("Error launching game:", e)
        sys.exit(1)

def remove_dll_files(cwd):
    """Removes unnecessary DLL files."""
    for dll in FILES_TO_REMOVE:
        dll_path = os.path.join(cwd, dll)
        if os.path.exists(dll_path):
            os.remove(dll_path)

def copy_players_cfg(cwd, resources_dir):
    """Copies player configuration to the game directory."""
    players_dir = os.path.join(cwd, "Players")
    if not os.path.exists(players_dir):
        os.mkdir(players_dir)
    src_cfg = os.path.join(resources_dir, "Players", "Mp.cfg")
    dst_cfg = os.path.join(players_dir, "Mp.cfg")
    if not os.path.exists(dst_cfg):
        shutil.copy(src_cfg, dst_cfg)

def copy_lpc_folder(cwd, resources_dir):
    """Copies the LPC folder to the game directory."""
    src_lpc = os.path.join(resources_dir, "LPC")
    dst_lpc = os.path.join(cwd, "LPC")
    if os.path.exists(dst_lpc):
        shutil.rmtree(dst_lpc)
    shutil.copytree(src_lpc, dst_lpc)

def extract_dll_zip(cwd, resources_dir, mode, reshade):
    """Extracts the appropriate DLL zip based on the mode and reshade option."""
    zip_name = "reshade_solo.zip" if reshade else "solo.zip" if mode == "offline" else "reshade_mp.zip" if reshade else "mp.zip"
    zip_path = os.path.join(resources_dir, zip_name)
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(cwd)

def change_name():
    """Change the player's name in the config."""
    config = load_config()
    new_name = input(Fore.YELLOW + "Enter new name: ").strip()
    if new_name:
        config["identity"]["name"] = new_name
        save_config(config)
    clear_screen()
    print(Fore.GREEN + f"✅ Name successfully modified to \"{new_name}\"!")
    input("Press Enter to resume the script...")
    clear_screen()
    main()

def clear_screen():
    """Clears the terminal screen."""
    # Check the device and use the appropriate command to clear the screen
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux or macOS
        os.system('clear')

def animate_dots():
    """Displays an animation of dots for waiting."""
    print(Fore.YELLOW + "Checking IPs", end="")
    for _ in range(3):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print()  # Move to the next line after the dots animation

def change_ip():
    """Change the IP address in the config."""
    config = load_config()
    clear_screen()
    print(Fore.RED + "Choose how you want to change the IP address:")
    print(Fore.YELLOW + "1. Choose from the recommended IPs")
    print(Fore.GREEN + "2. Manually input the IP address")

    choice = input("Enter your choice (1 or 2): ").strip()
    clear_screen()

    if choice == "1":
        ip_list = read_ip_addresses(server_ip_file)
        valid_ips = []

        # Ensure there's at least one IP in the list
        if not ip_list:
            print(Fore.RED + "❌ No IP addresses found in Ip_address.txt.")
            input("Press Enter to resume the script...")
            clear_screen()
            main()  # Return if no IPs found

        print(Fore.YELLOW + "Checking IPs...")

        # Check each IP
        for idx, ip in enumerate(ip_list, start=1):
            if ip == "127.0.0.1":
                print(Fore.YELLOW + "Skipping local IP...")
                continue  # Skip localhost
            
            print(Fore.CYAN + f"Checking IP {idx}: {ip}...", end="")
            time.sleep(1)  # Simulate the checking delay

            if is_server_online(ip):
                valid_ips.append(ip)
                print(Fore.GREEN + " ✅ Valid!")
            else:
                print(Fore.RED + f" ❌ IP invalid")

            time.sleep(0.5)  # Simulate a small delay between checks

        # If no valid IPs are found
        if len(valid_ips) == 0:
            print(Fore.RED + "❌ No valid IPs found.")
            back = input("1. Go Back to Main Menu\n2. Choose an IP anyways...\n\nPlease Pick your choice: ")
            if back == "1":
                clear_screen()
                main()
            elif back == "2":
                clear_screen()
                print(Fore.CYAN + "Here are all the IPs (including invalid ones):")
                for idx, ip in enumerate(ip_list):
                    print(f"  {idx}. {ip}")
                #print(f"\nWhich IP will it be?:")
                
                ip_choice = input(f"\nWhich IP will it be?: ").strip()
                if ip_choice.isdigit() and 0 <= int(ip_choice) < len(ip_list):
                    chosen_ip = ip_list[int(ip_choice)]
                    config["demonware"]["ipv4"] = chosen_ip
                    save_config(config)
                    print(Fore.GREEN + f"IP address changed to {chosen_ip}.")
                    input("Press Enter to resume the script...")
                    clear_screen()
                    main()
                else:
                    print(Fore.RED + "❌ Invalid IP choice.")
                    input("Press Enter to resume the script...")
                    clear_screen()
                    main()

        # If exactly one valid IP is found
        elif len(valid_ips) == 1:
            print(Fore.CYAN + "✅ Only one valid IP found:")
            print(f"  1. {valid_ips[0]}")
            input("Press Enter to select this IP.")
            chosen_ip = valid_ips[0]
            config["demonware"]["ipv4"] = chosen_ip
            save_config(config)
            print(Fore.GREEN + f"IP address changed to {chosen_ip}.")
            input("Press Enter to resume the script...")
            clear_screen()
            main()

        # If multiple valid IPs are found
        else:
            print(Fore.CYAN + "✅ Choose an IP from the list below:")
            for idx, ip in enumerate(valid_ips[:2], start=1):
                print(f"  {idx}. {ip}")

            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == "1":
                chosen_ip = valid_ips[0]
                input("IP Modified, Press Enter to resume the script...")
                clear_screen()
                main()
            elif choice == "2":
                chosen_ip = valid_ips[1]
                input("IP Modified, Press Enter to resume the script...")
                clear_screen()
                main()
            else:
                print(Fore.RED + "Invalid choice.")
                input("Press Enter to resume the script...")
                clear_screen()
                main()# Return to prevent further execution

            config["demonware"]["ipv4"] = chosen_ip
            save_config(config)
            print(Fore.GREEN + f"IP address changed to {chosen_ip}.")

    elif choice == "2":
        new_ip = input(Fore.RED + "Enter new IP address: ").strip()
        if validate_ip(new_ip):
            config["demonware"]["ipv4"] = new_ip
            save_config(config)
            print(Fore.GREEN + f"IP address changed to {new_ip}.")
            input("Press Enter to resume the script...")
            clear_screen()
            main()
        else:
            print(Fore.RED + "❌ Invalid IP address format.")
            input("Press Enter to resume the script...")
            clear_screen()
            main()# Return if the IP format is invalid

    else:
        print(Fore.RED + "Invalid option. Returning to main menu.")
        time.sleep(1)
        clear_screen()
        main()  # Return to prevent further execution

    # Clear the screen after the IP change
    clear_screen()

def check_other_ips():
    """Check available IPs (other than localhost) and verify their connectivity."""
    ip_file = "Ip_address.txt"
    ip_list = read_ip_addresses(ip_file)
    valid_ips = []

    for ip in ip_list:
        if ip == "127.0.0.1":
            continue  # Skip localhost
        if is_server_online(ip):
            valid_ips.append(ip)

    if valid_ips:
        print(Fore.CYAN + "✅ Valid IPs found:")
        for ip in valid_ips:
            print(f"  - {ip}")
    else:
        print(Fore.CYAN + "❌ No valid IPs found.")

    input("Press Enter to resume the script...")
    clear_screen()
    main()

def main():
    config = load_config()
    print("Choose an option:")
    print(Fore.LIGHTBLUE_EX + "     1. Play Offline")
    print(Fore.GREEN + "     2. Play Online")
    print(Fore.YELLOW + "     3. Change Name")
    print(Fore.RED + "     4. Change IP")
    print(Fore.MAGENTA + "     5. Check Valid IPs")  # New option to check IPs
    print("     99. Exit")  # New option to exit
    
    choice = input("\nEnter your choice: ").strip()
    if choice == "1":
        config["mode"] = "offline"
        save_config(config)
        run_offline()
    elif choice == "2":
        config["mode"] = "online"
        save_config(config)
        #check_ip_and_prompt()
        run_online()
    elif choice == "3":
        change_name()
    elif choice == "4":
        change_ip()
    elif choice == "5":
        check_other_ips()  # Call the new function
    elif choice == "99":
        print("\nExiting script...")
        sys.exit(0)  # Exit the script
    else:
        print("Invalid option.")
        sys.exit(1)

if __name__ == "__main__":
    main()
