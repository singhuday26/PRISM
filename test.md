# Quick PRISM Self-Check

Use this checklist to confirm the app is running correctly.

## 1) Start PRISM

```powershell
python start_prism.py
```

## 2) API health checks

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health/ping -UseBasicParsing | Select-Object -ExpandProperty Content
Invoke-WebRequest http://127.0.0.1:8000/health/ -UseBasicParsing | Select-Object -ExpandProperty Content
```

Expected:

- `status` is `ok`
- DB status is healthy/connected

## 3) Basic endpoint checks

```powershell
Invoke-WebRequest http://127.0.0.1:8000/diseases/ -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest http://127.0.0.1:8000/regions/ -UseBasicParsing | Select-Object StatusCode
```

Expected:

- Both return status code `200`

## 4) UI checks (open in browser)

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/ui/
- http://127.0.0.1:8501

Expected:

- Docs page loads
- React UI loads
- Streamlit dashboard loads

## 5) Error log tail

```powershell
Get-Content .\logs\prism_errors.log -Tail 50
```

Expected:

- No new critical errors while testing
