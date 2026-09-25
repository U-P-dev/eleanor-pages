# Open a page in Windows Chrome (headless) over CDP, run a JavaScript expression, and write its string result to a file.
# Used for the accessibility self-test (tools/preview/a11y.html) without the browser extension:
#
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\preview\evaluate.ps1 `
#     -Url http://localhost:4321/__preview/a11y.html -Expr "runAll().then(r => JSON.stringify(r))" -Out C:\path\result.json
#
# -ReducedMotion / -ForcedColors / -Print emulate the OS setting or print media (the motion and hero checks in a11y.html).
# The expression must return (or resolve to) a string. Headless tabs are not throttled like a background tab in a normal window.
# ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less UTF-8 scripts as the ANSI code page.
param(
  [Parameter(Mandatory = $true)][string]$Url,
  [Parameter(Mandatory = $true)][string]$Expr,
  [Parameter(Mandatory = $true)][string]$Out,
  [int]$Width = 1280,
  [int]$Height = 800,
  [int]$Port = 9334,
  [switch]$ReducedMotion,
  [switch]$ForcedColors,
  [switch]$Print,
  [int]$WaitMs = 1000
)
$ErrorActionPreference = 'Stop'
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
# A fresh profile each run, so no page or test script comes from the cache of an earlier run
$profileDir = Join-Path $env:TEMP ('eleanor-evaluate-' + [guid]::NewGuid().ToString('N'))
$chromeArgs = @('--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  "--user-data-dir=$profileDir", "--remote-debugging-port=$Port", 'about:blank')
$proc = Start-Process -FilePath $chrome -ArgumentList $chromeArgs -PassThru -WindowStyle Hidden
$ws = $null
$script:nextId = 0

function Receive-Message {
  $buffer = New-Object byte[] 65536
  $stream = New-Object System.IO.MemoryStream
  do {
    $segment = New-Object System.ArraySegment[byte] -ArgumentList (, $buffer)
    $result = $ws.ReceiveAsync($segment, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
    $stream.Write($buffer, 0, $result.Count)
  } while (-not $result.EndOfMessage)
  return [Text.Encoding]::UTF8.GetString($stream.ToArray())
}

function Send-Command([string]$Method, [hashtable]$Params) {
  $script:nextId++
  $id = $script:nextId
  $json = (@{ id = $id; method = $Method; params = $Params } | ConvertTo-Json -Depth 10 -Compress)
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)
  $segment = New-Object System.ArraySegment[byte] -ArgumentList (, $bytes)
  [void]$ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while ($true) {
    $text = Receive-Message
    if ($text -match ('^\{"id":' + $id + '[,}]')) { return $text }
  }
}

try {
  $version = $null
  for ($i = 0; $i -lt 60 -and -not $version; $i++) {
    try { $version = Invoke-RestMethod "http://127.0.0.1:$Port/json/version" } catch { Start-Sleep -Milliseconds 250 }
  }
  if (-not $version) { throw "Chrome did not open the debugging port $Port" }
  $targets = Invoke-RestMethod "http://127.0.0.1:$Port/json/list"
  $page = $targets | ForEach-Object { $_ } | Where-Object { $_.type -eq 'page' } | Select-Object -First 1
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  [void]$ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, [Threading.CancellationToken]::None).GetAwaiter().GetResult()

  [void](Send-Command 'Emulation.setDeviceMetricsOverride' @{ width = $Width; height = $Height; deviceScaleFactor = 1; mobile = $false })
  # -ReducedMotion / -ForcedColors / -Print: emulate the OS setting or print media before the page loads
  $features = @()
  if ($ReducedMotion) { $features += @{ name = 'prefers-reduced-motion'; value = 'reduce' } }
  if ($ForcedColors) { $features += @{ name = 'forced-colors'; value = 'active' } }
  if ($features.Count -gt 0 -or $Print) {
    $media = @{ features = $features }
    if ($Print) { $media.media = 'print' }
    [void](Send-Command 'Emulation.setEmulatedMedia' $media)
  }
  [void](Send-Command 'Page.enable' @{})
  [void](Send-Command 'Page.navigate' @{ url = $Url })
  [void](Send-Command 'Runtime.evaluate' @{ expression = 'new Promise((ok) => document.readyState === "complete" ? ok(true) : addEventListener("load", () => ok(true)))'; awaitPromise = $true })
  Start-Sleep -Milliseconds $WaitMs
  $reply = Send-Command 'Runtime.evaluate' @{ expression = $Expr; awaitPromise = $true; returnByValue = $true }
  $parsed = $reply | ConvertFrom-Json
  if ($parsed.result.exceptionDetails) { throw ("evaluation failed: " + ($parsed.result.exceptionDetails | ConvertTo-Json -Depth 5 -Compress)) }
  [IO.File]::WriteAllText($Out, [string]$parsed.result.result.value, (New-Object System.Text.UTF8Encoding $false))
  Write-Output "saved $Out"
}
finally {
  if ($ws) { $ws.Dispose() }
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
  Start-Sleep -Milliseconds 500
  Remove-Item -LiteralPath $profileDir -Recurse -Force -ErrorAction SilentlyContinue
}
