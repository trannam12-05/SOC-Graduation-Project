$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1})[0]
$asAction=([System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object {$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1})[0]
function AwaitResult($operation,$type){$task=$asTask.MakeGenericMethod($type).Invoke($null,@($operation));$task.GetAwaiter().GetResult()}
$dir='D:\SOC\docs\evidence\M4\report-M1-M4-20261108'
$file=AwaitResult ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Join-Path $dir 'Word-pagination-proof.pdf'))) ([Windows.Storage.StorageFile])
$pdf=AwaitResult ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$pageNums=@(0,5,12,24,38,([int]$pdf.PageCount-1))|Where-Object {$_ -ge 0 -and $_ -lt $pdf.PageCount}|Select-Object -Unique
foreach($i in $pageNums){
 $page=$pdf.GetPage([uint32]$i);$stream=[Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
 try{
  $op=$page.RenderToStreamAsync($stream)
  $task=$asAction.Invoke($null,@($op));$task.GetAwaiter().GetResult()
  $stream.Seek(0);$read=[System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
  $dest=[IO.File]::Create((Join-Path $dir ('page-'+($i+1)+'.png')))
  try{$read.CopyTo($dest)}finally{$dest.Dispose();$read.Dispose()}
 }finally{$page.Dispose();$stream.Dispose()}
}
Write-Output "Rendered sample pages; PDF pages=$($pdf.PageCount)"
