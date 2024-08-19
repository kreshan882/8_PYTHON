*** Settings ***
Library     RequestsLibrary
Library     Collections

*** Variables ***
${base_url}     http://localhost:8080
${city}     matale


*** Test Cases ***
Post_CustRegistrationK
    create session  myssionk    ${base_url}
    ${body}= creat dictionary    FistName=raj    LastName:kreshan    Age:11
    ${header}= creat dictionary    Content-Type=application/json
    ${response}=    post request     myssionk    /register  data=${body}    headers=${header}
    log to console  ${response.ststus_code}
    log to console  ${response.content}