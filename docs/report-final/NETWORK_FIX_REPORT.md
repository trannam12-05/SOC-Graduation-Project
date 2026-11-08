# 1. Báo cáo sửa phần Nam — Network & OPNsense

File gốc: `D:\SOC\BÁO CÁO SOC.docx`. File xuất: `BAO_CAO_SOC_DA_SUA.docx`. File gốc không ghi đè; backup nguyên byte ở `D:\SOC\temp\network-report-review\BAO_CAO_SOC.original.docx` (không xuất bản Git).

SHA-256 gốc: `0EE4C096C29C28CFCEAF4E455301222023F1CE6BD04A16BE5C36E30AF0AFE329`.

## 1.1. Nội dung đã sửa

| Mục | Thay đổi | Vị trí Word sau cập nhật |
|---|---|---|
|2.1.1,2.1.11|Phân biệt topology đầu vào nhiều switch với lab một Core; sửa quy hoạch thực tế thành30/40/50/60/99, VIP .1/.2/.3|Tra mục lục tự động|
|2.1.12|Đổi Bảng2.11 truy vết Nam thành Bảng2.3a; giữ Bảng2.11 tích hợp của phần khác|Trước mục2.2|
|2.2.1, Hình2.3–2.3e|Dựng sáu sơ đồ nền trắng chữ đen; một Core OVS, trunk vtnet0, VLAN60, state/policy và nguồn Mirror đúng|Mục2.2.1:trang52; Hình2.3a:trang54|
|Bảng2.4|Quy hoạch VLAN/subnet/CARP và IP riêng theo nghiệm thu|Trang56|
|Bảng2.4a–c|Bổ sung mapping, ma trận luồng đã thử và giới hạn HA/Mirror; sửa tham chiếu trong truy vết|Sau Bảng2.4|
|2.2.2–2.2.6|Giải thích VLAN/access/trunk/routing; LACP chưa triển khai; OVS Mirror ingressens3–ens9→ens10|Mục2.2|
|2.2.7–2.2.11|Cập nhật failover/recovery, một TCP, CARP/pfsync/XMLRPC, DHCP/DNS và một HTTPS SNAT; không nâng zero loss/NAT HA/lease HA|Mục2.2.7:trang60|
|2.2.12–2.2.18|DMZ60; OPNsense_3 và Wi-Fi là thiết kế; Management chỉ kiểm ICMP VIP; HA toàn SOC chưa đạt|Mục2.2|
|2.8.3|Nêu rõ Nam cung cấp nền phân vùng/gateway/HA/Mirror cho SOC và điểm API M5; giữ phân công Tùng/Minh/Thắng|Tra mục lục tự động|
|3.2.2/Bảng3.4|Bỏ cách ghi PASS theo checklist chưa có nguồn; thay bằng ca M2/M3 có bằng chứng; tách caption3.2c bị dính đoạn văn|Bảng3.4:trang149|
|3.2.7.3|Giữ kết quả M3; làm rõ runtime8UUID thuộc rule, ba pool là cấu hình|Trang169|
|3.2.7.4|Giữ sensor live/replay và M4 PARTIAL/BLOCKED; sửa kiểm kê node EVE so với VMware|Trang172|
|3.4.1,3.4.3,3.4.7|Đồng bộ riêng các kết luận Network mâu thuẫn; giữ luận điểm AI/Automation|Tra mục lục tự động|

Các số trang trên là vị trí vật lý Word được đọc từ bản đã cập nhật; nhãn/số trang in theo section có thể khác nếu mẫu gốc dùng cách đánh số riêng. Mục lục và danh mục trong DOCX là nguồn tra cứu cuối.

## 1.2. Định dạng và đánh số

Giữ nguyên mẫu gốc, bìa, danh sách nhóm, style hiện hữu, lề, header/footer và nội dung thành viên khác. Chỉ bổ sung hai style caption để cập nhật danh mục hình/bảng; giữ định dạng trực tiếp của chú thích. Không đánh lại toàn bộ bảng2.5 trở đi: sửa riêng số trùng ở bảng Nam bằng hậu tố2.3a, thêm2.4a/b/c đúng ngữ cảnh.

Các bảng Nam được giới hạn theo vùng in của mẫu gốc và lặp hàng tiêu đề; không thay định dạng tất cả bảng AI/SOC/Automation. Sáu sơ đồ được chèn theo đúng tỷ lệ; ảnh thực nghiệm cũ không chỉnh pixel. Danh mục hình/bảng trước đây là danh sách tay đã chuyển thành trường tự động; mục lục Heading tiếp tục dùng trường tự động của mẫu.

## 1.3. Phạm vi chưa sửa hoặc chưa kết luận

- Không thay ảnh topology gốc Hình2.1 hoặc đổi mọi chữ VLAN10 máy móc: chúng là bối cảnh đầu vào, có thuyết minh phân biệt với lab60.
- Không sửa mô hình AI, ELK, Wazuh/Mock và số liệu của Thắng, Minh, Tùng. Chỉ sửa tham chiếu/đóng góp Network và kết luận trực tiếp mâu thuẫn state HA.
- Không bổ sung kết quả NAT HA, lease HA, zero loss, RTO, API blockIP hoặc live pipeline chưa có nghiệm thu.
- Sơ đồ SVG là tệp vector chỉnh sửa được; bản hiển thị trong DOCX dùng PNG tương ứng để giữ tương thích mẫu Word. Không tuyên bố các nhãn trong PNG là shape Word riêng lẻ.
- Backup và dữ liệu trung gian ở `temp/` được giữ cục bộ, không commit. Không cung cấp PDF: tác vụ xuất toàn bộ không hoàn tất; bản DOCX đã lưu được kiểm tra trực tiếp bằng Word.

## 1.4. Kiểm tra cuối

Microsoft Word mở DOCX bình thường, lưu thành công và cập nhật ba mục lục/danh mục tự động. Kết quả: 226 trang, 50 ảnh inline, 89 bảng. Không phát hiện số hiệu trùng trong các caption hình/bảng thực tế (không tính lần lặp trong danh mục).

Đối chiếu 1.713 đoạn/bảng có chữ ngoài phạm vi sửa: giữ đủ nội dung sau chuẩn hóa khoảng trắng. Chín ảnh thực nghiệm Hình 3.17–3.25 giữ nguyên byte. Hash bản gốc khớp backup; bản gốc không thay đổi. Chi tiết tại [validation.json](images/validation.json).

Bốn ảnh chụp thật cửa sổ Word bằng PrintWindow và thời điểm UTC+07:00 được ghi ở [screenshot-index.csv](images/screenshot-index.csv). Đây là kiểm tra các trang trọng điểm, không phải tuyên bố đã duyệt trực quan toàn bộ 226 trang. Giữ nguyên định dạng của thành viên khác; các hạn chế có sẵn của mẫu ngoài phạm vi Nam không được tự sửa.

Git chỉ stage các đầu ra an toàn của đợt này và mã xử lý liên quan. Không add file báo cáo gốc hoặc các minh chứng local đã bị loại từ đợt trước. Không force push; nếu phát hiện xung đột hoặc remote đi trước, dừng push và ghi rõ.
