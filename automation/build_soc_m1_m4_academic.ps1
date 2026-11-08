$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing
$root='D:\SOC';$target=Join-Path $root 'docs\SOC_M1-M4_BaoCaoCaNhan.docx'
$ev=Join-Path $root 'docs\evidence\M4\report-M1-M4-20261108'
[void](New-Item -ItemType Directory -Path $ev -Force)
$stage=Join-Path $root ('temp\report-M1M4-'+[guid]::NewGuid().ToString('N'))
foreach($d in '_rels','word','word/_rels','word/media'){[void](New-Item -ItemType Directory -Path (Join-Path $stage $d) -Force)}
$body=[Text.StringBuilder]::new();$rels=[Collections.Generic.List[string]]::new()
$script:chapter=0;$script:figures=@{};$script:tables=@{};$script:images=0;$script:tableCount=0;$script:heading='';$script:imageIndex=@();$script:sources=@()
$w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
function Esc($s){[Security.SecurityElement]::Escape([string]$s)}
function Plain($s){$s=[regex]::Replace($s,'\[([^\]]+)\]\(([^)]+)\)','$1 ($2)');$s.Replace('**','').Replace('`','')}
function P($text,$style='Normal'){
 [void]$body.Append('<w:p><w:pPr><w:pStyle w:val="'+$style+'"/></w:pPr><w:r><w:t xml:space="preserve">'+(Esc (Plain $text))+'</w:t></w:r></w:p>')
}
function PageBreak{[void]$body.Append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')}
function AddHeading($text,$level=1){$script:heading=$text;P $text ('Heading'+$level)}
function Field($instruction,$placeholder){[void]$body.Append('<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> '+(Esc $instruction)+' </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>'+(Esc $placeholder)+'</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')}
function Caption($kind,$title){
 $isFigure=$kind -eq 'Hình';$counter=if($isFigure){$script:figures}else{$script:tables}
 if(-not $counter.ContainsKey($script:chapter)){$counter[$script:chapter]=0};$counter[$script:chapter]++
 $style=if($isFigure){'Caption'}else{'TableCaption'};$seq=if($isFigure){'Hinh'}else{'Bang'};$seq+=$script:chapter
 [void]$body.Append('<w:p><w:pPr><w:pStyle w:val="'+$style+'"/><w:keepNext/></w:pPr><w:r><w:t>'+ $kind+' '+$script:chapter+'.'+'</w:t></w:r><w:fldSimple w:instr=" SEQ '+$seq+' \* ARABIC "><w:r><w:t>'+$counter[$script:chapter]+'</w:t></w:r></w:fldSimple><w:r><w:t xml:space="preserve">. '+(Esc $title)+'</w:t></w:r></w:p>')
 return "$kind $script:chapter.$($counter[$script:chapter])"
}
function Table($lines,$title){
 $script:tableCount++;$label=Caption 'Bảng' $title
 $first=$lines[0].Trim().Trim('|').Split('|');$cols=$first.Count;$width=[int](9071/$cols)
 [void]$body.Append('<w:tbl><w:tblPr><w:tblW w:w="9071" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="808080"/><w:left w:val="single" w:sz="4" w:color="808080"/><w:bottom w:val="single" w:sz="4" w:color="808080"/><w:right w:val="single" w:sz="4" w:color="808080"/><w:insideH w:val="single" w:sz="4" w:color="AAAAAA"/><w:insideV w:val="single" w:sz="4" w:color="AAAAAA"/></w:tblBorders><w:tblCellMar><w:top w:w="65" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="65" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>')
 foreach($c in 1..$cols){[void]$body.Append('<w:gridCol w:w="'+$width+'"/>')};[void]$body.Append('</w:tblGrid>');$row=0
 foreach($line in $lines){if($line -match '^\s*\|?[\s:|\-]+\|?\s*$'){continue};$cells=$line.Trim().Trim('|').Split('|');[void]$body.Append('<w:tr><w:trPr><w:cantSplit/>'+$(if($row -eq 0){'<w:tblHeader/>'}else{''})+'</w:trPr>')
  foreach($cell in $cells){[void]$body.Append('<w:tc><w:tcPr><w:tcW w:w="'+$width+'" w:type="dxa"/>'+$(if($row -eq 0){'<w:shd w:fill="F0F0F0"/>'}else{''})+'</w:tcPr><w:p><w:pPr><w:pStyle w:val="TableText"/></w:pPr><w:r>'+$(if($row -eq 0){'<w:rPr><w:b/></w:rPr>'}else{''})+'<w:t xml:space="preserve">'+(Esc (Plain $cell.Trim()))+'</w:t></w:r></w:p></w:tc>')};[void]$body.Append('</w:tr>');$row++
 };[void]$body.Append('</w:tbl>');P ''
}
function LightCopy($path,$destination){
 $src=[Drawing.Bitmap]::new($path);$mono=$true
 try{
  # Không đảo ảnh màu. Kiểm tất cả pixel trước xử lý ảnh terminal đơn sắc.
  for($y=0;$y -lt $src.Height -and $mono;$y++){for($x=0;$x -lt $src.Width;$x++){$c=$src.GetPixel($x,$y);if($c.R -ne $c.G -or $c.G -ne $c.B){$mono=$false;break}}}
  $dark=$src.GetPixel($src.Width-2,$src.Height-2).R -lt 50
  if($mono -and $dark){$dst=[Drawing.Bitmap]::new($src.Width,$src.Height);try{for($y=0;$y -lt $src.Height;$y++){for($x=0;$x -lt $src.Width;$x++){$c=$src.GetPixel($x,$y);$dst.SetPixel($x,$y,[Drawing.Color]::FromArgb($c.A,255-$c.R,255-$c.G,255-$c.B))}};$dst.Save($destination,[Drawing.Imaging.ImageFormat]::Png)}finally{$dst.Dispose()};return 'Đổi nền đơn sắc sang trắng, giữ nguyên tọa độ/nội dung pixel; bản gốc được bảo toàn.'}
  [IO.File]::Copy($path,$destination,$true);return 'Ảnh gốc giữ nguyên màu và nội dung.'
 }finally{$src.Dispose()}
}
function Pic($relative,$caption,$explain,$timestamp){
 $path=Join-Path $root $relative;if(-not(Test-Path -LiteralPath $path)){throw "Missing evidence: $relative"}
 $script:images++;$id='img'+$script:images;$dest=Join-Path $stage "word/media/$id.png"
 $treatment=LightCopy $path $dest;$img=[Drawing.Image]::FromFile($dest)
 try{$cx=5580000L;$cy=[long]($cx*$img.Height/$img.Width);if($cy -gt 3300000){$cy=3300000L;$cx=[long]($cy*$img.Width/$img.Height)}}finally{$img.Dispose()}
 $rels.Add('<Relationship Id="'+$id+'" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/'+$id+'.png"/>')
 [void]$body.Append('<w:p><w:pPr><w:jc w:val="center"/><w:keepNext/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="'+$cx+'" cy="'+$cy+'"/><wp:docPr id="'+$script:images+'" name="'+$id+'" descr="'+(Esc $caption)+'"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="'+$id+'"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="'+$id+'"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="'+$cx+'" cy="'+$cy+'"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
 $label=Caption 'Hình' $caption;P $explain;P ("Nguồn: $relative. Thu: $timestamp. $treatment") 'SourceText'
 $script:imageIndex+=[pscustomobject]@{hinh=$label;ten_tep=[IO.Path]::GetFileName($relative);noi_dung=$caption;thoi_diem_thu=$timestamp;duong_dan=$relative;vi_tri_bao_cao=$script:heading;xu_ly=$treatment;sha256_goc=(Get-FileHash -LiteralPath $path).Hash}
}
function Markdown($text){
 $lines=$text -split "`r?`n";$i=0;$code=$false;$tableTitle=''
 while($i -lt $lines.Count){$line=$lines[$i];$i++
  if($line -match '^```'){$code=-not $code;continue};if($code){P $line 'Code';continue}
  if($line -match '^@TABLE\|'){$tableTitle=$line.Substring(7);continue}
  if($line -match '^@FIG\|'){$parts=$line.Split('|');Pic $parts[1] $parts[2] $parts[3] $parts[4];continue}
  if($line -match '^\|'){$rows=@($line);while($i -lt $lines.Count -and $lines[$i] -match '^\|'){$rows+=$lines[$i];$i++};Table $rows $tableTitle;continue}
  if($line -match '^(#{1,3})\s+(.+)$'){$level=$Matches[1].Length;$title=$Matches[2];if($title -match '^CHƯƠNG (\d+)'){$script:chapter=[int]$Matches[1]};AddHeading $title $level;continue}
  if($line.Trim()){P $line}
 }
}
# Kế thừa nền định dạng TNR13/A4/lề từ báo cáo M1–M3, không ghi đè báo cáo cũ.
$template=[IO.Compression.ZipFile]::OpenRead((Join-Path $root 'docs/M1-M3_BaoCaoTongHop.docx'))
try{$r=[IO.StreamReader]::new($template.GetEntry('word/styles.xml').Open());$templateStyles=$r.ReadToEnd();$r.Dispose()}finally{$template.Dispose()}
[xml]$check=$templateStyles
$styles='<w:styles xmlns:w="'+$w+'"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="26"/><w:lang w:val="vi-VN"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:jc w:val="both"/><w:spacing w:after="120" w:line="330" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
foreach($i in 1..3){$styles+='<w:style w:type="paragraph" w:styleId="Heading'+$i+'"><w:name w:val="heading '+$i+'"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:outlineLvl w:val="'+($i-1)+'"/><w:jc w:val="left"/><w:spacing w:before="200" w:after="120"/>'+$(if($i -eq 1){'<w:pageBreakBefore/>'}else{''})+'</w:pPr><w:rPr><w:b/><w:sz w:val="'+$(if($i -eq 1){'30'}else{'26'})+'"/></w:rPr></w:style>'}
foreach($name in 'Title','Subtitle','FrontHeading','Caption','TableCaption','TableText','Code','SourceText'){
 $size=switch($name){'Title'{34};'Subtitle'{28};'SourceText'{20};'Code'{22};'TableText'{23};default{24}}
 $center=$name -in 'Title','Subtitle','FrontHeading','Caption';$keep=$name -in 'Caption','TableCaption','FrontHeading'
 $styles+='<w:style w:type="paragraph" w:styleId="'+$name+'"><w:name w:val="'+$(if($name -eq 'TableCaption'){'Table Caption'}else{$name})+'"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="100" w:line="270" w:lineRule="auto"/><w:jc w:val="'+$(if($center){'center'}elseif($name -in 'Code','SourceText','TableText'){'left'}else{'both'})+'"/>'+$(if($keep){'<w:keepNext/>'}else{''})+$(if($name -eq 'Code'){'<w:shd w:fill="F5F5F5"/>'}else{''})+'</w:pPr><w:rPr><w:sz w:val="'+$size+'"/>'+$(if($name -in 'Title','FrontHeading','TableCaption'){'<w:b/>'}elseif($name -eq 'Caption'){'<w:i/>'}else{''})+'</w:rPr></w:style>'
};$styles+='</w:styles>'
P 'HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG' 'Subtitle'
P 'KHOA AN TOÀN THÔNG TIN' 'Subtitle';P '';P '';P 'BÁO CÁO CÁ NHÂN ĐỒ ÁN SOC' 'Title'
P 'THIẾT KẾ VÀ TRIỂN KHAI HẠ TẦNG MẠNG, OPNsense HA VÀ GIÁM SÁT AN NINH' 'Title'
P 'TỔNG HỢP M1–M4' 'Subtitle';P '';P 'Core Layer2 • OPNsense • Open vSwitch • Suricata • Wazuh' 'Subtitle';P ''
P 'Sinh viên thực hiện: ................................................................';P 'Mã sinh viên: .............................  Lớp: .............................';P 'Giảng viên hướng dẫn: ........................................................'
P '';P 'Hà Nội, năm2026' 'Subtitle';P 'Chốt hồ sơ triển khai:07/11/2026. Biên soạn:08/11/2026, UTC+07:00.' 'SourceText';P 'Thông tin định danh và phê duyệt để trống do chưa có nguồn xác nhận cho báo cáo cá nhân.' 'SourceText'
PageBreak;P 'TRANG PHÊ DUYỆT' 'FrontHeading';P 'Tên đề tài: Thiết kế và triển khai hạ tầng mạng, OPNsense HA và giám sát an ninh cho mô hình SOC.'
P 'Sinh viên: ........................................  MSSV: ........................................';P 'Phạm vi: M1 thiết kế, M2 Core L2, M3 firewall/HA và M4 giám sát theo hồ sơ thực nghiệm.'
P 'Nhận xét của giảng viên: ................................................................................................................................................................................................................................................................................'
P 'Kết quả đánh giá: ........................................';P 'Ngày ........ tháng ........ năm ........';P 'GIẢNG VIÊN HƯỚNG DẪN' 'Subtitle';P '(Ký và ghi rõ họ tên)' 'SourceText';P 'Trang dành cho xác nhận trực tiếp; báo cáo không tự xác nhận chữ ký hoặc kết quả phê duyệt.' 'SourceText'
PageBreak;P 'TRANG GIAO NHIỆM VỤ' 'FrontHeading'
P 'Sinh viên: ........................................  MSSV: ........................................';P 'Giảng viên hướng dẫn: ................................................................'
P 'Nhiệm vụ chuyên môn: quy hoạch phân vùng VLAN và gateway; dựng Core L2 bằng Open vSwitch; kết nối và kiểm chứng OPNsense HA; triển khai DHCP/DNS/firewall/NAT trong phạm vi được duyệt; xây dựng điểm quan sát Suricata và đánh giá tích hợp Wazuh theo bằng chứng.'
P 'Sản phẩm: topology/mapping, cấu hình có giải thích, kết quả kiểm thử, danh mục minh chứng và báo cáo cá nhân. Những phần chưa nghiệm thu phải có trạng thái và điều kiện hoàn thiện, không ghi thành kết quả đã triển khai.'
P 'Mốc hồ sơ thực nghiệm sử dụng:31/10–07/11/2026. Ngày giao nhiệm vụ chính thức:........................; ngày hoàn thành theo phân công:........................'
P 'Xác nhận phân công của giảng viên/nhóm:................................................................';P 'Phân công chính thức và định danh cá nhân cần được người có thẩm quyền xác nhận; phần phạm vi ở đây tổng hợp từ hồ sơ kỹ thuật.' 'SourceText'
PageBreak;P 'LỜI CẢM ƠN' 'FrontHeading'
P 'Em xin trân trọng cảm ơn các thầy, cô đã trang bị kiến thức về mạng máy tính, hệ điều hành và an toàn thông tin, tạo nền tảng để thực hiện nội dung đồ án. Em cảm ơn giảng viên hướng dẫn đã định hướng phương pháp thực hiện, kiểm chứng và trình bày kết quả.'
P 'Em cảm ơn các thành viên trong nhóm đã phối hợp trao đổi về kiến trúc, dữ liệu giám sát và phạm vi công việc. Quá trình thực hiện giúp em nhận thức rõ yêu cầu phân biệt thiết kế với triển khai, cấu hình với hành vi thực tế và cảnh báo riêng lẻ với chuỗi giám sát hoàn chỉnh.'
P 'Báo cáo được xây dựng trên các tài liệu và minh chứng đã lưu. Những giới hạn của hệ thống được trình bày cùng kết quả để người đọc có thể đối chiếu, đánh giá và tiếp tục phát triển một cách có căn cứ.'
PageBreak;P 'MỤC LỤC' 'FrontHeading';Field 'TOC \o "1-3" \h \z \u' 'Mục lục tự động; được cập nhật khi mở bằng Microsoft Word.'
PageBreak;P 'DANH MỤC HÌNH ẢNH' 'FrontHeading';Field 'TOC \h \z \t "Caption,1"' 'Danh mục hình tự động.'
PageBreak;P 'DANH MỤC BẢNG' 'FrontHeading';Field 'TOC \h \z \t "Table Caption,1"' 'Danh mục bảng tự động.'
PageBreak;P 'DANH MỤC TỪ VIẾT TẮT' 'FrontHeading'
P 'Tên sản phẩm, tên giao thức hoặc datasource không có dạng khai triển chính thức được giữ đúng tên. Giải thích đầy đủ về nguyên lý, vai trò và ví dụ nằm ở Chương1.'
Table @('| Ký hiệu | Tên tiếng Anh / tên chính thức | Nghĩa sử dụng trong báo cáo |','|---|---|---|','| SOC / SIEM | Security Operations Center / Security Information and Event Management | Trung tâm điều hành / quản lý thông tin và sự kiện an ninh |','| IDS / IPS | Intrusion Detection / Prevention System | Phát hiện / ngăn chặn xâm nhập |','| NIDS / HIDS | Network / Host-based Intrusion Detection System | Phát hiện dựa trên mạng / máy chủ |','| VLAN / VIP / VHID | Virtual LAN / Virtual IP address / Virtual Host Identifier | Mạng LAN ảo / IP ảo / định danh nhóm CARP |','| CARP / HA | Common Address Redundancy Protocol / High Availability | Dự phòng địa chỉ / sẵn sàng cao |','| NAT / SNAT / DNAT | Network / Source / Destination Network Address Translation | Dịch địa chỉ / nguồn / đích |','| DHCP / DNS | Dynamic Host Configuration Protocol / Domain Name System | Cấp tham số mạng / hệ thống tên miền |','| OVS / SPAN | Open vSwitch / Switched Port Analyzer | Chuyển mạch ảo / sao chép quan sát |','| XML-RPC / EVE | XML Remote Procedure Call / Extensible Event Format | Đồng bộ cấu hình / định dạng sự kiện |','| SSH / LACP | Secure Shell / Link Aggregation Control Protocol | Quản trị bảo mật / gộp liên kết |','| TCP / HTTP / TLS | Transmission Control Protocol / Hypertext Transfer Protocol / Transport Layer Security | Truyền vận / Web / bảo vệ truyền tin |','| QCOW2 / JSON | QEMU Copy On Write v2 / JavaScript Object Notation | Đĩa overlay / dữ liệu có cấu trúc |','| PF / MAC / TTL | Packet Filter / Media Access Control / Time To Live | Firewall state / địa chỉ liên kết / giới hạn hop |') 'Danh mục viết tắt sử dụng'
PageBreak;P 'MỞ ĐẦU' 'FrontHeading'
P 'Lý do chọn đề tài. Dữ liệu bảo mật xuất hiện ở nhiều vùng mạng và hệ thống. Muốn phân tích có cơ sở, trước hết cần nền mạng phân vùng đúng, gateway có kiểm soát và điểm thu phản ánh lưu lượng thực tế. Đề tài chọn cách triển khai từng tầng để đánh giá mạng, dự phòng và giám sát bằng bằng chứng độc lập.'
P 'Mục tiêu. Xây dựng mô hình Core L2–OPNsense, kiểm chứng VLAN/trunk/mirror, triển khai HA và dịch vụ mạng trong phạm vi lab; tiếp đó đánh giá Suricata và Wazuh theo mức dữ liệu thực sự thu được. Mục tiêu báo cáo là giải thích đủ nguyên lý và quy trình để người đọc phân biệt kết quả đã đạt với phần mở rộng.'
P 'Phạm vi và phương pháp. Báo cáo sử dụng hồ sơ M1–M4 tại D:\SOC, kế thừa mẫu Word M1–M3 ngày06/11 và dùng checkpoint07/11 làm cơ sở tiến độ cuối. Các phép thử PASS được tái sử dụng, không chạy lại. Nguồn trong docs/evidence/M5 chỉ được dùng cho chặng Manager/replay liên quan đầu ra M4 và ghi rõ xuất xứ.'
P 'Quy ước. PASS là đạt đúng ca và thời điểm có bằng chứng; PARTIAL là có phần đạt nhưng thiếu phạm vi/tích hợp; BLOCKED là chưa thể nghiệm thu vì điều kiện cụ thể; DESIGN ONLY là phương án hoặc chức năng chưa có bằng chứng triển khai. Lịch sử FAIL/BLOCKED không bị sửa thành PASS; nghiệm thu mới được ghi riêng. Không có kết quả đo mới ngày biên soạn.'
P 'Nhiệm vụ cá nhân và bố cục. Trọng tâm gồm Core L2, OPNsense HA và triển khai quan sát SOC. Chương1 trình bày cơ sở lý thuyết; Chương2–5 tương ứng M1–M4; Chương6 đánh giá và kết luận; phụ lục cung cấp lệnh, bảng ca thử và định vị minh chứng. Thông tin họ tên, MSSV, lớp và xác nhận giao nhiệm vụ được để trống vì tài liệu nhóm chưa xác định người yêu cầu là thành viên nào.'
Markdown (Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs/SOC_M1-M4_report-content.md'))
$script:chapter=7;AddHeading 'PHỤ LỤC A. CÁC LỆNH VÀ CẤU HÌNH QUAN TRỌNG'
P 'Các khối dưới đây phục vụ đọc hiểu hồ sơ; không phải yêu cầu thực thi lại trên lab. Lệnh đọc trạng thái được phân biệt với lệnh cấu hình. Dữ liệu bí mật và bản config.xml/ossec.conf đầy đủ không đưa vào phụ lục.'
AddHeading 'A.1. Đọc trạng thái Core và đối chiếu mapping' 2
foreach($line in 'ovs-vsctl show','ovs-vsctl list Port','ovs-vsctl list Mirror','sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding','ip -br address','ip route'){P $line 'Code'}
P 'ovs-vsctl đọc OVSDB; Port xác nhận tag/trunks, Mirror xác nhận nguồn/output; sysctl kiểm vai trò routing host; ip đọc địa chỉ và route. Kết luận Core L2 cần cả cấu hình và traffic proof, không chỉ một lệnh.'
AddHeading 'A.2. Đọc CARP, pfsync và state PF' 2
foreach($line in 'ifconfig -a','ifconfig pfsync0','pfctl -ss -vv','pfctl -sr','pfctl -sn'){P $line 'Code'}
P 'ifconfig xác nhận IP/VIP/VHID và syncdev/peer; pfctl -ss -vv cho tuple/state ID/creator/counter; -sr đọc rule, -sn đọc NAT. Hai entry trong M3.4B thuộc cùng TCP flow ở hai phía interface, không phải hai session.'
AddHeading 'A.3. Hook persistent và timeout Manager đã triển khai' 2
P '/usr/local/sbin/pluginctl -c pfsync' 'Code';P 'Lệnh native nằm trong hook96-soc-pfsync; không chạy lại trong quá trình biên soạn. Ý nghĩa là nạp runtime từ cấu hình hiện hữu, không hardcode peer khác. Sau reboot đã kiểm log gắn boot và syncok cuối.'
foreach($line in '[Service]','TimeoutStartSec=300'){P $line 'Code'}
P 'Hai dòng là nội dung drop-in Manager đã ghi trong hồ sơ. Không coi chúng là toàn bộ unit; chưa có nghiệm thu reboot sau sửa timeout.'
AddHeading 'A.4. Quy tắc Suricata lab nguyên văn từ cấu hình công khai' 2
$sensor=Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs/evidence/M4/topology-first-20261102/sensor-configuration-public.json')|ConvertFrom-Json
foreach($line in ($sensor.rules -split "`r?`n")){if($line -match '^alert '){P $line 'Code'}}
P 'Rule so nội dung ICMP với marker và sinh SID1000001/rev1. Dòng chú thích PREPARED trong tệp nguồn là lịch sử; trạng thái đã thực thi được xác định bằng alert live ngày02/11. Giữ nguyên chuỗi rule, không sửa dữ liệu nguồn.'
AddHeading 'A.5. Lệnh HTTPS nghiệm thu nguyên tham số' 2
$https=Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs/evidence/M3/M3-WAN-NAT-live-20261106/HTTPS-acceptance.json')|ConvertFrom-Json
P ('Các đối số được ghi theo thứ tự bên dưới từ acceptance JSON; --write-out là chuỗi JSON định dạng, không phải kết quả tự tạo.')
foreach($arg in $https.command){P ([string]$arg) 'Code'}
P 'Buộc IPv4/interface nguồn, bỏ proxy, không retry/redirect và kiểm TLS; dùng đích IP nên không phụ thuộc DNS Internet. Giá trị kết quả nằm ở bảng M3 trong nội dung chính.'
AddHeading 'A.6. Trích EVE thật có cấu trúc' 2
$live=Get-Content -Raw -Encoding UTF8 (Join-Path $root 'docs/evidence/M4/resume-20261102/sensor-public-after-marker.json')|ConvertFrom-Json
foreach($line in ($live.alerts[0]|ConvertTo-Json -Depth 12)-split "`r?`n"){P $line 'Code'}
P 'Đây là biểu diễn JSON từ tệp thực nghiệm đã lưu, không phải ảnh console hoặc event mới. Timestamp guest được giữ nguyên và chưa đồng bộ; collector_time được dùng riêng để truy vết thời điểm thu.'
AddHeading 'PHỤ LỤC B. MA TRẬN KIỂM THỬ VÀ NGUỒN NGHIỆM THU'
Table @('| Mã/phạm vi | Kết quả | Tệp đối chiếu gốc |','|---|---|---|','| M1 cấu trúc | PASS12/12 | M1/wazuh-link-20261105/independent-verification.json |','| M2 frame/persistence | PASS95/95 | M2/live-tests-20261101/final-collection/frame-cases.csv |','| M2 HTTP/policy | PASS1ca dương/2ca âm | M2/final-acceptance-20261103/M2-results.json |','| M3.1 | PASS | M3/todo-completion-20261103/M3.1-acceptance.json |','| M3.2 | PASS5VLAN | M3/todo-completion-20261103/M3.2-acceptance.json |','| M3.3 | PASS | M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json |','| M3.4B | PASS1session | M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json |','| M3.5 | PASS7/7live | M3/M3.5-network-services-20261105/M3.5-acceptance.json |','| XMLRPC | PASS8rule/3pool | M3/M3-runtime-review-20261106/acceptance.json |','| WAN/NAT | PASS1HEAD | M3/M3-WAN-NAT-live-20261106/M3-WAN-NAT-acceptance.json |','| Suricata marker | PASSphạm vi | M4/resume-20261102/sensor-public-after-marker.json |','| Manager replay | PASSreplay | M5/continuation-20261102/decoded-field-validation.json |','| M4.3/M4.4 | PARTIAL/BLOCKED | M4/M4.3-M4.4-20261107/report.md |') 'Định vị phép thử; đường dẫn tương đối từ docs/evidence'
P 'Không cộng các suite với số ảnh, số gói hoặc ca thử lại thành một tỷ lệ thành công tổng hợp. Bài M3.4 gián đoạn cũ khác M3.4B; trạng thái cũ được bảo toàn. Các tệp acceptance được ưu tiên khi có checkpoint tổng quát chưa cập nhật.'
AddHeading 'PHỤ LỤC C. DANH MỤC MINH CHỨNG HÌNH'
P 'Bảng dưới ghi vị trí dùng trong báo cáo, nguồn và thời điểm có múi giờ. Hash và phương pháp xử lý ảnh được lưu ở evidence-index.csv kèm báo cáo; các ảnh gốc không thay đổi. Không có ảnh Dashboard/Syslog đã nghiệm thu nên không thêm ảnh cho hai hạng mục này.'
$lines=@('| Hình | Nội dung | Thu (UTC+07:00 nếu không ghi khác) / đường dẫn |','|---|---|---|')
foreach($row in $script:imageIndex){$lines+='| '+$row.hinh+' | '+$row.noi_dung+' | '+$row.thoi_diem_thu+'; '+$row.duong_dan+' |'}
Table $lines 'Danh mục ảnh đã nhúng thực tế'
AddHeading 'PHỤ LỤC D. THUẬT NGỮ VÀ CÁCH ĐỌC TRẠNG THÁI'
P 'Danh mục từ viết tắt đầu báo cáo và Chương1 cùng phục vụ tra cứu. Các tên riêng OPNsense, Open vSwitch, QEMU, cloud-init, NoCloud, Suricata, Wazuh, EVE-NG được giữ tên chính thức. pfsync là tên cơ chế, không viết một dạng khai triển giả. Dưới đây là hướng dẫn liên hệ thuật ngữ với phép thử.'
Table @('| Nhóm thuật ngữ | Mục giải thích | Ví dụ và giới hạn |','|---|---|---|','| SOC/SIEM/Event/Log/Alert/Rule/Signature | 1.1 | Cùng dữ liệu có event sensor và alert Manager riêng; live chưa hoàn tất |','| IDS/IPS/NIDS/HIDS/Suricata/EVE/Wazuh | 1.2 | Sensor IDS thụ động; Manager replay; không suy IPS hoặc Dashboard |','| VLAN/Subnet/Gateway/L2/L3/Bridge/OVS | 1.3 | Core không IP, gateway ở OPNsense |','| Access/Trunk/802.1Q/Inter-VLAN/Firewall | 1.3 | Tag40→30, TTL64→63 tại firewall |','| NAT/SNAT/DNAT/DHCP/DNS | 1.4 | HTTPS và lease đã đạt; DNAT/leaseHA chưa |','| SPAN/Mirror/NIC/PCAP/TCP/MAC/TTL/SHA-256 | 1.4 | Mirror chọn ingress, cùng tuple/sequence/hash |','| HA/Failover/Recovery/CARP/VIP/VHID/pfsync/PF/XMLRPC | 1.5 | Năm VIP và một TCP đã đạt; không zero loss/NATHA |','| VMware/EVE-NG/QEMU/QCOW2/cloud-init/NoCloud/SSH/LACP/Syslog/HTTP/TLS | 1.6 | Công nghệ thực tế và phần chưa áp dụng được ghi riêng |') 'Tra cứu thuật ngữ theo ngữ cảnh thực nghiệm'
AddHeading 'TÀI LIỆU THAM KHẢO'
$references=@(
@('T1','Open vSwitch — Basic Configuration','https://docs.openvswitch.org/en/stable/faq/configuration/'),
@('T2','OPNsense — High Availability','https://docs.opnsense.org/manual/hacarp.html'),
@('T3','Suricata7.0.3 — EVE JSON Output','https://docs.suricata.io/en/suricata-7.0.3/output/eve/eve-json-output.html'),
@('T4','Wazuh — Architecture','https://documentation.wazuh.com/current/getting-started/architecture.html'),
@('T5','OPNsense — Rules','https://docs.opnsense.org/manual/firewall.html'),
@('T6','OPNsense — Network Address Translation','https://docs.opnsense.org/manual/nat.html'))
foreach($ref in $references){P ('['+$ref[0]+'] '+$ref[1]+'. '+$ref[2]+'. Đối chiếu08/11/2026; tài liệu lý thuyết không thay bằng chứng phiên bản/runtime của lab.')}
$sources=@(
@('E1','docs/M1/M1-final-acceptance-20261105.md','docs/M1/M1-design-consolidated-20261105.md','docs/M1/M1-topology-label-correction-20261105.md'),
@('E2','docs/M2/M2-final-summary-20261103.md'),
@('E3','docs/M2/M2-report-stage1-core-preparation-20261031-final.md','docs/M2/M2-report-ovs-offline-installed-20261101.md'),
@('E4','docs/M2/M2-isolated-bridge-results-20261101.md'),
@('E5','docs/M3/M3-report-primary-installed-verified-20261101.md'),
@('E6','docs/M3/M3-todo-completion-20261103.md'),
@('E7','docs/evidence/M3/todo-completion-20261103/M3.2-acceptance.json'),
@('E8','docs/evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json'),
@('E9','docs/evidence/M3/M3.4B-pfsync-state-20261104/evidence-index.md','docs/evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json'),
@('E10','docs/M3/M3.5-network-services-steps-1-5-20261105.md'),
@('E11','docs/M3/M3-runtime-verification-20261106.md','docs/evidence/M3/M3-runtime-review-20261106/acceptance.json'),
@('E12','docs/M3/M3-ha-wan-final-review-20261106.md','docs/M3/M3-pfsync-cause-NAT-proposal-20261106.md'),
@('E13','docs/M3/M3-WAN-NAT-final-acceptance-20261106.md','docs/M3/M3-Employee-Linux-readiness-20261106.md'),
@('E14','docs/evidence/M4/topology-first-20261102/sensor-configuration-public.json','docs/evidence/M4/resume-20261102/live-mirror-frames.json','docs/evidence/M4/resume-20261102/sensor-public-after-marker.json'),
@('E15','docs/M5-verification-and-demo-20261102.md','docs/evidence/M5/continuation-20261102/decoded-field-validation.json'),
@('E16','docs/evidence/M4/M4.3-M4.4-20261107/report.md','docs/evidence/M4/M4.3-M4.4-20261107/retry-diagnosis-20261107.txt'))
foreach($s in $sources){P ('['+$s[0]+'] Hồ sơ nội bộ: '+(($s|Select-Object -Skip 1)-join '; ')+'.');foreach($file in ($s|Select-Object -Skip 1)){$full=Join-Path $root $file;if(-not(Test-Path -LiteralPath $full)){throw "Source missing $file"};$script:sources+=[pscustomobject]@{id=$s[0];path=$file;sha256=(Get-FileHash -LiteralPath $full).Hash}}}
P 'Nguồn tiến độ: docs/SOC_TO_DO.md, checkpoint07/11/2026 và nghiệm thu từng hạng mục. Nguồn mẫu trình bày: docs/M1-M3_BaoCaoTongHop.docx. Các tài liệu gốc, ảnh, log và báo cáo cũ giữ nguyên.'
$rels.Add('<Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>')
$rels.Add('<Relationship Id="settings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>')
$rels.Add('<Relationship Id="footer" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>')
$doc='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="'+$w+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>'+$body.ToString()+'<w:sectPr><w:footerReference w:type="default" r:id="footer"/><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1701" w:header="567" w:footer="567"/><w:titlePg/></w:sectPr></w:body></w:document>'
$utf8=[Text.UTF8Encoding]::new($false)
function WriteXml($file,$text){[xml]$test=$text;[IO.File]::WriteAllText((Join-Path $stage $file),$text,$utf8)}
WriteXml 'word/document.xml' $doc;WriteXml 'word/styles.xml' $styles
WriteXml 'word/settings.xml' ('<w:settings xmlns:w="'+$w+'"><w:updateFields w:val="true"/><w:defaultTabStop w:val="360"/></w:settings>')
WriteXml 'word/footer1.xml' ('<w:ftr xmlns:w="'+$w+'"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">Trang </w:t></w:r><w:fldSimple w:instr=" PAGE "><w:r><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>')
WriteXml 'word/_rels/document.xml.rels' ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+($rels -join '')+'</Relationships>')
WriteXml '_rels/.rels' '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="doc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
WriteXml '[Content_Types].xml' '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>'
if(Test-Path -LiteralPath $target){throw 'Output already exists; preserve report for review.'}
[IO.Compression.ZipFile]::CreateFromDirectory($stage,$target)
$script:imageIndex|Export-Csv -LiteralPath (Join-Path $ev 'evidence-index.csv') -NoTypeInformation -Encoding UTF8
$script:sources|Export-Csv -LiteralPath (Join-Path $ev 'source-index.csv') -NoTypeInformation -Encoding UTF8
$stats=[ordered]@{file=$target;images=$script:images;tables=$script:tableCount;chapters=6;source_files=$script:sources.Count;stage=$stage;created_at=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o');template='docs/M1-M3_BaoCaoTongHop.docx';missing_identity='Họ tên, MSSV, lớp, giảng viên, chữ ký/ngày phê duyệt để trống, không suy từ danh sách nhóm.'}
$stats|ConvertTo-Json -Depth 4|Set-Content -Encoding UTF8 (Join-Path $ev 'build-stats.json')
$stats|ConvertTo-Json -Depth 4


