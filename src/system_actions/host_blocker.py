import os
import platform
import sys # To check if running as admin/root
import subprocess
import socket
import tempfile

# List of websites to block
blocked_sites = [
    "www.pornhub.com", "pornhub.com", "www.8tube.xxx", "8tube.xxx", "www.redtube.com", "redtube.com", 
    "www.kink.com", "kink.com", "www.youjizz.com", "youjizz.com", "www.xvideos.com", "xvideos.com", 
    "www.youporn.com", "youporn.com", "www.brazzers.com", "brazzers.com", "www.omegle.com", "omegle.com", 
    "www.paltalk.com", "paltalk.com", "www.talkwithstranger.com", "talkwithstranger.com", 
    "www.chatroulette.com", "chatroulette.com", "www.chat-avenue.com", "chat-avenue.com", 
    "www.chatango.com", "chatango.com", "www.teenchat.com", "teenchat.com", "www.wireclub.com", 
    "wireclub.com", "www.chathour.com", "chathour.com", "www.chatzy.com", "chatzy.com", 
    "www.chatib.us", "chatib.us", "www.e-chat.co", "e-chat.co", "www.4chan.org", "4chan.org", 
    "www.reddit.com", "reddit.com", "www.somethingawful.com", "somethingawful.com", 
    "www.topix.com", "topix.com", "www.stormfront.org", "stormfront.org", 
    "www.bodybuilding.com", "bodybuilding.com", "www.kiwifarms.net", "kiwifarms.net", 
    "www.voat.co", "voat.co", "www.8kun.top", "8kun.top", "www.incels.me", "incels.me", 
    "www.match.com", "match.com", "www.bumble.com", "bumble.com", "www.meetme.com", "meetme.com", 
    "www.okcupid.com", "okcupid.com", "www.pof.com", "pof.com", "www.eharmony.com", "eharmony.com", 
    "www.zoosk.com", "zoosk.com", "www.hinge.co", "hinge.co", "www.grindr.com", "grindr.com", 
    "www.ashleymadison.com", "ashleymadison.com", "www.adultfriendfinder.com", "adultfriendfinder.com", 
    "www.betonline.ag", "betonline.ag", "www.freespin.com", "freespin.com", "www.bovada.lv", "bovada.lv", 
    "www.slotocash.im", "slotocash.im", "www.royalacecasino.com", "royalacecasino.com", 
    "www.pokerstars.com", "pokerstars.com", "www.888casino.com", "888casino.com", 
    "www.sportsbetting.ag", "sportsbetting.ag", "www.betway.com", "betway.com", 
    "www.liveleak.com", "liveleak.com", "www.bestgore.com", "bestgore.com", 
    "www.theync.com", "theync.com", "www.documentingreality.com", "documentingreality.com", 
    "www.ogrish.tv", "ogrish.tv", "www.hackthissite.org", "hackthissite.org", 
    "www.thepiratebay.org", "thepiratebay.org", "www.wikileaks.org", "wikileaks.org", 
    "www.darkweblinks.net", "darkweblinks.net", "www.illegalhack.com", "illegalhack.com", 
    "www.gab.com", "gab.com", "www.nationalvanguard.org", "nationalvanguard.org", 
    "www.dailystormer.su", "dailystormer.su", "www.facebook.com", "facebook.com", 
    "m.facebook.com", "fb.com", "facebook.net", "www.facebook.net"
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
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0 # POSIX check for root
    except AttributeError:
        return False # os.getuid/geteuid not available on all OSes? Default to False.

def flush_dns_cache():
    """Flush DNS cache to ensure blocks take effect immediately."""
    system = platform.system().lower()
    try:
        if system == "windows":
            subprocess.run(["ipconfig", "/flushdns"], check=True, capture_output=True)
            return "✅ Windows DNS cache flushed."
        elif system == "linux":
            # Different distros have different commands
            try:
                # systemd-resolved
                subprocess.run(["systemd-resolve", "--flush-caches"], check=True, capture_output=True)
                return "✅ Linux DNS cache flushed (systemd-resolve)."
            except (subprocess.SubprocessError, FileNotFoundError):
                try:
                    # nscd
                    subprocess.run(["service", "nscd", "restart"], check=True, capture_output=True)
                    return "✅ Linux DNS cache flushed (nscd restart)."
                except (subprocess.SubprocessError, FileNotFoundError):
                    return "⚠️ Could not flush DNS cache. Changes may take time to propagate."
        elif system == "darwin":  # macOS
            subprocess.run(["dscacheutil", "-flushcache"], check=True, capture_output=True)
            subprocess.run(["killall", "-HUP", "mDNSResponder"], check=True, capture_output=True)
            return "✅ macOS DNS cache flushed."
        else:
            return "⚠️ Unsupported OS for DNS cache flushing."
    except Exception as e:
        return f"⚠️ Error flushing DNS cache: {e}"

def clear_browser_dns_cache():
    """Create a file with instructions to clear browser DNS caches."""
    system = platform.system().lower()
    instructions = """
BROWSER DNS CACHE CLEARING INSTRUCTIONS:

Chrome:
1. Enter chrome://net-internals/#dns in the address bar
2. Click the "Clear host cache" button

Firefox:
1. Enter about:config in the address bar
2. Search for "network.dnsCacheExpiration"
3. Set it to 0 temporarily, then back to default (60)

Edge:
1. Enter edge://net-internals/#dns in the address bar
2. Click the "Clear host cache" button

Opera:
1. Enter opera://net-internals/#dns in the address bar
2. Click the "Clear host cache" button
"""
    
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "browser_dns_instructions.txt")
    try:
        with open(file_path, 'w') as f:
            f.write(instructions)
        return file_path
    except Exception:
        return None

# Function to block websites (adds entries if not present)
def block_sites():
    if hosts_path is None:
        return "Error: Could not determine hosts file path for this OS."
    if not is_admin():
        return "Error: Permission Denied. Run as Administrator/root."

    try:
        # First, make sure all blocked sites have both with www and without www variants
        complete_blocked_sites = []
        for site in blocked_sites:
            complete_blocked_sites.append(site)
            # If site doesn't start with www. and doesn't already have a www. variant in the list
            if not site.startswith("www.") and f"www.{site}" not in blocked_sites:
                complete_blocked_sites.append(f"www.{site}")

        with open(hosts_path, 'r+') as file:
            content = file.read()
            lines_to_add = []
            needs_update = False

            # Check if block marker exists, if not, add it
            if block_marker_start not in content:
                lines_to_add.append(f"\n{block_marker_start}\n")
                needs_update = True

            for site in complete_blocked_sites:
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

                # Flush DNS cache to ensure changes take effect immediately
                dns_result = flush_dns_cache()
                browser_instructions = clear_browser_dns_cache()
                
                return f"✅ Sites blocked/updated successfully! {dns_result}"
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

        # Flush DNS cache to ensure changes take effect immediately
        dns_result = flush_dns_cache()
        
        return f"✅ Websites unblocked successfully! {dns_result}"
    except PermissionError:
        return "Error: Permission Denied. Run as Administrator/root."
    except Exception as e:
        return f"Error unblocking sites: {e}"

def test_site_blocking(site):
    """Test if blocking is effective for a specific site by attempting to resolve it."""
    try:
        ip = socket.gethostbyname(site)
        if ip == "127.0.0.1":
            return f"✅ Site {site} is correctly redirected to localhost."
        else:
            return f"⚠️ Site {site} resolves to {ip} instead of localhost. Blocking may be ineffective."
    except socket.gaierror:
        return f"⚠️ Could not resolve {site}. DNS resolution failed."
    except Exception as e:
        return f"⚠️ Error testing site blocking: {e}"

# Example usage when script is run directly
if __name__ == "__main__":
    print("Attempting to block sites...")
    status = block_sites()
    print(status)
    
    # Test blocking effectiveness for a common site
    if "successfully" in status:
        print(test_site_blocking("pornhub.com"))
    
    # Example: Wait and unblock
    # import time
    # time.sleep(10)
    # print("Attempting to unblock sites...")
    # status_unblock = unblock_sites()
    # print(status_unblock)
