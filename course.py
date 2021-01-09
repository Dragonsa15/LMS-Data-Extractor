import shutil 
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from decouple import config

#--------------------------------------------------------------
# CLASS FOR CREATING A COURSE
# Contains name, link to the coourse,links and names of different attributes inside the course
# Doing this makes it easily editable for anything new
# ------------------------------------------------------     

DOWNLOADS_FOLDER = config('DOWNLOADS_FOLDER')
PARENT_PATH = config('PARENT_PATH')

class Course:
    def __init__(self,name,link):
        self.name = name
        self.link = link
        self.atr_name = {'folder' : [],'quiz' : [],'forum' : [],'questionnaire' : [],'assign' : []}
        self.atr = self.atr_name.keys()
        self.attribute_links = {}
        self.attribute_names = {}
        
    def classify(self,link,name):
        for atrb in self.atr:
            if(atrb in link):
                self.atr_name[atrb].append(name)
                self.attribute_links[name] = link
                self.attribute_names[name] = []

    #--------------------------------------------------------------
    # For checking if all downloads have been complpeted or not
    # This is later done by combiniing it in an infinite loop and checking every 5 seconds
    # If the download is taking more than 30 mins the script stops with exception
    # ------------------------------------------------------     
    
    def AllDownloadsExist(self,files):
        bool_list = []
        print(files)
        for file in files:
            bool_list.append(os.path.exists(DOWNLOADS_FOLDER + '/' + file))
        if(False in bool_list):
            return False
        else:
            return True

    #--------------------------------------------------------------
    # For extracting al the download file links and the names 
    # Used by the special class name fp-filename-icon
    # Note: The first icon is for the folder and should be removed
    # ------------------------------------------------------     
  
    def study_material(self,driver,key):
        try:
            # Waiting till the page loads the element that I need
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fp-filename-icon"))
                )
            time.sleep(2)
            
        finally:
            # Extracting the study material in this case (slides and notes)
            study_material = driver.find_elements_by_class_name('fp-filename-icon')
            if(not study_material):
                return

            if(len(study_material) == 1):
                return

            study_material = study_material[1:]

            for i in range(len(study_material)):
                self.attribute_names[key].append(study_material[i].find_element_by_class_name('fp-filename').text)
                print(study_material[i].find_element_by_tag_name('a').get_attribute('href'))
                driver.get(study_material[i].find_element_by_tag_name('a').get_attribute('href'))
            
            
            dt_started = datetime.datetime.utcnow()
        
            while(not self.AllDownloadsExist(self.attribute_names[key]) or (dt_ended - dt_started).total_seconds() > 30 * 60):
                dt_ended = datetime.datetime.utcnow()
                time.sleep(5)

            if((dt_ended - dt_started).total_seconds() > 30 * 60):
                raise Exception('The download took too much time')
                
            for i in range(len(self.attribute_names[key])):
                shutil.move(DOWNLOADS_FOLDER + '/' + self.attribute_names[key][i],PARENT_PATH + '/' + self.name + '/' + key)

    #--------------------------------------------------------------
    # Generic Function To extract data from the resources 
    # Will contain specific extract function for each resource
    # Note: Each function can be created into a different class but too many modules for now ;-;
    # ------------------------------------------------------     
       
    def extract_resource(self,driver):
        for key in self.attribute_links:
            link = self.attribute_links[key]
            driver.get(link)
            if(key in self.atr_name['folder']):
                self.study_material(driver,key)
            if(key in self.atr_name['forum']):
                continue