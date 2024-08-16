from selenium import webdriver

browser = webdriver.Chrome(executable_path="C:\PORTABLE_K\DRIVER\chromedriver-win64\chromedriver.exe")
browser.get("https://demo.nopcommerce.com/")
browser.fine_element_by_name("username").send_keys("admin")
browser.fine_element_by_name("login").click()
browser.close()