import pathlib,json
base=pathlib.Path('/usr/local/opnsense/mvc/app/models/OPNsense/Kea')
files=[]
for p in sorted(base.rglob('*')):
    if p.is_file() and p.suffix in ['.xml','.php']:
        text=p.read_text(errors='replace')
        keep=[]
        for line in text.splitlines():
            low=line.lower()
            if any(k in low for k in ['subnet','pool','option','interface','router','dns','class kea','class dhcp']):keep.append(line.strip())
        files.append({'path':str(p),'bytes':p.stat().st_size,'relevant_lines':keep[:220]})
d={'files':files}
