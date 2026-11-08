$ErrorActionPreference='Stop'
$path='D:\SOC\docs\SOC_M1-M4_BaoCaoCaNhan.docx'
$out='D:\SOC\docs\evidence\M4\report-M1-M4-20261108'
$app=New-Object -ComObject Word.Application
$app.Visible=$false;$app.DisplayAlerts=0;$app.ScreenUpdating=$false
$doc=$null
try{
 $doc=$app.Documents.Open($path,$false,$false,$false)
 Write-Output 'Document opened.'
 $doc.Fields.Update()|Out-Null
 Write-Output 'Fields updated.'
 $tocCount=[int]$doc.TablesOfContents.Count
 for($i=1;$i -le $tocCount;$i++){$doc.TablesOfContents.Item($i).Update()}
 Write-Output 'Three lists updated.'
 $doc.Repaginate()
 for($i=1;$i -le $tocCount;$i++){$doc.TablesOfContents.Item($i).UpdatePageNumbers()}
 $doc.Repaginate()
 $pages=$doc.ComputeStatistics(2)
 $words=$doc.ComputeStatistics(0)
 $figures=$doc.InlineShapes.Count
 $tableCount=$doc.Tables.Count
 $fields=$doc.Fields.Count
 $tocCount=$doc.TablesOfContents.Count
 $doc.Save()
 Write-Output 'DOCX saved.'
 $doc.ExportAsFixedFormat((Join-Path $out 'Word-pagination-proof.pdf'),17)
 $stats=[ordered]@{path=$path;pages=$pages;words=$words;embedded_images=$figures;tables=$tableCount;fields=$fields;toc_fields=$tocCount;page_width_pt=$doc.PageSetup.PageWidth;page_height_pt=$doc.PageSetup.PageHeight;left_margin_pt=$doc.PageSetup.LeftMargin;right_margin_pt=$doc.PageSetup.RightMargin;top_margin_pt=$doc.PageSetup.TopMargin;bottom_margin_pt=$doc.PageSetup.BottomMargin;word_repaginated=$true;pdf_proof='Word-pagination-proof.pdf';checked_at=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(7)).ToString('o')}
 $stats|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $out 'word-validation.json')
 $doc.Close(0);$doc=$null
 # Mở lại đúng DOCX đã lưu để xác nhận field/media và số trang tồn tại.
 $doc=$app.Documents.Open($path,$false,$true,$false)
 [pscustomobject]@{reopened=$true;pages=$doc.ComputeStatistics(2);images=$doc.InlineShapes.Count;tables=$doc.Tables.Count;toc=$doc.TablesOfContents.Count}|ConvertTo-Json|Set-Content -Encoding UTF8 (Join-Path $out 'reopen-validation.json')
 $doc.Close(0);$doc=$null
 $stats|ConvertTo-Json
}finally{if($doc){$doc.Close(0)};$app.Quit()}
