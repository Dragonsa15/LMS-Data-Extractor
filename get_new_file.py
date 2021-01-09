from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from course import Course
from decouple import config
import os

DOWNLOADS_FOLDER = config('DOWNLOADS_FOLDER')
PARENT_PATH = config('PARENT_PATH')

#Function to create a New Tab with a name and a link
def OpenNewTab(link,name):
    driver.execute_script("window.open('" + link + "','" + name + "');")

# A helper function to log at which step we are currently at
def Logger(text):
    print('\n-------------- Log : ' + text + ' ------------------\n')

# A helper function to make a directory at a particular path
def makedir(path,directory_name):
    # Making a directory for the course
    if(not os.path.exists(path + '/' + directory_name)):
        # print(directory_name)
        new_path  = path + '/' + directory_name
        # print(new_path)
        mode = 0o666
        os.mkdir(new_path,mode)

PATH = config('CHROME_DRIVER_PATH')

# For hiding the Chrome driver tab
Options = Options()
# Options.headless = True

driver = webdriver.Chrome(executable_path = PATH,options=Options)

driver.get('https://learn.iiitb.net/login/index.php')
Logger('Logging into LMS')
print(driver.title)

#Loogin Code
strUrl_Login = driver.current_url

search = driver.find_element_by_id('username')
print(config('USERNAME'))
search.send_keys(config('USERNAME_LMS'))

search = driver.find_element_by_id('password')
search.send_keys(config('PASSWORD_LMS'))
search.send_keys(Keys.ENTER)

strUrl_check = driver.current_url

if(strUrl_Login == strUrl_check):
    raise Exception('Some error in Login')
    driver.close()
    driver.quit()


try:
    # Waiting for page to get loaded
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dashboard-card-deck"))
    )
    time.sleep(2)
    
finally:
    Logger('Appending the Courses')
    element = driver.find_elements_by_class_name('dashboard-card-deck')[2]
    #A list of all courses
    courses = element.find_elements_by_class_name('dashboard-card')
    
    course_list = []
    
    

    for course in courses:
        
        # Finding the course deets like name and link
        directory_name = course.find_element_by_class_name('multiline').text
        directory_name = directory_name.split('/')[-1].strip()

        course_list.append(Course(directory_name,course.find_element_by_tag_name('a').get_attribute('href')))
        print(course.find_element_by_class_name('multiline').text)
        
        makedir(PARENT_PATH,directory_name)
        
    # print(course_list)

    Logger('Checking for resources')
    for i in range(len(course_list)):
        OpenNewTab(course_list[i].link,course_list[i].name)
        driver.switch_to.window(driver.window_handles[i+1])
        element_links = driver.find_elements_by_class_name('aalink')
        # print(element_links)
        linking = {}
        
        # Getting all the attribute links that are present in each course
        for link in element_links:
            atr = link.find_element_by_class_name('instancename').text.split('\n')[0]
            # Making a directory for each of the link elements that we get
            makedir(PARENT_PATH + '/' + course_list[i].name,atr)
            
            course_list[i].classify(link.get_attribute('href'),atr)

        course_list[i].extract_resource(driver)

        print(course_list[i].name,course_list[i].attribute_links)
        


    time.sleep(5)

    

# For closing the tab
# driver.close()

#For closing the driver var
driver.quit()
