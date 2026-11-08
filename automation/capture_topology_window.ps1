param([string]$OutputPath='D:\SOC\staging\topology-first\eve-window.png')
# Chụp nguyên cửa sổ EVE thật bằng PrintWindow; không chỉnh sửa nội dung ảnh.
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public class SocTopologyCapture {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out Rect r);
 public struct Rect { public int L,T,R,B; }
}
'@
$p=@(Get-Process msedge | Where-Object {$_.MainWindowTitle -like 'EVE*'})
if($p.Count -ne 1){throw 'Không xác định được duy nhất cửa sổ EVE.'}
$r=New-Object SocTopologyCapture+Rect
[SocTopologyCapture]::GetWindowRect($p[0].MainWindowHandle,[ref]$r) | Out-Null
$b=New-Object Drawing.Bitmap ($r.R-$r.L),($r.B-$r.T)
$g=[Drawing.Graphics]::FromImage($b); $dc=$g.GetHdc()
try { if(-not [SocTopologyCapture]::PrintWindow($p[0].MainWindowHandle,$dc,2)){throw 'PrintWindow thất bại'} }
finally {$g.ReleaseHdc($dc)}
try {$b.Save($OutputPath)} finally {$g.Dispose();$b.Dispose()}
Write-Output $OutputPath
