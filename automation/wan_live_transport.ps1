param([ValidateSet('deploy','preflight','inspect','rollback','guard','https')][string]$Mode='deploy',[string]$Work)
$ErrorActionPreference='Stop'
$bundle=@{mode=$Mode;work=$Work;capture=[IO.File]::ReadAllText("$PSScriptRoot/capture_m2_core_console.py");decoder=[IO.File]::ReadAllText("$PSScriptRoot/decode_m2_console_transport.py");self=[IO.File]::ReadAllText("$PSScriptRoot/wan_live_transaction.py")}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($bundle|ConvertTo-Json -Depth 5 -Compress)))
$code="BUNDLE='$encoded'`n"+$bundle.self
$response=$code|& ssh.exe -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 -i C:/Users/ACER/.ssh/eve-ng-root-ed25519 root@192.168.220.143 python3 -
if($LASTEXITCODE -ne 0){throw 'Host transaction failed; inspect watchdog/state before retry'}
$data=$response|ConvertFrom-Json
$out=Join-Path $PSScriptRoot '../docs/evidence/M3/M3-WAN-NAT-live-20261106'
New-Item -ItemType Directory -Force $out|Out-Null
$stamp=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('yyyyMMddTHHmmsszzz').Replace(':','')
$folder=Join-Path $out ('transaction-'+$stamp);New-Item -ItemType Directory $folder|Out-Null
foreach($f in $data.files){if($f.name -ne [IO.Path]::GetFileName($f.name)){throw 'Invalid artifact name'};[IO.File]::WriteAllBytes((Join-Path $folder $f.name),[Convert]::FromBase64String($f.data))}
$data.result|ConvertTo-Json -Depth 30|Set-Content -Encoding UTF8 (Join-Path $folder 'result.json')
Write-Output ($data.result|Select-Object status,work,error|ConvertTo-Json -Compress)
