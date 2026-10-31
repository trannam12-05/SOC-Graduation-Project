"""Ban chot bao cao/bang minh chung v2, bao toan cac ban truoc."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence/M2'
STAGE=ROOT/'staging/soc-core-l2-20261031-stage1'

def write_new(path,text):
    with path.open('x',encoding='utf-8',newline='\n') as out:out.write(text)
def json_new(path,obj):write_new(path,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

data=json.loads((E/'M2-core-stage1-final-status-v2-20261031.json').read_text(encoding='utf-8'))
release=json.loads((STAGE/'payload-v2-finalization.json').read_text(encoding='utf-8'))
json_new(E/'M2-core-stage1-payload-v2-20261031.json',release)
json_new(E/'M2-core-stage1-seed-status-v2-20261031.json',data['seed-ready.json'])
json_new(E/'M2-core-stage1-bundle-validation-v2-20261031.json',data['bundle-validated.json'])
previous=(ROOT/'docs/M2/M2-report-stage1-core-preparation-20261031.md').read_text(encoding='utf-8')
old_seed='f4aea1d849fff37e272d0efbb117a670582751504cb5b8042a9e10c018258dbd'
old_bundle='f65ddae0f71bee455760ddb209153bfbc2377de3f0989af3475ad86061e4c03e'
text=previous.replace(old_seed,data['seed-ready.json']['seed_sha256']).replace(old_bundle,data['bundle-ready.json']['sha256'])
text=text.replace('ovs-noble-amd64-offline-20261031.tar','ovs-noble-amd64-offline-20261031-v2.tar')
memory=data['windows_memory']
text+='''

## 2.15. Bản chốt payload v2 và kiểm tra trước bước boot

Kiểm tra archive cuối phát hiện một mục `.deb.part-1` **0 byte**, do lần tải mạng bị timeout; không có package `.deb` sai checksum. Đã tạo bundle v2 loại mục tạm này và cập nhật SHA256SUMS bên trong archive. Bản v1 được giữ lại để đối chiếu; không xóa dữ liệu cũ. Tất cả 70 package thật của hai bản có cùng hash đã xác minh.

Chỉ seed của Core mới đang tắt được đóng gói lại bằng payload v2, giữ nguyên tài khoản, password hash, instance-id, public key và network-config. Seed v1 được lưu root-only ở staging riêng trước khi thay file `cdrom.iso` của Core; hai seed/image/lab cũ không thay đổi. Không boot guest để làm việc này. Các bảng hash/path bundle trong bản báo cáo chốt đã dùng **v2 hiện hành**; ảnh Hình 2.3–2.4 được chụp trước khi bỏ mục tạm và chỉ chứng minh trạng thái/cấu hình tại thời điểm chụp, không thay snapshot/hash v2.

'''
text+=f'''Bundle hiện hành: `{data['bundle-ready.json']['bundle']}`; SHA-256 `{data['bundle-ready.json']['sha256']}`. Seed hiện hành: `{data['seed-ready.json']['seed_path']}`; SHA-256 `{data['seed-ready.json']['seed_sha256']}`. Không có mục `.part-*` trong archive v2. Kiểm tra hash và control của 70 `.deb`, cùng APT download-only/no-download, đều đạt lại ở v2.

Snapshot chốt: `{data['collected_at_windows']}`. EVE status=0, 8 interface network_id=0, không Core QEMU process hoặc runtime directory. Chín file cũ tiếp tục khớp checksum ban đầu. RAM Windows tại `{memory['CollectedAt']}` chỉ còn **{memory['FreePhysicalMemoryKiB']/1024:.1f} MiB**; EVE memory tại cùng lần đọc được ghi nguyên văn trong JSON. Đây là mẫu mới hơn số liệu mục 2.12, **Windows vẫn chưa đạt ngưỡng vận hành 2 GiB đề xuất**.

Để tiếp tục, dùng `seed-ready-v2.json`, `bundle-ready-v2.json`, `bundle-validated-v2.json` trong `/opt/unetlab/soc-core-preparation-20261031/` và snapshot v2 trong thư mục minh chứng. Không coi các marker v1 là trạng thái payload mới nhất, không chạy lại thao tác tạo image/lab khi đã tồn tại. Chờ người dùng xử lý RAM và phê duyệt boot riêng Core; cài OVS hoặc nối mạng vẫn cần duyệt riêng.

[Danh mục minh chứng bản chốt](../evidence/M2/M2-core-stage1-final-evidence-index-20261031.md). Bản Word được kiểm tra ở mức ZIP/XML, định dạng trang/font và ảnh nhúng; chưa mở để kiểm tra bố cục trực quan bằng Word.
'''
report=ROOT/'docs/M2/M2-report-stage1-core-preparation-20261031-final.md'
write_new(report,text)
index='''# Danh mục minh chứng chốt giai đoạn đầu Core M2

## 1. Tài liệu hiện hành

- [Báo cáo Word chốt](../../M2/M2-report-stage1-core-preparation-20261031-final.docx).
- [Báo cáo Markdown chốt](../../M2/M2-report-stage1-core-preparation-20261031-final.md).
- [Danh mục ảnh và log ban đầu của giai đoạn](M2-core-stage1-evidence-index-20261031.md), [CSV ảnh](M2-core-stage1-evidence-index-20261031.csv).
- [Snapshot v2 chốt](M2-core-stage1-final-status-v2-20261031.json): trạng thái node, 8 NIC, không process/runtime, checksum cũ và RAM mới nhất.
- [Payload v2](M2-core-stage1-payload-v2-20261031.json): bundle/seed mới, hash và mục tạm 0 byte đã loại khỏi phát hành; v1 vẫn giữ.
- [Seed status v2](M2-core-stage1-seed-status-v2-20261031.json), [bundle validation v2](M2-core-stage1-bundle-validation-v2-20261031.json), [APT log v2](M2-core-stage1-apt-offline-check-v2-20261031.log).
- [Manifest 70 package không đổi giữa v1/v2](M2-core-stage1-package-manifest-20261031.json), [CSV package](M2-core-stage1-packages-20261031.csv), [metadata manifest](M2-core-stage1-metadata-manifest-20261031.json).
- `M2-core-stage1-SHA256SUMS-20261031.txt`: checksum bộ tài liệu/minh chứng giai đoạn, gồm các bản được bảo toàn.

## 2. Danh mục ảnh thật

| Tên ảnh | Nội dung | Thời điểm UTC+07:00 | Đường dẫn | Vị trí báo cáo |
|---|---|---|---|---|
| [M2-core-seed-ready-real-terminal-20261031.png](M2-core-seed-ready-real-terminal-20261031.png) | Terminal thật hoàn tất seed trước khi làm sạch payload v2; không chứa mật khẩu/hash | 31/10/2026 19:55:46 | docs/evidence/M2/M2-core-seed-ready-real-terminal-20261031.png | Hình 2.3, mục 2.10 |
| [M2-core-stopped-eight-nics-real-terminal-20261031.png](M2-core-stopped-eight-nics-real-terminal-20261031.png) | Terminal kiểm tra live: status0, 8 MAC không link, disk8GiB, bundle/seed chuẩn bị; không là guest console | 31/10/2026 19:57:58 | docs/evidence/M2/M2-core-stopped-eight-nics-real-terminal-20261031.png | Hình 2.4, mục 2.12 |

Ảnh chụp nguyên cửa sổ bằng Win32 PrintWindow, đã xem kiểm tra, không sửa nội dung kỹ thuật. Ảnh không chứa checksum v2; dùng snapshot v2 và manifest để xác nhận media hiện hành. Hai ảnh và CSV cũ được giữ nguyên, không ghi đè bằng ảnh giả.

## 3. Trạng thái nghiệm thu

Đã hoàn tất chuẩn bị image QCOW2 độc lập 8 GiB, seed quản trị riêng và node Core tắt 1CPU/2048MiB/8vNIC không link; bundle OVS 3.3.9 gồm 70 gói Noble amd64/all đã xác thực. Chưa boot Core, chưa thử cloud-init/login/NIC/kernel/filesystem trong guest, chưa cài OVS, chưa bridge/VLAN/trunk/mirror. Windows RAM ở snapshot v2 dưới ngưỡng đề xuất; chờ người dùng xử lý và duyệt boot.

Chưa có ảnh topology/settings GUI EVE trực tiếp. Người dùng có thể mở lab SOC-M2-Core-L2, chụp topology node tắt và settings Ethernet=8 bằng Snipping Tool, lưu PNG nguyên bản kèm thời điểm vào docs/evidence/M2 để bổ sung. Ảnh terminal không được đổi nhãn thành ảnh topology.
'''
write_new(E/'M2-core-stage1-final-evidence-index-20261031.md',index)
print(json.dumps({'report':str(report),'windows_free_MiB':memory['FreePhysicalMemoryKiB']/1024,'core_status':data['live_eve_node']['status'],'bundle_sha256':data['bundle-ready.json']['sha256'],'seed_sha256':data['seed-ready.json']['seed_sha256']}))
