import hou
import os
import shutil
from datetime import datetime


def backup_hip_to_cache(node=None):
    """将当前 HIP 备份到 File Cache 或 ROP Alembic 的输出目录。"""
    if node is None:
        node = hou.pwd()

    # File Cache / Geometry ROP: sopoutput
    # ROP Alembic Output / Alembic ROP: filename
    file_parm = None
    for parm_name in ("sopoutput", "filename"):
        file_parm = node.parm(parm_name)
        if file_parm is not None:
            break

    if file_parm is None:
        print(
            f"Warning: 节点 {node.path()} 上找不到输出参数 "
            "'sopoutput' 或 'filename'，已跳过 HIP 备份。"
        )
        return None

    try:
        # 求值会解析路径中的 Houdini 变量和参数表达式。
        file_path = file_parm.evalAsString()
        if not file_path.strip():
            print(f"Warning: {file_parm.path()} 路径为空，已跳过 HIP 备份。")
            return None

        file_dir = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(file_dir, exist_ok=True)

        # 保留原逻辑：先保存当前工程，再复制；当前工程路径不变。
        hou.hipFile.save()
        hip_path = hou.hipFile.path()
        name, ext = os.path.splitext(os.path.basename(hip_path))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = os.path.join(file_dir, f"{name}_{timestamp}{ext}")
        shutil.copy2(hip_path, backup_path)

    except (hou.Error, OSError) as exc:
        message = f"HIP 备份失败（{node.path()}）：{exc}"
        print(message)
        if hou.isUIAvailable():
            hou.ui.displayMessage(message, severity=hou.severityType.Error)
        return None

    ## print(f"HIP 已备份至：{backup_path}")
    return backup_path


# 直接运行脚本时执行；作为模块 import 时，由 Pre-Render 显式调用。
if __name__ == "__main__":
    backup_hip_to_cache()