# Screenshot a page at an exact viewport size with Windows Chrome (headless) over CDP.
# Chrome's --window-size cannot go below 500px wide, so phone-width shots need
# Emulation.setDeviceMetricsOverride. WSL (NAT) cannot reach Windows localhost, so this runs on the Windows side.
#
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\preview\shoot.ps1 `
#     -Url https://example.com/ -Out C:\path\shot.png -Width 390 -Height 844 -Mobile [-Full] [-Tabs 3]
# -Tabs N presses the Tab key N times as real key input before the shot (to see the focus ring; scripted focus() does not show it).
#
# ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less UTF-8 scripts as the ANSI code page.
param(
  [Parameter(Mandatory = $true)][string]$Url,
  [Parameter(Mandatory = $true)][string]$Out,
  [int]$Width = 1280,
  [int]$Height = 800,
  [double]$Scale = 2,
  [switch]$Mobile,
  [switch]$Full,
  [int]$Port = 9333,
  [int]$Tabs = 0,
  [int]$WaitMs = 1500
)
$ErrorActionPreference = 'Stop'
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$profileDir = Join-Path $env:TEMP 'eleanor-shoot-profile'
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

# Sends a CDP command and returns the raw JSON text of its reply (events received meanwhile are passed to $OnEvent).
function Send-Command([string]$Method, [hashtable]$Params, [scriptblock]$OnEvent) {
  $script:nextId++
  $id = $script:nextId
  $json = (@{ id = $id; method = $Method; params = $Params } | ConvertTo-Json -Depth 10 -Compress)
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)
  $segment = New-Object System.ArraySegment[byte] -ArgumentList (, $bytes)
  # GetResult() of a non-generic Task still yields a VoidTaskResult object in PowerShell 5.1, so discard it.
  [void]$ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
  while ($true) {
    $text = Receive-Message
    if ($text -match ('^\{"id":' + $id + '[,}]')) { return $text }
    if ($OnEvent) { & $OnEvent $text }
  }
}

try {
  $version = $null
  for ($i = 0; $i -lt 60 -and -not $version; $i++) {
    try { $version = Invoke-RestMethod "http://127.0.0.1:$Port/json/version" } catch { Start-Sleep -Milliseconds 250 }
  }
  if (-not $version) { throw "Chrome did not open the debugging port $Port" }
  # Windows PowerShell 5.1 passes a JSON array down the pipeline as one object, so enumerate it from a variable.
  $targets = Invoke-RestMethod "http://127.0.0.1:$Port/json/list"
  $page = $targets | ForEach-Object { $_ } | Where-Object { $_.type -eq 'page' } | Select-Object -First 1
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  [void]$ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, [Threading.CancellationToken]::None).GetAwaiter().GetResult()

  [void](Send-Command 'Emulation.setDeviceMetricsOverride' @{ width = $Width; height = $Height; deviceScaleFactor = $Scale; mobile = [bool]$Mobile })
  if ($Mobile) { [void](Send-Command 'Emulation.setTouchEmulationEnabled' @{ enabled = $true }) }
  [void](Send-Command 'Page.enable' @{})
  $script:loaded = $false
  [void](Send-Command 'Page.navigate' @{ url = $Url } { param($t) if ($t -like '*"Page.loadEventFired"*') { $script:loaded = $true } })
  $deadline = (Get-Date).AddSeconds(30)
  while (-not $script:loaded -and (Get-Date) -lt $deadline) {
    $t = Receive-Message
    if ($t -like '*"Page.loadEventFired"*') { $script:loaded = $true }
  }
  # Let web fonts and late layout settle.
  [void](Send-Command 'Runtime.evaluate' @{ expression = 'document.fonts.ready.then(() => true)'; awaitPromise = $true })
  Start-Sleep -Milliseconds $WaitMs
  for ($i = 0; $i -lt $Tabs; $i++) {
    foreach ($type in @('keyDown', 'keyUp')) {
      [void](Send-Command 'Input.dispatchKeyEvent' @{ type = $type; key = 'Tab'; code = 'Tab'; windowsVirtualKeyCode = 9; nativeVirtualKeyCode = 9 })
    }
    Start-Sleep -Milliseconds 150
  }

  $params = @{ format = 'png' }
  if ($Full) {
    # Scroll through the page so lazy-loaded images load, then wait for them and go back to the top.
    $scroll = 'new Promise(async (ok) => { for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight / 2) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); } await Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))); scrollTo(0, 0); setTimeout(() => ok(true), 300); })'
    [void](Send-Command 'Runtime.evaluate' @{ expression = $scroll; awaitPromise = $true })
    $metrics = Send-Command 'Page.getLayoutMetrics' @{}
    $h = [int][double]([regex]::Match($metrics, '"cssContentSize":\{[^}]*"height":([0-9.]+)').Groups[1].Value)
    $params = @{ format = 'png'; captureBeyondViewport = $true; clip = @{ x = 0; y = 0; width = $Width; height = $h; scale = 1 } }
  }
  $reply = Send-Command 'Page.captureScreenshot' $params
  # The reply can exceed ConvertFrom-Json's 2MB limit, so the base64 is cut out directly.
  $start = $reply.IndexOf('"data":"') + 8
  $end = $reply.IndexOf('"', $start)
  [IO.File]::WriteAllBytes($Out, [Convert]::FromBase64String($reply.Substring($start, $end - $start)))
  Write-Output "saved $Out"
}
finally {
  if ($ws) { $ws.Dispose() }
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}
