param([switch]$CaptureOnly,[switch]$StatusOnly,[string]$Payload,[string]$OutputDir,[int]$ExecuteWait=3,[string]$StatusCommand,[string[]]$Nodes)
$ErrorActionPreference='Stop'
$bundle=@{capture=[IO.File]::ReadAllText("$PSScriptRoot/capture_m2_core_console.py");decoder=[IO.File]::ReadAllText("$PSScriptRoot/decode_m2_console_transport.py");payload=[IO.File]::ReadAllText("$PSScriptRoot/m3_readonly_review.py");nodes=@('OPNsense-Primary','OPNsense-Secondary');capture_only=[bool]$CaptureOnly}
if($Payload){$bundle.payload=[IO.File]::ReadAllText((Resolve-Path $Payload))}
if($Nodes){$bundle.nodes=$Nodes}
$bundle.execute_wait=$ExecuteWait
if($StatusCommand){$bundle.capture_only=$true;$bundle.status_command=$StatusCommand}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($bundle|ConvertTo-Json -Depth 5 -Compress)))
if($StatusOnly){$bundle.capture_only=$true;$bundle.status_command="ifconfig -a | grep 'carp:'; ifconfig pfsync0; configctl kea status";$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($bundle|ConvertTo-Json -Depth 5 -Compress)))}
$code="BUNDLE='$encoded'`n"+[IO.File]::ReadAllText("$PSScriptRoot/m3_remote_review_runner.py")
$response=$code | & ssh.exe -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 -i C:/Users/ACER/.ssh/eve-ng-root-ed25519 root@192.168.220.143 python3 -
if($LASTEXITCODE -ne 0){throw 'Remote collection failed'}
$data=$response|ConvertFrom-Json
$out=Join-Path $PSScriptRoot '../docs/evidence/M3/M3-runtime-review-20261106'
if($OutputDir){$out=$OutputDir}
New-Item -ItemType Directory -Force $out|Out-Null
$stamp=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('yyyyMMddTHHmmsszzz').Replace(':','')
foreach($i in $data.images){$stem=Join-Path $out ($i.label+'-'+$stamp);[IO.File]::WriteAllBytes($stem+'.png',[Convert]::FromBase64String($i.facts.capture.png_base64));$i.facts.capture.PSObject.Properties.Remove('png_base64');$i.facts|Add-Member collected_at ([DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o'));$i.facts|ConvertTo-Json -Depth 20|Set-Content -Encoding UTF8 ($stem+'.json')}
$data.results|ConvertTo-Json -Depth 80|Set-Content -Encoding UTF8 (Join-Path $out ('results-'+$stamp+'.json'))
Write-Output "Saved $($data.images.Count) real screenshots; timestamp $stamp"
