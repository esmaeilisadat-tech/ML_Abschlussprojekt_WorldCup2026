$json = Get-Content 'notebooks\08_final_presentation_dashboard.ipynb' -Raw | ConvertFrom-Json
$i = 0
foreach ($cell in $json.cells) {
    if ($cell.outputs) {
        foreach ($out in $cell.outputs) {
            if ($out.output_type -eq 'error') {
                Write-Output ("Cell " + $i + " error: " + $out.ename + " - " + $out.evalue)
                foreach ($line in $out.traceback) { Write-Output $line }
            }
            if ($out.output_type -eq 'stream' -and $out.name -eq 'stdout') {
                $text = $out.text -join ""
                if ($text -match 'خطا|ارور|Exception|Traceback|not found|error') {
                    Write-Output ("Cell " + $i + " print: " + $text)
                }
            }
        }
    }
    $i++
}
