$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing
$target='D:\SOC\Thuyết trình nhóm 1.pptx'
$dir='D:\SOC\docs\evidence\M4\slide-light-background-20261108'
[void](New-Item -ItemType Directory -Path $dir -Force)
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
public static class SOCMonochrome {
 public static long[] Convert(Bitmap src, Bitmap dst) {
  long neutral=0,colored=0,verified=0;
  for(int y=0;y<src.Height;y++) for(int x=0;x<src.Width;x++) {
   Color c=src.GetPixel(x,y), d;
   if(c.R==c.G && c.G==c.B) {d=Color.FromArgb(c.A,255-c.R,255-c.G,255-c.B);neutral++;}
   else {d=c;colored++;}
   dst.SetPixel(x,y,d);
   Color actual=dst.GetPixel(x,y);
   bool ok=c.R==c.G && c.G==c.B ? actual.R==255-c.R && actual.G==255-c.G && actual.B==255-c.B && actual.A==c.A : actual.ToArgb()==c.ToArgb();
   if(!ok) throw new Exception("Pixel verification failed");
   verified++;
  }
  return new long[]{neutral,colored,verified};
 }
}
'@
$z=[IO.Compression.ZipFile]::OpenRead($target)
$processed=@{};$rows=@();$before=@{}
function HashEntry($entry){$h=[Security.Cryptography.SHA256]::Create();$s=$entry.Open();try{[Convert]::ToBase64String($h.ComputeHash($s))}finally{$s.Dispose();$h.Dispose()}}
try {
 foreach($entry in $z.Entries){$before[$entry.FullName]=HashEntry $entry}
 foreach($name in 'soc-live-vlan-vip.png','soc-live-ha-failover.png','soc-live-span.png'){
  $entry=$z.GetEntry("ppt/media/$name");$s=$entry.Open();$mem=[IO.MemoryStream]::new();try{$s.CopyTo($mem)}finally{$s.Dispose()};$mem.Position=0
  $src=[Drawing.Bitmap]::new($mem);$dst=[Drawing.Bitmap]::new($src.Width,$src.Height,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
  try{
   $counts=[SOCMonochrome]::Convert($src,$dst)
   $dest=Join-Path $dir $name;$dst.Save($dest,[Drawing.Imaging.ImageFormat]::Png)
   $processed[$entry.FullName]=[IO.File]::ReadAllBytes($dest)
   $rows+=[pscustomobject]@{image=$entry.FullName;width=$src.Width;height=$src.Height;neutral_pixels_converted=$counts[0];colored_pixels_unchanged=$counts[1];pixels_verified=$counts[2];method='Đổi mức xám v thành 255-v tại cùng tọa độ; giữ nguyên pixel có màu và alpha; không OCR hoặc tạo chữ mới';derived_image=$dest;timestamp=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o')}
  }finally{$src.Dispose();$dst.Dispose();$mem.Dispose()}
 }
}finally{$z.Dispose()}
# Khóa độc quyền; không cưỡng bức nếu PowerPoint đang giữ file.
$stream=[IO.File]::Open($target,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
$zip=[IO.Compression.ZipArchive]::new($stream,[IO.Compression.ZipArchiveMode]::Update,$true)
try{foreach($key in $processed.Keys){$zip.GetEntry($key).Delete();$entry=$zip.CreateEntry($key);$s=$entry.Open();try{$bytes=$processed[$key];$s.Write($bytes,0,$bytes.Length)}finally{$s.Dispose()}}}finally{$zip.Dispose();$stream.Dispose()}
$check=[IO.Compression.ZipFile]::OpenRead($target);$changed=@()
try{foreach($entry in $check.Entries){if((HashEntry $entry) -ne $before[$entry.FullName]){$changed+=$entry.FullName}}}finally{$check.Dispose()}
if(@($changed|Where-Object {$_ -notin $processed.Keys}).Count){throw 'Unexpected change outside image assets'}
$report=[ordered]@{file=$target;changed_parts=$changed;other_parts_unchanged=$true;topology_image_unchanged=$true;pixel_verification=$rows;original_evidence_untouched=$true}
$report|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 (Join-Path $dir 'validation.json')
$rows|Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $dir 'evidence-index.csv')
$report|ConvertTo-Json -Depth 5
