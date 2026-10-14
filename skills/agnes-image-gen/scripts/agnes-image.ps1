param(
	[string]$Prompt,
	[string]$Size = '2K',
	[string]$Ratio = '1:1',
	[string]$Model = 'agnes-image-2.5-flash',
	[string]$Out,
	[string]$ApiKey
)

# Генерация изображения текстом через Agnes AI (прямой HTTP).
# Коды возврата: 0 — успех, 1 — ошибка API (шлюз), 2 — ошибка конфигурации.
# Base64 из ответа никогда не печатаем — только url и метаданные файла.
#
# Ключ ищем в порядке приоритета: -ApiKey -> AGNES_API_KEY -> api-key.md рядом со скриптом.
# Значение ключа в stdout/логи не попадает: в сообщениях об ошибках его нет.

$ErrorActionPreference = 'Stop'

function Write-Stderr([string]$Message) {
	[Console]::Error.WriteLine($Message)
}

# --- Ключ: -ApiKey > AGNES_API_KEY > api-key.md рядом со скриптом ---
# api-key.md лежит в корне скилла (scripts/../api-key.md); ищем и в папке скрипта, и в родителе.
# $PSCommandPath пуст только при интерактивной вставке кода — тогда файл просто не ищем,
# скрипт честно дойдёт до проверки конфигурации и выйдет с кодом 2.
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
	$ApiKey = $env:AGNES_API_KEY
}
if ([string]::IsNullOrWhiteSpace($ApiKey) -and -not [string]::IsNullOrWhiteSpace($PSCommandPath)) {
	$scriptDir = Split-Path -Parent $PSCommandPath
	$candidates = @(
		(Join-Path -Path $scriptDir -ChildPath 'api-key.md'),
		(Join-Path -Path (Split-Path -Parent $scriptDir) -ChildPath 'api-key.md')
	)
	foreach ($candidate in $candidates) {
		if (-not (Test-Path -LiteralPath $candidate)) {
			continue
		}
		$keyContent = Get-Content -LiteralPath $candidate -Raw
		if ($keyContent -match 'sk-[A-Za-z0-9]{16,}') {
			$ApiKey = $Matches[0]
			break
		}
	}
}

# --- Проверка конфигурации: до любого HTTP-запроса ---
$validRatios = @('1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9')

if ([string]::IsNullOrWhiteSpace($Prompt)) {
	Write-Stderr 'config error: -Prompt is required'
	exit 2
}
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
	Write-Stderr 'config error: API key is missing; set AGNES_API_KEY, pass -ApiKey, or create api-key.md next to the script'
	exit 2
}
if ($validRatios -notcontains $Ratio) {
	Write-Stderr ("config error: invalid -Ratio '{0}'; allowed: {1}" -f $Ratio, ($validRatios -join ' '))
	exit 2
}

# --- Запрос генерации ---
$endpoint = 'https://apihub.agnes-ai.com/v1/images/generations'
$bodyObject = @{
	model       = $Model
	prompt      = $Prompt
	size        = $Size
	ratio       = $Ratio
	extra_body  = @{ response_format = 'url' }
}
$bodyJson = $bodyObject | ConvertTo-Json -Depth 5

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
	$resp = Invoke-RestMethod -Method Post -Uri $endpoint `
		-Headers @{ Authorization = "Bearer $ApiKey" } `
		-ContentType 'application/json' `
		-Body $bodyJson -TimeoutSec 300 -UseBasicParsing
}
catch {
	$stopwatch.Stop()
	# Компактный разбор ошибки шлюзера, оба формата: {code,message} и {error:{code,message}}
	$apiCode = $null
	$apiMessage = $null
	try {
		$response = $_.Exception.Response
		if ($null -ne $response) {
			$stream = $response.GetResponseStream()
			$reader = New-Object System.IO.StreamReader($stream)
			$errorBody = $reader.ReadToEnd()
			$reader.Dispose()
			$parsed = $errorBody | ConvertFrom-Json
			if ($null -ne $parsed.PSObject.Properties['code']) {
				$apiCode = $parsed.code
				$apiMessage = $parsed.message
			}
			elseif ($null -ne $parsed.error -and $null -ne $parsed.error.PSObject.Properties['code']) {
				$apiCode = $parsed.error.code
				$apiMessage = $parsed.error.message
			}
		}
	}
	catch { }
	if ($null -ne $apiCode) {
		Write-Stderr ("API error {0}: {1}" -f $apiCode, $apiMessage)
	}
	else {
		Write-Stderr ("API error: {0}" -f $_.Exception.Message)
	}
	exit 1
}

# --- Разбор ответа: base64 не печатаем никогда ---
$imageUrl = $null
if ($null -ne $resp -and $null -ne $resp.data -and $resp.data.Count -gt 0) {
	$imageUrl = $resp.data[0].url
}
if ([string]::IsNullOrWhiteSpace($imageUrl)) {
	Write-Stderr 'API error: no url in response (base64 payloads are not printed by design)'
	exit 1
}

if ([string]::IsNullOrWhiteSpace($Out)) {
	$stopwatch.Stop()
	Write-Output ("url: {0}" -f $imageUrl)
	Write-Output ("elapsed: {0:n1}s" -f $stopwatch.Elapsed.TotalSeconds)
	exit 0
}

# --- Скачивание в файл ---
$outFull = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Out)
$outDir = Split-Path -Parent $outFull
if (-not [string]::IsNullOrWhiteSpace($outDir) -and -not (Test-Path -LiteralPath $outDir)) {
	New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

try {
	Invoke-WebRequest -Uri $imageUrl -OutFile $outFull -TimeoutSec 300 -UseBasicParsing | Out-Null
}
catch {
	$stopwatch.Stop()
	Write-Stderr ("API error: image download failed: {0}" -f $_.Exception.Message)
	exit 1
}
$stopwatch.Stop()

# --- Метаданные: размеры из заголовка PNG (IHDR, big-endian) ---
$pngBytes = [System.IO.File]::ReadAllBytes($outFull)
$pngSignatureOk = $pngBytes.Length -ge 24 -and
	$pngBytes[0] -eq 0x89 -and $pngBytes[1] -eq 0x50 -and $pngBytes[2] -eq 0x4E -and $pngBytes[3] -eq 0x47 -and
	$pngBytes[12] -eq 0x49 -and $pngBytes[13] -eq 0x48 -and $pngBytes[14] -eq 0x44 -and $pngBytes[15] -eq 0x52

Write-Output ("file: {0}" -f $outFull)
if ($pngSignatureOk) {
	# Приведение к [int] обязательно: -shl на [byte] возвращает [byte] и сдвиг теряет старшие байты
	$width = ([int]$pngBytes[16] -shl 24) -bor ([int]$pngBytes[17] -shl 16) -bor ([int]$pngBytes[18] -shl 8) -bor [int]$pngBytes[19]
	$height = ([int]$pngBytes[20] -shl 24) -bor ([int]$pngBytes[21] -shl 16) -bor ([int]$pngBytes[22] -shl 8) -bor [int]$pngBytes[23]
	Write-Output ("pixels: {0}x{1}" -f $width, $height)
}
else {
	Write-Output 'pixels: unknown (not a PNG header)'
}
Write-Output ("bytes: {0}" -f $pngBytes.Length)
Write-Output ("elapsed: {0:n1}s" -f $stopwatch.Elapsed.TotalSeconds)
exit 0
