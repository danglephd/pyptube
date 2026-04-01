' ============================================
' pyptube + Node.js Server - Invisible Mode Launcher
' ============================================
' Run npm start (Node.js server) and pyptube.py in hidden console windows

Set objShell = CreateObject("WScript.Shell")
strCurrentDir = objShell.CurrentDirectory
strBatchFile = strCurrentDir & "\run_pyptube.bat"

' Window Style: 0 = hidden, 1 = normal
' Parameters: command, windowStyle, bWaitOnReturn

' Start Node.js server (npm start) in hidden mode
' Using cmd /c to run the command
objShell.Run "cmd /c npm start", 0, False

' Small delay to allow npm server to start
WScript.Sleep 2000

' Run pyptube.py batch file in hidden mode
objShell.Run strBatchFile, 0, False

' Optional: Log that services started
' Uncomment to create a log entry
' Set objFSO = CreateObject("Scripting.FileSystemObject")
' Set objFile = objFSO.CreateTextFile("services_started.log", True)
' objFile.WriteLine Now & " - npm server and pyptube started in invisible mode"
' objFile.Close
