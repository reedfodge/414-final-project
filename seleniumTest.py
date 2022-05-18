from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.blueapron.com/cookbook")
list_links = driver.find_elements_by_tag_name('a')
print(list_links)
