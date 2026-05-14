<#
.SYNOPSIS
    WSL에 카메라 USB 재연결 (usbipd-win)

.DESCRIPTION
    BUSID를 받아 usbipd detach 후 --wsl로 다시 attach한다.

    BUSID 찾는 법 (PowerShell):
        usbipd list
    출력에서 카메라 디바이스(예: "USB Video Device", "UVC Camera") 행의
    BUSID 컬럼 값(예: 2-5)을 인자로 전달한다.

    참고:
    - detach 는 관리자 권한이 필요할 수 있다.
    - attach --wsl 는 사전에 'usbipd bind --busid X-X' (관리자 권한)이
      한 번 실행되어 있어야 한다.

.PARAMETER BusId
    USB BUSID (예: 2-5)

.EXAMPLE
    .\camera_usb_reattach.ps1 2-5
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$BusId
)

usbipd detach --busid $BusId
usbipd attach --wsl --busid $BusId
