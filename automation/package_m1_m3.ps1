$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root='D:\SOC';$stage=Join-Path $root ('temp\soc-package-'+[guid]::NewGuid().ToString('N'));New-Item -ItemType Directory -Force $stage|Out-Null
$selected=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach($folder in @('docs/M1','docs/M2','docs/M3','network')){Get-ChildItem (Join-Path $root $folder) -File -Recurse|Where-Object Extension -in '.md','.docx','.csv','.mmd','.unl','.json'|ForEach-Object{[void]$selected.Add($_.FullName)}}
[void]$selected.Add("$root\docs\SOC_TO_DO.md")
$evidence=@('M1/design-review-20261105','M1/wazuh-link-20261105','M1/label-correction-20261105','M2/final-acceptance-20261103','M2/acceptance-group1-20261103','M2/group2c-20261103','M3/todo-completion-20261103','M3/M3.3-failover-20261104/run-105204','M3/M3.4B-pfsync-state-20261104','M3/M3.5-network-services-20261105','M3/M3-runtime-review-20261106','M3/Employee-Linux-20261106','M3/M3-WAN-NAT-live-20261106')
foreach($folder in $evidence){Get-ChildItem (Join-Path "$root/docs/evidence" $folder) -File -ErrorAction SilentlyContinue|Where-Object{ $_.Extension -in '.json','.csv','.md' -and $_.Name -notmatch '\d{8}T|login|private|secret|password|authentication|auth-|backup|execute|header|page' }|ForEach-Object{[void]$selected.Add($_.FullName)}}
$pictures=@('M1/label-correction-20261105/topology-labels-corrected-20261105T0928+0700.png','M1/wazuh-link-20261105/topology-overview-20261105T091848+0700.png','M2/final-acceptance-20261103/core-runtime-root-20261103T171628+0700.png','M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.png','M2/final-acceptance-20261103/dc-http-results-summary-20261103T171916+0700.png','M3/M3-WAN-NAT-live-20261106/OPNsense-Primary-status-20261106T214654+0700.png','M3/M3-WAN-NAT-live-20261106/OPNsense-Secondary-status-20261106T214654+0700.png','M3/M3-WAN-NAT-live-20261106/Employee-Linux-status-20261106T214535+0700.png','M3/Employee-Linux-20261106/Employee-Linux-status-20261106T211238+0700.png')
foreach($p in $pictures){[void]$selected.Add((Join-Path "$root/docs/evidence" $p))}
$last=Get-ChildItem "$root/docs/evidence/M3/M3-WAN-NAT-live-20261106" -Directory|Sort-Object Name|Select-Object -Last 1
foreach($name in @('employee.pcap','wan.pcap','state.json','https-result.json')){[void]$selected.Add((Join-Path $last.FullName $name))}
$secretKey='(?i)(password|passwd|passphrase|secret|token|authorization|cookie|private.?key|authorized.?keys|ssh.?key)'
$secretValue='(?i)(-----BEGIN [^-]*(?:PRIVATE KEY|OPENSSH)[^-]*-----|Authorization\s*:\s*(?:Basic|Bearer)\s+\S+|(?:password|passwd|passphrase|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[=:]\s*[^\s,;<>]{3,})'
function Clean-Object($x){
 if($null -eq $x){return $null}
 if($x -is [string]){if($x -match $secretValue){return '[REDACTED: potential credential]'};return $x}
 if($x -is [pscustomobject]){$o=[ordered]@{};foreach($p in $x.PSObject.Properties){$o[$p.Name]=if($p.Name -match $secretKey){'[REDACTED]'}else{Clean-Object $p.Value}};return [pscustomobject]$o}
 if($x -is [array]){return ,@($x|ForEach-Object{Clean-Object $_})}
 return $x
}
$manifest=@();$excluded=@()
foreach($file in ($selected|Sort-Object)){
 if(!(Test-Path -LiteralPath $file -PathType Leaf)){continue}
 $rel=$file.Substring($root.Length+1);$dest=Join-Path $stage $rel;New-Item -ItemType Directory -Force (Split-Path $dest)|Out-Null
 $ext=[IO.Path]::GetExtension($file).ToLower();$action='unchanged'
 if($ext -eq '.docx'){
  $z=[IO.Compression.ZipFile]::OpenRead($file);try{$text='';foreach($entry in $z.Entries|Where-Object FullName -Like '*.xml'){$sr=[IO.StreamReader]::new($entry.Open());try{$text+=$sr.ReadToEnd()}finally{$sr.Dispose()}}}finally{$z.Dispose()}
  if($text -match $secretKey){$excluded+="$rel : DOCX omitted conservatively; Markdown counterpart retained";continue}
  Copy-Item -LiteralPath $file -Destination $dest
 }elseif($ext -in '.png','.pcap'){Copy-Item -LiteralPath $file -Destination $dest
 }elseif($ext -eq '.json'){
  try{$o=Get-Content -Raw -Encoding UTF8 -LiteralPath $file|ConvertFrom-Json;$clean=Clean-Object $o;$clean|ConvertTo-Json -Depth 100|Set-Content -Encoding UTF8 -LiteralPath $dest;$action='structured credential fields redacted if present'}catch{$excluded+="$rel : invalid/unsupported JSON omitted";continue}
 }elseif($ext -eq '.unl'){
  [xml]$xml=Get-Content -Raw -Encoding UTF8 -LiteralPath $file
  foreach($n in @($xml.SelectNodes('//*'))){if($n.Name -match '^(configs|configurations|config_data)$'){[void]$n.ParentNode.RemoveChild($n);continue};foreach($a in @($n.Attributes)){if($a.Name -match $secretKey){$a.Value='[REDACTED]'}}}
  $xml.Save($dest);$action='topology only; startup configs and credential attributes excluded'
 }else{
  $text=Get-Content -Raw -Encoding UTF8 -LiteralPath $file
  $text=[regex]::Replace($text,'(?s)-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----','[REDACTED PRIVATE KEY]')
  $lines=$text -split "`r?`n";($lines|ForEach-Object{if($_ -match $secretValue){'[REDACTED: potential credential line]'}else{$_}})|Set-Content -Encoding UTF8 -LiteralPath $dest;$action='credential-pattern lines redacted if present'
 }
 $manifest+=[pscustomobject]@{path=$rel.Replace('\','/');processing=$action;sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash}
}
$manifest|Export-Csv -Encoding UTF8 -NoTypeInformation (Join-Path $stage 'PACKAGE_MANIFEST.csv')
$excluded|Set-Content -Encoding UTF8 (Join-Path $stage 'PACKAGE_EXCLUSIONS.txt')
@'
SOC M1–M3 — bản nguồn đóng gói 06/11/2026 (UTC+07:00).
Giữ đường dẫn docs/ và network/. Điểm bắt đầu: docs/SOC_TO_DO.md; M1-final-acceptance-20261105.md; M2-final-summary-20261103.md; M3-WAN-NAT-final-acceptance-20261106.md.
Topology hiện tại: network/topology/SOC-M1-M3-current-20261106.unl (xuất chỉ đọc); sơ đồ M1 và ảnh M1 là minh chứng lịch sử, không phải topology cuối sau Employee Linux/WAN.
VLAN/IP lịch sử: network/ip-plan/vlan-ip-plan.md. Runtime mới nhất: M3 report/acceptance (WAN .144/.145, gateway .220.2; Employee DHCP .40.110).
Chỉ chọn ảnh thật đã xem, giữ nguyên pixel; không gom ảnh login/chưa rà soát. JSON/text được lọc credential; DOCX có dấu hiệu nhạy cảm bị bỏ, dùng Markdown tương ứng. Không chứa raw firewall configs, seed, khóa, token, image VM hoặc toàn bộ raw logs. Các liên kết trong báo cáo có thể trỏ tới hồ sơ lịch sử không chọn vào gói; danh sách thực có trong PACKAGE_MANIFEST.csv.
Hai PCAP M3 là traffic duy nhất đã duyệt tới1.1.1.1 TCP443, snaplen128; không phải dump toàn mạng.
Không thay lab hoặc kết quả nghiệm thu gốc. Dữ liệu gốc ở workspace giữ nguyên; redaction chỉ áp dụng bản trong ZIP. PACKAGE_EXCLUSIONS.txt ghi trường hợp bỏ bảo thủ. Không dùng ZIP này tự động restore firewall/startup config.
'@|Set-Content -Encoding UTF8 (Join-Path $stage 'README_PACKAGE.txt')
$zip="$root\docs\SOC_M1-M3_Source.zip";$tempZip="$root\docs\SOC_M1-M3_Source.building.zip"
if(Test-Path -LiteralPath $tempZip){throw 'Existing building ZIP; inspect before overwrite'}
[IO.Compression.ZipFile]::CreateFromDirectory($stage,$tempZip,[IO.Compression.CompressionLevel]::Optimal,$false)
$check=[IO.Compression.ZipFile]::OpenRead($tempZip);try{if($check.Entries.Count -ne $manifest.Count+3){throw 'Archive entry count mismatch'};foreach($entry in $check.Entries){$s=$entry.Open();try{$s.CopyTo([IO.Stream]::Null)}finally{$s.Dispose()}}}finally{$check.Dispose()}
if(Test-Path -LiteralPath $zip){Move-Item -LiteralPath $zip -Destination ($zip+'.previous-'+[DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))}
Move-Item -LiteralPath $tempZip -Destination $zip
$hash=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash;Set-Content -Encoding ASCII -LiteralPath ($zip+'.sha256') ($hash+'  SOC_M1-M3_Source.zip')
if(!(($stage+'\').StartsWith($root+'\temp\soc-package-',[StringComparison]::OrdinalIgnoreCase))){throw 'Unsafe staging cleanup path'}
Remove-Item -LiteralPath $stage -Recurse -Force
[pscustomobject]@{zip=$zip;files=$manifest.Count;excluded=$excluded.Count;bytes=(Get-Item -LiteralPath $zip).Length;sha256=$hash}|ConvertTo-Json -Compress
