import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "report"))
from update_report import update_report

DRIVER_PATH = Path(__file__).resolve().parents[1] / "utils" / "msedgedriver.exe"
LOGIN_URL = "https://opticore-system.vercel.app/login"
STUDENT_DASHBOARD_URL = "https://opticore-system.vercel.app/student"
TS = "TS-001"

def login(email, password):
    driver = webdriver.Edge(service=Service(str(DRIVER_PATH)))
    driver.get(LOGIN_URL)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    return driver


def get_messages(driver):
    """Return the validation errors and toast text shown on the page, if any."""
    def read(d):
        texts = [e.text.strip() for e in d.find_elements(By.CSS_SELECTOR, "[role=alert]") if e.text.strip()]
        return texts or False
    try:
        return " | ".join(WebDriverWait(driver, 5).until(read))
    except Exception:
        return ""

def run_case(tc, email, password, check, pass_msg, fail_msg, location):
    driver = login(email, password)
    messages = get_messages(driver)
    try:
        check(driver)
        status, actual = "Pass", pass_msg
    except Exception:
        status, actual = "Fail", messages
    finally:
        driver.quit()

    if messages:
        actual += f'. Error message: "{messages}"'
    update_report(TS, tc, actual, status, location)
    print(f"{TS}/{tc} {status.upper()}: {actual}")


def expect_student_dashboard(driver):
    WebDriverWait(driver, 10).until(EC.url_contains("/student"))

def expect_stay_on_login(driver):
    time.sleep(5)  # give the API call time to respond before checking
    assert "/student" not in driver.current_url
    assert "/login" in driver.current_url

run_case(
    "TC-001", "joangelbolingo5@gmail.com", "yel12345", expect_student_dashboard, 
    "Student has successfully logged in and redirected to the student dashboard",
    "Student hasn't successfully logged in",
    f"{LOGIN_URL} -> {STUDENT_DASHBOARD_URL}"
)

run_case(
    "TC-002", "wwss@gmail.com", "sssx12312321", expect_stay_on_login, 
    "Student hasn't successfully logged in",
    "Student has successfully logged in and redirected to the student dashboard",
    LOGIN_URL
)