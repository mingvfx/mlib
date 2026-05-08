import hou

def MlibSetColor():
    for n in hou.selectedItems():
        # set null shape and color
        #n.setUserData("nodeshape", "squared")
        col=(1,0,0);
        n.setColor(hou.Color(col));
        
def MlibCreateShotSetup():
    obj_level = hou.node("/obj")
    mlibshotsetup = obj_level.createNode("Mlib_ShotSetup")
        

def _create_out_null(parent, item, port_index, total_ports):
    """
    内部辅助函数：专门用来生成 Null 节点并处理连线
    """
    suffix = f"_{port_index}" if total_ports > 1 else ""
    
    # 获取节点名字，并剥除开头的下划线（处理 __dot1 变成 dot1 的情况）
    clean_name = item.name().lstrip('_')
    
    # 组合名字，确保只有一个下划线
    null_name = f"Out_{clean_name}{suffix}"
    
    # 创建节点
    null = parent.createNode('null', null_name)
    
    # 计算位置
    pos = item.position()
    offset_x = (port_index - (total_ports - 1) / 2.0) * 1.5 if total_ports > 1 else 0
    
    # 针对 Dot 节点做特殊偏移微调
    if item.networkItemType() == hou.networkItemType.NetworkDot:
        offset_x -= 0.5 
        
    null.setPosition(hou.Vector2(pos[0] + offset_x, pos[1] - 1.0))
    
    # 外观设置
    null.setUserData("nodeshape", "squared") 
    if hasattr(item, "color"): 
        null.setColor(item.color())
        
    # --- 区分 Node 和 Dot 获取连线的方式 ---
    connections_to_reconnect = []
    if item.networkItemType() == hou.networkItemType.NetworkDot:
        # Dot 没有多个端口，直接获取所有连线
        connections_to_reconnect = item.outputConnections()
    elif item.networkItemType() == hou.networkItemType.Node:
        # Node 按特定端口抓取连线
        if port_index < len(item.outputConnectors()):
            connections_to_reconnect = item.outputConnectors()[port_index]
            
    # 输出重定向
    for conn in connections_to_reconnect:
        out_node = conn.outputNode()
        out_item = conn.outputItem()
        input_idx = conn.inputIndex()
        
        if out_node:
            out_node.setInput(input_idx, null)
        elif isinstance(out_item, hou.NetworkDot):
            out_item.setInput(input_idx, null)
                
    # --- 区分 Node 和 Dot 设置输入的方式 ---
    if item.networkItemType() == hou.networkItemType.NetworkDot:
        null.setInput(0, item) # Dot 不需要传递 port_index
    else:
        null.setInput(0, item, port_index)
        
    null.setSelected(True)
    
    return null


def mlib_create_null_objm():
    selected_items = hou.selectedItems()
    if not selected_items:
        return 

    with hou.undos.group("Create Nulls and Object Merges"):
        for item in selected_items:
            parent = item.parent()
            item.setSelected(False) 
            item_type = item.networkItemType()

            # --- 场景 1: 选中的是 NetworkDot ---
            if item_type == hou.networkItemType.NetworkDot:
                _create_out_null(parent, item, port_index=0, total_ports=1)
                continue 

            # --- 场景 2: 选中的是 Node ---
            if item_type == hou.networkItemType.Node:
                if item.type().name() != "null":
                    num_ports = max(1, len(item.outputConnectors()))
                    for port_index in range(num_ports):
                        _create_out_null(parent, item, port_index, num_ports)
                        
                else:
                    objm = parent.createNode('object_merge', f"OBJM_{item.name()}")
                    pos = item.position()
                    objm.setPosition(hou.Vector2(pos[0], pos[1] - 1))
                    
                    objm.parm("objpath1").set(item.path())
                    objm.parm("xformtype").set(1) 
                    
                    shape = item.userData("nodeshape") or "rect"
                    objm.setUserData("nodeshape", shape) 
                    objm.setColor(item.color())
            
                    objm.setSelected(True)
                    objm.setRenderFlag(True)
                    objm.setDisplayFlag(True)

def MlibExtractPath():
    # get path attribute name
    button_index,text= hou.ui.readInput("Attribute Name(primitive)", buttons=("OK", "Cancel"))
    # print(button_index)
    # print(text)


    # get current nodes
    currentNodes = hou.selectedNodes() 
    # print(currentNode)

    for i in currentNodes:

        # col = (0.5,0.5,0.5)
        # i.setColor(hou.Color(col))
        
        nodepath = i.path() # get path
        root = i.parent().path() # get root
        # print(root)
        nodepos = i.position() # get current node position
        # print(nodepos)
        
        pathAttcode = i.geometry().findPrimAttrib(text) # get path attribute
        pathAtt = []
        
        if pathAttcode :
            for path in pathAttcode.strings() :
                # print(path)
                pathAtt.append(path) # get all uniuqe attributes List
            # print(pathAtt)
            
        for ib in range(len(pathAtt)):
            # print(ib)
            # print(pathAtt[ib])
            
            name = pathAtt[ib].split("/") # get name
            # print(name[-1])
            name_fix = name[-1].replace(":", "_") 
            # fix name from ":" to "_", otherwise node name will be error
            
            # create blast
            blast = hou.node(root).createNode("blast","ExtraPath_" + name_fix)
            
            blast.setPosition(hou.Vector2(nodepos[0]+ib*3,nodepos[1]-1))
            blast.setInput(0, i)
            
            blast.parm("group").set("@" + text + "=" + pathAtt[ib])
            blast.parm("negate").set(1)
            
            # create null
            null = blast.createOutputNode("null","Out_ExtraPath_" + name_fix)
            
            null.setGenericFlag(hou.nodeFlag.DisplayComment,True)
            null.setComment(name[-1])
            
            
        

def MlibCreateGeo():
    #if tord==0:
    create=[]
        
    #choose nodes to run script
    for n in hou.selectedNodes():

        geos=hou.node('/obj').createNode('geo','{0}'.format(n.name()))
        
        objmerge=geos.createNode('object_merge','{0}'.format(n.name()))
        objmerge.parm('xformtype').set(1)
        objmerge.parm('objpath1').set(n.path())
       
        #create geo col
        col=(.5,0,1)
        geos.setColor(hou.Color(col))
        
        father=n.parent()
        pos=father.position()
        
        
        create.append(geos)
        
        # set position of each geo node
        for i in range(len(create)):
           geos.setPosition(hou.Vector2(pos[0]+i*3,pos[1]-4))
        
        # go back to obj level
        pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        pane.setPwd(hou.node("/obj"))
        
        # select new node
        for i, n in enumerate(create):
            n.setSelected(True, clear_all_selected=(i == 0))
            
            
            
            
def MlibGeoToRs():

    # def find_cameras(node):
    #     cameras = []
    #     if node.type().name() == "cam":
    #         cameras.append(node.path())
    #     # 遍历子节点
    #     for child in node.children():
    #         cameras.extend(find_cameras(child))
    #     return cameras
    # # 获取 /obj 层级下的所有相机，包括子层级
    # obj_node = hou.node("/obj")
    # all_cameras = find_cameras(obj_node)
    # 输出所有相机路径
    # print(all_cameras)
    # print(len(all_cameras)!=0)
    create=[]
    #choose  nodes to render
    for n in hou.selectedNodes():
        # print(n)# 在选中节点下创建ROP网络（若不存在）
        # 在ROP网络中创建Redshift渲染节点
        rs_render = hou.node("/out").createNode("Redshift_ROP","rndr_" + "{0}".format(n.name()))
        # 设置基本渲染参数（示例）
        rs_render.parm("trange").set("on")
        # if(len(all_cameras)!=0):
            # rs_render.parm("RS_renderCamera").set(all_cameras[0])    # 指定渲染相机
        rs_render.parm("RS_outputFileNamePrefix").set("$HIP/render/v001/$OS/$OS.$F4.exr")  # image输出路径
        rs_render.parm("RS_archive_file").set("$HIP/rop/v001/$OS/$OS.$F4.rs")  # proxy输出路径
        #rs_render.parm("RS_archive_enable").set(True)
        rs_render.parm("RS_objects_candidate").set("")  # object
        rs_render.parm("RS_objects_force").set("{0}".format(n.name()))
        rs_render.parm("RS_lights_candidate").set("")  # light
        rs_render.setCurrent(True,True)
        create.append(rs_render)
        pos=(0,0,0)
        for i in range(len(create)):
            rs_render.setPosition(hou.Vector2(pos[0]+i*3,pos[1]-6))
    hou.ui.setStatusMessage(" Redshift node creation is complete and has been associated to the selected nodes ")
    # hou.ui.displayMessage("Redshift节点创建完成并已关联到: {}".format(n.name()))
    
    
    
def MlibExtractGroups():
    # 1. 获取当前选择的节点
    selected_nodes = hou.selectedNodes()
    
    if not selected_nodes:
        hou.ui.displayMessage("(Please select a node first).")
        return

    node = selected_nodes[0]
    parent = node.parent()
    geo = node.geometry()
    
    if not geo:
        hou.ui.displayMessage("(Selected node has no geometry).")
        return
        
    # --- 布局参数 ---
    base_pos = node.position()
    start_x = base_pos.x()
    start_y = base_pos.y()
    
    # 间距设置
    x_gap = 2.0  # 水平间距
    y_gap = 1.0  # 垂直间距 (Blast 在源节点下方多少)
    
    # 组计数器 (用来计算向右偏移的倍数)
    group_counter = 0
    
    # set color
    color_A = hou.Color((0.4, 0.5, 0.7))   # Point Group 颜色
    color_B = hou.Color((0.7, 0.5, 0.3)) # Primitive Group 颜色
    
    # 用于收集新创建的节点以便后续排版
    created_nodes = []

    # 定义一个内部函数来创建 Blast 和 Null
    def create_extract_setup(group_name, group_type_val, index, node_color):
        # 计算坐标
        # 第一个节点(index=0) X轴不变，后续每增加一个，X轴增加 x_gap
        current_x = start_x + (index * x_gap)
        
        blast_pos_y = start_y - y_gap
        null_pos_y = start_y - (y_gap * 2) # Null 再往下挪一个单位
        
        # group_type_val: 1 for Points, 2 for Primitives
        
        # 创建 Blast 节点
        blast = parent.createNode("blast", f"blast_{group_name}")
        blast.setInput(0, node)
        blast.parm("group").set(group_name)
        blast.parm("grouptype").set(group_type_val) # 设置组类型 (点或面)
        blast.parm("negate").set(1) # 勾选 Delete Non Selected (保留组)
        
        # 设置 Blast 位置
        # blast.setColor(node_color)
        blast.setPosition(hou.Vector2(current_x, blast_pos_y))
        
        
        # 创建 Null 节点
        null_node = parent.createNode("null", f"OUT_{group_name}")
        null_node.setInput(0, blast)
        
        # 设置 Null 节点的颜色 (例如黑色/深灰色，方便识别)
        null_node.setColor(node_color)
        null_node.setUserData("nodeshape", "squared") 
        
        # 设置 Null 位置 (X轴与Blast对齐，Y轴更靠下)
        null_node.setPosition(hou.Vector2(current_x, null_pos_y))
        
        # 
        created_nodes.append(blast)
        created_nodes.append(null_node)

    # 2. 遍历所有的 Primitive Groups (面组)
    for group in geo.primGroups():
        create_extract_setup(group.name(), 4, group_counter, color_B)
        group_counter += 1

    # 3. 遍历所有的 Point Groups (点组)
    for group in geo.pointGroups():
        create_extract_setup(group.name(), 3, group_counter, color_A)
        group_counter += 1
        

    # 4. print text
    if created_nodes:
        print(f"already extract {len(created_nodes)//2} groups")
    else:
        print("X(No groups found).")
