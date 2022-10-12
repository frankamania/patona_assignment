import os
from pathlib import Path
import csv
import hashlib
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


def get_extension(url,default='png'):
    """
    gets the file ext from a url
    can pass a default for handileing errors

    """
    try:
        return url.rsplit('.', 1)[-1]
    except:
        return default



class Scrape():
    # base configs

    driver = webdriver.Chrome(ChromeDriverManager().install())
    base_url = 'https://dermnetnz.org/image-library'
    rows = []

    # define all the selectors here

    IMAGELIST__GROUP__ITEM_SELECTOR = 'div.content__main > div.\[.js-content-images.\] > div.imageList div.imageList__group a.imageList__group__item'
    IMAGELIST__GROUP__ITEM__COPY_NAME_SELECTOR = 'div.imageList__group__item__copy h6'
    IMAGELIST__GROUP__ITEM__IMAGE_SELECTOR = 'div.imageList__group__item__image img'

    def __init__(self, base_path):
        self.base_path = base_path
        self.images_folder = self.base_path + '/' + 'Images/'
        Path(self.images_folder).mkdir(parents=True, exist_ok=True)

    def scrape(self):
        self.driver.get(self.base_url)
        for imageList__group__item in self.driver.find_elements(by=By.CSS_SELECTOR,value=self.IMAGELIST__GROUP__ITEM_SELECTOR):

            Disease_Name = imageList__group__item.find_element(by=By.CSS_SELECTOR,value=self.IMAGELIST__GROUP__ITEM__COPY_NAME_SELECTOR).text

            Disease_Url = imageList__group__item.get_attribute('href')

            Disease_Logo_Image_url = imageList__group__item.find_element(by=By.CSS_SELECTOR,value=self.IMAGELIST__GROUP__ITEM__IMAGE_SELECTOR).get_attribute('src')

            img_ext = get_extension(Disease_Logo_Image_url)

            Disease_Logo_File_Name = hashlib.md5(Disease_Logo_Image_url.encode()).hexdigest() + '.' + img_ext

            try:
                #download all the image urls useing request lib
                with requests.get(Disease_Logo_Image_url, stream=True) as img_resp, open(
                        self.images_folder + Disease_Logo_File_Name, 'wb') as img_file:
                    img_file.write(img_resp.content)


            except Exception as e:
                print(e, Disease_Logo_Image_url, Disease_Logo_File_Name)
                Disease_Logo_File_Name = None


            self.rows.append(
                dict(

                        Disease_Name=Disease_Name,
                        Disease_Url=Disease_Url,
                        Disease_Logo_Image_url=Disease_Logo_Image_url,
                        Disease_Logo_File_Name=Disease_Logo_File_Name

                     )
            )

    def finish(self):

        if len(self.rows) !=0:

            with open('output.csv','w',encoding='utf-8') as csvFile:
                csvFileDictwriter = csv.DictWriter(csvFile,fieldnames=[x for x in self.rows[0].keys()])
                csvFileDictwriter.writeheader()
                csvFileDictwriter.writerows(self.rows)


        self.driver.close()


if __name__ == '__main__':
    s = Scrape(os.getcwd())
    s.scrape()
    s.finish()
