$ErrorActionPreference = "Stop"

$workspaceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $workspaceRoot "venv\\Scripts\\python.exe"
$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }

$services = @(
    @{ Name = "gateway"; Dir = "gateway"; Port = 8000 },
    @{ Name = "users"; Dir = "user-service"; Port = 8001 },
    @{ Name = "products"; Dir = "product-service"; Port = 8002 },
    @{ Name = "cart"; Dir = "cart-service"; Port = 8003 },
    @{ Name = "orders"; Dir = "order-service"; Port = 8004 },
    @{ Name = "inventory"; Dir = "inventory-service"; Port = 8005 },
    @{ Name = "payments"; Dir = "payment-service"; Port = 8006 }
)

$started = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url
    )

    try {
        $res = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 8
        return [PSCustomObject]@{
            Name = $Name
            Url = $Url
            Status = $res.StatusCode
            Result = "PASS"
            Detail = ""
        }
    }
    catch {
        $statusCode = "N/A"
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }

        return [PSCustomObject]@{
            Name = $Name
            Url = $Url
            Status = $statusCode
            Result = "FAIL"
            Detail = $_.Exception.Message
        }
    }
}

try {
    Write-Host "Starting gateway and all microservices..." -ForegroundColor Cyan

    foreach ($svc in $services) {
        $servicePath = Join-Path $workspaceRoot $svc.Dir
        $args = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$($svc.Port)")

        $proc = Start-Process -FilePath $pythonCmd -ArgumentList $args -WorkingDirectory $servicePath -PassThru -WindowStyle Hidden
        $started += [PSCustomObject]@{
            Name = $svc.Name
            Port = $svc.Port
            Process = $proc
        }
    }

    Start-Sleep -Seconds 5

    $tests = @(
        @{ Name = "Gateway root"; Url = "http://127.0.0.1:8000/" },
        @{ Name = "Users direct"; Url = "http://127.0.0.1:8001/api/users" },
        @{ Name = "Products direct"; Url = "http://127.0.0.1:8002/" },
        @{ Name = "Cart direct"; Url = "http://127.0.0.1:8003/api/cart/1" },
        @{ Name = "Orders direct"; Url = "http://127.0.0.1:8004/api/orders" },
        @{ Name = "Inventory direct"; Url = "http://127.0.0.1:8005/api/inventory" },
        @{ Name = "Payments direct"; Url = "http://127.0.0.1:8006/api/payments" },
        @{ Name = "Users via gateway"; Url = "http://127.0.0.1:8000/users/api/users" },
        @{ Name = "Products via gateway"; Url = "http://127.0.0.1:8000/products/" },
        @{ Name = "Cart via gateway"; Url = "http://127.0.0.1:8000/cart/api/cart/1" },
        @{ Name = "Orders via gateway"; Url = "http://127.0.0.1:8000/orders/api/orders" },
        @{ Name = "Inventory via gateway"; Url = "http://127.0.0.1:8000/inventory/api/inventory" },
        @{ Name = "Payments via gateway"; Url = "http://127.0.0.1:8000/payments/api/payments" }
    )

    $results = foreach ($t in $tests) {
        Test-Endpoint -Name $t.Name -Url $t.Url
    }

    Write-Host ""
    Write-Host "Verification Results" -ForegroundColor Yellow
    $results | Format-Table -AutoSize

    $failed = $results | Where-Object { $_.Result -eq "FAIL" }

    if ($failed.Count -gt 0) {
        Write-Host ""
        Write-Host "One or more checks failed." -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "All gateway and microservice checks passed." -ForegroundColor Green
    exit 0
}
finally {
    foreach ($item in $started) {
        if ($item.Process -and -not $item.Process.HasExited) {
            Stop-Process -Id $item.Process.Id -Force
        }
    }
}