$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root='D:\SOC'
$source=Join-Path $root 'Thuyết trình nhóm 1.pptx'
$output=Join-Path $root 'Thuyết trình nhóm 1_SOC_Corrected.pptx'
$z=[IO.Compression.ZipFile]::OpenRead($source)
$a='http://schemas.openxmlformats.org/drawingml/2006/main'
$p='http://schemas.openxmlformats.org/presentationml/2006/main'
function ReadEntry($name){$r=[IO.StreamReader]::new($z.GetEntry($name).Open());try{$r.ReadToEnd()}finally{$r.Dispose()}}
function NS($doc){$n=[Xml.XmlNamespaceManager]::new($doc.NameTable);$n.AddNamespace('a',$a);$n.AddNamespace('p',$p);return ,$n}
function EditText($doc,$old,$new){
 $n=NS $doc;$found=$false
 foreach($s in $doc.SelectNodes('//p:sp',$n)){
  $ts=@($s.SelectNodes('.//a:t',$n));$text=($ts|ForEach-Object InnerText)-join ''
  if($text -ne $old){continue};$found=$true
  $body=$s.SelectSingleNode('p:txBody',$n);$para=$body.SelectSingleNode('a:p',$n)
  $template=$para.CloneNode($true);$rp=$para.SelectSingleNode('.//a:rPr',$n)
  foreach($item in @($body.SelectNodes('a:p',$n))){[void]$body.RemoveChild($item)}
  foreach($line in ($new -split "`n")){
   $np=$template.CloneNode($true)
   foreach($c in @($np.ChildNodes)){if($c.LocalName -ne 'pPr'){[void]$np.RemoveChild($c)}}
   $run=$doc.CreateElement('a','r',$a);if($rp){[void]$run.AppendChild($rp.CloneNode($true))}
   $t=$doc.CreateElement('a','t',$a);$t.InnerText=$line;[void]$run.AppendChild($t);[void]$np.AppendChild($run);[void]$body.AppendChild($np)
  }
  $bp=$body.SelectSingleNode('a:bodyPr',$n)
  foreach($fit in @($bp.SelectNodes('a:noAutofit|a:spAutoFit|a:normAutofit',$n))){[void]$bp.RemoveChild($fit)}
  [void]$bp.AppendChild($doc.CreateElement('a','normAutofit',$a))
 }
 if(-not $found){throw "Text not found: $old"}
}
$changes=@{}
[xml]$v=ReadEntry 'ppt/slides/slide15.xml'
$map=@{
 '10'='60';'192.168.10.0/24'='192.168.60.0/24';'192.168.10.1'='192.168.60.1'
 'Web / Mail'='HTTP80 lab';'AAA / DB / File'='HTTP8000 lab';'Wi-Fi khách'='VPCS DHCP';'Windows / Linux'='VPCS / Linux'
 'HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỀN THÔNG'='HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG'
 'BẢNG 2.3-2.4 • PHƯƠNG ÁN THIẾT KẾ'='M3: VLAN / VIP ĐÃ KIỂM CHỨNG'
 'MẠNG NỘI BỘ'='DC · TCP8000';'CHÂN'='PASS';'Mặc định từ chối truy cập nội bộ'='Đã thử: Guest → DC TCP8000 bị chặn'
 'Chỉ dịch vụ nghiệp vụ được cho phép'='Đã thử: Employee → DC TCP8000 được phép'
 'DMZ / WEB-MAIL'='DMZ / WEB';'Chỉ dịch vụ công khai cần thiết'='DESIGN: chưa nghiệm thu DNAT công bố DMZ'
 'Giới hạn máy quản trị và quyền thao tác'='PARTIAL: .99.100 → VIP ICMP đã đạt'
 'Guest chỉ mở ngoại lệ hạ tầng cần thiết (DNS/DHCP).'='DHCP/DNS Employee, Guest đã đạt; chưa nghiệm thu DHCP HA.'
 'Lưu ý: Chính sách & HA là phương án thiết kế.'='PASS theo ca thử; chưa đủ ma trận liên vùng.'
}
foreach($k in $map.Keys){EditText $v $k $map[$k]};$changes['ppt/slides/slide15.xml']=$v.OuterXml
[xml]$h=ReadEntry 'ppt/slides/slide16.xml'
$map=@{
 'HÌNH 2.4 · PHƯƠNG ÁN THIẾT KẾ'='M3 · ĐÃ NGHIỆM THU'
 'Trạng thái minh họa'='Trạng thái nghiệm thu'
 'OPNsense FW1'='FW1 · PRIMARY';'OPNsense FW2'='FW2 · SECONDARY'
 'KÊNH ĐỒNG BỘ'='SYNC 10.255.255.0/30'
 'Khi chuyển vai, FW2 tiếp nhận VIP; state và policy cần kiểm chứng riêng.'='FW2 nhận 5 VIP; một phiên TCP nội bộ tiếp tục, không reconnect.'
 'Quản lý VIP và chuyển quyền sở hữugateway khi node hoạt động thay đổi.'="VIP .1 trên VLAN30/40/50/60/99;`nfailover và recovery: PASS."
 'Đồng bộ trạng thái phiên kết nối,nhằm giảm gián đoạn khi failover.'="State ID/creator khớp hai phía;`nmột phiên TCP qua failover: PASS."
 'Đồng bộ các cấu hình được chọngiữa hai firewall.'="Đã kiểm tám rule và ba pool DHCP;`nkhông suy đồng bộ toàn cấu hình."
 'Không mặc định đồng bộ blocklist runtime.'='Chưa kiểm chứng blocklist runtime.'
 'Mục tiêu: giữ gateway và chính sách liên vùng khi một firewall gặp sự cố.'='M3.3: failover/recovery 5 VLAN PASS; M3.4B: một TCP/HTTP session PASS.'
 'HA / failover live: chưa có phép đo.'='Chưa đo zero loss; chưa nghiệm thu NAT HA.'
}
foreach($k in $map.Keys){EditText $h $k $map[$k]};$changes['ppt/slides/slide16.xml']=$h.OuterXml
[xml]$s=ReadEntry 'ppt/slides/slide17.xml'
$map=@{
 'Bản sao traffic  →  Kiểm tra chữ ký  →  Sinh EVE JSON  →  Chuyển tiếp dữ liệu giám sát'='Core mirror → capture0 → Suricata → EVE JSON; Wazuh mới đạt replay cục bộ'
 'THIẾT KẾ GIÁM SÁT SURICATA Ở CHẾ ĐỘ THỤ ĐỘNG'='SURICATA NIDS THỤ ĐỘNG · ĐÃ CHẠY VÀ CÓ ALERT THẬT'
 'MỤC 2.3.6–2.3.8 · PHƯƠNG ÁN THIẾT KẾ'='M2 / M4 · PASS THEO PHẠM VI THỬ'
 'Firewall / ACL'='Routing / Firewall'
 'SPAN / Port Mirror'='SPAN ens10 · PASS'
 'Capture NIC · Passive IDS'='capture0 · không IP · IDS'
 'SPAN / capture NIC · HOME_NET'='ens3–ens9 ingress → ens10 → capture0'
 'Signature, SID / rev · flow & giao thức'='PASS: marker ICMP · SID1000001 / rev1'
 'alert · flow · dns · http · tls'='Đã kiểm event_type=alert; có flow_id'
 'timestamp · flow_id · src/dest IP · rule ID'='timestamp · flow_id · IP · VLAN · SID'
 'Mũi tên nét đứt: lưu lượng được sao chép cho sensor, không đi qua sensor để forward.'='Nguồn thử: host bơm marker vào TAP Core; sensor nhận bản sao, không forward.'
 'Nguyên tắc: Suricata thụ động chỉ quan sát và tạo sự kiện; hành động chặn do firewall / Automation thực thi.'='Wazuh: replay PASS; truyền live PARTIAL. Automation chặn IP: DESIGN.'
 'SPAN / luồng live: cần kiểm chứng riêng'='SPAN / alert: PASS · Log live: PARTIAL'
}
foreach($k in $map.Keys){EditText $s $k $map[$k]};$changes['ppt/slides/slide17.xml']=$s.OuterXml
# Slide hiển thị 12 vốn là một ảnh. Dựng lại sơ đồ bằng shape/text, giữ header/footer PTIT của slide HA.
[xml]$t=ReadEntry 'ppt/slides/slide16.xml';$n=NS $t;$tree=$t.SelectSingleNode('//p:spTree',$n)
foreach($shape in @($tree.ChildNodes)){
 $off=$shape.SelectSingleNode('.//a:xfrm/a:off',$n)
 if($off -and [double]$off.y -ge 3.6*914400 -and [double]$off.y -lt 10.65*914400){[void]$tree.RemoveChild($shape)}
}
EditText $t '14' '12'
EditText $t 'TƯỜNG LỬA VÀ DỰ PHÒNG' 'THIẾT KẾ HẠ TẦNG MẠNG'
EditText $t 'THIẾT KẾ OPNsense FIREWALL VÀ HA' 'THIẾT KẾ TOPOLOGY MẠNG'
EditText $t 'Dự phòng Active–Passive  •  CARP VIP  •  Đồng bộ trạng thái và cấu hình' 'Core L2 • Trunk 802.1Q • OPNsense: routing, firewall, NAT và DHCP'
$script:shapeId=500
function Box($x,$y,$w,$height,$text,$size=18,$fill='FFFFFF',$color='202733',$border='E7BFC4',$bold=$false){
 $script:shapeId++;$id=$script:shapeId;$xx=[long]($x*914400);$yy=[long]($y*914400);$ww=[long]($w*914400);$hh=[long]($height*914400);$sz=[int]($size*100);$b=if($bold){'1'}else{'0'}
 $paras=foreach($line in ($text -split "`n")){$escaped=[Security.SecurityElement]::Escape($line);"<a:p><a:pPr algn=`"ctr`"/><a:r><a:rPr lang=`"vi-VN`" sz=`"$sz`" b=`"$b`"><a:solidFill><a:srgbClr val=`"$color`"/></a:solidFill><a:latin typeface=`"Arial`"/><a:ea typeface=`"Arial`"/><a:cs typeface=`"Arial`"/></a:rPr><a:t>$escaped</a:t></a:r></a:p>"}
 $xml="<p:sp xmlns:p=`"$p`" xmlns:a=`"$a`"><p:nvSpPr><p:cNvPr id=`"$id`" name=`"SOC editable $id`"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x=`"$xx`" y=`"$yy`"/><a:ext cx=`"$ww`" cy=`"$hh`"/></a:xfrm><a:prstGeom prst=`"roundRect`"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val=`"$fill`"/></a:solidFill><a:ln w=`"12700`"><a:solidFill><a:srgbClr val=`"$border`"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr wrap=`"square`" lIns=`"91440`" rIns=`"91440`" tIns=`"45720`" bIns=`"45720`" anchor=`"ctr`"><a:normAutofit/></a:bodyPr><a:lstStyle/>$($paras -join '')</p:txBody></p:sp>"
 $frag=$t.CreateDocumentFragment();$frag.InnerXml=$xml;[void]$tree.AppendChild($frag)
}
function Line($x1,$y1,$x2,$y2,$dash=$false){
 $script:shapeId++;$id=$script:shapeId;$x=[long]([math]::Min($x1,$x2)*914400);$y=[long]([math]::Min($y1,$y2)*914400);$w=[long]([math]::Abs($x2-$x1)*914400);$height=[long]([math]::Abs($y2-$y1)*914400)
 $d=if($dash){'<a:prstDash val="dash"/>'}else{''};$flip=if($y2 -lt $y1){' flipV="1"'}else{''}
 $frag=$t.CreateDocumentFragment();$frag.InnerXml="<p:cxnSp xmlns:p=`"$p`" xmlns:a=`"$a`"><p:nvCxnSpPr><p:cNvPr id=`"$id`" name=`"SOC link $id`"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm$flip><a:off x=`"$x`" y=`"$y`"/><a:ext cx=`"$w`" cy=`"$height`"/></a:xfrm><a:prstGeom prst=`"line`"><a:avLst/></a:prstGeom><a:ln w=`"25400`"><a:solidFill><a:srgbClr val=`"C8102E`"/></a:solidFill>$d</a:ln></p:spPr></p:cxnSp>";[void]$tree.AppendChild($frag)
}
Box 0.85 3.7 18.3 0.48 'TOPOLOGY TRIỂN KHAI · VLAN 30 / 40 / 50 / 60 / 99' 19 'FAEFF1' 'C8102E' 'FAEFF1' $true
# Hai WAN và hai trunk là các liên kết riêng; SYNC không nằm trong Core.
Line 3.6 4.9 4.35 4.9;Line 3.9 4.9 3.9 4.3;Line 3.9 4.3 11.15 4.3;Line 11.15 4.3 11.15 4.5
Line 8.35 5.05 9.15 5.05 $true
Line 6.35 5.65 6.35 7.3;Line 11.15 5.65 11.15 7.3;Line 6.35 7.3 11.15 7.3
Line 8.75 7.65 8.75 8.15;Line 2.65 8.15 17.25 8.15
foreach($xx in 2.65,6.3,9.95,13.6,17.25){Line $xx 8.15 $xx 8.4}
Line 10.6 7.4 13.5 7.4 $true;Line 13.5 7.4 13.5 7.1 $true;Line 13.5 7.1 14.1 7.1 $true;Line 16.35 6.7 16.35 6.15 $true
Box 1.15 4.55 2.45 1.6 "WAN / pnet0`n192.168.220.0/24`nGW .220.2" 16 'F5F7FA'
Box 4.35 4.5 4 1.15 "OPNsense PRIMARY`nWAN .220.144 · MASTER" 18 'FFF3F4' '202733' 'E7BFC4' $true
Box 9.15 4.5 4 1.15 "OPNsense SECONDARY`nWAN .220.145 · BACKUP" 18 'F5F7FA' '202733' 'E7BFC4' $true
Box 8.35 5.73 4.8 0.46 'SYNC vtnet2 · 10.255.255.1 ↔ .2 /30' 14 'FFFFFF' '657388' 'FFFFFF'
Box 4.35 6.25 8.8 0.42 'CARP VIP .1 · pfsync state · XMLRPC: 8 rule / 3 pool' 16 'FFFFFF' '657388' 'FFFFFF'
Box 4.45 6.76 3.2 0.36 'Trunk 802.1Q · FW1' 14 'FFFFFF' '657388' 'FFFFFF'
Box 9.2 6.76 3.2 0.36 'Trunk 802.1Q · FW2' 14 'FFFFFF' '657388' 'FFFFFF'
Box 6.9 7.12 3.7 0.58 'CORE SWITCH L2 · OVS' 18 'F5F7FA' '202733' 'CED5DF' $true
Box 14.1 4.48 4.5 1.66 "SOC / WAZUH MANAGER`nĐã xử lý EVE replay`nLive sensor → Wazuh: chưa đạt`nIndexer/Dashboard: chưa nghiệm thu" 15 'FFF8F9' '202733' 'E7BFC4'
Box 14.1 6.72 4.5 0.96 "SURICATA 7.0.3 · NIDS`nens10 → capture0 · SPAN PASS`nAlert marker live: PASS" 15 'FFF3F4' 'C8102E' 'E7BFC4' $true
Box 14.15 6.14 4.4 0.4 'Log trực tiếp: PARTIAL' 13 'FFFFFF' '657388' 'FFFFFF'
$regions=@(@('DMZ · VLAN60','192.168.60.0/24','Ubuntu / HTTP80'),@('DATA CENTER · 30','192.168.30.0/24','Ubuntu / HTTP8000'),@('EMPLOYEE · 40','192.168.40.0/24','VPCS / Linux lab'),@('GUEST · VLAN50','192.168.50.0/24','VPCS / DHCP'),@('MANAGEMENT · 99','192.168.99.0/24','Quản trị / SOC'))
for($i=0;$i -lt 5;$i++){$xx=0.95+3.65*$i;Box $xx 8.4 3.4 0.4 $regions[$i][0] 16 'C8102E' 'FFFFFF' 'C8102E' $true;Box $xx 8.85 3.4 0.85 "$($regions[$i][2])`n$($regions[$i][1]) · VIP .1" 14 'FFF8F9'}
Box 0.95 10.05 18 0.45 'M3: failover/recovery + một TCP nội bộ PASS; NAT một HTTPS PASS. Chưa nghiệm thu NAT HA / zero loss.' 16 'FFF3F4' 'C8102E' 'E7BFC4'
$changes['ppt/slides/slide14.xml']=$t.OuterXml
$changes['ppt/slides/_rels/slide14.xml.rels']=ReadEntry 'ppt/slides/_rels/slide16.xml.rels'
if(Test-Path -LiteralPath $output){Remove-Item -LiteralPath $output}
$out=[IO.Compression.ZipFile]::Open($output,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($entry in $z.Entries){$e=$out.CreateEntry($entry.FullName,[IO.Compression.CompressionLevel]::Optimal);$dst=$e.Open();try{if($changes.ContainsKey($entry.FullName)){$bytes=[Text.UTF8Encoding]::new($false).GetBytes($changes[$entry.FullName]);$dst.Write($bytes,0,$bytes.Length)}else{$src=$entry.Open();try{$src.CopyTo($dst)}finally{$src.Dispose()}}}finally{$dst.Dispose()}}}finally{$out.Dispose();$z.Dispose()}
Write-Output $output
