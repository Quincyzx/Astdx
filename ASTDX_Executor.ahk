#SingleInstance Force
SetTitleMatchMode, 2
SetBatchLines -1
CoordMode, Mouse, Screen
CoordMode, Pixel, Screen

; Globals
global isRunning := false
global loopThread := 0
global macroList := []
global macroFiles := []

; Load Macros
MacroDir := A_ScriptDir "\macros"
if !FileExist(MacroDir)
    FileCreateDir MacroDir
Loop Files, %MacroDir%\*.json
{
    FileRead, data, %A_LoopFileFullPath%
    try
        obj := JSON_Load(data)
    catch
        continue
    macroList.Push(obj.name)
    macroFiles.Push(A_LoopFileFullPath)
}

; Run the selected macro
RunMacro(selected)
{
    index := macroList.IndexOf(selected) - 1
    file := macroFiles[index]
    FileRead, data, %file%
    try macro := JSON_Load(data)
    catch
    {
        MsgBox, Failed to load macro.
        return
    }

    ; Execute macro actions
    for _, action in macro.actions
    {
        if (action.type = "wait")
        {
            Sleep action.duration
        }
        else if (action.type = "click")
        {
            Click %action.x%, %action.y%
        }
        else if (action.type = "type_text")
        {
            Send % action.text
        }
        else if (action.type = "key_sequence")
        {
            Send % action.keys
        }

        Sleep 100
    }
}
