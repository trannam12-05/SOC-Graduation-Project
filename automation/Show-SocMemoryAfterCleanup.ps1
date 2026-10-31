$Host.UI.RawUI.WindowTitle = 'SOC M2 - Read-only memory after cleanup'
$socOut = 'D:\SOC\docs\evidence\M2\M2-memory-after-cleanup-20261031-02.json'
& D:\SOC\automation\Measure-SocMemoryReadOnly.ps1 -OutputPath $socOut | Out-Null
$socD = Get-Content -LiteralPath $socOut -Raw -Encoding UTF8 | ConvertFrom-Json
$socE = Get-Content -LiteralPath 'D:\SOC\docs\evidence\M2\M2-eve-after-cleanup-memory-20261031-01.json' -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host ('WINDOWS MEMORY - live read-only sample: '+$socD.CollectedAt)
Write-Host ('Available: {0:N1} MiB / required 2048 MiB; installed: {1:N0} MiB' -f $socD.AvailableMiB,$socD.InstalledPhysicalMiB)
Write-Host ('Commit: {0:N1} / {1:N1} MiB; headroom {2:N1} MiB' -f $socD.CommittedMiB,$socD.CommitLimitMiB,($socD.CommitLimitMiB-$socD.CommittedMiB))
Write-Host ('Pagefile allocated/used: {0}/{1} MiB (system managed)' -f $socD.Pagefiles[0].AllocatedBaseSize,$socD.Pagefiles[0].CurrentUsage)
Write-Host 'Top processes by Private Bytes; WS = resident; PB = private committed:'
$socD.Top15ByPrivateBytes | Select-Object -First 10 @{N='Process';E={$_.Name}},PID,@{N='WS_MiB';E={$_.WorkingSetMiB}},@{N='PB_MiB';E={$_.PrivateBytesMiB}} | Format-Table -AutoSize | Out-Host
Write-Host ('EVE /proc sample: '+$socE.collector_time)
Write-Host (($socE.meminfo -split "`n" | Where-Object {$_ -match '^MemAvailable:'}) -join '')
Write-Host 'EVE QEMU: Ubuntu-Test and Ubuntu-Console-Test running; Core still OFF.'
if ($socD.AvailableMiB -lt 2048) {Write-Host 'GATE FAIL: Windows available < 2048 MiB. NO CORE START.'}
else {Write-Host 'RAM gate reached; further commit/stability/preflight check required before start.'}
Write-Host 'No process stopped. No OVS install, network, image or seed changes.'
Write-Host 'Snapshot saved. You may close this diagnostic window when finished.'
