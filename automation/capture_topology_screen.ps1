param([string]$OutputPath)
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public class SocScreenCapture {
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out Rect r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 public struct Rect { public int L,T,R,B; }
}
'@
$p=@(Get-Process msedge | Where-Object {$_.MainWindowTitle -like 'EVE*'})
if($p.Count -ne 1){throw 'Cannot identify exactly one EVE window.'}
[SocScreenCapture]::SetForegroundWindow($p[0].MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$r=New-Object SocScreenCapture+Rect
if(-not [SocScreenCapture]::GetWindowRect($p[0].MainWindowHandle,[ref]$r)){throw 'Cannot read window bounds.'}
$w=$r.R-$r.L; $h=$r.B-$r.T
if($w -lt 300 -or $h -lt 300){throw 'EVE window is too small.'}
$b=New-Object Drawing.Bitmap $w,$h
$g=[Drawing.Graphics]::FromImage($b)
try {
 $g.CopyFromScreen($r.L,$r.T,0,0,(New-Object Drawing.Size $w,$h))
 $b.Save($OutputPath,[Drawing.Imaging.ImageFormat]::Png)
} finally {$g.Dispose();$b.Dispose()}
Write-Output $OutputPath
