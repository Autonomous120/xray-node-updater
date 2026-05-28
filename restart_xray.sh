#!/bin/bash

echo "========== Xray 重启脚本 =========="
echo ""

# 1. 停止服务
echo "[1/3] 正在停止 Xray..."
systemctl --user stop xray

# 2. 等待服务完全停止（最多等待10秒）
echo "[2/3] 等待服务完全关闭..."
for i in {1..10}
do
    sleep 1
    STATUS=$(systemctl --user is-active xray)
    if [ "$STATUS" == "inactive" ]; then
        echo "✔ Xray 已完全停止"
        break
    fi

    if [ $i -eq 10 ]; then
        echo "⚠ 停止超时，尝试继续启动"
    fi
done

# 3. 启动服务
echo ""
echo "[3/3] 正在启动 Xray..."
systemctl --user start xray

# 稍微等一下再检查状态
sleep 2

# 4. 检查状态
STATUS=$(systemctl --user is-active xray)

echo ""
echo "========== 状态检查 =========="

if [ "$STATUS" == "active" ]; then
    echo "✔ Xray 启动成功，当前状态：RUNNING"
else
    echo "✖ Xray 启动失败，当前状态：$STATUS"
    echo ""
    echo "详细状态如下："
    systemctl --user status xray
fi

echo ""
echo "================================"
echo "按任意键退出..."
read -n 1
