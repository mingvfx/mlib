import hou
import os, shutil,time
# file_path获取缓存文件的绝对路径
file_parm = hou.parm("sopoutput")
file_path = file_parm.eval()
# 判断缓存目录是否存在
file_dir = os.path.dirname(file_path)
if(os.path.exists(file_dir)==0):
    os.makedirs(file_dir)
# 保存并将hip文件拷贝到缓存目录下
hou.hipFile.save()
hip_path = hou.hipFile.path()
shutil.copy2(hip_path, file_dir)
