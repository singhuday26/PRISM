# kill_prism.ps1
# Forcefully terminates all PRISM-related processes

Write-Host "[*] Searching for PRISM processes..." -ForegroundColor Cyan

$processNames = @("uvicorn", "streamlit")
$keyword = "PRISM"

# Find python processes running PRISM scripts
$prismScripts = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { 
    $_.CommandLine -like "*start_prism.py*" -or 
    $_.CommandLine -like "*backend.app:app*" -or 
    $_.CommandLine -like "*streamlit run*" -or
    $_.CommandLine -like "*run_dashboard.py*" -or
    $_.CommandLine -like "*start_backend.py*"
}

$count = 0

if ($prismScripts) {
    foreach ($p in $prismScripts) {
        Write-Host "[!] Terminating process $($p.ProcessId): $($p.CommandLine)" -ForegroundColor Yellow
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        $count++
    }
}

# Also try to kill by name for generic uvicorn/streamlit if they aren't caught
foreach ($name in $processNames) {
    try {
        $procs = Get-Process -Name $name -ErrorAction SilentlyContinue
        if ($procs) {
            foreach ($proc in $procs) {
                Write-Host "[!] Terminating generic process $($proc.Id) ($name)" -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                $count++
            }
        }
    } catch {}
}

if ($count -gt 0) {
    Write-Host "[+] Terminated $count PRISM-related processes." -ForegroundColor Green
} else {
    Write-Host "[i] No PRISM processes found." -ForegroundColor DarkCyan
}
