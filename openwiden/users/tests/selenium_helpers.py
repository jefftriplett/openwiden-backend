import os

from selenium import webdriver


def save_current_state(driver: webdriver.Remote, prefix: str, name: str):
    """
    Selenium debug helper.
    """
    driver.step = getattr(driver, "step", 1)

    # Build path
    path = os.path.join(os.path.dirname(__file__), "selenium")
    page_src_path = os.path.join(path, f"{prefix}_{driver.step}_{name}.html")
    screenshot_path = os.path.join(path, f"{prefix}_{driver.step}_{name}.png")
    info_path = os.path.join(path, f"{prefix}_{driver.step}_{name}.txt")

    # Save page source
    with open(page_src_path, "w") as file:
        file.write(driver.page_source)

    # Save driver info
    with open(info_path, "w") as file:
        data = {
            "title": driver.title,
            "current_url": driver.current_url,
            **driver.__dict__,
        }
        file.writelines([f"{k}: {v}\n" for k, v in data.items()])

    # Save browser screenshot and increase step count
    driver.save_screenshot(screenshot_path)
    driver.step += 1
