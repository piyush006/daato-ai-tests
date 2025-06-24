import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Input: url, username, password, scenario (plain English)
url, username, password, scenario_text = sys.argv[1:5]

# Setup browser
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def fail_and_exit(message):
    print(f"❌ {message}")
    driver.quit()
    sys.exit(1)

def find_by_text(text):
    xpath = f"//*[normalize-space(text())='{text}']"
    return driver.find_elements(By.XPATH, xpath)

def get_xpath(el):
    return driver.execute_script("""
        function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) ++position;
                }
                return position;
            };
            for (; element && !(element instanceof Document); element = element.nodeType ==Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = {};
                comp.name = element.nodeName;
                comp.position = getPos(element);
                comps.push(comp);
            }
            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase();
                if (comp.position !== null && comp.position > 1) {
                    xpath += '[' + comp.position + ']';
                }
            }
            return xpath;
        }
        return absoluteXPath(arguments[0]);
    """, el)

try:
    driver.get(url)
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
    time.sleep(3)

    if "login" in driver.current_url.lower():
        fail_and_exit("Login failed: still on login page")

    # Step-by-step: split scenario_text by > or comma
    steps = [s.strip() for s in scenario_text.replace(">", ",").split(",") if s.strip()]

    for step in steps:
        candidates = find_by_text(step)
        if not candidates:
            print(f"⚠️ Could not find element with text: {step}")
            continue
        for el in candidates:
            if el.is_displayed():
                el.click()
                time.sleep(2)
                print(f"✅ Clicked: {step}")
                break

    time.sleep(1)

    # Extract visible elements
    elements = driver.find_elements(By.XPATH, "//*")
    extracted = []

    for el in elements:
        try:
            if el.is_displayed() and (el.tag_name in ['input', 'button', 'select', 'textarea']):
                extracted.append({
                    "tag": el.tag_name,
                    "text": el.text.strip(),
                    "xpath": get_xpath(el),
                    "type": el.get_attribute("type") or ""
                })
        except:
            continue

    with open("element_dump.json", "w") as f:
        json.dump(extracted, f, indent=2)
    print("✅ element_dump.json written.")

except Exception as e:
    fail_and_exit(f"Script failed: {str(e)}")
finally:
    driver.quit()
