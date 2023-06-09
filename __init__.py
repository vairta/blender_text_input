# -*- coding: UTF-8 -*-

# 引入所需库
import bpy
from bpy.types import Operator, PropertyGroup, UIList, Panel
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty
from typing import Collection
import os, platform

# 插件管理面板信息
bl_info = {
    "name": "text input",
    "author": "vairta",
    "version": (0, 1, 1),
    "blender": (2, 93, 0),
    "location": "3d Viewport > Create Panel",
    "description": "快捷的添加、输入和编辑（中文）文字对象",
    "warning": "测试版，Linux、Mac未经过测试，可点击下方文档查看更新及反馈BUG",
    "doc_url": "https://github.com/vairta/blender_text_input",
    "tracker_url": "https://github.com/vairta/blender_text_input/issues",
    "wiki_url": "https://github.com/vairta/blender_text_input",
    "category": "Mesh",
}

def font_poll(self, object):
    return object.field and object.field.type =='FONT'

# 系统字体路径
info = platform.system().lower()
if info == "windows":
    font_fol = os.getenv("SystemRoot") + "\\Fonts"
    font_def = "msyh.ttc"
elif info == "linux":
    font_fol = "/usr/share/fonts/"
    font_def = None
else:
    font_fol = "/System/Library/Fonts"
    font_def = "PingFang.otf"


#  获取字体列表
def getList():
    fontsls = []
    list = os.listdir(font_fol)
    for i in list:
        count = 0
        path = os.path.join(font_fol,i)
        if os.path.isfile(path):
            fileExtension = os.path.splitext(path)[-1].lower()
            if fileExtension != ".fon":
                id = str(i)
                name = str(i[:-4])
                description = str(i)
                fontsls.append((id, name, description))
                count += 1
    return fontsls

# 设置字体
class TextinSet(bpy.types.Operator):
    bl_idname = "textin.setfont"
    bl_label = "字体列表"
    bl_description = "选择和设置字体\n当前"
    bl_property = "font_list"

    fonts = getList()
    font_list: EnumProperty(
        items = fonts
    )

    def execute(self, context):
        fontName = self.font_list
        fontPath = os.path.join(font_fol, fontName)
        fontFile = bpy.data.fonts.load(filepath = fontPath)
        allFonts = bpy.data.fonts
        for i in range(len(allFonts)):
            if allFonts[i].name == fontFile.name:
                bpy.context.active_object.data.font = allFonts[i]
            else:
                bpy.context.active_object.data.font = fontFile
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

# 追加换行
class TextinWra (bpy.types.Operator):
    bl_idname = "textin.wrap"
    bl_label = "插入换行符"
    bl_description = "在尾部插入换行符"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        bpy.context.active_object.data.body += "\n"
        return {'FINISHED'}

# 竖排文字
class TextinVer(bpy.types.Operator):
    bl_idname = "textin.vertical"
    bl_label = "改为竖向文字"
    bl_description = "改为竖向文字"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ob = context.active_object
        txt = ob.data.body[:]
        textArray = ob.data.body.split("\n")
        maxLength = 0
        for i in textArray:
            if len(i) > maxLength:
                maxLength = len(i)
        for i, v in enumerate(textArray):
            diff = maxLength - len(v)
            textArray[i] += ("\x20" * diff) #中文空格
        verticalArray = zip(*reversed(textArray))
        verticalStr = ""
        for i, val in enumerate(verticalArray):
            _t = ""
            for j in val:
                _t += j
            verticalStr += _t + "\n"
        verticalStr = verticalStr[:-1]
        ob.data.body = verticalStr
        ob.data.align_x = "RIGHT"
        return {'FINISHED'}

# 添加文字对象
class TextinAdd(bpy.types.Operator):
    bl_idname = "textin.add"
    bl_label = "添加文字对象"
    bl_description = "添加文字对象"

    def execute(self, context):
        # 添加文字对象
        bpy.ops.object.text_add(
            enter_editmode = False, 
            align = 'WORLD', 
            location = (0, 0, 0)
            )
        # 设置系统默认字体
        fontPath = os.path.join(font_fol, font_def)
        fontFile = bpy.data.fonts.load(filepath = fontPath)
        bpy.context.active_object.data.font = fontFile
        # 设置内容
        context.object.data.body = "文字内容"
        return {'FINISHED'}

# print test
def CustProps():
    print("TEST")

# 字体样式
class FontStyle(bpy.types.PropertyGroup):
    # 默认样式
    word: bpy.props.StringProperty(
        name = "word", 
        default = "文字内容"
        )
    # 字体对象扩展属性
    fontwidth: bpy.props.FloatProperty(
        name = "fontwidth", 
        type= bpy.types.TextCurve, 
        min = 0, 
        max = 1, 
        default = 1.0, 
        update = CustProps(), 
        )

# UI
class Textin_UI(bpy.types.Panel):
    bl_label = "创建文字"
    # bl_description = "快捷的添加、输入和编辑（中文）文字对象"
    bl_idname = "_PT_textin_PT_"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Create"
    # bl_context = "data"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        # 添加文本
        row = layout.row()
        row.scale_y = 1.5
        # 原生API
        # row.operator("object.text_add", text="添加文本对象", icon="OUTLINER_OB_FONT")
        # 自定义方法
        row.operator("textin.add", text="添加文字对象", icon="OUTLINER_OB_FONT")
        @classmethod
        def poll(cls, context):
            active = bpy.context.active_object
            if active is not None:
                active_type = active.type
            else:
                active_type = ""
            return active_type=='FONT'

        fontname = context.active_object.data.font.name
        # 编辑内容
        layout.label(text=" 编辑文字内容:")
        row = layout.row()
        row.scale_y = 3.0
        # 原生API
        row.prop(obj.data, "body", text="", expand=True)
        # 排版字符
        row = layout.row(align=True)
        row.operator("textin.vertical", text="横排")
        row.operator("textin.vertical", text="竖排")
        sub = row.row()
        sub.scale_x = 2.0
        sub.operator("textin.wrap", text="追加换行")
        # 设置字体
        row = layout.row()
        layout.label(text=" 字体:")
        box = layout.box()
        box.scale_y = 1.5
        box.operator("textin.setfont", text = fontname)
        row = layout.row(align=True)
        row.prop(obj.data, "size", text="大小")
        row.prop(obj.data, "extrude", text="厚度")
        # 两栏
        split = layout.split()
        col = split.column(align=True)
        # col.label(text="字间距行间距:")
        col.prop(obj.data, "space_character", text="字距")
        col.prop(obj.data, "space_line", text="行距")
        col = split.column(align=True)
        # col.label(text="字宽字高:")
        col.prop(obj.data, "shear", text="倾斜")
        # col.prop(obj.data, "fontwidth", text="字宽")
        # col.prop(context.active_object.data, "scale[1]", text="字高")
        # 对齐
        # row = layout.row()
        # layout.label(text=" 对齐:")
        # row = layout.row(align=True)
        # row.scale_y = 1.5
        # row.operator("bpy.context.object.data.align_x", "LEFT", text="左")
        # row.operator("bpy.context.object.data.align_x", "RIGHT", text="右")
        # row.operator("bpy.context.object.data.align_x", "CENTER", text="居中")
        # row.operator("bpy.context.object.data.align_x", "FLUSH", text="分散")

classes = [
    TextinSet, 
    TextinWra, 
    TextinVer, 
    TextinAdd,
    # FontStyle,
    Textin_UI
]

def register():
    for cl in classes:
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)

if __name__ == "__main__":
    register()
