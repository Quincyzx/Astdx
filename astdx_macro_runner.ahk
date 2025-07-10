; ASTDX Macro Runner
; This script executes macros from JSON files created by the Macro Maker
; Usage: AutoHotkey.exe astdx_macro_runner.ahk "path/to/macro.json"

#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; Check if a macro file was provided as a parameter
if A_Args.Length() < 1
{
    MsgBox, 16, Error, No macro file specified.`n`nUsage: AutoHotkey.exe astdx_macro_runner.ahk "path/to/macro.json"
    ExitApp
}

MacroFile := A_Args[1]

; Check if the macro file exists
if !FileExist(MacroFile)
{
    MsgBox, 16, Error, Macro file not found: %MacroFile%
    ExitApp
}

; Read the macro file
FileRead, JsonContent, %MacroFile%
if ErrorLevel
{
    MsgBox, 16, Error, Failed to read macro file: %MacroFile%
    ExitApp
}

; Parse JSON (simple parser for our specific format)
MacroData := ParseJsonMacro(JsonContent)
if !MacroData
{
    MsgBox, 16, Error, Failed to parse macro file. Invalid JSON format.
    ExitApp
}

; Display confirmation dialog
MacroName := MacroData.name ? MacroData.name : "Unknown Macro"
ActionsCount := MacroData.actions.Length()
Duration := MacroData.total_duration ? MacroData.total_duration : 0

MsgBox, 4, Confirm Execution, Are you sure you want to execute the macro?`n`nName: %MacroName%`nActions: %ActionsCount%`nDuration: %Duration% seconds`n`nClick Yes to continue or No to cancel.
IfMsgBox No
{
    ExitApp
}

; Wait 3 seconds before starting execution
MsgBox, 0, Starting Execution, Macro execution will begin in 3 seconds...`n`nPress Ctrl+Alt+Q to stop execution at any time., 3

; Set up hotkey to stop execution
Hotkey, ^!q, StopExecution

; Execute the macro
ExecuteMacro(MacroData.actions)

; Show completion message
MsgBox, 0, Execution Complete, Macro execution completed successfully!
ExitApp

; Function to stop execution
StopExecution:
    MsgBox, 0, Execution Stopped, Macro execution has been stopped by user.
    ExitApp

; Function to execute macro actions
ExecuteMacro(Actions)
{
    global
    
    if !Actions
        return
        
    ; Sort actions by timestamp to ensure proper execution order
    SortedActions := SortActionsByTimestamp(Actions)
    
    LastTimestamp := 0
    
    for Index, Action in SortedActions
    {
        ; Check if user wants to stop
        if GetKeyState("Ctrl", "P") && GetKeyState("Alt", "P") && GetKeyState("Q", "P")
        {
            MsgBox, 0, Stopped, Execution stopped by user.
            return
        }
        
        ; Calculate wait time based on timestamp
        CurrentTimestamp := Action.timestamp
        if (CurrentTimestamp > LastTimestamp)
        {
            WaitTime := (CurrentTimestamp - LastTimestamp) * 1000
            if (WaitTime > 0)
                Sleep, %WaitTime%
        }
        
        ; Execute the action
        ActionType := Action.type
        
        if (ActionType = "click")
        {
            X := Action.x
            Y := Action.y
            Button := Action.button
            
            ; Move mouse to position
            MouseMove, %X%, %Y%, 0
            
            ; Perform click based on button type
            if (Button = "left")
                Click
            else if (Button = "right")
                Click, Right
            else if (Button = "middle")
                Click, Middle
            else
                Click ; Default to left click
        }
        else if (ActionType = "key_press")
        {
            Key := Action.key
            
            ; Handle special keys
            if (Key = "space")
                Send, {Space}
            else if (Key = "enter")
                Send, {Enter}
            else if (Key = "tab")
                Send, {Tab}
            else if (Key = "backspace")
                Send, {BackSpace}
            else if (Key = "delete")
                Send, {Delete}
            else if (Key = "shift")
                Send, {Shift}
            else if (Key = "ctrl")
                Send, {Ctrl}
            else if (Key = "alt")
                Send, {Alt}
            else if (Key = "up")
                Send, {Up}
            else if (Key = "down")
                Send, {Down}
            else if (Key = "left")
                Send, {Left}
            else if (Key = "right")
                Send, {Right}
            else if (Key = "home")
                Send, {Home}
            else if (Key = "end")
                Send, {End}
            else if (Key = "page_up")
                Send, {PgUp}
            else if (Key = "page_down")
                Send, {PgDn}
            else if (Key = "escape")
                Send, {Escape}
            else if (Key = "f1")
                Send, {F1}
            else if (Key = "f2")
                Send, {F2}
            else if (Key = "f3")
                Send, {F3}
            else if (Key = "f4")
                Send, {F4}
            else if (Key = "f5")
                Send, {F5}
            else if (Key = "f6")
                Send, {F6}
            else if (Key = "f7")
                Send, {F7}
            else if (Key = "f8")
                Send, {F8}
            else if (Key = "f9")
                Send, {F9}
            else if (Key = "f10")
                Send, {F10}
            else if (Key = "f11")
                Send, {F11}
            else if (Key = "f12")
                Send, {F12}
            else if (StrLen(Key) = 1)
                Send, %Key%
            else
                Send, {%Key%}
        }
        else if (ActionType = "wait")
        {
            Duration := Action.duration
            WaitMs := Duration * 1000
            Sleep, %WaitMs%
        }
        
        LastTimestamp := CurrentTimestamp
    }
}

; Function to sort actions by timestamp
SortActionsByTimestamp(Actions)
{
    SortedActions := []
    
    ; Simple bubble sort for timestamp ordering
    for i, Action in Actions
    {
        SortedActions.Push(Action)
    }
    
    ; Sort by timestamp
    for i := 1 to SortedActions.Length()
    {
        for j := 1 to SortedActions.Length() - i
        {
            if (SortedActions[j].timestamp > SortedActions[j+1].timestamp)
            {
                ; Swap elements
                Temp := SortedActions[j]
                SortedActions[j] := SortedActions[j+1]
                SortedActions[j+1] := Temp
            }
        }
    }
    
    return SortedActions
}

; Simple JSON parser for our specific macro format
ParseJsonMacro(JsonString)
{
    ; Remove whitespace and newlines
    JsonString := RegExReplace(JsonString, "\s+", " ")
    JsonString := Trim(JsonString)
    
    ; Create object to store parsed data
    MacroData := {}
    MacroData.actions := []
    
    ; Extract macro name
    if RegExMatch(JsonString, """name""\s*:\s*""([^""]+)""", NameMatch)
        MacroData.name := NameMatch1
    
    ; Extract total duration
    if RegExMatch(JsonString, """total_duration""\s*:\s*([0-9.]+)", DurationMatch)
        MacroData.total_duration := DurationMatch1
    
    ; Extract actions array
    if RegExMatch(JsonString, """actions""\s*:\s*\[(.*?)\](?=\s*[,}])", ActionsMatch)
    {
        ActionsString := ActionsMatch1
        
        ; Split actions by object boundaries
        Actions := ParseActionsArray(ActionsString)
        MacroData.actions := Actions
    }
    
    return MacroData
}

; Function to parse actions array
ParseActionsArray(ActionsString)
{
    Actions := []
    
    ; Find all action objects in the string
    Pos := 1
    while (Pos <= StrLen(ActionsString))
    {
        ; Find the start of an action object
        if (SubStr(ActionsString, Pos, 1) = "{")
        {
            ; Find the matching closing brace
            BraceCount := 1
            StartPos := Pos
            Pos++
            
            while (Pos <= StrLen(ActionsString) && BraceCount > 0)
            {
                Char := SubStr(ActionsString, Pos, 1)
                if (Char = "{")
                    BraceCount++
                else if (Char = "}")
                    BraceCount--
                Pos++
            }
            
            if (BraceCount = 0)
            {
                ; Extract the action object
                ActionString := SubStr(ActionsString, StartPos, Pos - StartPos)
                Action := ParseActionObject(ActionString)
                if (Action)
                    Actions.Push(Action)
            }
        }
        else
        {
            Pos++
        }
    }
    
    return Actions
}

; Function to parse a single action object
ParseActionObject(ActionString)
{
    Action := {}
    
    ; Extract type
    if RegExMatch(ActionString, """type""\s*:\s*""([^""]+)""", TypeMatch)
        Action.type := TypeMatch1
    
    ; Extract timestamp
    if RegExMatch(ActionString, """timestamp""\s*:\s*([0-9.]+)", TimestampMatch)
        Action.timestamp := TimestampMatch1
    
    ; Extract coordinates for click actions
    if RegExMatch(ActionString, """x""\s*:\s*([0-9]+)", XMatch)
        Action.x := XMatch1
    if RegExMatch(ActionString, """y""\s*:\s*([0-9]+)", YMatch)
        Action.y := YMatch1
    
    ; Extract button for click actions
    if RegExMatch(ActionString, """button""\s*:\s*""([^""]+)""", ButtonMatch)
        Action.button := ButtonMatch1
    
    ; Extract key for key_press actions
    if RegExMatch(ActionString, """key""\s*:\s*""([^""]+)""", KeyMatch)
        Action.key := KeyMatch1
    
    ; Extract duration for wait actions
    if RegExMatch(ActionString, """duration""\s*:\s*([0-9.]+)", DurationMatch)
        Action.duration := DurationMatch1
    
    return Action
}
