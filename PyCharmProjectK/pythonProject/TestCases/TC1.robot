*** Settings ***
Library  SeleniumLibrary

*** Variables ***
${browser}  chrome
${url}  https://demo.nopcommerce.com/

*** Test Cases ***
LoginTest
#    create webdriver    chrome  --allowed-ips  executable_path="C:\PORTABLE_K\DRIVER\chromedriver-win64\chromedriver.exe"
#    open browser    https://demo.nopcommerce.com/    chrome
    open browser    ${url}    ${browser}
#    click link      xpath://a[@class='ico-login']
#    passInputValueK
##    input text  id:Email    kreshan882@gmail.com
##    input text  id:Password     123456
#    click element   xpath://input[@class='button-1 login-button']
#    close browser

*** Keywords ***
passInputValueK
    input text  id:Email    kreshan882@gmail.com
    input text  id:Password     123456