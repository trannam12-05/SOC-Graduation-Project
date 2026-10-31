# Nhap mat khau chi trong TTY SSH; khong Start-Transcript/khong log input.
$Host.UI.RawUI.WindowTitle = 'SOC M2 - Secure Core console password'
Write-Host 'Nhap mat khau console moi truc tiep o cua so nay. Khong gui vao chat.'
& ssh.exe -tt -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 -i "$env:USERPROFILE\.ssh\eve-ng-root-ed25519" root@192.168.220.143 python3 /opt/unetlab/soc-core-preparation-20261031/create_core_seed_interactive.py
Write-Host 'Phien nhap mat khau da ket thuc. Khong dan mat khau/hash vao chat.'
