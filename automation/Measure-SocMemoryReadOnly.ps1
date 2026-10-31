param([Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputPath) { throw 'Refuse overwrite existing evidence' }
$socSystem = Get-CimInstance Win32_ComputerSystem
$socDimms = Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum
$socOs = Get-CimInstance Win32_OperatingSystem
$socMemory = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
$socPerf = @(Get-CimInstance Win32_PerfFormattedData_PerfProc_Process | Where-Object { $_.IDProcess -gt 0 -and $_.Name -ne '_Total' })
$socApps = @{}
Get-Process | ForEach-Object {
    $socDescription = ''
    try { $socDescription = $_.Description } catch {}
    $socApps[[int]$_.Id] = [pscustomobject]@{Name=$_.ProcessName;Description=$socDescription}
}
$socProcesses = @($socPerf | ForEach-Object {
    $socApp = $socApps[[int]$_.IDProcess]
    $socName = if ($socApp) { $socApp.Name } else { $_.Name }
    [pscustomobject]@{
        PID=$_.IDProcess;Name=$socName;Application=$socApp.Description
        WorkingSetMiB=[math]::Round($_.WorkingSet/1MB,1)
        PrivateWorkingSetMiB=[math]::Round($_.WorkingSetPrivate/1MB,1)
        PrivateBytesMiB=[math]::Round($_.PrivateBytes/1MB,1)
        Category=$(if ($socName -match '^(vmware|vmnat|vmnet|vmtools|mksSandbox)') {'VMware'} else {'Other Windows'})
    }
})
$socGrouped = @($socProcesses | Group-Object Name | ForEach-Object {
    [pscustomobject]@{Name=$_.Name;Count=$_.Count;PrivateWorkingSetMiB=[math]::Round(($_.Group | Measure-Object PrivateWorkingSetMiB -Sum).Sum,1);WorkingSetSumMiB=[math]::Round(($_.Group | Measure-Object WorkingSetMiB -Sum).Sum,1)}
} | Sort-Object PrivateWorkingSetMiB -Descending)
$socVmIdentities = @(Get-CimInstance Win32_Process -Filter "Name='vmware-vmx.exe'" | ForEach-Object {
    $socMatches = [regex]::Matches($_.CommandLine, '(?i)(?:[^\\/"\s]+)\.vmx')
    [pscustomobject]@{PID=$_.ProcessId;VMConfigBasename=@($socMatches | ForEach-Object {$_.Value})}
})
$socResult = [ordered]@{
    CollectedAt=(Get-Date -Format o)
    InstalledPhysicalMiB=[math]::Round($socDimms.Sum/1MB,1)
    PhysicalModuleCount=$socDimms.Count
    VisiblePhysicalMiB=[math]::Round($socOs.TotalVisibleMemorySize/1024,1)
    AvailableMiB=[math]::Round($socMemory.AvailableBytes/1MB,1)
    FreePhysicalMemoryKiB=$socOs.FreePhysicalMemory
    CommittedMiB=[math]::Round($socMemory.CommittedBytes/1MB,1)
    CommitLimitMiB=[math]::Round($socMemory.CommitLimit/1MB,1)
    CommitPercent=$socMemory.PercentCommittedBytesInUse
    PoolNonpagedMiB=[math]::Round($socMemory.PoolNonpagedBytes/1MB,1)
    PoolPagedMiB=[math]::Round($socMemory.PoolPagedBytes/1MB,1)
    ProcessPrivateBytesSumMiB=[math]::Round(($socProcesses | Measure-Object PrivateBytesMiB -Sum).Sum,1)
    AutomaticManagedPagefile=$socSystem.AutomaticManagedPagefile
    Pagefiles=@(Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,CurrentUsage,PeakUsage,TempPageFile)
    PagefileUnits='MiB for allocated/current/peak'
    Top10ByWorkingSet=@($socProcesses | Sort-Object WorkingSetMiB -Descending | Select-Object -First 10)
    Top15ByPrivateBytes=@($socProcesses | Sort-Object PrivateBytesMiB -Descending | Select-Object -First 15)
    GroupsByPrivateBytes=@($socProcesses | Group-Object Name | ForEach-Object {
        [pscustomobject]@{Name=$_.Name;Count=$_.Count;PrivateBytesMiB=[math]::Round(($_.Group | Measure-Object PrivateBytesMiB -Sum).Sum,1);PrivateWorkingSetMiB=[math]::Round(($_.Group | Measure-Object PrivateWorkingSetMiB -Sum).Sum,1)}
    } | Sort-Object PrivateBytesMiB -Descending)
    GroupsByPrivateWorkingSet=$socGrouped
    VMwareProcesses=@($socProcesses | Where-Object Category -eq 'VMware')
    VMIdentities=$socVmIdentities
    Note='Read-only. Working sets include shared pages; do not sum as physical total. PrivateBytes are committed private virtual memory, not resident RAM. Samples are sequential.'
}
$socJson = $socResult | ConvertTo-Json -Depth 7
[System.IO.File]::WriteAllText($OutputPath,$socJson,[System.Text.UTF8Encoding]::new($false))
[pscustomobject]$socResult | Select-Object CollectedAt,InstalledPhysicalMiB,VisiblePhysicalMiB,AvailableMiB,CommittedMiB,CommitLimitMiB,PoolNonpagedMiB,PoolPagedMiB,ProcessPrivateBytesSumMiB,Pagefiles,Top15ByPrivateBytes,VMwareProcesses | ConvertTo-Json -Depth 5
