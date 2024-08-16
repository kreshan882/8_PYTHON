UOB-Robot Framework

VisualStudioCode ---> plugin [PyDev] install
1)   Python Install download python-3.12.3-amd64.exe and install
     pyDev [Plugin for VSC]
     PyCharm IDE  --> https://www.jetbrains.com/pycharm/download/?section=windows   [PyCharm Community Edition]  -- not working | installed
        [https://bitbucketp.sg.uobnet.com/users/tmp5bv/repos/uob-tools/browse/tools/pycharm-community-2020.2.1.exe]

2) terminal changed to windows [VSC]
    Vs-Code => setting -> user-> feature -> Terminal [Integrated › Default Profile: Windows] --> comment prompet

3) PIP | Python EnvVar Path set

4) install with PIP
    pip --version
    pip install -U selenium --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
    pip install robotframework --trusted-host=pypi.org --trusted-host=files.pythonhosted.org   ======> done success

    pip install --upgrade setuptools wheel --trusted-host=pypi.org --trusted-host=files.pythonhosted.org  --======bug fixed
    pip install webdriver_manager --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
    pip install robotframework-seleniumlibrary --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
    pip list =====> all installed libeary

5) Learn: https://www.youtube.com/watch?v=UbYxkUq0Hec&list=PLUDwpEzHYYLsCHiiihnwl3L0xPspL7BPG
	Accepted test deriven developement (user test)
	basic code ---> min 3.35

    RobotFrameworkID[ RIDE | pycharm with intellibot plugin]
===============================================================================
6) Create New project [Pycharm IDE] 
        Add new project [D:\8_PYTHON\PyCharmProjectK]

7) Add 3 libeary to pyCharm IDE[project]	
	pycharm IDE-> select project -> file-> settings-> project:pythonProject -> Python Interpritor(select) 
    -> + add libearies (selenium | robotframework |robotframework-seleniumlibrary| webdriver-manager) |Install ---> restart

8) add plugin
    pycharm IDE-> select project -> file-> settings-> plugin -> market place
    search[intellibot] --> IntelliBot @SeleniumLibrary Patched |install

9) download chrome driver
    https://www.selenium.dev/downloads/ 
    https://googlechromelabs.github.io/chrome-for-testing/

9) Coading [https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html ]
    A. TC1.robot [4 secetion]

10) Run in pyChan IDE
    terminal -> D:\8_PYTHON\PyCharmProjectK\pythonProject> robot TestCases/TC1.robot 
        OutPUT --> log.html | report.html |  output.xml

==============================================================
video 3-----> cont...