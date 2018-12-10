Function zip(fso, src, dst)

  Set shell = CreateObject("WScript.Shell")  
  
  If Not fso.FileExists(dst) Then
    call create_new_zipfile(fso, dst)
  End If
 
  Set app = CreateObject("Shell.Application")

  i = 0
  For Each file In app.NameSpace(src).items
    app.NameSpace(dst).CopyHere file
    i = i + 1

  ' Apparently there's no way to do an automatic synchronous copy.
  ' This is a stupid way of doing it but I couldn't find a better 
  ' technique online. 
  
  n = 0
  maxn = 60
  st = 1000
  On Error Resume Next
  Do Until i = app.NameSpace(dst).Items.Count
    Wscript.Sleep(st)
    n = n + 1
    If n > maxn Then 
      WScript.Echo "Timeout occurred copying " & file & " (" & Cstr(st*maxn / 1000) & "s)."
      WScript.Quit
    End If
  Loop
  On Error GoTo 0
  Next 
End Function
 
Sub create_new_zipfile(fso, dst)
  ' Do some magic to fool windows into thinking this is a real zip file
  Set f = fso.CreateTextFile(dst)
  f.Write Chr(80) & Chr(75) & Chr(5) & Chr(6) & String(18, 0)
  f.Close
  Set f = Nothing
  Wscript.Sleep(500) ' Never trust vbScript to be synchronous....
End Sub

' Entry code

Set fso = CreateObject("Scripting.FileSystemObject")
src = fso.GetAbsolutePathName(WScript.Arguments(0))
dst = fso.GetAbsolutePathName(WScript.Arguments(1))

zip fso, src, dst