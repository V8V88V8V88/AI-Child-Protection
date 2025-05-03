import os
import json
import shutil
import tempfile
import platform
import webbrowser
from .host_blocker import blocked_sites

def create_chrome_extension():
    """
    Generate a Chrome extension for blocking websites.
    Returns path to the extension directory.
    """
    ext_dir = os.path.join(tempfile.gettempdir(), "ai_child_protection_extension")
    
    
    os.makedirs(ext_dir, exist_ok=True)
    
    
    manifest = {
        "name": "AI Child Protection",
        "version": "1.0",
        "description": "Blocks access to inappropriate websites",
        "manifest_version": 3,
        "permissions": ["webRequest", "webRequestBlocking", "tabs"],
        "host_permissions": ["<all_urls>"],
        "background": {
            "service_worker": "background.js"
        },
        "action": {
            "default_popup": "popup.html",
            "default_icon": {
                "16": "icon16.png",
                "48": "icon48.png",
                "128": "icon128.png"
            }
        },
        "icons": {
            "16": "icon16.png", 
            "48": "icon48.png",
            "128": "icon128.png"
        }
    }
    
    
    background_js = """
// List of sites to block
const blockedSites = %s;

// Function to check if a URL should be blocked
function shouldBlockUrl(url) {
    for (const site of blockedSites) {
        if (url.includes(site)) {
            return true;
        }
    }
    return false;
}

// Listen for web requests
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        if (shouldBlockUrl(details.url)) {
            return {cancel: true};
        }
        return {cancel: false};
    },
    {urls: ["<all_urls>"]},
    ["blocking"]
);

// Listen for tab updates
chrome.tabs.onUpdated.addListener(
    function(tabId, changeInfo, tab) {
        if (changeInfo.url && shouldBlockUrl(changeInfo.url)) {
            chrome.tabs.update(tabId, {url: "blocked.html"});
        }
    }
);
""" % json.dumps(blocked_sites)
    
    
    popup_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Child Protection</title>
    <style>
        body {
            width: 300px;
            padding: 10px;
            font-family: Arial, sans-serif;
        }
        h2 {
            color: #4285f4;
        }
        .status {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h2>AI Child Protection</h2>
    <p>Status: <span class="status">Active</span></p>
    <p>This extension is protecting against inappropriate content.</p>
</body>
</html>
"""
    
    
    blocked_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Blocked</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f8f9fa;
        }
        .blocked-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #d32f2f;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
        }
        .icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="blocked-container">
        <div class="icon">🚫</div>
        <h1>Access Blocked</h1>
        <p>This website has been blocked by AI Child Protection.</p>
        <p>This system is designed to protect against inappropriate content.</p>
    </div>
</body>
</html>
"""
    
    
    with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
    
    with open(os.path.join(ext_dir, "background.js"), "w") as f:
        f.write(background_js)
    
    with open(os.path.join(ext_dir, "popup.html"), "w") as f:
        f.write(popup_html)
    
    with open(os.path.join(ext_dir, "blocked.html"), "w") as f:
        f.write(blocked_html)
    
    
    icon_sizes = [16, 48, 128]
    for size in icon_sizes:
        
        
        icon_file = os.path.join(ext_dir, f"icon{size}.png")
        
        with open(icon_file, "w") as f:
            f.write("")
    
    return ext_dir

def create_firefox_extension():
    """
    Generate a Firefox extension for blocking websites.
    Returns path to the extension directory.
    """
    ext_dir = os.path.join(tempfile.gettempdir(), "ai_child_protection_firefox_extension")
    
    
    os.makedirs(ext_dir, exist_ok=True)
    
    
    manifest = {
        "name": "AI Child Protection",
        "version": "1.0",
        "description": "Blocks access to inappropriate websites",
        "manifest_version": 2,
        "permissions": ["webRequest", "webRequestBlocking", "tabs", "<all_urls>"],
        "background": {
            "scripts": ["background.js"]
        },
        "browser_action": {
            "default_popup": "popup.html",
            "default_icon": {
                "16": "icon16.png",
                "48": "icon48.png",
                "128": "icon128.png"
            }
        },
        "icons": {
            "16": "icon16.png",
            "48": "icon48.png",
            "128": "icon128.png"
        }
    }
    
    
    background_js = """
// List of sites to block
const blockedSites = %s;

// Function to check if a URL should be blocked
function shouldBlockUrl(url) {
    for (const site of blockedSites) {
        if (url.includes(site)) {
            return true;
        }
    }
    return false;
}

// Listen for web requests
browser.webRequest.onBeforeRequest.addListener(
    function(details) {
        if (shouldBlockUrl(details.url)) {
            return {cancel: true};
        }
        return {cancel: false};
    },
    {urls: ["<all_urls>"]},
    ["blocking"]
);

// Listen for tab updates
browser.tabs.onUpdated.addListener(
    function(tabId, changeInfo, tab) {
        if (changeInfo.url && shouldBlockUrl(changeInfo.url)) {
            browser.tabs.update(tabId, {url: "blocked.html"});
        }
    }
);
""" % json.dumps(blocked_sites)
    
    
    popup_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Child Protection</title>
    <style>
        body {
            width: 300px;
            padding: 10px;
            font-family: Arial, sans-serif;
        }
        h2 {
            color: #4285f4;
        }
        .status {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h2>AI Child Protection</h2>
    <p>Status: <span class="status">Active</span></p>
    <p>This extension is protecting against inappropriate content.</p>
</body>
</html>
"""
    
    blocked_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Blocked</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f8f9fa;
        }
        .blocked-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #d32f2f;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
        }
        .icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="blocked-container">
        <div class="icon">🚫</div>
        <h1>Access Blocked</h1>
        <p>This website has been blocked by AI Child Protection.</p>
        <p>This system is designed to protect against inappropriate content.</p>
    </div>
</body>
</html>
"""
    
    
    with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
    
    with open(os.path.join(ext_dir, "background.js"), "w") as f:
        f.write(background_js)
    
    with open(os.path.join(ext_dir, "popup.html"), "w") as f:
        f.write(popup_html)
    
    with open(os.path.join(ext_dir, "blocked.html"), "w") as f:
        f.write(blocked_html)
    
    
    icon_sizes = [16, 48, 128]
    for size in icon_sizes:
        icon_file = os.path.join(ext_dir, f"icon{size}.png")
        with open(icon_file, "w") as f:
            f.write("")
    
    return ext_dir

def create_instructions_file(chrome_ext_path, firefox_ext_path):
    """Create a file with instructions for installing the extensions."""
    instructions = f"""
BROWSER EXTENSION INSTALLATION INSTRUCTIONS
===========================================

These extensions provide an additional layer of protection beyond the hosts file blocking.
They work by intercepting web requests and blocking access to inappropriate sites directly
in the browser.

Chrome/Edge/Opera Extension:
---------------------------
1. Open Chrome/Edge/Opera
2. Go to chrome://extensions/ (or edge://extensions/ or opera://extensions/)
3. Enable "Developer mode" (toggle switch in the top right)
4. Click "Load unpacked"
5. Navigate to: {chrome_ext_path}
6. Select the folder and click "Open"

Firefox Extension:
----------------
1. Open Firefox
2. Go to about:debugging#/runtime/this-firefox
3. Click "Load Temporary Add-on..."
4. Navigate to: {firefox_ext_path}
5. Select the manifest.json file and click "Open"

Note: These are temporary extensions and will need to be reinstalled if the browser is restarted.
For permanent installation, you would need to publish them to the respective extension stores.
"""
    
    instructions_file = os.path.join(tempfile.gettempdir(), "browser_extension_instructions.txt")
    with open(instructions_file, "w") as f:
        f.write(instructions)
    
    return instructions_file

def setup_browser_extensions():
    """Generate browser extensions and return instructions."""
    try:
        chrome_ext_path = create_chrome_extension()
        firefox_ext_path = create_firefox_extension()
        instructions_file = create_instructions_file(chrome_ext_path, firefox_ext_path)
        
        return {
            "chrome_extension_path": chrome_ext_path,
            "firefox_extension_path": firefox_ext_path,
            "instructions_file": instructions_file,
            "status": "✅ Browser extensions created successfully!"
        }
    except Exception as e:
        return {
            "status": f"❌ Error creating browser extensions: {e}"
        }

def open_extension_instructions():
    """Open the instructions file with the default text editor."""
    result = setup_browser_extensions()
    if "instructions_file" in result:
        try:
            if platform.system().lower() == "windows":
                os.startfile(result["instructions_file"])
            elif platform.system().lower() == "darwin":  
                os.system(f"open {result['instructions_file']}")
            else:  
                os.system(f"xdg-open {result['instructions_file']}")
            return "✅ Opened extension installation instructions."
        except Exception as e:
            return f"❌ Error opening instructions: {e}"
    else:
        return result["status"]

if __name__ == "__main__":
    print(open_extension_instructions()) 