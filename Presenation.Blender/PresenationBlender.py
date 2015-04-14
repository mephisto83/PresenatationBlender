
bl_info = {
    "name": "Presentation Maker",
    "category": "Animation",
}

import math
import mathutils
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
    
    presentation_armatures = []
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
            self.clearObjects()
        except Exception as e:
            print(e)
        try:
            f = open(settings, 'r')
            filecontents = f.read()
            
            obj = json.loads(filecontents)
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
        self.armatures = self.loadArmaturesConfig(self.scenes[0])
        newobjects = self.createObjectsUsed()
        self.createStage()
        
        for i in range(len(newobjects)):
            self.presentation_objects.append(newobjects[i])
        self.parentCreatedObjects()
        self.configureArmature()
        self.processSettings()
        self.processArmatures()
        self.processKeyFrames()
    def processSettings(self):
        print("Process settings")
        if "RenderEngine" in self.settings:
            print("set render engine")
            self.context.scene.render.engine = self.settings["RenderEngine"]
        if "Materials" in self.settings:
            print("setup materials")
            matsettings = self.settings["Materials"]
            mat_location = matsettings["File"]

            material_locator = "\\Material\\"  
            for i in range(len(matsettings["Names"])):
                matname = matsettings["Names"][i]
                opath = mat_location

                print(matname)
                print(opath)
                with bpy.data.libraries.load(opath) as (data_from, data_to):
                    data_to.materials = [name for name in data_from.materials if not self.hasMaterialByName(name)]
    def hasGroupByName(self, name):
        print("has group by name")
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                print("found group")
                return True
        print("group not found")
        return False
    def getGroupByName(self, name):
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                return group
        return group
    def hasMaterialByName(self, name):
        print("has materials by name")
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return True
        return False
    def getMaterialByName(self,name):
        print("has materials by name")
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return material
        return None

    def processArmatures(self):
        print("process armatures")
        #self.presentation_armatures.append({"bone_chains":bone_chains,"armature"
        #: armature, "rig":rig})
        bpy.ops.object.mode_set(mode='OBJECT')
        if len(self.presentation_armatures) > 0 :
            bpy.ops.object.mode_set(mode='POSE')
            print(len(self.presentation_armatures))
            for i in range(len(self.presentation_armatures)):
                bone_chains = self.presentation_armatures[i]["bone_chains"]
                armature = self.presentation_armatures[i]["armature"]
                config = self.presentation_armatures[i]["configuration"]
                print("armature chains")
                print("len(self.presentation_armatures)")
                print(len(self.presentation_armatures))
                print(i)
                chains = self.armatures[i]["chain"]
                print("has armature chains")
                rig = self.presentation_armatures[i]["rig"]
                scn = self.context.scene
                print("setting active to rig")
                scn.objects.active = rig
                self.arrangeArmature(bone_chains, config, chains)
            
        bpy.ops.object.mode_set(mode='OBJECT')
           

    def arrangeArmature(self, bone_chains,  config, chains):
        print("setting to POSE mode")
        print("arrange armature") 
        arrange = "spiral"
        if "arrange" in config:
            arrange = config["arrange"]

        count = 0
        thresh = 0
        print("for each bone in chain")
        if arrange == "spiral":
            for j in range(len(bone_chains)):
                bone_chain = bone_chains[j]
                chain = chains[j]
                if count == thresh:
                    rig.pose.bones["bone.chain." + chain].rotation_quaternion[3] = 1
                    count = 0
                    thresh = thresh + 1
                count = count + 1
        elif arrange == "line":
            print("arrange line")
    def configureArmature(self):
        print("armatures")
        
        if self.armatures:
            print("foreach armature config")
            for i in range(len(self.armatures)):
                armatureConfig = self.armatures[i]
                print("new armature()")
                armature = bpy.data.armatures.new(armatureConfig["name"])
                print("new rig()")
                rig = bpy.data.objects.new("Rig$" + armatureConfig["name"], armature)
                if "origin" in armatureConfig:
                    rig.location = [armatureConfig["origin"]["x"],armatureConfig["origin"]["y"],armatureConfig["origin"]["z"]]
                else :
                    rig.location = [0,0,0]
                rig.show_x_ray = True
                armature.draw_type = "STICK"
                armature.show_names = True
                scn = self.context.scene
                scn.objects.link(rig)
                scn.objects.active = rig
                print("update scene")
                scn.update()
                
                bpy.ops.object.mode_set(mode='EDIT')
                chains = armatureConfig["chain"]
                bone_chains = []
                grid = {"x":1,"y":1,"z":1}
                if "grid" in armatureConfig:
                    grid = armatureConfig["grid"]
                if "x" in grid:
                    print("x in grid")
                else:
                    print("no x in grid")
                x_grid = grid["x"]
                last_bone = False
                for j  in range(len(chains)):
                    chain = chains[j]
                    bone_chain = armature.edit_bones.new("bone.chain." + chain)
                    bone_chains.append(bone_chain)
                    bone_chain.head = (j * x_grid,0,0)
                    bone_chain.tail = ((j + 1) * x_grid,0,0)
                    if last_bone:
                        bone_chain.parent = last_bone
                        bone_chain.use_connect = True
                    last_bone = bone_chain
                #connect bones to targets
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                print("Object mode")
                for j in range(len(chains)):
                    chain = chains[j]
                    mdObj = self.getObjectByName(chain)
                    print("Deselect all objects")
                    bpy.ops.object.select_all(action='DESELECT')
                    print("Deselected all objects")
                    mdObj["object"].select = True
                    mdObj["object"].location = bone_chains[j].head + rig.location
                    print("Pose mode")
                    if "forceFit" in armatureConfig and armatureConfig["forceFit"] == "True":
                        print("Force fit")
                        mdObj["object"].dimensions[0] = grid["x"]
                    bpy.ops.object.mode_set(mode='POSE')
                    armature.bones.active = rig.pose.bones["bone.chain." + chain].bone
                    print("setting parent to bone")
                    bpy.ops.object.parent_set(type='BONE')
                    print("deselecting")
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    mdObj["object"].select = False
                self.presentation_armatures.append({"bone_chains":bone_chains,"armature" : armature, "rig":rig, "configuration": armatureConfig})
        bpy.ops.object.mode_set(mode='OBJECT')
        

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
    def parentCreatedObjects(self):
        print("Parent created objects")
        for i in range(len(self.scenes)):
            print("scene parent ")
            objs = self.scenes[i]["objects"]
            for j in range(len(objs)):
                obj = objs[j]
                print("scene parent  > OBJECTS")
                createdObject = self.getObjectByName(obj["name"])
                if "parent" in obj:
                    print("has a parent : " + obj["parent"])
                if createdObject and "parent" in obj:
                    print("parent name : " + obj["parent"])
                    parentObj = self.getObjectByName(obj["parent"])
                    if parentObj:
                        self.parentObject(parentObj, createdObject)

    def parentObject(self, b, a):
        print("Parent object a to b")
        if "object" in a:
            print("A has object")
        if "object" in b:
            print("B has object")
        a["object"].parent = b["object"]
        #bpy.ops.object.select_all(action='DESELECT')
        #a["object"].select = True
        #b["object"].select = True
        #bpy.context.scene.objects.active = a["object"]
        #bpy.ops.object.parent_set()
    def deselectAll(self):
        print("object mode")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = None
    def setObjectProperty(self, obj, config, frame):
        print("obj type : " + obj["type"])
        print(type(obj["object"]))
        if "position" in config:
            pos = config["position"]
            if "x" in pos:
                obj["object"].location.x = float(pos["x"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
            if "y" in pos:
                obj["object"].location.y = float(pos["y"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
            if "z" in pos:
                obj["object"].location.z = float(pos["z"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)
   
        if "scale" in config and config["scale"]: 
            scale = config["scale"] 
            if "x" in scale:
                obj["object"].scale.x = scale["x"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = float(scale["y"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = float(scale["z"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)
        if "position_rel" in config and config["position_rel"]:
            print("position relative to ")
            target = config["position_rel"]["target"]
            target_obj = self.getObjectByName(target)
            distance = 7
            if "distance" in config["position_rel"]:
                distance = config["position_rel"]["distance"]
            if "offset" in config["position_rel"]:
                offset = config["position_rel"]["offset"]
            else :
                offset = {"x":0,"y":0,"z":0}
            if config["position_rel"]["position"] == "front":
                print("matrix world to euler")
                direction = target_obj["object"].matrix_world.to_euler()
                direction = mathutils.Vector(direction)
                direction.normalize()
                print("direction normalized")
                print(direction)
                
                location = target_obj["object"].matrix_world * mathutils.Vector((0,-distance ,0)) #target_obj["object"].matrix_world.translation
                
                t = location #+ (7 * direction)
                obj["object"].location.x = t[0] + offset["x"]
                obj["object"].location.y = t[1] + offset["y"]
                obj["object"].location.z = t[2] + offset["z"]
                print("Set location")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
                print("set keyframe ")
            elif config["position_rel"]["position"] == "top":
                print("location + dimension")
                l = target_obj["object"].matrix_world * mathutils.Vector((0,0,distance)) 
                obj["object"].location.x = l[0] + offset["x"]
                obj["object"].location.y = l[1] + offset["y"]
                obj["object"].location.z = l[2] + offset["z"]
                print("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            elif config["position_rel"]["position"] == "center":
                print("location + dimension")
                l = target_obj["object"].matrix_world.translation
                obj["object"].location.x = l[0] 
                obj["object"].location.y = l[1] 
                obj["object"].location.z = l[2]
                print("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            
                

        if "target" in config and config["target"]: 
            print("track target")
            target = config["target"]
            target_obj = self.getObjectByName(target)
            bpy.ops.object.select_all(action='DESELECT')
            obj["object"].select = True
            constraint = obj["object"].constraints.new(type='TRACK_TO')
            constraint.target = target_obj["object"]
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            constraint.up_axis = "UP_Y"

        if "rotation" in config and config["rotation"]: 
            rotation = config["rotation"] 
            self.rotation(obj, rotation, True, frame)

        if "scale" in config and config["scale"]:
            scale = config["scale"]
            self.scale(obj, scale, True, frame)

    def scale(self, obj, scale, keyframe, frame):
            if "x" in scale:
                print(scale["x"])
                obj["object"].scale.x = (scale["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = (scale["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = (scale["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)

    def rotation(self, obj, rotation, keyframe, frame):
            if "x" in rotation:
                print(rotation["x"])
                obj["object"].rotation_euler.x = math.radians(rotation["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=0)
                
            if "y" in rotation:
                obj["object"].rotation_euler.y = math.radians(rotation["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=1)
                
            if "z" in rotation:
                obj["object"].rotation_euler.z = math.radians(rotation["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=2)
                           
    def getObjectByName(self, name):
        for i in range(len(self.presentation_objects)):
            obj = self.presentation_objects[i]
            if obj["name"] == name:
                return obj

        return 0

    def setFrame(self, keyframe):
        self.context.scene.frame_current = keyframe["frame"]    
    def createStage(self):
        print("create stage")
        for i in range(len(self.scenes)):
            scene = self.scenes[i]
            if "stage" in scene:
                stageConfig = scene["stage"]
                if "File" in stageConfig:
                    opath = stageConfig["File"]
                    if "Group" in stageConfig:
                        if not self.hasGroupByName(stageConfig["Group"]):
                            with bpy.data.libraries.load(opath) as (data_from, data_to):
                                data_to.groups = [stageConfig["Group"]]
                        group = bpy.data.groups[stageConfig["Group"]]
                        for j in range(len(group.objects)):
                            obj = group.objects[j]
                            print("stage: add object")
                            o = bpy.ops.object.add_named(name=obj.name)
                            self.context.active_object.location.x = 0
                            self.context.active_object.location.y = 0
                            self.context.active_object.location.z = 0

    def createObjectsUsed(self):
        objects = []
        objectnames = []
        for i in range(len(self.scenes)):
            scene = self.scenes[i]
            keyframes = scene["keyframes"]
            for k in range(len(keyframes)):
                print("keyframe")
                keyframe = keyframes[k]
                keyframe_objects = keyframe["objects"]
                for j in range(len(keyframe_objects)):
                    obj = keyframe_objects[j]
                    count = objectnames.count(obj["name"])
                    if count == 0:
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
        if "type" in scene_object_config:
            print(scene_object_config["type"])
            result["type"] = scene_object_config["type"]
        else:
           print("Type is missing")
        if(scene_object_config["type"] == "cube"):
            bpy.ops.mesh.primitive_cube_add(radius=1, location=(0, 0, 0))
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
            
        elif scene_object_config["type"] == "camera":
            print("create camera")
            bpy.ops.object.camera_add()
            result["object"] = self.context.active_object
            
        elif scene_object_config["type"] == "empty":
            print("create empty")
            bpy.ops.object.empty_add(type="PLAIN_AXES")
            result["object"] = self.context.active_object
            
        elif scene_object_config["type"] == "lamp":
            print("create lamp")
            light = "POINT"
            if "light" in scene_object_config:
                light = scene_object_config["light"]
            bpy.ops.object.lamp_add(type=light)
            result["object"] = self.context.active_object
            if "strength" in scene_object_config:
                strength = scene_object_config["strength"]
                print("setting strength")
                print(strength)
                if result["object"].data and result["object"].data.node_tree:
                    result["object"].data.node_tree.nodes["Emission"].inputs[1].default_value = strength
        elif scene_object_config["type"] == "text":
            bpy.ops.object.text_add()
            result["text"] = True
            result["object"] = self.context.active_object
            if "value" in scene_object_config:
                result["object"].data.body = scene_object_config["value"]
            result["mesh"] = self.context.active_object.data
            
            if "extrude" in scene_object_config and scene_object_config["extrude"]:
                result["object"].data.extrude = scene_object_config["extrude"]
                
            if "align" in scene_object_config and scene_object_config["align"]:
                result["object"].data.align = scene_object_config["align"]
            if "font" in scene_object_config:
                loaded = self.ensureFontLoaded(scene_object_config["font"])
                if loaded: 
                    font = self.getFont(scene_object_config["font"])
                    print("got font " + scene_object_config["font"])
                    if font != 0:
                        print("setting font ")
                        result["object"].data.font = font
            bpy.ops.object.convert(target="MESH")
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        if "scale" in scene_object_config and scene_object_config["scale"]:
            scale = scene_object_config["scale"]
            self.scale(result, scale, False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale= True)

        if "rotation" in scene_object_config:
            self.rotation(result, scene_object_config["rotation"], False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale= False)
        
        
        if "material" in scene_object_config and scene_object_config["material"]:
            if self.hasMaterialByName(scene_object_config["material"]):
                material = self.getMaterialByName(scene_object_config["material"])
                print("append material " + scene_object_config["material"])
                result["object"].data.materials.append(material)

        return result
    def getFont(self, fontname):
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
        return config["scenes"]
    def loadArmaturesConfig(self,config):
        print("Load armatures config")
        if "armatures" in config:
            return config["armatures"]
        return None

    def loadSettings(self, config):
        return config["settings"]

    def clearObjects(self):
        del self.presentation_objects[:]
        del self.presentation_armatures[:]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action = 'SELECT')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        for item in bpy.data.armatures:
            bpy.data.armatures.remove(item)
        for item in bpy.data.cameras:
            bpy.data.cameras.remove(item)
        


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