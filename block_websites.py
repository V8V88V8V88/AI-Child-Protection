import os

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

# Path to the hosts file (Windows)
hosts_path = r"C:\Windows\System32\drivers\etc\hosts"

# Function to block websites
def block_sites():
    try:
        with open(hosts_path, "a") as file:
            for site in blocked_sites:
                file.write(f"127.0.0.1 {site}\n")
        print("✅ Adult content and harmful sites blocked successfully!")
    except PermissionError:
        print("⚠️ Permission Denied! Run this script as Administrator.")

# Function to unblock websites
def unblock_sites():
    try:
        with open(hosts_path, "r") as file:
            lines = file.readlines()

        with open(hosts_path, "w") as file:
            for line in lines:
                if not any(site in line for site in blocked_sites):
                    file.write(line)

        print("✅ Websites unblocked successfully!")
    except PermissionError:
        print("⚠️ Permission Denied! Run this script as Administrator.")

# Run the blocking function when the script is executed
if __name__ == "__main__":
    block_sites()
