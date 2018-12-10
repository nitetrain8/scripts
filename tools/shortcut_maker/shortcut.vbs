Option Explicit
dim fso, target, shortcut

Sub make_shortcut(target, shortcut)
    ' from https://superuser.com/questions/392061/how-to-make-a-shortcut-from-cmd
    dim shell, oLink
    Set shell = CreateObject("WScript.Shell")
   
    if not Right(shortcut, 4) = ".lnk" then
        shortcut = shortcut & ".lnk"
    end if
    set oLink = shell.CreateShortcut(shortcut)
    oLink.TargetPath = target
     '  oLink.Arguments = ""
     '  oLink.Description = "MyProgram"   
     '  oLink.HotKey = "ALT+CTRL+F"
     '  oLink.IconLocation = "C:\Program Files\MyApp\MyProgram.EXE, 2"
     '  oLink.WindowStyle = "1"   
     '  oLink.WorkingDirectory = "C:\Program Files\MyApp"
    oLink.Save
End Sub

Set fso = CreateObject("Scripting.FileSystemObject")
target = fso.GetAbsolutePathName(WScript.Arguments(0))
shortcut = fso.GetAbsolutePathName(WScript.Arguments(1))
make_shortcut target, shortcut