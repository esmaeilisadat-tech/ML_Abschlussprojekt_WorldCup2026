$json = Get-Content 'notebooks\08_final_presentation_dashboard.ipynb' -Raw | ConvertFrom-Json
$last_cell = $json.cells[-1]
foreach ($out in $last_cell.outputs) {
    if ($out.output_type -eq 'error') {
        Write-Output $out.ename
        Write-Output $out.evalue
    }
}
