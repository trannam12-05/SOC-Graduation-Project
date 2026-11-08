#!/bin/sh
# Bản chuẩn bị: chỉ chạy trên Employee-Linux sau khi được duyệt tạo/bật node.
# Không đổi mạng, renew DHCP, cài gói hoặc gửi lưu lượng Internet.
set -eu
hostname
ip -br -4 address
ip -4 route show
if command -v curl >/dev/null 2>&1; then
    curl --version
elif command -v python3 >/dev/null 2>&1; then
    python3 -c 'import ssl; print(ssl.OPENSSL_VERSION); print(ssl.get_default_verify_paths())'
else
    echo 'BLOCKED: chua co HTTPS client duoc xac minh' >&2
    exit 1
fi
