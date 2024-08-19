*** Settings ***
Library  RequestsLibrary

*** Variables ***
${base_url}     http://localhost:8080
${city}     matale


*** Test Cases ***
Get_msgDetailsK
    create session  myssionk    ${base_url}
    ${response}=    get request     myssionk    /getlist/${city}
    log to console  ${response.ststus_code}
    log to console  ${response.content}

    #validation checking..
    