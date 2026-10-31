"""Xuat ban thao Markdown M2 sang DOCX bang thu vien chuan; khong cai phan mem.

Ho tro heading, doan van, bang Markdown, khoi lenh va anh PNG nguyen ven.
Chi tao tep DOCX moi; Times New Roman 13/12, A4, le trai 3 cm, con lai 2 cm.
"""
import argparse
import datetime as dt
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

NS = {
 'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
 'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
 'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
 'pic':'http://schemas.openxmlformats.org/drawingml/2006/picture',
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix,uri)

def elem(parent,tag,attrs=None):
    prefix,name=tag.split(':')
    data={f'{{{NS[k.split(":")[0]]}}}{k.split(":")[1]}':str(v) if v is not None else ''
          for k,v in (attrs or {}).items()}
    return ET.SubElement(parent,f'{{{NS[prefix]}}}{name}',data)

def plain(text):
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
    return text.replace('**','').replace('`','')

def paragraph(parent,text='',style=None):
    p=elem(parent,'w:p')
    if style:
        prop=elem(p,'w:pPr'); elem(prop,'w:pStyle',{'w:val':style})
    r=elem(p,'w:r'); t=elem(r,'w:t'); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); t.text=plain(text)
    return p

def xml_bytes(root):
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def build(source):
    target=source.with_suffix('.docx')
    if target.exists():
        raise FileExistsError('Khong ghi de bao cao DOCX da co: '+str(target))
    document=ET.Element(f'{{{NS["w"]}}}document')
    body=elem(document,'w:body')
    relationships=[]
    media=[]
    rows=source.read_text(encoding='utf-8').splitlines()
    i=0
    in_code=False
    while i<len(rows):
        line=rows[i].strip()
        if line.startswith('```'):
            in_code=not in_code; i+=1; continue
        if not line:
            i+=1; continue
        if in_code:
            paragraph(body,rows[i],'Code'); i+=1; continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:
            image_path=(source.parent/image.group(2)).resolve()
            blob=image_path.read_bytes()
            if not blob.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Chi nhung PNG that')
            width,height=struct.unpack('>II',blob[16:24])
            number=len(media)+1
            rid='rIdImage'+str(number)
            media_name='image'+str(number)+'.png'
            relationships.append((rid,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image','media/'+media_name))
            media.append(('word/media/'+media_name,blob))
            p=elem(body,'w:p'); pp=elem(p,'w:pPr'); elem(pp,'w:jc',{'w:val':'center'}); elem(pp,'w:keepNext')
            drawing=elem(elem(p,'w:r'),'w:drawing')
            inline=elem(drawing,'wp:inline',{'wp:distT':'0','wp:distB':'0','wp:distL':'0','wp:distR':'0'})
            # wp:inline attributes dist* are unqualified in OOXML.
            inline.attrib.clear(); inline.attrib.update({'distT':'0','distB':'0','distL':'0','distR':'0'})
            cx=5577840; cy=round(cx*height/width)
            extent=elem(inline,'wp:extent'); extent.attrib.update({'cx':str(cx),'cy':str(cy)})
            docpr=elem(inline,'wp:docPr'); docpr.attrib.update({'id':str(number),'name':image_path.name,'descr':image.group(1)})
            graphic=elem(inline,'a:graphic'); gd=elem(graphic,'a:graphicData'); gd.set('uri',NS['pic'])
            pic=elem(gd,'pic:pic'); nv=elem(pic,'pic:nvPicPr'); cn=elem(nv,'pic:cNvPr'); cn.attrib.update({'id':'0','name':media_name}); elem(nv,'pic:cNvPicPr')
            fill=elem(pic,'pic:blipFill'); elem(fill,'a:blip',{'r:embed':rid}); elem(elem(fill,'a:stretch'),'a:fillRect')
            sp=elem(pic,'pic:spPr'); xform=elem(sp,'a:xfrm'); off=elem(xform,'a:off'); off.attrib.update({'x':'0','y':'0'}); ext=elem(xform,'a:ext'); ext.attrib.update({'cx':str(cx),'cy':str(cy)})
            geom=elem(sp,'a:prstGeom'); geom.set('prst','rect'); elem(geom,'a:avLst')
            i+=1; continue
        if line.startswith('|'):
            table=elem(body,'w:tbl'); props=elem(table,'w:tblPr'); elem(props,'w:tblW',{'w:w':'9071','w:type':'dxa'})
            borders=elem(props,'w:tblBorders')
            for side in ['top','left','bottom','right','insideH','insideV']:
                elem(borders,'w:'+side,{'w:val':'single','w:sz':'4','w:color':'777777'})
            table_rows=[]
            while i<len(rows) and rows[i].strip().startswith('|'):
                cells=[cell.strip() for cell in rows[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',cell) for cell in cells):
                    table_rows.append(cells)
                i+=1
            grid=elem(table,'w:tblGrid')
            for _ in table_rows[0]: elem(grid,'w:gridCol',{'w:w':str(9071//len(table_rows[0]))})
            for index,cells in enumerate(table_rows):
                row=elem(table,'w:tr')
                if index==0: elem(elem(row,'w:trPr'),'w:tblHeader')
                for text in cells:
                    cell=elem(row,'w:tc'); paragraph(cell,text,'TableHeader' if index==0 else 'TableText')
            paragraph(body)
            continue
        heading=re.match(r'^(#{1,3}) (.+)$',line)
        if heading:
            paragraph(body,heading.group(2),'Heading'+str(len(heading.group(1)))); i+=1; continue
        if line.startswith('**Hình '):
            paragraph(body,line,'Caption'); i+=1; continue
        if line.startswith('- ') or re.match(r'^\d+\. ',line):
            paragraph(body,line,'ListParagraph'); i+=1; continue
        parts=[line]; i+=1
        while i<len(rows) and rows[i].strip() and not rows[i].strip().startswith(('#','|','!','```','- ')):
            parts.append(rows[i].strip()); i+=1
        paragraph(body,' '.join(parts))
    section=elem(body,'w:sectPr')
    elem(section,'w:pgSz',{'w:w':'11906','w:h':'16838'})
    elem(section,'w:pgMar',{'w:top':'1134','w:right':'1134','w:bottom':'1134','w:left':'1701','w:header':'567','w:footer':'567','w:gutter':'0'})
    styles=ET.Element(f'{{{NS["w"]}}}styles')
    defaults=elem(styles,'w:docDefaults'); default_run=elem(elem(defaults,'w:rPrDefault'),'w:rPr')
    elem(default_run,'w:rFonts',{'w:ascii':'Times New Roman','w:hAnsi':'Times New Roman','w:eastAsia':'Times New Roman','w:cs':'Times New Roman'})
    elem(default_run,'w:sz',{'w:val':'26'}); elem(default_run,'w:szCs',{'w:val':'26'}); elem(default_run,'w:lang',{'w:val':'vi-VN'})
    pdefault=elem(elem(defaults,'w:pPrDefault'),'w:pPr'); elem(pdefault,'w:spacing',{'w:after':'120','w:line':'276','w:lineRule':'auto'})
    for name in ['Normal','Heading1','Heading2','Heading3','Caption','TableText','TableHeader','Code','ListParagraph']:
        style=elem(styles,'w:style',{'w:type':'paragraph','w:styleId':name})
        if name=='Normal': style.set(f'{{{NS["w"]}}}default','1')
        elem(style,'w:name',{'w:val':name})
        if name!='Normal': elem(style,'w:basedOn',{'w:val':'Normal'})
        pp=elem(style,'w:pPr'); rp=elem(style,'w:rPr')
        if name.startswith('Heading'):
            elem(pp,'w:keepNext'); elem(pp,'w:outlineLvl',{'w:val':str(int(name[-1])-1)}); elem(rp,'w:b')
        if name=='Caption': elem(pp,'w:jc',{'w:val':'center'}); elem(rp,'w:i')
        if name in ['Caption','TableText','TableHeader','Code']:
            elem(rp,'w:sz',{'w:val':'24'}); elem(rp,'w:szCs',{'w:val':'24'})
        if name=='TableHeader': elem(rp,'w:b')
    relationships.append(('rIdStyles','http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles','styles.xml'))
    relns='http://schemas.openxmlformats.org/package/2006/relationships'
    rels=ET.Element('Relationships',xmlns=relns)
    for rid,kind,target_path in relationships:
        ET.SubElement(rels,'Relationship',Id=rid,Type=kind,Target=target_path)
    rootrels=ET.Element('Relationships',xmlns=relns)
    ET.SubElement(rootrels,'Relationship',Id='rIdDocument',Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument',Target='word/document.xml')
    content_types=ET.Element('Types',xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
    for extension,typ in [('rels','application/vnd.openxmlformats-package.relationships+xml'),('xml','application/xml'),('png','image/png')]:
        ET.SubElement(content_types,'Default',Extension=extension,ContentType=typ)
    for path,typ in [('/word/document.xml','application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'),('/word/styles.xml','application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml')]:
        ET.SubElement(content_types,'Override',PartName=path,ContentType=typ)
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,value in [('[Content_Types].xml',xml_bytes(content_types)),('_rels/.rels',xml_bytes(rootrels)),('word/document.xml',xml_bytes(document)),('word/styles.xml',xml_bytes(styles)),('word/_rels/document.xml.rels',xml_bytes(rels))]+media:
            archive.writestr(name,value)
    print(target)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    build(parser.parse_args().source.resolve())
