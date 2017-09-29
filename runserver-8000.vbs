Set WinScriptHost = CreateObject( "WScript.shell" )

WinScriptHost.Run Chr(34) & "C:\inetpub\wwwroot\StockAdmin\runserver-8000.py" & Chr(34), 0

Set WinScriptHost = Nothing