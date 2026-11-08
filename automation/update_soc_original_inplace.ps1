$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing
$target='D:\SOC\Thuyết trình nhóm 1.pptx'
$base='D:\SOC\Thuyết trình nhóm 1_SOC_Corrected.pptx'
$evidence='D:\SOC\docs\evidence\M4\slide-inplace-20261108'
[void](New-Item -ItemType Directory -Path $evidence -Force)
$a='http://schemas.openxmlformats.org/drawingml/2006/main';$p='http://schemas.openxmlformats.org/presentationml/2006/main'
$rns='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
$z=[IO.Compression.ZipFile]::OpenRead($base)
function ReadEntry($name){$r=[IO.StreamReader]::new($z.GetEntry($name).Open());try{$r.ReadToEnd()}finally{$r.Dispose()}}
function NS($doc){$n=[Xml.XmlNamespaceManager]::new($doc.NameTable);$n.AddNamespace('a',$a);$n.AddNamespace('p',$p);return ,$n}
# Tái sử dụng bộ dựng shape/text; không thực thi thao tác xuất bản sao PPTX.
$builder=Get-Content -Raw -Encoding UTF8 'D:\SOC\automation\correct_soc_slides.ps1'
$start=$builder.IndexOf('function Box(');$end=$builder.IndexOf('Box 0.85',$start)
. ([scriptblock]::Create($builder.Substring($start,$end-$start)))
$script:shapeId=2000
$patch=@{};$assets=@{};$script:used=@()
function InitSlide($number){
 $script:t=[xml](ReadEntry "ppt/slides/slide$number.xml");$script:n=NS $t;$script:tree=$t.SelectSingleNode('//p:spTree',$n)
 $script:rels=[xml](ReadEntry "ppt/slides/_rels/slide$number.xml.rels")
}
function RemoveRegion($minX,$minY,$maxY,$maxX=30){
 foreach($shape in @($tree.ChildNodes)){$off=$shape.SelectSingleNode('.//a:xfrm/a:off',$n);if($off -and [double]$off.x -ge $minX*914400 -and [double]$off.x -lt $maxX*914400 -and [double]$off.y -ge $minY*914400 -and [double]$off.y -lt $maxY*914400){[void]$tree.RemoveChild($shape)}}
}
function Photo($path,$x,$y,$w,$h,$assetName,$caption){
 $full=Join-Path 'D:\SOC' $path;$img=[Drawing.Image]::FromFile($full);try{$ratio=[double]$img.Width/$img.Height}finally{$img.Dispose()}
 $fw=$w;$fh=$w/$ratio;if($fh -gt $h){$fh=$h;$fw=$h*$ratio};$x+=($w-$fw)/2;$y+=($h-$fh)/2
 $script:shapeId++;$id=$script:shapeId;$rid="rIdSOC$id"
 $xx=[long]($x*914400);$yy=[long]($y*914400);$ww=[long]($fw*914400);$hh=[long]($fh*914400)
 $caption=[Security.SecurityElement]::Escape($caption)
 $frag=$t.CreateDocumentFragment();$frag.InnerXml="<p:pic xmlns:p=`"$p`" xmlns:a=`"$a`" xmlns:r=`"$rns`"><p:nvPicPr><p:cNvPr id=`"$id`" name=`"Ảnh triển khai $id`" descr=`"$caption`"/><p:cNvPicPr><a:picLocks noChangeAspect=`"1`"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed=`"$rid`"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x=`"$xx`" y=`"$yy`"/><a:ext cx=`"$ww`" cy=`"$hh`"/></a:xfrm><a:prstGeom prst=`"rect`"><a:avLst/></a:prstGeom></p:spPr></p:pic>";[void]$tree.AppendChild($frag)
 $rel=$rels.CreateElement('Relationship',$rels.DocumentElement.NamespaceURI);$rel.SetAttribute('Id',$rid);$rel.SetAttribute('Type',"$rns/image");$rel.SetAttribute('Target',"../media/$assetName");[void]$rels.DocumentElement.AppendChild($rel)
 $assets["ppt/media/$assetName"]=[IO.File]::ReadAllBytes($full)
 $script:used+=[pscustomobject]@{source=$path;embedded="ppt/media/$assetName";caption=[Net.WebUtility]::HtmlDecode($caption);sha256=(Get-FileHash -LiteralPath $full).Hash}
}
function FinishSlide($num){$patch["ppt/slides/slide$num.xml"]=[Text.UTF8Encoding]::new($false).GetBytes($t.OuterXml);$patch["ppt/slides/_rels/slide$num.xml.rels"]=[Text.UTF8Encoding]::new($false).GetBytes($rels.OuterXml)}
InitSlide 14
RemoveRegion 0 3.6 10.65
Box 0.85 3.7 18.3 0.46 'TOPOLOGY EVE-NG THẬT VÀ PHẠM VI ĐÃ NGHIỆM THU' 19 'FAEFF1' 'C8102E' 'FAEFF1' $true
Photo 'docs/evidence/M1/label-correction-20261105/topology-labels-corrected-20261105T0928+0700.png' 0.95 4.3 11.4 5.75 'soc-live-topology.png' 'Topology EVE-NG ngày 05/11/2026; ảnh cấu trúc trước mở rộng WAN, một số nhãn lịch sử chưa cập nhật.'
Box 0.95 10.05 11.4 0.48 'Ảnh 05/11: trước mở rộng WAN; nhãn HA cũ không thay nghiệm thu M3.' 14 'FFF3F4' '657388' 'E7BFC4'
Box 12.65 4.35 6.2 0.85 "CORE L2 → TRUNK 802.1Q → OPNsense`nVLAN 30 / 40 / 50 / 60 / 99" 17 'F5F7FA' '202733' 'CED5DF' $true
Box 12.65 5.35 6.2 1.12 "Primary MASTER · Secondary BACKUP`nCARP VIP .1 · SYNC 10.255.255.0/30`nRouting / Firewall / NAT / DHCP tại OPNsense" 16 'FFF3F4'
Box 12.65 6.65 6.2 1.25 "WAN: pnet0 / 192.168.220.0/24`nFW1 .144 · FW2 .145 · gateway .2`nM3: một HTTPS qua SNAT PASS`nChưa nghiệm thu NAT HA / WAN VIP" 16 'FFFFFF'
Box 12.65 8.08 6.2 1.15 "Core ens10 → Suricata capture0`nSPAN và alert marker live: PASS`nWazuh: replay PASS; truyền live PARTIAL" 16 'FFF8F9'
Box 12.65 9.45 6.2 0.98 "M3: failover/recovery + một TCP PASS`nM4.4 Syslog: BLOCKED (07/11)`nIndexer/Dashboard: chưa nghiệm thu" 15 'F5F7FA'
FinishSlide 14
InitSlide 15
RemoveRegion 12.35 4.45 9.95
Box 12.65 4.5 6.15 0.4 'CARP VIP THỰC TẾ · PRIMARY MASTER' 17 'FFFFFF' '202733' 'FFFFFF' $true
Photo 'docs/evidence/M3/M3.4B-pfsync-state-20261104/primary-recovery-carp-readable-20261104T170827+0700.png' 12.65 5.02 6.15 3.42 'soc-live-vlan-vip.png' 'Primary sau recovery 04/11/2026: năm VLAN, IP .2 và CARP VIP .1.'
Box 12.65 8.48 6.15 0.4 'Ảnh 04/11: IP .2 / VIP .1 trên đủ năm VLAN.' 14 'FFFFFF' '657388' 'FFFFFF'
Box 12.65 8.98 6.15 1.02 "PASS: Employee → DC TCP8000; Guest bị chặn.`nDHCP/DNS Employee và Guest đã đạt.`nPARTIAL: quản trị; DESIGN: DNAT Internet → DMZ." 14 'FFF3F4'
FinishSlide 15
InitSlide 16
RemoveRegion 1.15 4.95 9.6 12.35
# Bỏ đường nối trang trí chạy từ sơ đồ cũ sang cột giải thích.
foreach($shape in @($tree.ChildNodes)){$off=$shape.SelectSingleNode('.//a:xfrm/a:off',$n);$ext=$shape.SelectSingleNode('.//a:xfrm/a:ext',$n);if($off -and $ext -and [double]$off.x -gt 9.7*914400 -and [double]$off.x -lt 12.3*914400 -and [double]$off.y -gt 4.9*914400 -and [double]$off.y -lt 9.6*914400){[void]$tree.RemoveChild($shape)}}
Photo 'docs/evidence/M3/M3.4B-pfsync-state-20261104/secondary-after-native-readable-20261104T165711+0700.png' 1.2 5.05 10.9 4.18 'soc-live-ha-failover.png' 'M3.4B 04/11/2026: Secondary MASTER năm VHID, state TCP ESTABLISHED sau Primary OFF; không reconnect.'
Box 1.2 9.3 10.8 0.55 '04/11: Secondary MASTER 5 VLAN; cùng state TCP còn ESTABLISHED sau failover.' 14 'FFF3F4' '202733' 'E7BFC4'
FinishSlide 16
InitSlide 17
RemoveRegion 1.1 4.9 9.92 12.35
Box 1.25 5.12 10.85 0.4 'Core ens10 → capture0 → Suricata NIDS → EVE JSON' 17 'FFF3F4' 'C8102E' 'E7BFC4' $true
Photo 'docs/evidence/M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.png' 1.25 5.65 10.85 3.75 'soc-live-span.png' 'OVS Mirror thực tế 03/11/2026: span-suricata, VLAN30/40/50/60/99; tx_packets48; có PCAP marker GET.'
Box 1.25 9.52 10.85 0.39 'Ảnh SPAN 03/11: tx_packets48; alert Suricata có minh chứng riêng ngày 02/11.' 13 'FFFFFF' '657388' 'FFFFFF'
FinishSlide 17
$z.Dispose()
# Đọc/khóa độc quyền trước khi ghi; dừng nếu PowerPoint đang giữ khóa.
$stream=[IO.File]::Open($target,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
$archive=[IO.Compression.ZipArchive]::new($stream,[IO.Compression.ZipArchiveMode]::Update,$true)
$before=@{}
function EntryHash($entry){$s=$entry.Open();$sha=[Security.Cryptography.SHA256]::Create();try{[Convert]::ToBase64String($sha.ComputeHash($s))}finally{$s.Dispose();$sha.Dispose()}}
try{
 foreach($entry in $archive.Entries){$before[$entry.FullName]=EntryHash $entry}
 foreach($key in @($patch.Keys)){$old=$archive.GetEntry($key);if($old){$old.Delete()};$entry=$archive.CreateEntry($key);$s=$entry.Open();try{$bytes=$patch[$key];$s.Write($bytes,0,$bytes.Length)}finally{$s.Dispose()}}
 foreach($key in @($assets.Keys)){$old=$archive.GetEntry($key);if($old){$old.Delete()};$entry=$archive.CreateEntry($key);$s=$entry.Open();try{$bytes=$assets[$key];$s.Write($bytes,0,$bytes.Length)}finally{$s.Dispose()}}
}finally{$archive.Dispose();$stream.Dispose()}
$check=[IO.Compression.ZipFile]::OpenRead($target);$changed=@();$added=@()
try{foreach($entry in $check.Entries){if(-not $before.ContainsKey($entry.FullName)){$added+=$entry.FullName}elseif((EntryHash $entry) -ne $before[$entry.FullName]){$changed+=$entry.FullName}}}finally{$check.Dispose()}
$expected=@($patch.Keys);$unexpected=@($changed|Where-Object {$_ -notin $expected})
$validation=[ordered]@{path=$target;recorded_at=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o');changed_parts=$changed;added_parts=$added;other_existing_parts_unchanged=($unexpected.Count -eq 0);photos=$used;sha256=(Get-FileHash -LiteralPath $target).Hash}
$validation|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 (Join-Path $evidence 'validation.json')
if($unexpected.Count){throw 'Unexpected package changes'}
Write-Output "Saved in place: $target; only four target slides and their relationships changed; four real photos embedded."
