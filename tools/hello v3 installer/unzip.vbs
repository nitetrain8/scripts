'The location of the zip file.

'If the extraction location does not exist create it.
Set fso = CreateObject("Scripting.FileSystemObject")

src = fso.GetAbsolutePathName(Wscript.arguments(0))
dst = fso.GetAbsolutePathName(Wscript.arguments(1))

If NOT fso.FolderExists(dst) Then
   fso.CreateFolder(dst)
End If

'Extract the contants of the zip file.
set objShell = CreateObject("Shell.Application")
set files=objShell.NameSpace(src).items
objShell.NameSpace(dst).CopyHere files, 20
Set fso = Nothing
Set objShell = Nothing