import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Reusable functions
def click_element(driver, locator_type, locator_value):
    wait = WebDriverWait(driver, 4)
    element = wait.until(EC.element_to_be_clickable((locator_type, locator_value)))
    element.click()

def test_insider_home_page():
    chrome_options = webdriver.ChromeOptions()
#   chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')  # Avoid shared memory issues
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU rendering
    chrome_options.add_argument('--window-size=1680,936')  # Set window size
    chrome_options.add_argument('--disable-logging')
    driver = webdriver.Remote(
        command_executor='http://chrome-node-service:4444/wd/hub',
        options=chrome_options
    )
    
    try:
        wait = WebDriverWait(driver, 4)  # Wait time

        # Visit the Insider homepage
        driver.get("https://useinsider.com/")
        
        # Wait for the homepage to load and ensure the title contains "Insider"
        wait.until(EC.title_contains("#1 Leader in Individualized, Cross-Channel CX — Insider"))
        print("Homepage loaded successfully.")
        
        # Navigate to Careers page with Company menu
        try:
            click_element(driver, By.LINK_TEXT, "Company")
            click_element(driver, By.LINK_TEXT, "Careers")
            print("Clicked on menu.")
        except Exception as e:
            print(f"Error clicking on menu: {e}")
            return

        # Verify the title of the Careers page
        title = driver.title
        assert title == "Ready to disrupt? | Insider Careers"
        print("Careers page title verified successfully.")

        if driver.find_elements(By.XPATH, "//*[@id='career-our-location']/div/div/div/div[1]/h3"):
            print("Locations section exists.")
        else:
            print("Locations section does not exist.")

        if driver.find_elements(By.XPATH, "//*[@id='career-find-our-calling']/div/div/div[1]/h3"):
            print("Teams section exists.")
        else:
            print("Teams section does not exist.")

        if driver.find_elements(By.XPATH, "/html/body/div[2]/section[4]/div/div/div/div[1]/div/h2"):
            print("Life section exists.")
        else:
            print("life section does not exist.")


        driver.get("https://useinsider.com/careers/quality-assurance/")
        print("Navigated to QA jobs page.")
        
        see_all_jobs_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='See all QA jobs']")))
        see_all_jobs_button.click()
        print("Clicked on 'See all QA jobs' button.")

        time.sleep(4)

        # Filter by location - Istanbul, Turkey
        driver.find_element(By.XPATH, "//*[@id='select2-filter-by-location-container']").click()
        driver.find_element(By.XPATH, "//li[contains(text(), 'Istanbul, Turkey')]").click()
        print("Filtered jobs by location: Istanbul, Turkey.")

        time.sleep(2)

        # Filter by department - Quality Assurance
        driver.find_element(By.XPATH, "//*[@id='select2-filter-by-department-container']").click()
        driver.find_element(By.XPATH, "//*[@id='top-filter-form']/div[2]/span").click()
        print("Filtered jobs by department: Quality Assurance.")

        # Verify the presence of job listings
        job_listings = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='jobs-list']/div/div")))
        assert len(job_listings) > 0, "No job listings found."
        print(f"Found {len(job_listings)} job listings.")

        # Find all job listings
        job_listings = driver.find_elements(By.XPATH, "//*[@id='jobs-list']/div[@class='position-list-item']")
        # Check that all jobs contain "Quality Assurance" 
        for job in job_listings:
            position = job.find_element(By.XPATH, ".//p[contains(@class, 'position-title')]").text
            department = job.find_element(By.XPATH, ".//span[contains(@class, 'position-department')]").text
            location = job.find_element(By.XPATH, ".//div[contains(@class, 'position-location')]").text      
            # Debugging line 
            print(f"Position: {position}, Department: {department}, Location: {location}") 
            # Perform assertions 
            assert "Quality Assurance" in position, f"Position does not contain 'Quality Assurance': {position}"
            assert "Quality Assurance" in department, f"Department does not contain 'Quality Assurance': {department}"
            assert "Istanbul, Turkey" in location, f"Location is not 'Istanbul, Turkey': {location}"        
        print("All jobs contain the correct Position, Department, and Location.")

        # Click on the "View Role" button and check the Lever application page
        button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-navy.rounded.pt-2.pr-5.pb-2.pl-5")))     
        # Click the button using JavaScript to bypass visibility issues
        driver.execute_script("arguments[0].click();", button)   
        print("Clicked on 'View Role' button.")
        
        # Get the current window handles
        window_handles = driver.window_handles
        # Switch to the new tab
        driver.switch_to.window(window_handles[1])  
        # Check if the current URL contains the specified text
        text_to_check = 'lever'
        current_url = driver.current_url
        if text_to_check in current_url:
            print("Redirected to Lever application form page.")
        else:
            print(f"The URL does not contain '{text_to_check}'.")

    finally:
        driver.quit()

test_insider_home_page()