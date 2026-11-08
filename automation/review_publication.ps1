$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root='D:\SOC';$dir=Join-Path $root 'temp\publication-review'
[void](New-Item -ItemType Directory -Path $dir -Force)
$tracked=@(git -c core.quotepath=false ls-files)|ForEach-Object {$_.Trim('"')}
$new=@(git -c core.quotepath=false ls-files --others --exclude-standard)|ForEach-Object {$_.Trim('"')}
$paths=@($tracked+$new|Sort-Object -Unique)
$approvedImages=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$index=Join-Path $root 'docs/evidence/M4/report-M1-M4-20261108/evidence-index.csv'
foreach($row in (Import-Csv -Encoding UTF8 -LiteralPath $index)){[void]$approvedImages.Add($row.duong_dan.Replace('\','/'))}
# Ảnh dẫn xuất từ báo cáo/slide đã kiểm trực quan; cùng dữ liệu kỹ thuật đã rà soát.
$pictureAllowed='^docs/evidence/M4/(slide-correction-20261108|slide-inplace-20261108|slide-light-background-20261108)/'
$sensitivePath='(?i)(^|/)(private-backups|secrets|credentials|auth|\.ssh)(/|$)|\.(pem|key|dpapi|enc|pfx|p12|qcow2|iso|vmdk|pcap|pcapng)$|(^|/)\.env($|\.)|(^|/)(config\.xml|ossec\.conf|user-data|authorized_keys|id_rsa|id_ed25519)$'
$unreviewed='(?i)(login|password|secret|authentication|authenticated|auth-observe|root-ready|seed-readonly|console-transfer|console-export|(?:^|/)runtime-primary/|(?:^|/)temp-carp-check/|(?:^|/)recovery-check/)'
$patterns=[ordered]@{
 private_key='-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'
 provider_token='(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|sk-proj-[A-Za-z0-9_-]{25,})'
 ssh_key='ssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/]{35,}'
 auth_header='(?i)Authorization["\x27]?\s*[:=]\s*["\x27]?(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]{12,}'
 literal_credential='(?im)(?:["\x27]?(?:password|passwd|passphrase|accountPassword|api[_-]?key|access[_-]?token|client[_-]?secret)["\x27]?)\s*(?:=>|:|=)\s*["\x27]([^"\x27\r\n]{3,})["\x27]'
 xml_credential='(?is)<(?:password|passwd|secret|token|privatekey)>[^<\s][^<]{2,}</(?:password|passwd|secret|token|privatekey)>'
 password_hash='\$(?:2[aby]|6|y)\$[A-Za-z0-9./$]{15,}'
}
$findings=@();$decisions=@();$total=0L
foreach($path in $paths){
 $full=Join-Path $root $path;if(-not(Test-Path -LiteralPath $full -PathType Leaf)){continue}
 $file=Get-Item -LiteralPath $full;$existing=$path -in $tracked;$reason='';$hits=@()
 if($path -match $sensitivePath){$reason='credential/VM/capture path'}
 elseif($path.StartsWith('temp/') -or $path.StartsWith('automation/debug/') -or $path -match '\.previous-|_SOC_Corrected\.pptx$|Word-pagination-proof\.pdf$|^docs/slide12-source\.png$'){$reason='temporary or superseded duplicate'}
 elseif($file.Length -gt 95MB){$reason='excessive size'}
 elseif($path -like 'docs/evidence/*' -and $path -match $unreviewed){$reason='authentication/secret/console evidence withheld'}
 elseif($file.Extension -eq '.png' -and -not $existing -and -not $approvedImages.Contains($path) -and $path -notmatch $pictureAllowed){$reason='raw image not individually reviewed for publication'}
 elseif($path -match '(?i)(?:execute|header|page-\d|payload|staged|command-\d|serial|raw-console)' -and $path -like 'docs/evidence/*'){$reason='raw console/encoded transport withheld'}
 if(-not $reason -and $file.Extension -notin '.png','.jpg','.jpeg','.pdf','.docx','.pptx'){
  if($file.Length -gt 8MB){$reason='large raw text needs separate review'}else{
   $text=[IO.File]::ReadAllText($full)
   foreach($key in $patterns.Keys){$match=[regex]::Match($text,$patterns[$key]);if($match.Success){
    # Chỉ lưu tên loại phát hiện, không xuất giá trị bí mật.
    $hits+=$key
   }}
   if($text -match '(?i)"(?:b64|payload_b64|base64|config_xml|config_raw)"\s*:\s*"[A-Za-z0-9+/=]{180,}'){$hits+='encoded raw payload'}
  }
 }elseif(-not $reason -and $file.Extension -in '.docx','.pptx'){
  $zip=[IO.Compression.ZipFile]::OpenRead($full)
  try{foreach($entry in $zip.Entries|Where-Object {$_.FullName -match '\.xml$|\.rels$'}){$reader=[IO.StreamReader]::new($entry.Open());try{$text=$reader.ReadToEnd()}finally{$reader.Dispose()};foreach($key in $patterns.Keys){if([regex]::IsMatch($text,$patterns[$key])){$hits+="$key in Office XML"}}}}finally{$zip.Dispose()}
 }
 if($hits.Count){$reason='potential credential; needs review';$findings+=[pscustomobject]@{path=$path;types=($hits|Sort-Object -Unique)-join ';'}}
 $allow=-not [bool]$reason
 if($allow){$total+=$file.Length}
 $decisions+=[pscustomobject]@{path=$path;include=$allow;tracked=$existing;bytes=$file.Length;reason=$reason}
}
$decisions|Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $dir 'decisions.csv')
$findings|Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $dir 'findings.csv')
$allow=@($decisions|Where-Object include|ForEach-Object path)
[IO.File]::WriteAllLines((Join-Path $dir 'allow.txt'),$allow,[Text.UTF8Encoding]::new($false))
$findings|Select-Object -First 65
[pscustomobject]@{reviewed=$decisions.Count;included=$allow.Count;excluded=@($decisions|Where-Object {-not $_.include}).Count;credential_findings=$findings.Count;included_MiB=[math]::Round($total/1MB,2)}|ConvertTo-Json
