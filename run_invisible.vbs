' ============================================
' pyptube - Invisible Mode Launcher
' ============================================
' Run pyptube.py in hidden console window

Set objShell = CreateObject("WScript.Shell")
strBatchFile = objShell.CurrentDirectory & "\run_pyptube.bat"

' Window Style: 0 = hidden, 1 = normal
' Parameters: command, windowStyle, bWaitOnReturn
objShell.Run strBatchFile, 0, False

' Optional: Log that service started
' Uncomment to create a log entry
' Set objFSO = CreateObject("Scripting.FileSystemObject")
' Set objFile = objFSO.CreateTextFile("pyptube_started.log", True)
' objFile.WriteLine Now & " - pyptube started in invisible mode"
' objFile.Close
