
$WshShell = New-Object -ComObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcut = $WshShell.CreateShortcut("$desktopPath\SERVLIM - Informes.lnk")
$shortcut.TargetPath = "$PSScriptRoot\panel_informes.html"
$shortcut.IconLocation = "$PSScriptRoot\servlim_icono.ico"
$shortcut.Save()
