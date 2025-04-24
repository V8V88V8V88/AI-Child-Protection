import os
import platform
import sys # To check if running as admin/root

# List of websites to block
blocked_sites = [
    "www.pornhub.com", "www.8tube.xxx", "www.redtube.com", "www.kink.com", "www.youjizz.com",
    "www.xvideos.com", "www.youporn.com", "www.brazzers.com", "www.omegle.com", "www.paltalk.com",
    "www.talkwithstranger.com", "www.chatroulette.com", "www.chat-avenue.com", "www.chatango.com",
    "www.teenchat.com", "www.wireclub.com", "www.chathour.com", "www.chatzy.com", "www.chatib.us",
    "www.e-chat.co", "www.4chan.org", "www.reddit.com", "www.somethingawful.com", "www.topix.com",
    "www.stormfront.org", "www.bodybuilding.com", "www.kiwifarms.net", "www.voat.co", "www.8kun.top",
    "www.incels.me", "www.match.com", "www.bumble.com", "www.meetme.com", "www.okcupid.com",
    "www.pof.com", "www.eharmony.com", "www.zoosk.com", "www.hinge.co", "www.grindr.com",
    "www.ashleymadison.com", "www.adultfriendfinder.com", "www.betonline.ag", "www.freespin.com",
    "www.bovada.lv", "www.slotocash.im", "www.royalacecasino.com", "www.pokerstars.com",
    "www.888casino.com", "www.sportsbetting.ag", "www.betway.com", "www.liveleak.com",
    "www.bestgore.com", "www.theync.com", "www.documentingreality.com", "www.ogrish.tv",
    "www.hackthissite.org", "www.thepiratebay.org", "www.wikileaks.org", "www.darkweblinks.net",
    "www.illegalhack.com", "www.gab.com", "www.nationalvanguard.org", "www.dailystormer.su"
]

# --- OS Detection and Hosts File Path ---
def get_hosts_path():
    system = platform.system().lower()
    if system == "windows":
        # Construct path dynamically even for Windows
        system_root = os.environ.get('SYSTEMROOT', 'C:\\Windows')
        return os.path.join(system_root, "System32", "drivers", "etc", "hosts")
    elif system in ["linux", "darwin"]: # darwin is macOS
        return "/etc/hosts"
    else:
        # Raise error for unsupported OS
        raise OSError(f"Unsupported operating system: {system}")

# Attempt to get the hosts path at module load time
try:
    hosts_path = get_hosts_path()
except OSError as e:
    print(f"Error determining hosts file path: {e}")
    # Set to None or a dummy value to prevent errors later if path is critical
    hosts_path = None

redirect_ip = "127.0.0.1"
block_marker_start = "# AI-Child-Protection Block Start"
block_marker_end = "# AI-Child-Protection Block End"

def is_admin():
    """Check if the script is running with admin/root privileges."""
    try:
        if platform.system().lower() == "windows":
            # This is a simple check; a more robust one might involve ctypes
            return os.getuid() == 0 # Windows admin check can be complex
        else:
            return os.geteuid() == 0 # POSIX check for root
    except AttributeError:
        return False # os.getuid/geteuid not available on all OSes? Default to False.

# Function to block websites (adds entries if not present)
def block_sites():
    if hosts_path is None:
        return "Error: Could not determine hosts file path for this OS."
    if not is_admin():
        return "Error: Permission Denied. Run as Administrator/root."

    try:
        with open(hosts_path, 'r+') as file:
            content = file.read()
            lines_to_add = []
            needs_update = False

            # Check if block marker exists, if not, add it
            if block_marker_start not in content:
                lines_to_add.append(f"\n{block_marker_start}\n")
                needs_update = True

            for site in blocked_sites:
                entry = f"{redirect_ip} {site}"
                # Check if site is already blocked *within* our markers or generally
                if entry not in content:
                     lines_to_add.append(f"{entry}\n")
                     needs_update = True

            # Check if end marker exists, if not, add it
            if block_marker_end not in content:
                 lines_to_add.append(f"{block_marker_end}\n")
                 needs_update = True

            if needs_update:
                # Find start marker or append to end
                if block_marker_start in content:
                     # Insert new entries just after the start marker
                    pos = content.find(block_marker_start) + len(block_marker_start)
                    file.seek(pos)
                    remaining_content = file.read() # Read rest of file
                    file.seek(pos) # Go back to insert point
                    file.write("\n" + "".join(lines_to_add).strip() + "\n") # Write new lines
                    file.write(remaining_content) # Write back the rest
                    file.truncate() # Remove potential trailing content if insert was shorter
                else:
                    # If markers somehow weren't added, append everything to the end
                    file.seek(0, os.SEEK_END) # Go to end of file
                    if not content.endswith('\n'): file.write('\n') # Ensure newline
                    file.write("\n".join(lines_to_add))

                return "✅ Sites blocked/updated successfully!"
            else:
                return "✅ Sites already blocked."

    except PermissionError:
        return "Error: Permission Denied. Run as Administrator/root."
    except Exception as e:
        return f"Error blocking sites: {e}"

# Function to unblock websites (removes entries between markers)
def unblock_sites():
    if hosts_path is None:
        return "Error: Could not determine hosts file path for this OS."
    if not is_admin():
        return "Error: Permission Denied. Run as Administrator/root."

    try:
        with open(hosts_path, 'r') as file:
            lines = file.readlines()

        with open(hosts_path, 'w') as file:
            in_block_section = False
            for line in lines:
                if block_marker_start in line:
                    in_block_section = True
                    # Optionally keep the start marker line itself, or remove it too
                    # file.write(line) # Uncomment to keep marker
                    continue # Skip writing this line
                elif block_marker_end in line:
                    in_block_section = False
                    # Optionally keep the end marker line itself
                    # file.write(line) # Uncomment to keep marker
                    continue # Skip writing this line

                # Write line only if it's outside our block section
                if not in_block_section:
                    file.write(line)

        return "✅ Websites unblocked successfully!"
    except PermissionError:
        return "Error: Permission Denied. Run as Administrator/root."
    except Exception as e:
        return f"Error unblocking sites: {e}"

# Example usage when script is run directly
if __name__ == "__main__":
    print("Attempting to block sites...")
    status = block_sites()
    print(status)
    # Example: Wait and unblock
    # import time
    # time.sleep(10)
    # print("Attempting to unblock sites...")
    # status_unblock = unblock_sites()
    # print(status_unblock)
