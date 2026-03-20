$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\tlfse\OneDrive\Desktop\CoreLink.lnk")
$Shortcut.TargetPath = "C:\Users\tlfse\corelink-mvp\CoreLink.bat"
$Shortcut.WorkingDirectory = "C:\Users\tlfse\corelink-mvp"
$Shortcut.Description = "CoreLink Email Generator"
$Shortcut.IconLocation = "C:\Users\tlfse\corelink-mvp\src\icon.ico"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop."
