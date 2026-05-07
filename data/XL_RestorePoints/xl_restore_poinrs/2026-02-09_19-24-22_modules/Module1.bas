Attribute VB_Name = "Module1"

Sub ApplyColumnGroup_ByIndex()
   
    ' Make Specific Columns of "dat_mnl_main" Visible for Manual Input
    ' This macro ask you to go to the column groups sheet
    ' and select the groups of columns
    ' you want to display while entering data or processing data.
    
    ' It will then hide all of the data columns in the data manual main sheet
    ' and then make visible the meta-columns and the columns selected by this group name.
'
'
    Dim wsData As Worksheet
    Dim wsGroups As Worksheet
    Dim grpRow As Long
    Dim lastCol As Long
    Dim col As Long
    Dim visFlag As String

    Set wsData = Worksheets("dat_mnl_main")
    Set wsGroups = Worksheets("ColumnGroups")

    If ActiveSheet.Name <> "ColumnGroups" Then
        MsgBox "Go to the ColumnGroups sheet and click a group name."
        Exit Sub
    End If

    grpRow = Selection.Row
    If grpRow < 3 Then
        MsgBox "Select a group name in column A."
        Exit Sub
    End If

    'Unhide all columns safely
    wsData.Columns.Hidden = False

    lastCol = wsGroups.Cells(1, wsGroups.Columns.Count).End(xlToLeft).Column

    For col = 1 To lastCol
        visFlag = wsGroups.Cells(grpRow, col).Value
        If LCase(visFlag) = "u" Then
            wsData.Columns(col).Hidden = False
        Else
            wsData.Columns(col).Hidden = True
        End If
    Next col

    wsData.Activate


End Sub


Sub ShowAllColumns()
    'Worksheets("dat_mnl_main").Columns.Hidden = False
    'Sub ShowAllColumns()
    ActiveSheet.Columns.Hidden = False
End Sub



Sub zSyncLabelsToRow2()
    Dim wsData As Worksheet
    Dim wsGroups As Worksheet
    Dim lastCol As Long
    Dim col As Long

    Set wsData = Worksheets("dat_mnl_main")
    Set wsGroups = Worksheets("ColumnGroups")

    lastCol = wsData.Cells(1, wsData.Columns.Count).End(xlToLeft).Column

    For col = 1 To lastCol
        wsGroups.Cells(2, col + 1).Value = wsData.Cells(1, col).Value
    Next col
End Sub
Sub zSyncNamesToData_UsingID()

' This macro goes down the list of names in column two of the attributes spreadsheet looks at the ID
' looks at the ID number
' then goes to that ID number of the columns
' writes that name into the label of that column.

    Dim dataSheet As Worksheet
    Dim attrSheet As Worksheet
    Dim lastRow As Long
    Dim ID As Long
    Dim datasetName As String
    Dim r As Long

    Set dataSheet = Sheets("Data")
    Set attrSheet = Sheets("Attributes")
    

    ' Find last used row in Attributes sheet
    lastRow = attrSheet.Cells(attrSheet.Rows.Count, 1).End(xlUp).Row

    ' Loop through each attribute row
    For r = 2 To lastRow
        
        ID = attrSheet.Cells(r, 1).Value          ' Column 1 = ID
        datasetName = attrSheet.Cells(r, 2).Value ' Column 2 = dataset name
        
        ' Write dataset name into Data sheet column header
        dataSheet.Cells(1, ID).Value = datasetName
        
    Next r

End Sub

Sub Z_HighlightActiveGroup()
'Made obsolete by adjusting the visibility with the
    Dim ws As Worksheet
    Dim grpRow As Long
    Dim lastCol As Long

    Set ws = Worksheets("ColumnGroups")

    If ActiveSheet.Name <> "ColumnGroups" Then Exit Sub

    grpRow = Selection.Row
    If grpRow < 3 Then Exit Sub

    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    ws.Rows("3:" & ws.Rows.Count).Interior.ColorIndex = xlNone

    ws.Range(ws.Cells(grpRow, 1), ws.Cells(grpRow, lastCol)).Interior.Color = RGB(200, 230, 255)
End Sub

Sub zCreateNewGroup()
'Think this is obsolete because we know make the groups with Excel
    Dim ws As Worksheet
    Dim nextRow As Long
    Dim lastCol As Long

    Set ws = Worksheets("ColumnGroups")

    nextRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row + 1
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    ws.Cells(nextRow, 1).Value = "New_Group_" & nextRow - 2
    ws.Range(ws.Cells(nextRow, 2), ws.Cells(nextRow, lastCol)).Value = ""

    ws.Cells(nextRow, 1).Select
End Sub

Sub Z_AutoExpandIndexRow()
    Dim wsData As Worksheet
    Dim wsGroups As Worksheet
    Dim lastCol As Long
    Dim col As Long

    Set wsData = Worksheets("dat_mnl_main")
    Set wsGroups = Worksheets("ColumnGroups")

    lastCol = wsData.Cells(1, wsData.Columns.Count).End(xlToLeft).Column

    For col = 1 To lastCol
        wsGroups.Cells(1, col + 1).Value = col
    Next col
End Sub


Sub GoToValue46000()
    'Goes to a value that is close to today will step it up as time goes on
    
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim r As Long
    Dim dat_col As String
    
    'Set your sheet name
    Set ws = Worksheets("dat_mnl_main")
    ws.Activate

    'Set which column "dat_col" refers to
    dat_col = "C"   '<<< change this if needed

    'Clear previous highlights
    ws.Cells.Interior.ColorIndex = xlNone

    'Find last used row in that column
    lastRow = ws.Cells(ws.Rows.Count, dat_col).End(xlUp).Row

    'Loop through rows
    For r = 1 To lastRow
    ' ================================ set dtv here =============================================
        If ws.Cells(r, dat_col).Value = 46077 Then
    ' ================================ set dtv here =============================================
            'Highlight the row
            ' ws.Rows(r).Interior.Color = vbYellow
            
            'Scroll so the row appears near the top
            Dim scrollRow As Long
            scrollRow = Application.Max(1, r - 7)
            ws.Cells(scrollRow, 1).Select
            
            Exit Sub
        End If
    Next r

    MsgBox "No row found where " & dat_col & " = 46000.", vbInformation

End Sub

Sub zShowColumns_Toggle(choice As String)
    ' Obsolete?=====================================================
    ' Clean, Modular VBA Version (Uses Selected Cell)\
    Dim ws As Worksheet
    Dim rowName As String
    Dim targetRow As Long
    Dim lastCol As Long
    Dim c As Long

    Set ws = ActiveWorkbook.Worksheets("ColumnGroups")

    ' Use ActiveCell instead of Selection
    If ActiveCell.Column <> 1 Then
        MsgBox "Please click a name in Column A first.", vbExclamation
        Exit Sub
    End If

    rowName = ActiveCell.Value

    If Trim(rowName) = "" Then
        MsgBox "The selected cell is empty. Select a valid name in Column A.", vbExclamation
        Exit Sub
    End If

    ' Find the row
    On Error Resume Next
    targetRow = ws.Columns(1).Find(What:=rowName, LookIn:=xlValues, LookAt:=xlWhole).Row
    On Error GoTo 0

    If targetRow = 0 Then
        MsgBox "Row name not found in Column A.", vbExclamation
        Exit Sub
    End If

    ' Determine last column
    lastCol = ws.Cells(targetRow, ws.Columns.Count).End(xlToLeft).Column

    ' Hide all columns except A
    ws.Columns.Hidden = False
    ws.Range(ws.Columns(2), ws.Columns(lastCol)).EntireColumn.Hidden = True

    ' Unhide matching columns
    For c = 2 To lastCol
        If LCase(ws.Cells(targetRow, c).Value) = choice Then
            ws.Columns(c).Hidden = False
        End If
    Next c

End Sub

Sub ShowColumns_H()
    ' Makes visible all of the columns that have an "h"
    Call ShowColumns_Toggle("h")
End Sub

Sub ShowColumns_U()
    ' Makes visible all of the columns that have an "h"
    Call ShowColumns_Toggle("u")
End Sub

Sub SyncColumnNames()
    '' This macro sinks any changes made in the "col_nam_cls" data column names to the corresponding data column names
    ' dat_mnl_main" and the "ColumnGroups"
    
    Dim wsMap As Worksheet
    Dim wsMain As Worksheet
    Dim wsGroups As Worksheet
    Dim lastRow As Long
    Dim r As Long
    Dim idx As Variant
    Dim newName As String
    Dim targetCol As Long

    ' Set sheet references (works across any workbook)
    Set wsMap = ActiveWorkbook.Worksheets("col_nam_cls")
    Set wsMain = ActiveWorkbook.Worksheets("dat_mnl_main")
    Set wsGroups = ActiveWorkbook.Worksheets("ColumnGroups")

    ' Determine last used row in the mapping sheet
    lastRow = wsMap.Cells(wsMap.Rows.Count, 1).End(xlUp).Row

    ' Loop through mapping rows starting at row 3
    For r = 3 To lastRow

        idx = wsMap.Cells(r, 1).Value
        newName = wsMap.Cells(r, 2).Value

        ' Skip blank or invalid rows
        If Trim(idx) <> "" And Trim(newName) <> "" Then

            ' Find the matching column in dat_mnl_main (Row 1)
            On Error Resume Next
            targetCol = wsMain.Rows(1).Find(What:=idx, LookIn:=xlValues, LookAt:=xlWhole).Column
            On Error GoTo 0

            If targetCol >= 3 Then
                wsMain.Cells(2, targetCol).Value = newName
            End If

            ' Find the matching column in ColumnGroups (Row 1)
            On Error Resume Next
            targetCol = wsGroups.Rows(1).Find(What:=idx, LookIn:=xlValues, LookAt:=xlWhole).Column
            On Error GoTo 0

            If targetCol >= 3 Then
                wsGroups.Cells(2, targetCol).Value = newName
            End If

        End If

    Next r

    MsgBox "Column names synchronized successfully.", vbInformation

End Sub


Sub SyncBack_From_Main_To_All()
' Does not work when filters are applied or columns are hidden. It's supposed to will try to fix it at a later time
    Dim wb As Workbook
    Set wb = ActiveWorkbook

    Dim wsMap As Worksheet
    Dim wsMain As Worksheet
    Dim wsGroups As Worksheet

    Dim lastCol As Long
    Dim c As Long
    Dim idx As Variant
    Dim newName As String
    Dim mapRow As Long
    Dim grpCol As Long
    Dim rng As Range

    Set wsMap = wb.Worksheets("col_nam_cls")
    Set wsMain = wb.Worksheets("dat_mnl_main")
    Set wsGroups = wb.Worksheets("ColumnGroups")

    ' Determine last used column in dat_mnl_main row 1
    lastCol = wsMain.Cells(1, wsMain.Columns.Count).End(xlToLeft).Column

    ' Loop through columns starting at column 3
    For c = 3 To lastCol

        idx = wsMain.Cells(1, c).Value
        newName = wsMain.Cells(2, c).Value

        If Trim(idx) <> "" Then

            '--- Update col_nam_cls ---
            Set rng = wsMap.Columns(1).Find(What:=idx, LookIn:=xlValues, LookAt:=xlWhole, SearchFormat:=False)
            If Not rng Is Nothing Then
                If rng.Row >= 3 Then
                    wsMap.Cells(rng.Row, 2).Value = newName
                End If
            End If

            '--- Update ColumnGroups ---
            Set rng = wsGroups.Rows(1).Find(What:=idx, LookIn:=xlValues, LookAt:=xlWhole, SearchFormat:=False)
            If Not rng Is Nothing Then
                If rng.Column >= 3 Then
                    wsGroups.Cells(2, rng.Column).Value = newName
                End If
            End If

        End If

    Next c

    MsgBox "Reverse sync complete (visibility-proof).", vbInformation

End Sub

Sub ShowColumns_Toggle(mode As String)

    Dim wsGroups As Worksheet
    Dim wsData As Worksheet
    Dim selRow As Long
    Dim lastCol As Long
    Dim i As Long
    Dim headerVal As String

    Set wsGroups = ActiveWorkbook.Worksheets("ColumnGroups")
    Set wsData = ActiveSheet

    ' Operator must select a row in ColumnGroups
    If ActiveSheet.Name <> "ColumnGroups" Then
        MsgBox "Select a row in ColumnGroups first."
        Exit Sub
    End If

    selRow = ActiveCell.Row
    lastCol = wsData.Cells(1, wsData.Columns.Count).End(xlToLeft).Column

    ' Loop through all columns regardless of visibility
    For i = 1 To lastCol
        headerVal = wsGroups.Cells(selRow, i).Value

        Select Case mode
            Case "h"
                wsData.Columns(i).Hidden = (headerVal <> "h")
            Case "u"
                wsData.Columns(i).Hidden = (headerVal <> "u")
        End Select
    Next i

End Sub
Sub CopyVisibleFromPreviousRow()
    'From yesterday two today for only the visible columns
    Dim ws As Worksheet
    Dim r As Long
    Dim c As Long
    Dim lastCol As Long

    Set ws = Worksheets("dat_mnl_main")

    ' Ensure we are on the correct sheet
    If ActiveSheet.Name <> ws.Name Then
        MsgBox "Go to dat_mnl_main and select a cell in the row you want to update."
        Exit Sub
    End If

    ' Determine active row
    r = ActiveCell.Row
    If r <= 1 Then
        MsgBox "No previous row to copy from."
        Exit Sub
    End If

    ' Determine last used column
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    ' Loop through columns E onward
    For c = 6 To lastCol   ' Column F = 6

        ' Only copy if column is visible
        If ws.Columns(c).Hidden = False Then
            ws.Cells(r, c).Value = ws.Cells(r - 1, c).Value
        End If

    Next c

End Sub


'----------------------------------
Sub CreateRestorePoint()

    Dim backupPath As String
    Dim modulePath As String
    Dim ts As String
    Dim wb As Workbook
    Dim vbComp As Object
    Dim fso As Object
    
    Set wb = ThisWorkbook
    
    ts = Format(Now, "yyyy-mm-dd_hh-nn-ss")
    
    backupPath = "C:\Users\bhuns\OneDrive\xl_restore_poinrs\" & ts & "_backup.xlsm"
    modulePath = "C:\Users\bhuns\OneDrive\xl_restore_poinrs\" & ts & "_modules\"
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FolderExists(modulePath) Then
        fso.CreateFolder modulePath
    End If
    
    wb.SaveCopyAs backupPath
    
    For Each vbComp In wb.VBProject.VBComponents
        Select Case vbComp.Type
            Case 1, 2, 3
                vbComp.Export modulePath & vbComp.Name & ".bas"
        End Select
    Next vbComp
    
    MsgBox "Restore point created:" & vbCrLf & _
           backupPath & vbCrLf & _
           "Modules exported to: " & modulePath, vbInformation

End Sub

