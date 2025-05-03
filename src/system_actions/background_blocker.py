import sys
import os
import time
import argparse
import platform
import logging
import tempfile
from .host_blocker import block_sites, unblock_sites, is_admin, get_hosts_path, block_marker_start, block_marker_end, redirect_ip, blocked_sites


log_file = os.path.join(tempfile.gettempdir(), "aichildprotect_blocker.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


CHECK_INTERVAL_SECONDS = 15 
MAX_HOSTS_FILE_SIZE = 5 * 1024 * 1024 


def check_termination_signal(signal_file):
    """Check if the termination signal file exists."""
    return os.path.exists(signal_file)

def ensure_block_applied(hosts_path):
    """More careful check and application of the block."""
    try:
        
        if os.path.exists(hosts_path) and os.path.getsize(hosts_path) > MAX_HOSTS_FILE_SIZE:
            logging.error(f"Hosts file {hosts_path} is too large (> {MAX_HOSTS_FILE_SIZE} bytes). Skipping modification.")
            return f"Error: Hosts file too large."

        with open(hosts_path, 'r+') as file:
            content = file.read()
            lines_to_add = []
            needs_update = False

            
            start_index = content.find(block_marker_start)
            end_index = content.find(block_marker_end)

            if start_index == -1 or end_index == -1 or start_index >= end_index:
                
                logging.info("Block markers not found or invalid. Adding new block section.")
                
                content = content.replace(block_marker_start, "").replace(block_marker_end, "")
                content = content.strip() 

                file.seek(0)
                file.write(content) 
                if not content.endswith('\n') and content:
                     file.write('\n')
                file.write(f"\n{block_marker_start}\n")
                for site in blocked_sites:
                    file.write(f"{redirect_ip} {site}\n")
                file.write(f"{block_marker_end}\n")
                file.truncate()
                needs_update = True 
                logging.info("Added new block section to hosts file.")
                return "✅ Block section created."

            else:
                
                current_block = content[start_index:end_index + len(block_marker_end)]
                existing_blocked = set()
                for line in current_block.splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[0] == redirect_ip:
                        existing_blocked.add(parts[1])

                missing_sites = [site for site in blocked_sites if site not in existing_blocked]

                if missing_sites:
                    logging.info(f"Found missing sites in block: {missing_sites}. Adding them.")
                    
                    insert_pos = end_index
                    new_entries = "".join([f"{redirect_ip} {site}\n" for site in missing_sites])

                    file.seek(insert_pos)
                    remaining_content = file.read() 
                    file.seek(insert_pos)
                    file.write(new_entries)
                    file.write(remaining_content)
                    file.truncate()
                    needs_update = True 
                    logging.info(f"Added {len(missing_sites)} missing sites to block section.")
                    return f"✅ Added {len(missing_sites)} missing sites."
                else:
                     logging.debug("All required sites seem present in the block section.")
                     return "✅ Block already seems correct."

    except PermissionError:
        logging.error("Permission denied when trying to access hosts file.")
        return "Error: Permission Denied."
    except IOError as e:
        logging.error(f"I/O error accessing hosts file: {e}")
        return f"Error: I/O Error {e}"
    except Exception as e:
        logging.exception("Unexpected error during block application check.")
        return f"Error: Unexpected error {e}"



def main(signal_file):
    logging.info("Background blocker script started.")
    logging.info(f"Monitoring termination signal file: {signal_file}")

    if not is_admin():
        logging.error("Script not running with admin/root privileges. Exiting.")
        print("Error: This script requires Administrator/root privileges.", file=sys.stderr)
        sys.exit(1)

    hosts_path = None
    try:
        hosts_path = get_hosts_path()
        logging.info(f"Using hosts file: {hosts_path}")
    except OSError as e:
        logging.error(f"Failed to get hosts file path: {e}. Exiting.")
        print(f"Error: Cannot determine hosts file path: {e}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(hosts_path):
         logging.error(f"Hosts file not found at: {hosts_path}. Exiting.")
         print(f"Error: Hosts file not found at {hosts_path}", file=sys.stderr)
         sys.exit(1)


    while True:
        
        if check_termination_signal(signal_file):
            logging.info("Termination signal detected.")
            print("Termination signal received. Attempting to unblock sites...")
            try:
                
                unblock_status = unblock_sites() 
                logging.info(f"Unblock attempt status: {unblock_status}")
                print(f"Unblock status: {unblock_status}")
                
                try:
                    os.remove(signal_file)
                    logging.info(f"Removed signal file: {signal_file}")
                except OSError as e:
                    logging.warning(f"Could not remove signal file {signal_file}: {e}")
            except Exception as e:
                 logging.exception("Error during unblocking process.")
                 print(f"Error during unblocking: {e}", file=sys.stderr)
            finally:
                 logging.info("Background blocker script finished.")
                 sys.exit(0) 

        
        logging.info("Checking and applying website block...")
        try:
            status = ensure_block_applied(hosts_path)
            logging.info(f"Block status: {status}")
            if "Error" in status:
                 print(f"Blocker status: {status}", file=sys.stderr) 
        except Exception as e:
            logging.exception("Error during block application loop.")
            print(f"Error in blocker loop: {e}", file=sys.stderr)


        
        logging.debug(f"Sleeping for {CHECK_INTERVAL_SECONDS} seconds.")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Background process to persistently block websites.")
    parser.add_argument("--signal-file", required=True, help="Path to the file used for termination signal.")
    args = parser.parse_args()

    main(args.signal_file) 