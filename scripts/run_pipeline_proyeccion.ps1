<#
.SYNOPSIS
    Ejecuta el pipeline completo del modelo M6 (predicción de tendencia de población):
    descarga INE -> validación -> entrenamiento -> ONNX (oracle\onnx\m6_proyeccion.onnx).

.EXAMPLE
    .\scripts\run_pipeline_proyeccion.ps1
    .\scripts\run_pipeline_proyeccion.ps1 -Anios 25 -InstalarDependencias
    .\scripts\run_pipeline_proyeccion.ps1 -SinDescarga
    .\scripts\run_pipeline_proyeccion.ps1 -DesdeSnapshot data\raw\ine\ine_padron_2881_6y_snapshot_20261025.json
#>
[CmdletBinding()]
param(
    [int]$Anios = 30,
    [switch]$SinDescarga,
    [string]$DesdeSnapshot = "",
    [switch]$Forzar,
    [switch]$InstalarDependencias,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

if ($Python -eq "") {
    $venv = Join-Path $raiz ".venv\Scripts\python.exe"
    if (Test-Path $venv) { $Python = $venv } else { $Python = "python" }
}
Write-Host "Python: $Python"

if ($InstalarDependencias) {
    & $Python -m pip install -r requirements.txt
    & $Python -m pip install skl2onnx onnxruntime requests pyyaml
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias" }
}

$argumentos = @("scripts/run_pipeline_proyeccion.py", "--anios", $Anios)
if ($SinDescarga)          { $argumentos += "--sin-descarga" }
if ($DesdeSnapshot -ne "") { $argumentos += @("--desde-snapshot", $DesdeSnapshot) }
if ($Forzar)               { $argumentos += "--forzar" }

& $Python @argumentos
if ($LASTEXITCODE -ne 0) {
    Write-Error "El pipeline falló (código $LASTEXITCODE). Revisa el mensaje anterior."
    exit $LASTEXITCODE
}
Write-Host "`nONNX listo en: $(Join-Path $raiz 'oracle\onnx\m6_proyeccion.onnx')" -ForegroundColor Green
