# Chi chup cua so terminal SOC da hoan tat nhap mat khau, khong chup desktop.
param([Parameter(Mandatory=$true)][string]$OutputPath,[string]$TitleFragment='SOC M2 - Secure Core console password',[int]$MinimumHeight=0)
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class SocWindowCapture {
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [StructLayout(LayoutKind.Sequential)] public struct Rect { public int L,T,R,B; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc proc, IntPtr p);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder b, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out Rect r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int width, int height, uint flags);
}
'@
if (Test-Path -LiteralPath $OutputPath) { throw 'Khong ghi de anh cu' }
$socMatches = [System.Collections.Generic.List[System.IntPtr]]::new()
[SocWindowCapture]::EnumWindows({param($socHwnd,$socParam)
  $socTitle = [System.Text.StringBuilder]::new(512)
  [void][SocWindowCapture]::GetWindowText($socHwnd,$socTitle,512)
  if ($socTitle.ToString().Contains($TitleFragment)) { $socMatches.Add($socHwnd) }
  return $true
},[IntPtr]::Zero) | Out-Null
if ($socMatches.Count -ne 1) { throw 'Khong tim thay duy nhat cua so SOC; can chup thu cong' }
$socRect = New-Object SocWindowCapture+Rect
[void][SocWindowCapture]::GetWindowRect($socMatches[0],[ref]$socRect)
if ($MinimumHeight -gt ($socRect.B-$socRect.T)) {
  if ($MinimumHeight -gt 1200) { throw 'Requested window height too large' }
  [void][SocWindowCapture]::SetWindowPos($socMatches[0],[IntPtr]::Zero,0,0,($socRect.R-$socRect.L),$MinimumHeight,0x16)
  Start-Sleep -Milliseconds 700
  [void][SocWindowCapture]::GetWindowRect($socMatches[0],[ref]$socRect)
}
$socWidth=$socRect.R-$socRect.L; $socHeight=$socRect.B-$socRect.T
if ($socWidth -lt 200 -or $socHeight -lt 100) { throw 'Cua so khong du kich thuoc' }
$socBitmap = [System.Drawing.Bitmap]::new($socWidth,$socHeight)
$socGraphics = [System.Drawing.Graphics]::FromImage($socBitmap)
$socDc = $socGraphics.GetHdc()
try { $socResult=[SocWindowCapture]::PrintWindow($socMatches[0],$socDc,2) }
finally { $socGraphics.ReleaseHdc($socDc); $socGraphics.Dispose() }
if (-not $socResult) { $socBitmap.Dispose(); throw 'PrintWindow khong ho tro; can chup thu cong' }
$socBitmap.Save($OutputPath,[System.Drawing.Imaging.ImageFormat]::Png)
$socBitmap.Dispose()
[pscustomobject]@{Path=$OutputPath;Width=$socWidth;Height=$socHeight;CollectedAt=(Get-Date -Format o);Source='Actual SOC interactive terminal window via Win32 PrintWindow; no image content edits'} | ConvertTo-Json -Compress
