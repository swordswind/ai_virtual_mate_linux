import serial.tools.list_ports


def list_available_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("未发现可用串口设备。")
        return
    print("发现以下串口设备：")
    print("-" * 50)
    print("{:<12} {:<20} {:<20}".format("端口", "描述", "硬件ID"))
    print("-" * 50)
    for port in ports:
        try:
            # 获取端口信息
            port_name = port.device
            port_description = port.description
            port_hwid = port.hwid
            # 处理常见设备类型
            if 'USB' in port_hwid:
                device_type = "USB 串口设备"
            elif 'Bluetooth' in port_description:
                device_type = "蓝牙串口"
            elif 'COM' in port_name and port_name.startswith('COM'):
                device_type = "传统串口"
            else:
                device_type = "未知类型"
            print(f"{port_name:<12} {port_description[:20]:<20} {port_hwid[:20]:<20}")
            print(f"  └─ 设备类型: {device_type}")
            # 尝试获取额外信息
            if hasattr(port, 'product') and port.product:
                print(f"  └─ 产品: {port.product}")
            if hasattr(port, 'manufacturer') and port.manufacturer:
                print(f"  └─ 制造商: {port.manufacturer}")
            if hasattr(port, 'vid') and port.vid:
                print(f"  └─ VID:PID = {port.vid:04x}:{port.pid:04x}")
            print("-" * 50)
        except Exception as e:
            print(f"获取端口 {port.device} 信息时出错: {e}")
            print("-" * 50)


list_available_ports()
