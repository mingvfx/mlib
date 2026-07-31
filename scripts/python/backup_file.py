import hou
import os
import shutil
import time

def backup_hip_to_cache():
    # 1. 动态获取当前执行该脚本的节点
    # 如果是 HDA 按钮回调，推荐换成 node = kwargs['node']
    node = hou.pwd() 
    
    # 2. 安全获取参数
    file_parm = node.parm("sopoutput")
    if not file_parm:
        # 如果找不到参数，在控制台提示而不是抛出红字报错
        print(f"Warning: 节点 {node.path()} 上找不到 'sopoutput' 参数。")
        return

    file_path = file_parm.eval()
    if not file_path:
        print("Warning: 'sopoutput' 路径为空。")
        return

    # 3. 优雅地创建缓存目录
    file_dir = os.path.dirname(file_path)
    if file_dir:
        os.makedirs(file_dir, exist_ok=True)

    # 4. 保存当前工作流的 HIP 文件
    try:
        hou.hipFile.save()
    except hou.OperationFailed:
        hou.ui.displayMessage("保存当前 HIP 文件失败，请检查文件权限。", severity=hou.severityType.Error)
        return

    # 5. 生成带时间戳的备份文件名 (避免覆盖历史备份)
    # 例如: my_project_20260508_161716.hip
    hip_path = hou.hipFile.path()
    hip_basename = os.path.basename(hip_path)
    name, ext = os.path.splitext(hip_basename)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{name}_{timestamp}{ext}"
    
    backup_path = os.path.join(file_dir, backup_filename)

    # 6. 执行拷贝并捕获底层 IO 异常
    try:
        shutil.copy2(hip_path, backup_path)
        # 可选：如果你希望执行成功后有个视觉反馈，可以取消下面这行的注释
        # hou.ui.displayMessage(f"工程已成功备份至:\n{backup_path}")
    except IOError as e:
        hou.ui.displayMessage(f"拷贝文件时发生 IO 错误: {e}", severity=hou.severityType.Error)

# 执行函数
backup_hip_to_cache()