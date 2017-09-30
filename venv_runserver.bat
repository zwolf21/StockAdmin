@echo off

set "VIRTUAL_ENV=.."



if not defined PROMPT (

    set "PROMPT=$P$G"

)

if defined _OLD_VIRTUAL_PROMPT (

    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"

)

if defined _OLD_VIRTUAL_PYTHONHOME (

    set "PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%"

)

set "_OLD_VIRTUAL_PROMPT=%PROMPT%"

set "PROMPT=(Django1.10.5) %PROMPT%"



if defined PYTHONHOME (

    set "_OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%"

    set PYTHONHOME=

)



if defined _OLD_VIRTUAL_PATH (

    set "PATH=%_OLD_VIRTUAL_PATH%"

) else (

    set "_OLD_VIRTUAL_PATH=%PATH%"

)



set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

rem C:\Users\HS\Desktop\Django\Django1.10.5\StockAdmin2\manage.py runserver
manage.py runserver 0.0.0.0:8888

:END

