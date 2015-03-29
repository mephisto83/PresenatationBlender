bl_info = {
    "name": "Presentation Maker",
    "category": "Animation",
}

import bpy
import os.path
import json

class PresentationBlenderGUI(bpy.types.Panel):
    """Presentation GUI"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Movie"
    bl_label = "Generate Presentation"
 
    def draw(self, context):
        TheCol = self.layout.column(align=True)
        TheCol.prop(context.scene, "presentation_settings")
        TheCol.operator("object.presentation_blender_maker", text="Update")



class PresentationBlenderAnimation(bpy.types.Operator):
    """Presentation Blender Animation"""
    bl_idname = "object.presentation_blender_maker"
    bl_label = "Presentation Maker"
    bl_options = {'REGISTER', 'UNDO'}

    presentation_objects = []
    # total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        settings = context.scene.presentation_settings
        print(context.scene.presentation_settings)
        try:
            f = open(settings, 'r')
            filecontents = f.read()
            print(filecontents)
            obj = json.loads(filecontents)
            self.clearObjects()
            self.processAnimation(obj)
        except Exception as e:
            print("didnt work out") 
            print(e)
        print("Executing")
        #for i in range(self.total):
        #    obj_new = obj.copy()
        #    scene.objects.link(obj_new)

        #    factor = i / self.total
        #    obj_new.location = (obj.location * factor) + (cursor * (1.0 -
        #    factor))

        return {'FINISHED'}
    def processAnimation(self, config):
        print("processing animation")
        self.settings = self.loadSettings(config)
        self.scenes = self.loadSceneConfig(config)
        newobjects = self.createObjectsUsed()
        for i in range(len(newobjects)):
            self.presentation_objects.append(newobjects[i])
        self.processKeyFrames()
    def processKeyFrames(self):
        print("process key frames")
        for i in range(len(self.scenes)):
            scene = self.scenes[i]
            keyframes = scene["keyframes"]
            for k in range(len(keyframes)):
                keyframe = keyframes[k]
                #self.setFrame(keyframe)
                self.setObjectsProperty(keyframe)
    def setObjectsProperty(self, keyframe):
        print("set objects property")
        objects = keyframe["objects"]
        for i in range(len(objects)):
            obj = self.getObjectByName(objects[i]["name"])
            if obj == 0:
                print("object not found, thats not good!")
            else :
                self.setObjectProperty(obj, objects[i], keyframe["frame"])

    def setObjectProperty(self, obj, config, frame):
        print("set obj property")

        if config["position"]:
            pos = config["position"]
            if "x" in pos:
                obj["object"].location.x = pos["x"]
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
            if "y" in pos:
                obj["object"].location.y = pos["y"]
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
            if "z" in pos:
                obj["object"].location.z = pos["z"]
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)
            print("setting active object")
        if "scale" in config and config["scale"]: 
            scale = config["scale"] 
            if "x" in scale:
                obj["object"].scale.x = scale["x"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = scale["y"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = scale["z"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)
            
    def getObjectByName(self, name):
        print("get object by name")
        for i in range(len(self.presentation_objects)):
            obj = self.presentation_objects[i]
            if obj["name"] == name:
                return obj

        return 0

    def setFrame(self, keyframe):
        print("set frame")
        self.context.scene.frame_current = keyframe["frame"]    

    def createObjectsUsed(self):
        print("create objects used")
        objects = []
        objectnames = []
        for i in range(len(self.scenes)):
            print("createing objects for each scene")
            scene = self.scenes[i]
            keyframes = scene["keyframes"]
            for k in range(len(keyframes)):
                print("keyframe")
                keyframe = keyframes[k]
                keyframe_objects = keyframe["objects"]
                for j in range(len(keyframe_objects)):
                    obj = keyframe_objects[j]
                    print("check if count is zero")
                    count = objectnames.count(obj["name"])
                    if count == 0:
                        print("create Object for scene")
                        objectnames.append(obj["name"])
                        newobj = self.createObject(obj, scene["objects"])
                        objects.append(newobj)
        return objects

    def createObject(self, obj, scene_objects):
        print("create object")
        for i in range(len(scene_objects)):
            so = scene_objects[i]
            if so["name"] == obj["name"]:
                res = self.createObjectWithConfig(so)
                res["name"] = obj["name"]
                return res

    def createObjectWithConfig(self, scene_object_config):
        print("Create object with configuration")
        result = {}
        if(scene_object_config["type"] == "cube"):
            print("creating a cube")
            bpy.ops.mesh.primitive_cube_add(radius=1, location=(0, 0, 0))
            print("cube created")
            result["object"] = self.context.active_object
            print("got active object")
            result["mesh"] = self.context.active_object.data
            print("got active object mesh")
            return result
        elif scene_object_config["type"] == "text":
            print("creating text")
            bpy.ops.object.text_add()
            result["text"] = True
            result["object"] = self.context.active_object
            if "value" in scene_object_config:
                result["object"].data.body = scene_object_config["value"]
            result["mesh"] = self.context.active_object.data
            
            if "extrude" in scene_object_config and scene_object_config["extrude"]:
                result["object"].data.extrude = scene_object_config["extrude"]

            if "font" in scene_object_config:
                loaded = self.ensureFontLoaded(scene_object_config["font"])
                if loaded: 
                    font = self.getFont(scene_object_config["font"])
                    print("got font " + scene_object_config["font"])
                    if font != 0:
                        print("setting font ")
                        result["object"].data.font = font
            return result

    def getFont(self, fontname):
        print("get font")
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            print(font.name.lower())
            if font.filepath.lower() == self.getFontPath(fontname).lower():
                return font
        return 0

    def getFontPath(self, fontname):
        print("get font paths")
        fontlocation = "c:\\Windows\\Fonts\\"
        if "fonts" in self.settings:
            fontlocation = self.settings["fonts"]
        if os.path.isfile(fontlocation + fontname + ".ttf"): 
            return (fontlocation + fontname + ".ttf")
        return 0

    def ensureFontLoaded(self, fontname):
        print("ensure font loaded")
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            if font.name.lower() == fontname.lower():
                return True
        
        fontlocation = self.getFontPath(fontname)
        if os.path.isfile(fontlocation): 
            bpy.data.fonts.load(fontlocation)
            return True
        return False

    def loadSceneConfig(self, config):
        print("Load scene configs")
        return config["scenes"]

    def loadSettings(self, config):
        print("Loading settings")
        return config["settings"]

    def clearObjects(self):
        print("Clearing objects")
        print(self)
        print(self.presentation_objects)
        objlength = len(self.presentation_objects)
        print(" objects to remove")
        for i in range(objlength):
            obj = self.presentation_objects[i]
            obj["object"].select = True

        print("deleting objects")
        bpy.ops.object.delete()

        print("deleted objects")
        for i in range(objlength):
            obj = self.presentation_objects[i]
            print("removing meshes")
            if "text" in obj:
                bpy.data.curves.remove(obj["mesh"])
            else:
                bpy.data.meshes.remove(obj["mesh"])

        del self.presentation_objects[:]


def menu_func(self, context):
    self.layout.operator(PresentationBlenderAnimation.bl_idname)

# store keymaps here to access after registration
# addon_keymaps = []
def register():
    bpy.utils.register_class(PresentationBlenderAnimation)
    bpy.utils.register_class(PresentationBlenderGUI)
    bpy.types.Scene.presentation_settings = bpy.props.StringProperty \
      (name = "Movie settings",
        subtype = "FILE_PATH",
        description = "JSON description of the movie to generate")
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    #wm = bpy.context.window_manager
    #km = wm.keyconfigs.addon.keymaps.new(name='Object Mode',
    #space_type='EMPTY')
    #kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'SPACE', 'PRESS',
    #ctrl=True, shift=True)
    #kmi.properties.total = 4
    #addon_keymaps.append((km, kmi))
def unregister():
    bpy.utils.unregister_class(PresentationBlenderAnimation)
    del bpy.types.Scene.presentation_settings
    bpy.utils.unregister_class(PresentationBlenderGUI)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # handle the keymap
    #for km, kmi in addon_keymaps:
    #    km.keymap_items.remove(kmi)
    #addon_keymaps.clear()
if __name__ == "__main__":
    register()