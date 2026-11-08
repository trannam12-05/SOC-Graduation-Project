$ErrorActionPreference='Stop'
$root='D:\SOC';$dir=Join-Path $root 'docs\report-final';$path=Join-Path $dir 'BAO_CAO_SOC_DA_SUA.docx';$work=Join-Path $root 'temp\network-report-review'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;using System.Runtime.InteropServices;public class SOCWordCapture{[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[StructLayout(LayoutKind.Sequential)]public struct RECT{public int L,T,R,B;}[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out RECT r);[DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);}
'@
[void][SOCWordCapture]::SetProcessDPIAware();$app=New-Object -ComObject Word.Application;$app.Visible=$false;$app.DisplayAlerts=0;$app.ScreenUpdating=$false;$doc=$null
try{
 $doc=$app.Documents.Open($path,$false,$false,$false)
 Write-Output 'Opened corrected report.'
 $doc.Fields.Update()|Out-Null
 $count=[int]$doc.TablesOfContents.Count
 for($i=1;$i -le $count;$i++){$doc.TablesOfContents.Item($i).Update()}
 $doc.Repaginate()
 for($i=1;$i -le $count;$i++){$doc.TablesOfContents.Item($i).UpdatePageNumbers()}
 Write-Output "Updated $count automatic lists."
 $positions=@();$queries=@('2.2.1 Phân lớp core, distribution và access','Hình 2.3a. Topology logic','Bảng 2.4. VLAN, subnet','2.2.7 Firewall OPNsense Active-Passive','Bảng 3.4. Các ca mạng','3.2.7.3 M3 – OPNsense HA','3.2.7.4 M4 – Suricata')
 foreach($query in $queries){$range=$doc.Content.Duplicate;$find=$range.Find;$find.ClearFormatting();$find.Text=$query;$find.Forward=$false;$find.Wrap=0;if($find.Execute()){$positions+=[pscustomobject]@{text=$query;page=$range.Information(3);start=$range.Start;end=$range.End}}}
 $positions|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $work 'pages.json')
 $stats=[ordered]@{pages=$doc.ComputeStatistics(2);words=$doc.ComputeStatistics(0);images=$doc.InlineShapes.Count;tables=$doc.Tables.Count;toc=$count;normal_open=$true;checked_at=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o')}
 try{$doc.Save();$stats.saved_by='Word Save'}catch{
  # Ghi gói Flat OPC mà Word đã tính field; không mất cache mục lục nếu Word bị khóa rename.
  [IO.File]::WriteAllText((Join-Path $work 'updated-flat-opc.xml'),$doc.WordOpenXML,[Text.UTF8Encoding]::new($false));$stats.saved_by='Flat OPC serialization after Word pagination';$stats.save_warning=$_.Exception.Message
 }
 $stats.pdf_export='Không xuất PDF; kiểm tra trực tiếp trong Word.'
 $stats|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $work 'word-validation.json')
 Write-Output 'Saved report; capturing the actual Word window.'
 # Ảnh chụp thật của cửa sổ Word, không dựng khung UI giả.
 $app.ScreenUpdating=$true;$app.Visible=$true;$app.WindowState=1
 $shots=@();$n=0
 foreach($entry in @($positions|Where-Object {$_.text -match 'Hình 2.3a|Bảng 2.4\.|2.2.7|Bảng 3.4\.'})){
  $n++;$range=$doc.Content.Duplicate;$find=$range.Find;$find.ClearFormatting();$find.Text=$entry.text;$find.Forward=$false;$find.Wrap=0;if(-not $find.Execute()){throw 'Capture text not found'};Write-Output $range.Text;$app.ActiveWindow.View.Type=3;$app.ActiveWindow.View.Zoom.PageColumns=1;$app.ActiveWindow.View.Zoom.PageRows=1;$app.ActiveWindow.View.Zoom.PageFit=1;$doc.Activate();$range.Select();$app.ActiveWindow.ScrollIntoView($range,$true);if($n -gt 1){$app.ActiveWindow.LargeScroll(1,0,0,0)};$app.ScreenRefresh();Start-Sleep -Milliseconds 1000
  $handle=[IntPtr]$app.ActiveWindow.Hwnd;$rect=[SOCWordCapture+RECT]::new();[void][SOCWordCapture]::GetWindowRect($handle,[ref]$rect)
  $width=$rect.R-$rect.L;$height=$rect.B-$rect.T
  if($width -gt 100 -and $height -gt 100){$bmp=[Drawing.Bitmap]::new($width,$height);$graphics=[Drawing.Graphics]::FromImage($bmp);$dc=$graphics.GetHdc();try{$ok=[SOCWordCapture]::PrintWindow($handle,$dc,2)}finally{$graphics.ReleaseHdc($dc)}
   try{if($ok){$name='Word-screen-'+$n+'.png';$bmp.Save((Join-Path $dir ('images\'+$name)),[Drawing.Imaging.ImageFormat]::Png);$shots+=[pscustomobject]@{file=$name;page=$entry.page;section=$entry.text;type='Ảnh chụp thật cửa sổ Word qua PrintWindow';timestamp=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o')}}}finally{$graphics.Dispose();$bmp.Dispose()}
  }
 }
 $shots|Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $dir 'images\screenshot-index.csv')
 $doc.Close(0);$doc=$null;$stats|ConvertTo-Json
}finally{if($doc){$doc.Close(0)};$app.Quit()}
