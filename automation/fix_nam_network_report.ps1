$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing
$root='D:\SOC';$src=Join-Path $root 'BÁO CÁO SOC.docx'
$out=Join-Path $root 'docs\report-final';$imgs=Join-Path $out 'images'
[void](New-Item -ItemType Directory -Path $imgs -Force)
$target=Join-Path $out 'BAO_CAO_SOC_DA_SUA.docx'
$z=[IO.Compression.ZipFile]::OpenRead($src)
function ReadPart($name){$r=[IO.StreamReader]::new($z.GetEntry($name).Open());try{$r.ReadToEnd()}finally{$r.Dispose()}}
[xml]$doc=ReadPart 'word/document.xml';[xml]$rels=ReadPart 'word/_rels/document.xml.rels';[xml]$styles=ReadPart 'word/styles.xml'
$w='http://schemas.openxmlformats.org/wordprocessingml/2006/main';$a='http://schemas.openxmlformats.org/drawingml/2006/main'
$ns=[Xml.XmlNamespaceManager]::new($doc.NameTable);$ns.AddNamespace('w',$w);$ns.AddNamespace('a',$a);$ns.AddNamespace('wp','http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
$body=$doc.SelectSingleNode('//w:body',$ns);$nodes=@($body.ChildNodes);$modified=[Collections.Generic.HashSet[int]]::new();$changes=[Collections.Generic.List[object]]::new();$patch=@{}
function Esc($s){[Security.SecurityElement]::Escape([string]$s)}
function TextOf($node){($node.SelectNodes('.//w:t',$ns)|ForEach-Object InnerText)-join ''}
function SetText($node,$text){$ts=@($node.SelectNodes('.//w:t',$ns));if($ts.Count){$ts[0].InnerText=$text;for($k=1;$k -lt $ts.Count;$k++){$ts[$k].InnerText=''}}else{$r=$doc.CreateElement('w','r',$w);$t=$doc.CreateElement('w','t',$w);$t.InnerText=$text;[void]$r.AppendChild($t);[void]$node.AppendChild($r)}}
function Edit($i,$text,$reason){SetText $nodes[$i] $text;[void]$modified.Add($i);$changes.Add([pscustomobject]@{original_index=$i;section=$reason;new_text=$text})}
function Para($text,$model=599){$p=$nodes[$model].CloneNode($true);foreach($c in @($p.ChildNodes)){if($c.LocalName -ne 'pPr'){[void]$p.RemoveChild($c)}};$r=$doc.CreateElement('w','r',$w);$rp=$nodes[$model].SelectSingleNode('w:r/w:rPr',$ns);if($rp){[void]$r.AppendChild($rp.CloneNode($true))};$t=$doc.CreateElement('w','t',$w);$space=$doc.CreateAttribute('xml','space','http://www.w3.org/XML/1998/namespace');$space.Value='preserve';[void]$t.Attributes.Append($space);$t.InnerText=$text;[void]$r.AppendChild($t);[void]$p.AppendChild($r);return ,$p}
function After($anchor,$node){[void]$body.InsertAfter($node,$anchor);return ,$node}
function CaptionNode($text,$model=593){$p=Para $text $model;return ,$p}
$sect=$doc.SelectSingleNode('//w:sectPr[last()]',$ns);$pg=$sect.SelectSingleNode('w:pgSz',$ns);$mar=$sect.SelectSingleNode('w:pgMar',$ns)
$usable=[int]$pg.GetAttribute('w',$w)-[int]$mar.GetAttribute('left',$w)-[int]$mar.GetAttribute('right',$w)
if($usable -lt 7000 -or $usable -gt 11000){$usable=9071}
function NewTable($data,$model=594){
 $table=$nodes[$model].CloneNode($true);foreach($c in @($table.ChildNodes)){if($c.LocalName -in 'tr','tblGrid'){[void]$table.RemoveChild($c)}}
 $pr=$table.SelectSingleNode('w:tblPr',$ns);$tw=$pr.SelectSingleNode('w:tblW',$ns);[void]$tw.SetAttribute('w',$w,[string]$usable);[void]$tw.SetAttribute('type',$w,'dxa')
 $count=$data[0].Count;$width=[int]($usable/$count);$grid=$doc.CreateElement('w','tblGrid',$w)
 for($c=0;$c -lt $count;$c++){$g=$doc.CreateElement('w','gridCol',$w);[void]$g.SetAttribute('w',$w,[string]$width);[void]$grid.AppendChild($g)};[void]$table.AppendChild($grid)
 $cellModel=$nodes[594].SelectSingleNode('w:tr/w:tc',$ns)
 for($ri=0;$ri -lt $data.Count;$ri++){
  $tr=$doc.CreateElement('w','tr',$w);$trpr=$doc.CreateElement('w','trPr',$w);[void]$trpr.AppendChild($doc.CreateElement('w','cantSplit',$w));if($ri -eq 0){[void]$trpr.AppendChild($doc.CreateElement('w','tblHeader',$w))};[void]$tr.AppendChild($trpr)
  foreach($value in $data[$ri]){$cell=$cellModel.CloneNode($true);foreach($c in @($cell.ChildNodes)){if($c.LocalName -ne 'tcPr'){[void]$cell.RemoveChild($c)}};$cp=$cell.SelectSingleNode('w:tcPr',$ns);$cw=$cp.SelectSingleNode('w:tcW',$ns);if($cw){[void]$cw.SetAttribute('w',$w,[string]$width)};$p=Para ([string]$value) 599;$pp=$p.SelectSingleNode('w:pPr',$ns);foreach($i in @($pp.SelectNodes('w:ind|w:keepNext',$ns))){[void]$pp.RemoveChild($i)};foreach($rp in $p.SelectNodes('.//w:rPr',$ns)){$s=$rp.SelectSingleNode('w:sz',$ns);if(-not $s){$s=$doc.CreateElement('w','sz',$w);[void]$rp.AppendChild($s)};[void]$s.SetAttribute('val',$w,'23')};[void]$cell.AppendChild($p);[void]$tr.AppendChild($cell)};[void]$table.AppendChild($tr)
 };return ,$table
}
function ReplaceTable($i,$data){$new=NewTable $data $i;[void]$body.ReplaceChild($new,$nodes[$i]);[void]$modified.Add($i)}
# Các đoạn khác của Tùng/Minh/Thắng chỉ được chạm khi có mâu thuẫn Network trực tiếp.
$map=@{
474='Topology gốc ở Hình 2.1 có hai Core, nhiều switch access và OPNsense_3 tại DMZ; đây là tài liệu kiến trúc mục tiêu. Lab đã triển khai M1–M3 sử dụng một Core Open vSwitch trên Ubuntu, hai OPNsense Primary/Secondary và năm VLAN 30/40/50/60/99. Không dùng số thiết bị trên sơ đồ đầu vào để kết luận đã triển khai hai Core hoặc firewall DMZ riêng [63].'
475='Kiến trúc đã thống nhất: Core Open vSwitch chỉ chuyển mạch Layer 2 (lớp liên kết dữ liệu); OPNsense thực hiện inter-VLAN routing (định tuyến giữa VLAN), firewall, NAT và DHCP. Core không có IP ngoài loopback hoặc gateway và forwarding host IPv4/IPv6 bằng 0 tại nghiệm thu. Phương án firewall DMZ riêng không được coi là cấu hình lab đã có [63].'
503='Nghiệm thu mạng dùng cả ca được phép và bị từ chối có đối chứng. M2 có HTTP TCP8000 qua firewall và hai ca deny; M3.3 đã kiểm chuyển năm VIP và recovery; M3.4B giữ cùng một phiên TCP/HTTP sau takeover. Các phép thử không xác nhận RTO chính xác hoặc zero packet loss; bảng tổng hợp nằm ở mục 3.2.7 [63].'
547='Trong lab M1–M3, lưu lượng liên VLAN đã kiểm chứng đi qua OPNsense, còn lưu lượng cùng VLAN có thể chuyển trực tiếp tại Core. Mirror thực tế chọn ingress cả access ens3–ens7 và trunk ens8/ens9, không chỉ một uplink; do đó phạm vi quan sát cần đọc theo nguồn chọn, không khẳng định cảm biến thấy mọi lưu lượng WAN/SYNC [63].'
553='Quy hoạch lab đã nghiệm thu dùng VLAN 30/Data Center:192.168.30.0/24; VLAN 40/Employee:192.168.40.0/24; VLAN 50/Guest:192.168.50.0/24; VLAN 60/DMZ:192.168.60.0/24; VLAN 99/Management:192.168.99.0/24. CARP VIP .1, Primary .2 và Secondary .3 trên mỗi subnet được đối chiếu M3. Nhãn DMZ VLAN10 của topology đầu vào được giữ đúng bối cảnh lịch sử, không dùng cho lab hiện thực [63].'
562='Phần Nam phụ trách hạ tầng Network và OPNsense được truy vết trong Bảng 2.3a. Kết luận dựa trên nghiệm thu M2/M3 và đúng phạm vi các ca thử; các thiết kế AI, SOC và Automation của thành viên khác không được suy là đã tích hợp live chỉ từ kết quả mạng.'
563='Bảng 2.3a. Truy vết nhiệm vụ Network–OPNsense của Nam theo nghiệm thu'
569='Hạ tầng lab sử dụng trunk IEEE 802.1Q (gắn thẻ VLAN) từ một Core Open vSwitch Layer 2 tới từng OPNsense. Cặp firewall làm gateway CARP VIP, định tuyến liên VLAN, thực thi firewall rule, NAT và DHCP. Các kết quả M2–M3 đã được nghiệm thu theo phạm vi mục 3.2.7; kiến trúc nhiều switch và các mở rộng chưa triển khai được ghi riêng, không đồng nhất với lab [63].'
573='Topology nhiều Core/distribution/access là kiến trúc mục tiêu, chưa phải cấu hình đã triển khai. Lab M1–M3 chỉ có một Core Open vSwitch, bridge br-core-l2; Core không làm routing, không đặt SVI/gateway quản trị và dùng console EVE trong phạm vi hiện có. Hai trunk tới hai firewall độc lập không tạo LACP hoặc một Core dự phòng [63].'
574='VLAN — Virtual Local Area Network (mạng LAN ảo) chia miền quảng bá Layer 2. Access port là cổng truy cập một VLAN; trunk port mang nhiều VLAN bằng thẻ IEEE 802.1Q. Trong lab, ens3–ens7 lần lượt access VLAN30/40/50/60/99; ens8/ens9 trunk tới Primary/Secondary; ens10 là output mirror. Mapping này đã được đối chiếu runtime và traffic M2 [63].'
575='Thiết kế nhiều switch có liên kết dự phòng cần kiểm soát vòng lặp; chưa có nghiệm thu hai Core, stack/MLAG hoặc LACP trong lab một Core. Hai trunk firewall được giữ là liên kết độc lập, không gộp port-channel xuyên hai firewall. Các mô tả dự phòng lớp truy cập ở dưới là hướng phát triển, không phải kết quả đã triển khai.'
576='Hình 2.3–2.3e là các sơ đồ nguyên lý được dựng lại từ mapping và nghiệm thu; không phải ảnh chụp lab. Gateway/routing nằm trên OPNsense, Core chỉ chuyển mạch. Ảnh triển khai thật và giới hạn kiểm thử được giữ ở Hình 3.17–3.25 [63].'
580='Hình 2.3. Core L2 và định tuyến liên VLAN tại OPNsense'
582='Hình 2.3a. Topology logic của lab một Core và hai OPNsense'
584='Hình 2.3b. Access, trunk và mapping cổng đã kiểm chứng'
586='Hình 2.3c. Packet walk của phiên TCP nội bộ qua CARP'
588='Hình 2.3d. Nguyên lý quyết định state và firewall rule'
590='Hình 2.3e. Nguồn Mirror OVS và ranh giới truyền log SOC'
593='Bảng 2.4. VLAN, subnet, CARP VIP và IP riêng đã nghiệm thu M3'
600='CARP — Common Address Redundancy Protocol (giao thức dự phòng địa chỉ chung) điều phối VIP — Virtual IP address (địa chỉ IP ảo). VIP .1 là gateway thiết kế, Primary .2 và Secondary .3 là địa chỉ riêng. Không suy mọi endpoint đã đổi default route: bài M3.4B giữ DC default .30.2 và chỉ thêm host route .40.100/32 qua VIP .30.1; DHCP Employee/Guest đã cấp gateway VIP [63].'
613='LACP — Link Aggregation Control Protocol (giao thức điều khiển gộp liên kết) yêu cầu các đối tác hỗ trợ nhóm logic phù hợp. Lab chỉ có một Core với ens8/ens9 nối hai firewall khác nhau nên không cấu hình/không nghiệm thu LACP. Việc khảo sát gộp liên kết hoặc nhiều Core là DESIGN ONLY, không áp nhãn PASS cho T-16/T-17 dự kiến.'
625='SPAN — Switched Port Analyzer, hay port mirroring, sao chép frame phục vụ quan sát. Core lab dùng đối tượng Mirror của OVS: ingress ens3–ens9, VLAN30/40/50/60/99, output ens10; select_all=false và select_dst_port rỗng. M2 có PCAP marker GET và counter48frame/4.278byte; không mô tả là mirror toàn bộ RX+TX hoặc mọi lưu lượng [63].'
627='Sensor có capture0 không IP nhận bản sao từ Core ens10; mgmt0 tách riêng trên segment Management. NIDS — Network Intrusion Detection System (hệ phát hiện xâm nhập mạng) thụ động chỉ quan sát và tạo EVE JSON, không nằm inline để forward/chặn IP. IP quản trị sensor .99.20 và Wazuh .99.30 trong thiết kế chưa có nghiệm thu cấu hình, không coi là địa chỉ đã triển khai [63].'
632='Cặp OPNsense đã triển khai HA — High Availability (tính sẵn sàng cao) theo Active–Passive: Primary MASTER và Secondary BACKUP trên năm VLAN ở trạng thái nghiệm thu. CARP quản lý VIP, pfsync quản lý state và XMLRPC đồng bộ nhóm cấu hình được chọn; ba cơ chế cần bằng chứng riêng [11], [12], [63].'
634='M3.3 đã nghiệm thu failover/recovery ngày04/11: shutdown mềm Primary làm Secondary tự MASTER đủ năm VIP; boot lại Primary đưa hai phía về MASTER/BACKUP, pfsync sẵn sàng. M3.4B nghiệm thu một phiên TCP .40.100:44341→.30.10:8000 tiếp tục qua Secondary và hoàn tất HTTP200/350byte, không reconnect. Không có phép đo zero packet loss/RTO chính xác; WAN VIP/NAT HA, lease DHCP HA và automation HA chưa được nghiệm thu [63].'
642='CARP dùng VIP .1/24 trên VLAN30/40/50/60/99, VHID tương ứng VLAN, advbase1 và advskew Primary0/Secondary100 theo nghiệm thu. Hai firewall vẫn giữ IP riêng .2/.3; SYNC10.255.255.1/30↔.2/30 trên vtnet2 không có CARP VIP mới. WAN .220.144/.145 là lease DHCP riêng, chưa có WAN VIP [63].'
648='pfsync là tên cơ chế đồng bộ state của PF (Packet Filter), khác sao chép cấu hình rule. M3.1 đã kiểm tự áp sau reboot từng firewall qua syshook96-soc-pfsync, syncdev vtnet2/peer đúng, syncok1/demotion0. M3.4B so cùng state ID/creator trước và sau takeover; gói protocol240 hai chiều chỉ là một phần bằng chứng, không thay đối chiếu state [63].'
650='M3.4B duy trì cùng một TCP session và một HTTP request, có một SYN, 11marker ACK sau Primary OFF và response350byte khớp hash. Hai state ID075deb6a00000000/085deb6a00000000, creator d57c33f6 không đổi tại Secondary tiếp quản. Request hoàn tất trước recovery nên không tuyên bố phiên đã đóng còn sống qua recovery; chưa nghiệm thu mọi flow, IPv6, tải dài hạn hoặc zero loss [63].'
654='XMLRPC — XML Remote Procedure Call (gọi thủ tục từ xa bằng XML) chuyển nhóm cấu hình được chọn giữa firewall. Đã đối chiếu đầy đủ XML tám rule và ba pool DHCP, có log syncHTTP200/restore true và8/8UUID rule nạp ở mỗi máy; không suy đồng bộ toàn cấu hình, state runtime, lease DHCP hay blocklist động [63].'
660='Firewall rule quyết định lưu lượng được phép; NAT — Network Address Translation (dịch địa chỉ mạng) thay địa chỉ/cổng theo ánh xạ. DHCP — Dynamic Host Configuration Protocol cấp tham số mạng: Kea cấp Employee/Guest pool .110–.199, gateway/DNS VIP .1; bảy ca M3.5 đã đạt. Đồng bộ cấu hình ba pool không chứng minh lease HA [63].'
661='WAN/NAT tối thiểu đã nghiệm thu06/11: DHCP WAN Primary192.168.220.144/24, Secondary .145/24, gateway .220.2; Hybrid SNAT cho .40.110/32→1.1.1.1/32 TCP443. Một HTTPS HEAD trả HTTP301 với curlrc0/TLSverify0; PCAP cùng SYN chứng minh dịch nguồn. Chưa có WAN VIP, NAT giữ phiên failover hoặc DNAT công bố Web/Mail DMZ [63].'
666='Topology gốc ở Hình 2.1 có OPNsense_3 tại DMZ; đây là mô tả đầu vào. Trong lab đã nghiệm thu, DMZ là VLAN60/192.168.60.0/24, gateway CARP192.168.60.1 trên cặp firewall chính. Chưa có bằng chứng triển khai OPNsense_3 hoặc VLAN10 cho DMZ thực tế; phương án firewall DMZ riêng cần thiết kế transit/đường về và nghiệm thu khác [63].'
683='2.2.15 Vùng Employee VLAN 40 và phương án Wi-Fi'
684='Lab đã kiểm Employee VLAN40 bằng VPCS/client thử và node Employee-Linux trong các cửa sổ riêng; chưa có nghiệm thu AP, SSID, WPA3-Enterprise hoặc RADIUS. Employee nhận DHCP .40.110/24 và gateway/DNS .40.1 trong M3.5; nguồn .40.100 trong M2/M3.4B thuộc các client thử khác, không coi mọi địa chỉ đó cùng một máy [63].'
689='2.2.16 Vùng Guest VLAN 50 và phương án Wi-Fi'
690='Guest VLAN50 trong lab là endpoint VPCS nhận DHCP .50.110/24, gateway/DNS .50.1; ca Guest→DC TCP8000 bị chặn đúng kỳ vọng. Wi-Fi Guest, AP Isolation và Captive Portal vẫn là thiết kế chưa nghiệm thu, không suy từ tên vùng hoặc việc nhận lease rằng đã có AP/portal [63].'
696='VLAN99 là segment Management; endpoint .99.100/24 đã kiểm ICMP tới VIP .99.1. Kết nối Wazuh e0 vào segment99 đã đạt về cấu trúc EVE, không chứng minh guest IP hoặc live log. Syslog là cơ chế chuyển nhật ký; M4.4 OPNsense→Wazuh còn BLOCKED ngày07/11. API — Application Programming Interface (giao diện lập trình ứng dụng) của OPNsense là điểm tích hợp M5; chặn IP tự động live chưa nghiệm thu [63].'
704='M3 đã có nghiệm thu CARP failover/recovery và continuity một TCP session theo mục3.2.7; phần HA end-to-end của toàn SOC, NAT/lease/automation HA và thời gian phục hồi dịch vụ toàn chuỗi chưa nghiệm thu. Không dùng thời gian restart service hoặc độ trễ watcher làm RTO toàn hệ thống; M4 hiện PARTIAL/BLOCKED [63].'
1443='NAM phụ trách Network và OPNsense; TÙNG phụ trách SOC, MINH phụ trách AI, THẮNG phụ trách Automation theo phân công. Nam cung cấp nền phân vùng Core L2, gateway/firewall OPNsense, HA và điểm mirror phục vụ SOC; kết quả các mảng còn lại được đánh giá riêng theo bằng chứng của từng thành viên [1], [7], [63].'
1883='Bảng 3.4 dưới đây chỉ tổng hợp các ca có nghiệm thu M2–M3 và tách riêng nội dung chưa kiểm. Những mã T-01…T-19 cũ là checklist dự kiến, không dùng để tự gán PASS khi chưa có kết quả cùng nguồn/đích/dịch vụ. Các ảnh 3.2c–3.2g thuộc phiên minh họa riêng, không thay PCAP/state của nghiệm thu M3 [63].'
1884='Bảng 3.4. Các ca mạng và HA đã nghiệm thu, kèm giới hạn'
1888='M2-P01 chứng minh HTTP .40.100→.30.10:8000 qua OPNsense bằng cùng SYN, tag40→30, TTL64→63 và counter rule. Hai ca âm M2-N01/N02 có đối chứng dịch vụ/PCAP, không chỉ timeout. M3.5 kiểm Employee/Guest/Management tới VIP, DNS qua VIP và Employee/Guest tới DC TCP8000; kết quả không đại diện mọi cặp VLAN hay IPv6 [63].'
1889='Ảnh 3.2c–3.2g dưới đây giữ nguyên như minh họa của phiên nhóm đã có, không suy từ một ảnh ping hoặc log block thành chặn hoàn toàn mọi gói/port. Kết luận nghiệm thu được lấy từ Bảng 3.4 và hồ sơ mục 3.2.7.'
1891='Hình 3.2d. Minh họa phiên nhóm: Employee kiểm ICMP tới Data Center; không gán thêm mã ca nghiệm thu M2.'
1893='Hình 3.2e. Log OPNsense của phiên minh họa nhóm; cần đọc theo nguồn/đích/giao thức hiển thị.'
1895='Hình 3.2f. Minh họa phiên nhóm: Guest kiểm ICMP tới Data Center; timeout riêng không thay bằng chứng policy có đối chứng.'
1896='Hình 3.2g. Log block của phiên minh họa nhóm; kết luận chỉ áp dụng luồng được hiển thị.'
2050='Đối tượng Mirror span-suricata chọn ingress từ ens3–ens9 và VLAN30/40/50/60/99, xuất ra ens10; select_dst_port rỗng. Suite frame M2 đạt95/95 và có kiểm persistence qua reboot. Cửa sổ HTTP có PCAP chứa marker GET, counter48frame/4.278byte; không cộng counter này thành số phiên hay số alert [63].'
2067=''
2090='Checkpoint07/11 ghi M4.3 PARTIAL/BLOCKED và M4.4 BLOCKED: EVE reboot, Primary .220.144 offline; Wazuh .220.146 là instance VMware ngoài runtime QEMU đang xét và từ chối khóa SSH. TCP514 refused không chứng minh UDP514. Kiểm kê node Wazuh-SOC lịch sử không có gói Indexer/Dashboard/Filebeat; chưa kiểm kê đầy đủ instance VMware, không lấy ảnh Kibana phiên khác thay Wazuh Dashboard node này [63].'
2258='Kiến trúc đích nhiều switch thể hiện phân tách tài sản/chính sách; lab một Core đã có nghiệm thu VLAN/access/trunk/OVS Mirror và routing/firewall chọn lọc M2–M3. Chưa có nghiệm thu hai Core, LACP, DHCP Snooping hoặc DAI. Ảnh Ubuntu/Kibana của phiên khác không thay kết quả mạng [63].'
2265='HA firewall đã có nghiệm thu M3.3/M3.4B về năm VIP, recovery và một TCP session. Khả năng sẵn sàng toàn SOC vẫn cần thiết kế/kiểm thử độc lập ở Core, host, nguồn log và pipeline; không nhân độ sẵn sàng giả định để công bố uptime chưa đo [63].'
2281='Các đóng góp chưa được chứng minh gồm hiệu lực chặn IP tự động qua OPNsense API, HA của automation/NAT/DHCP lease, tăng chất lượng phát hiện nhờ AI và mức giảm công việc analyst. Riêng đồng bộ state và continuity một TCP nội bộ đã đạt M3.4B, không còn xếp vào nhóm chưa kiểm. Kết quả này không chứng minh toàn chuỗi AI→block IP live [63].'
}
# Bảng 2067 được xử lý theo cấu trúc, không xóa nội dung bằng SetText.
$map.Remove(2067)
foreach($i in $map.Keys){Edit ([int]$i) $map[$i] ('Network: '+$i)}
# Tách caption bị dính vào đoạn văn; chuyển drawing nguyên vẹn, không dựng lại ảnh.
foreach($i in 1889,1891,1895){
 $drawings=@($nodes[$i].SelectNodes('.//w:drawing',$ns))
 if($drawings.Count){$picPara=Para '' 599;foreach($r in @($picPara.SelectNodes('w:r',$ns))){[void]$picPara.RemoveChild($r)}
  foreach($drawing in $drawings){$run=$doc.CreateElement('w','r',$w);[void]$run.AppendChild($drawing.CloneNode($true));[void]$picPara.AppendChild($run);[void]$drawing.ParentNode.RemoveChild($drawing)}
  if($i -eq 1889){[void]$body.InsertAfter($picPara,$nodes[$i]);[void](After $picPara (CaptionNode 'Hình 3.2c. Minh họa phiên nhóm: Employee kiểm gateway; không thay nghiệm thu M3.5.' 580))}
  else{[void]$body.InsertBefore($picPara,$nodes[$i])}
 }
}
$trace=@(
@('Nhiệm vụ Nam','Hình/bảng','Kết quả và giới hạn'),
@('Core L2, VLAN/access/trunk','Hình2.3a/b; Bảng2.4/2.4a','PASS M2:95/95frame; một Core OVS, không có LACP.'),
@('Routing và firewall','Hình2.3c/d; Bảng2.4b,3.4,3.10','PASS các ca TCP8000/8001; không mọi cặp VLAN/IPv6.'),
@('Mirror cho Suricata','Hình2.3e; Bảng2.4c','PASS OVS Mirror/PCAP; sensor marker live đã đạt riêng.'),
@('OPNsense HA và dịch vụ','Hình2.4,3.21–3.23; Bảng3.11','PASS5VIP, state/1TCP, XMLRPC8rule/3pool và1HTTPS NAT.'),
@('Bàn giao SOC/Automation','Bảng3.12; mục3.2.7.4–.5','M4 còn PARTIAL/BLOCKED; API blockIP live M5 chưa nghiệm thu.'))
ReplaceTable 564 $trace
$vlan=@(@('VLAN/vùng','Subnet','VIP / Primary / Secondary'),@('30 – Data Center','192.168.30.0/24','192.168.30.1 / .2 / .3'),@('40 – Employee','192.168.40.0/24','192.168.40.1 / .2 / .3'),@('50 – Guest','192.168.50.0/24','192.168.50.1 / .2 / .3'),@('60 – DMZ','192.168.60.0/24','192.168.60.1 / .2 / .3'),@('99 – Management','192.168.99.0/24','192.168.99.1 / .2 / .3'))
ReplaceTable 594 $vlan
$anchor=$body.ChildNodes|Where-Object { $_.LocalName -eq 'tbl' -and (TextOf $_) -like 'VLAN/vùngSubnetVIP*'}|Select-Object -First 1
$extra=@(
@('Bảng 2.4a. Mapping access, trunk và output mirror đã kiểm chứng',@(@('Core EVE/Ubuntu','Vai trò','Đích/VLAN'),@('e0/ens3; e1/ens4','Access','Data Center30; Employee40'),@('e2/ens5; e3/ens6','Access','Guest50; DMZ60'),@('e4/ens7','Access','Management99'),@('e5/ens8; e6/ens9','Hai trunk riêng','Primary/Secondary vtnet0;30,40,50,60,99'),@('e7/ens10','Mirror output','Suricata e0/capture0; không IP'))),
@('Bảng 2.4b. Luồng firewall và mức kiểm chứng thực tế',@(@('Luồng','Kết quả','Giới hạn'),@('Employee→DC TCP8000','PASS M2/M3.5','Theo nguồn/đích đã kiểm, không mọi nghiệp vụ'),@('Guest→DC TCP8000','PASS deny M3.5','Không suy mọi port/IPv6'),@('Employee/Guest→VIP DNS/ICMP','PASS M3.5','Kèm lease .40.110/.50.110'),@('Management .99.100→VIP ICMP','PASS M3.5','Quyền quản trị thiết bị còn PARTIAL'),@('Employee-Linux→1.1.1.1 TCP443','PASS1HEAD/SNAT','Không Internet mọi VLAN hoặc NAT HA'),@('Internet→DMZ; API blockIP live','Chưa nghiệm thu','Thiết kế/mở rộng M5'))),
@('Bảng 2.4c. HA, mirror và đường dữ liệu SOC',@(@('Cơ chế','Đã kiểm','Phần chưa nghiệm thu'),@('CARP/pfsync','5VIP; failover/recovery;1TCP','Zero loss/RTO chính xác; mọi flow'),@('XMLRPC','8rule và3pool đầy đủ','Toàn config, leaseHA, blocklist runtime'),@('OVS Mirror','Ingress ens3–ens9; output ens10','Không toàn bộ WAN/SYNC'),@('Suricata/Manager','Marker live; replay EVE thật','Đường vận chuyển live'),@('Syslog/API','M4.4 BLOCKED; API là điểm nối M5','Log firewall nhận thật; block/unblock tự động'))))
foreach($item in $extra){$anchor=After $anchor (CaptionNode $item[0]);$anchor=After $anchor (NewTable $item[1]);$anchor=After $anchor (Para 'Nguồn: nghiệm thu M2–M3 và checkpoint M4 trong hồ sơ [63].')}
$tests=@(@('Ca/phạm vi','Luồng','Bằng chứng chính','Đánh giá'),@('M2 frame','Access/trunk5VLAN và mirror','Suite frame95/95, có kiểm sau reboot','PASS phạm vi'),@('M2-P01','Employee .40.100→DC .30.10:8000','HTTP200/164byte; tag40→30;TTL64→63','PASS allow'),@('M2-N01/N02','Sai nguồn .40.101; kết nối ngược TCP8001','Có dịch vụ đối chứng;6SYN/ca ingress,0egress; counter deny','PASS deny'),@('M3.3/M3.4B','CARP5VLAN; .40.100:44341→.30.10:8000','Secondary takeover; cùng state/creator; HTTP200/350byte; recovery','PASS;1TCP'),@('M3.5/XMLRPC','DHCP/DNS/rule Employee,Guest,Management','7ca live;8rule/3pool XML khớp,8UUID nạp mỗi máy','PASS phạm vi'),@('WAN/NAT','Employee-Linux .40.110→1.1.1.1:443','1HEAD;HTTP301/TLSverify0/curlrc0; PCAP SNAT','PASS1HTTPS'),@('Chưa nghiệm thu','NAT HA, leaseHA, API blockIP; IPv6/mọi cặp vùng','Không có bài thử tương ứng','DESIGN/PARTIAL'))
ReplaceTable 1886 $tests
# Sửa bảng M3: pool là cấu hình; runtime8/8 áp cho rule, không cho lease.
$table=$nodes[2067];foreach($t in $table.SelectNodes('.//w:t',$ns)){if($t.InnerText -match '8/8 rule và 3 pool'){$t.InnerText=$t.InnerText.Replace('8/8 rule và 3 pool được đối chiếu XML và runtime hai phía','8rule/3pool khớp XML;8/8UUID rule nạp mỗi máy; Kea running')}};[void]$modified.Add(2067)
$contribution='Đóng góp của Nam nối trực tiếp hạ tầng với SOC: Core L2 phân vùng và đưa gói liên VLAN tới OPNsense; OPNsense là gateway/firewall; OVS Mirror cấp bản sao cho Suricata tạo EVE; log/alert là đầu vào cho Tùng phân tích, Minh bổ sung AI và Thắng điều phối phản ứng. Nhánh Automation→OPNsense API là điểm thực thi chính sách của M5, chưa có nghiệm thu chặn IP live. Hai chặng sensor live và Manager replay đã đạt riêng không được trình bày như chuỗi mạng→AI→block đã hoàn chỉnh [63].'
[void](After $nodes[1448] (Para $contribution));$changes.Add([pscustomobject]@{original_index=1448;section='2.8.3 đóng góp Nam';new_text=$contribution})
# Sáu sơ đồ mới được vẽ từ dữ liệu cấu trúc; SVG nguồn chỉnh sửa được và PNG in A4.
$script:bitmap=$null;$script:g=$null;$script:svg=$null
function StartDiagram($title){$script:bitmap=[Drawing.Bitmap]::new(1400,820);$script:g=[Drawing.Graphics]::FromImage($bitmap);$g.Clear([Drawing.Color]::White);$g.SmoothingMode='AntiAlias';$g.TextRenderingHint='AntiAliasGridFit';$script:svg=[Text.StringBuilder]::new('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820"><rect width="1400" height="820" fill="white"/>');Label 20 12 1360 60 $title 36 $true}
function Label($x,$y,$width,$height,$text,$size=30,$bold=$false){$font=[Drawing.Font]::new('Times New Roman',[single]$size,$(if($bold){[Drawing.FontStyle]::Bold}else{[Drawing.FontStyle]::Regular}),[Drawing.GraphicsUnit]::Pixel);$fmt=[Drawing.StringFormat]::new();$fmt.Alignment='Center';$fmt.LineAlignment='Center';try{$g.DrawString($text,$font,[Drawing.Brushes]::Black,[Drawing.RectangleF]::new($x,$y,$width,$height),$fmt)}finally{$font.Dispose();$fmt.Dispose()};$lines=$text -split "`n";for($j=0;$j -lt $lines.Count;$j++){[void]$svg.Append('<text x="'+($x+$width/2)+'" y="'+($y+$height/2-($lines.Count-1)*$size*0.55+$j*$size*1.1+$size*0.3)+'" text-anchor="middle" font-family="Times New Roman" font-size="'+$size+'" font-weight="'+$(if($bold){'bold'}else{'normal'})+'">'+(Esc $lines[$j])+'</text>')}}
function Box($x,$y,$width,$height,$text,$size=30){$pen=[Drawing.Pen]::new([Drawing.Color]::Black,2);$g.FillRectangle([Drawing.Brushes]::White,$x,$y,$width,$height);$g.DrawRectangle($pen,$x,$y,$width,$height);$pen.Dispose();[void]$svg.Append('<rect x="'+$x+'" y="'+$y+'" width="'+$width+'" height="'+$height+'" fill="white" stroke="black" stroke-width="2"/>');Label $x $y $width $height $text $size $true}
function Arrow($x1,$y1,$x2,$y2,$dash=$false){$pen=[Drawing.Pen]::new([Drawing.Color]::Black,3);$pen.EndCap='ArrowAnchor';if($dash){$pen.DashStyle='Dash'};$g.DrawLine($pen,$x1,$y1,$x2,$y2);$pen.Dispose();[void]$svg.Append('<path d="M'+$x1+','+$y1+' L'+$x2+','+$y2+'" fill="none" stroke="black" stroke-width="3"'+$(if($dash){' stroke-dasharray="10 7"'}else{''})+'/>')}
function FinishDiagram($name,$nodeIndex,$rid){Label 20 754 1360 52 'SƠ ĐỒ TÁI DỰNG THEO HỒ SƠ [63] — KHÔNG PHẢI ẢNH CHỤP THỰC NGHIỆM' 23;$g.Dispose();$png=Join-Path $imgs ($name+'.png');$bitmap.Save($png,[Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose();[void]$svg.Append('</svg>');[IO.File]::WriteAllText((Join-Path $imgs ($name+'.svg')),$svg.ToString(),[Text.UTF8Encoding]::new($false));$relationship=$rels.Relationships.Relationship|Where-Object Id -eq $rid;$relationship.Target='media/'+$name+'.png';$patch['word/media/'+$name+'.png']=[IO.File]::ReadAllBytes($png);$picture=$nodes[$nodeIndex];$width=[long]($usable*635);$height=[long]($width*820/1400);foreach($extent in $picture.SelectNodes('.//wp:extent|.//a:xfrm/a:ext',$ns)){[void]$extent.SetAttribute('cx',[string]$width);[void]$extent.SetAttribute('cy',[string]$height)};[void]$modified.Add($nodeIndex)}
StartDiagram 'CORE L2 VÀ ĐIỂM ĐỊNH TUYẾN LIÊN VLAN'
Box 30 170 310 130 "Employee VLAN40`nClient kiểm thử";Box 500 170 330 130 "Core Open vSwitch`nChỉ chuyển mạch L2";Box 980 170 380 130 "OPNsense`nRouting + firewall/state";Box 500 530 330 130 "Data Center VLAN30`n192.168.30.10:8000"
Arrow 340 225 500 225;Arrow 830 200 980 200;Arrow 980 270 830 270;Arrow 665 300 665 530
Label 870 115 200 55 'Trunk tag40' 27;Label 850 310 240 60 'Sau route: tag30' 27
Label 30 420 1280 80 'Gói liên VLAN phải qua firewall; Core không có IP/gateway hoặc SVI dữ liệu.' 32
Label 30 665 1300 60 'M2-P01: cùng SYN tag40→30, TTL64→63; HTTP200 qua OPNsense.' 30
FinishDiagram 'Hinh-2-3-Core-L2' 577 'rId12'
StartDiagram 'TOPOLOGY LOGIC — LAB MỘT CORE / HAI FIREWALL'
Box 530 90 360 80 'WAN pnet0 · .220.0/24' 28;Box 90 220 380 110 "Primary MASTER`nWAN .144 · VLAN IP .2";Box 930 220 380 110 "Secondary BACKUP`nWAN .145 · VLAN IP .3"
Arrow 600 170 280 220;Arrow 820 170 1120 220;Arrow 470 270 930 270 $true;Label 480 190 440 60 "SYNC vtnet2`n10.255.255.1↔.2/30" 25
Box 450 420 490 100 "CORE OVS L2 · 5 VLAN`nTrunk ens8 / ens9 → vtnet0";Arrow 280 330 520 420;Arrow 1120 330 870 420
Box 1050 425 310 90 "Suricata capture0`nMirror ens10" 28;Arrow 940 470 1050 470 $true
Box 1050 580 310 90 "Wazuh Manager`nReplay đã đạt" 28;Arrow 1200 515 1200 580 $true;Label 960 675 420 55 'Log live chưa nghiệm thu' 25
foreach($v in @(@(20,'30 · Data Center'),@(275,'40 · Employee'),@(530,'50 · Guest'),@(785,'60 · DMZ'))){Box $v[0] 590 235 80 $v[1] 27;Arrow 650 520 ($v[0]+118) 590};Label 50 685 900 50 'VLAN99 Management: endpoint, mgmt0 và Wazuh nối segment.' 27
FinishDiagram 'Hinh-2-3a-Topology' 581 'rId13'
StartDiagram 'MAPPING ACCESS / TRUNK / MIRROR ĐÃ KIỂM CHỨNG'
$labels=@('ens3 · VLAN30 · Data Center','ens4 · VLAN40 · Employee','ens5 · VLAN50 · Guest','ens6 · VLAN60 · DMZ','ens7 · VLAN99 · Management')
for($i=0;$i -lt 5;$i++){Box 25 (110+108*$i) 510 82 $labels[$i] 30;Arrow 535 (151+108*$i) 650 (151+108*$i)}
Box 650 110 290 515 "br-core-l2`nOpen vSwitch`n`nKhông IP`nKhông gateway`nForwarding host=0" 31
Box 1060 140 310 110 "Primary vtnet0`nTrunk ens8" 30;Box 1060 340 310 110 "Secondary vtnet0`nTrunk ens9" 30;Arrow 940 195 1060 195;Arrow 940 395 1060 395
Label 965 255 420 60 'Tagged30/40/50/60/99' 27
Box 1040 560 330 100 "Suricata capture0`nOutput ens10" 28;Arrow 940 590 1040 610 $true
Label 20 660 1350 60 'Access: endpoint không tag; trunk: VLAN có tag; hai firewall không gộp LACP.' 30
FinishDiagram 'Hinh-2-3b-Mapping' 583 'rId14'
StartDiagram 'PACKET WALK — PHIÊN TCP NỘI BỘ M3.4B'
$x=@(150,500,850,1220);$heads=@("Client .40.100`nGateway VIP .40.1",'Core L2',"OPNsense`nVIP .40.1 / .30.1","DC .30.10`nTCP8000")
for($i=0;$i -lt 4;$i++){Box ($x[$i]-140) 95 280 95 $heads[$i] 28;$g.DrawLine([Drawing.Pens]::Gray,$x[$i],195,$x[$i],685);[void]$svg.Append('<line x1="'+$x[$i]+'" y1="195" x2="'+$x[$i]+'" y2="685" stroke="gray"/>')}
Arrow 150 240 500 240;Label 160 200 330 35 'SYN tới .30.10:8000' 26;Arrow 500 300 850 300;Label 510 260 330 35 'Trunk tag40' 27
Arrow 850 360 500 360;Label 500 320 350 35 'Rule/state; tag30; TTL63' 25;Arrow 500 420 1220 420;Label 640 380 540 35 'Access30 bỏ tag → DC' 27
Arrow 1220 480 500 480;Label 650 440 540 35 'Phản hồi tới VIP .30.1 qua Core' 26;Arrow 500 540 850 540;Label 510 500 330 35 'Trunk tag30 → firewall' 25
Arrow 850 600 500 600;Label 510 560 330 35 'Khớp state; trunk tag40' 25;Arrow 500 660 150 660;Label 160 620 330 35 'Access40 bỏ tag → client' 25
Label 20 690 1360 55 "DC giữ default .30.2; riêng .40.100/32 đi via VIP .30.1.`nCùng HTTP session qua Secondary; không reconnect, chưa đo zero loss." 25
FinishDiagram 'Hinh-2-3c-Packet-walk' 585 'rId15'
StartDiagram 'FIREWALL CÓ TRẠNG THÁI — SƠ ĐỒ NGUYÊN LÝ'
Box 25 130 290 110 "Gói tới interface`nVLAN nguồn";Box 430 130 300 110 'Khớp state hợp lệ?';Arrow 315 185 430 185;Box 1010 130 350 110 'Xử lý theo state';Arrow 730 185 1010 185;Label 790 125 160 45 'Có' 28
Box 430 350 450 110 "Kết nối mới: kiểm rule`nTheo interface/nhóm/floating/quick" 28;Arrow 580 240 580 350;Label 600 265 150 45 'Không' 28
Box 1010 350 350 110 "Rule cho phép`nTạo/theo dõi state" 29;Arrow 880 400 1010 400
Box 430 560 450 95 "Không có rule cho phép phù hợp`nDefault deny" 29;Arrow 655 460 655 560
Label 15 675 1360 65 "Đã thử: Employee→DC TCP8000 allow; Guest→DC TCP8000 deny.`nSơ đồ giản lược, không thay quy trình đánh giá toàn bộ ruleset OPNsense." 28
FinishDiagram 'Hinh-2-3d-Firewall-flow' 587 'rId16'
StartDiagram 'OVS MIRROR → SURICATA; LOG LIVE CÒN THIẾU'
Box 30 140 410 170 "Core br-core-l2`nIngress ens3–ens9`nVLAN30/40/50/60/99" 32;Box 570 140 350 170 "Suricata capture0`nKhông IP · NIDS`nChỉ nhận bản sao" 31;Arrow 440 225 570 225 $true;Label 420 320 230 55 'Output ens10' 28
Box 1010 140 350 170 "EVE JSON thật`nSID1000001`nVLAN[30] · ICMP" 31;Arrow 920 225 1010 225
Box 570 505 350 110 "mgmt0 riêng`nSegment Management99" 28;Box 1010 505 350 110 "Wazuh Manager`nReplay EVE → alert86601" 28
Arrow 1180 310 1180 505 $true;Label 920 360 460 100 "Nét đứt: tuyến vận chuyển live`nchưa nghiệm thu" 27
Label 20 640 1360 80 "Mirror M2: counter48frame + PCAP marker GET. Suricata: marker live đã đạt riêng.`nKhông chọn mọi RX+TX; không coi Syslog/API blockIP đã hoàn thành." 28
FinishDiagram 'Hinh-2-3e-Mirror-SOC' 589 'rId17'
# Giải thích mục đích/nội dung/kết quả/ý nghĩa cho từng sơ đồ (không ảnh minh chứng giả).
$explain=@{580='Sơ đồ nguyên lý thể hiện một Core L2 và firewall định tuyến. Ca M2 đã đối chiếu tag/TTL/MAC; sơ đồ không là ảnh capture và không chứng minh mọi flow.';582='Sơ đồ logic rút gọn theo lab: hai WAN riêng, hai trunk và SYNC độc lập. VLAN99 và đường log được ghi theo phạm vi đã biết; Wazuh replay không thay live ingestion.';584='Bảng cổng được chuyển thành sơ đồ để đọc mapping khi in A4. Parent firewall là vtnet0, không vtnet1 của bản minh họa cũ; VLAN60 thay VLAN10 trong triển khai DMZ.';586='Luồng mô tả đúng tuple/cổng và route riêng của M3.4B; không sử dụng ví dụ .40.10:443 như một ca đã chạy. Phản hồi dựa state, không cần mở kết nối mới chiều ngược.';588='Sơ đồ giản lược phục vụ giải thích state và policy; không gán mọi rule là first-match ngoài ngữ cảnh. Các ca đã đạt tách khỏi quản trị/DNAT chưa kiểm.';590='Mirror OVS chọn ingress cả access/trunk; capture và quản trị sensor tách riêng. Nét đứt giữa EVE và Manager biểu diễn đường live chưa nghiệm thu, không giả làm đường đã chạy.'}
foreach($i in $explain.Keys){[void](After $nodes[[int]$i] (Para $explain[$i]))}
# Chú thích ảnh nghiệm thu vẫn giữ nguyên file ảnh; chỉ chuẩn hóa dòng giải thích có giới hạn.
foreach($i in 2043,2049,2053,2060,2065,2072,2077,2082,2086){$old=TextOf $nodes[$i];if($i -eq 2082){Edit $i ($old+' Ảnh console thể hiện thao tác xuất trạng thái; giá trị alert được kiểm ở sensor-public-after-marker.json, không tuyên bố toàn bộ EVE hiển thị trên ảnh.') '3.2.7 chú thích Suricata'}elseif($i -eq 2043){Edit $i ($old+' Ảnh05/11 trước mở rộng WAN; nhãn HA/WAN cũ trên canvas không thay nghiệm thu M3.') '3.2.7 chú thích topology'}}
# Caption styles chỉ phục vụ danh mục tự động; giữ trực tiếp font/căn lề của mọi chú thích gốc.
foreach($style in @(@('SOCFigureCaption','SOC Figure Caption'),@('SOCTableCaption','SOC Table Caption'))){$fragment=$styles.CreateDocumentFragment();$fragment.InnerXml='<w:style xmlns:w="'+$w+'" w:type="paragraph" w:styleId="'+$style[0]+'"><w:name w:val="'+$style[1]+'"/><w:basedOn w:val="Normal"/></w:style>';[void]$styles.DocumentElement.AppendChild($fragment)}
foreach($pnode in @($body.SelectNodes('w:p',$ns))){$text=(TextOf $pnode).Trim();if($pnode -in $nodes[11..132]){continue};if($text -match '^(Hình|Bảng)\s+(?:\d+\.\d+[a-z]?|PL\.[A-Z]\.\d+)\s*[\.:]'){$sid=if($Matches[1] -eq 'Hình'){'SOCFigureCaption'}else{'SOCTableCaption'};$pp=$pnode.SelectSingleNode('w:pPr',$ns);if(-not $pp){$pp=$doc.CreateElement('w','pPr',$w);[void]$pnode.PrependChild($pp)};$ps=$pp.SelectSingleNode('w:pStyle',$ns);if(-not $ps){$ps=$doc.CreateElement('w','pStyle',$w);[void]$pp.PrependChild($ps)};[void]$ps.SetAttribute('val',$w,$sid);$orig=[array]::IndexOf($nodes,$pnode);if($orig -ge 0){[void]$modified.Add($orig)}}}
function ListField($instr){$p=Para '' 11;foreach($r in @($p.SelectNodes('w:r',$ns))){[void]$p.RemoveChild($r)};$f=$doc.CreateDocumentFragment();$f.InnerXml='<w:r xmlns:w="'+$w+'"><w:fldChar w:fldCharType="begin"/></w:r><w:r xmlns:w="'+$w+'"><w:instrText xml:space="preserve"> '+(Esc $instr)+' </w:instrText></w:r><w:r xmlns:w="'+$w+'"><w:fldChar w:fldCharType="separate"/></w:r><w:r xmlns:w="'+$w+'"><w:t>Danh mục được cập nhật bằng Microsoft Word.</w:t></w:r><w:r xmlns:w="'+$w+'"><w:fldChar w:fldCharType="end"/></w:r>';[void]$p.AppendChild($f);return ,$p}
[void]$body.InsertBefore((ListField 'TOC \h \z \t "SOC Figure Caption,1"'),$nodes[11]);foreach($i in 11..47){[void]$body.RemoveChild($nodes[$i]);[void]$modified.Add($i)}
[void]$body.InsertBefore((ListField 'TOC \h \z \t "SOC Table Caption,1"'),$nodes[49]);foreach($i in 49..132){[void]$body.RemoveChild($nodes[$i]);[void]$modified.Add($i)}
foreach($field in $doc.SelectNodes('//w:instrText',$ns)){if($field.InnerText -match '^\s*TOC' -and $field.InnerText.Contains('Heading')){$field.InnerText=' TOC \h \u \z \t "Heading 1,1,Heading 2,2,Heading 3,3" ';[void]$modified.Add(8)}}
# Bảo toàn đoạn ngoài phạm vi trước khi Word chỉ cập nhật field/phân trang.
$preservation=@();for($i=0;$i -lt $nodes.Count;$i++){if(-not $modified.Contains($i) -and $nodes[$i].ParentNode -eq $body){$preservation+=[pscustomobject]@{original_index=$i;text=(TextOf $nodes[$i]);xml=$nodes[$i].OuterXml}}}
$preservation|ConvertTo-Json -Depth 3|Set-Content -Encoding UTF8 (Join-Path $root 'temp/network-report-review/preserved.json')
$changes|ConvertTo-Json -Depth 4|Set-Content -Encoding UTF8 (Join-Path $root 'temp/network-report-review/changes.json')
$patch['word/document.xml']=[Text.UTF8Encoding]::new($false).GetBytes($doc.OuterXml);$patch['word/styles.xml']=[Text.UTF8Encoding]::new($false).GetBytes($styles.OuterXml);$patch['word/_rels/document.xml.rels']=[Text.UTF8Encoding]::new($false).GetBytes($rels.OuterXml)
if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target}
$dest=[IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Create)
try{foreach($entry in $z.Entries){$new=$dest.CreateEntry($entry.FullName);$s=$new.Open();try{if($patch.ContainsKey($entry.FullName)){$bytes=$patch[$entry.FullName];$s.Write($bytes,0,$bytes.Length);$patch.Remove($entry.FullName)}else{$stream=$entry.Open();try{$stream.CopyTo($s)}finally{$stream.Dispose()}}}finally{$s.Dispose()}};foreach($key in @($patch.Keys)){$entry=$dest.CreateEntry($key);$s=$entry.Open();try{$bytes=$patch[$key];$s.Write($bytes,0,$bytes.Length)}finally{$s.Dispose()}}}finally{$dest.Dispose();$z.Dispose()}
$stats=[ordered]@{source=$src;source_sha256=(Get-FileHash -LiteralPath $src).Hash;output=$target;edited_paragraphs=$changes.Count;new_diagrams=6;untouched_body_nodes=$preservation.Count;source_backup='temp/network-report-review/BAO_CAO_SOC.original.docx';usable_table_width_twips=$usable;scope='Nam Network/OPNsense và tham chiếu trực tiếp; ảnh3.17–3.25 giữ byte gốc.'}
$stats|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $root 'temp/network-report-review/build-validation.json')
$stats|ConvertTo-Json
