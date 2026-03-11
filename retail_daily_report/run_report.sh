#!/bin/bash
# 零售日报启动脚本 - 自动选择最佳Python环境

cd "$(dirname "$0")"

# 尝试不同的Python路径
PYTHON_PATHS=(
    "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    "/usr/local/bin/python3"
    "/usr/bin/python3"
)

PYTHON=""
for p in "${PYTHON_PATHS[@]}"; do
    if [ -x "$p" ]; then
        PYTHON="$p"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "$(date): 错误 - 未找到可用的Python" >> logs/launchd_stderr.log
    exit 1
fi

echo "$(date): 使用Python: $PYTHON" >> logs/launchd_stdout.log

# 执行主程序
exec "$PYTHON" main.py --send-now 2>> logs/launchd_stderr.log >> logs/launchd_stdout.log
