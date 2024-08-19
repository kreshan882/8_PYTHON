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
    ${ststus_code}=     convert to string   ${response.ststus_code}
    should be equal     ${status_code}      200


    ${body}=     convert to string   ${response.content}
    should content     ${body}      matale


    ${contentValueType}=     get from dictionary   ${response.headder}      Content-Type
    should be equal     ${contentValueType}      application/json


    #endSession 2
