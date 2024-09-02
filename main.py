from classes.gameobject import GameObject
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
from classes.vec3 import Vec3
from classes.renderer import Renderer
import pygame as pg
import importlib
script_classes = importlib.import_module("assets.scripts")
import pyrr.matrix44 as mat4
import json
from typing import TypedDict
from typing import Any

class App:
    def __init__(self) -> None:
        self.width = 1920
        self.height = 1080
        self.renderer = Renderer(self.width, self.height)
        self.init_objects()
        self.clock = pg.time.Clock()
        running = True
        self.delta_time = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
            if len(self.game_objects) > 0:
                try:
                    self.renderer.view_matrix = self.game_objects[0].scripts[0].get_view_matrix()
                except:
                    self.renderer.view_matrix = mat4.create_identity()
                self.update_game_objects()
                self.renderer.render_objects(self.game_objects)
            self.delta_time = self.clock.tick(144) / 1000
        self.destroy()

    def init_objects(self):
        # First game object is the camera
        # self.game_objects: list[GameObject] = [
        #     GameObject(
        #         "main", Transform(Vec3(0, 0, 0), Vec3(1, 1, 1), Vec3(0, 0, 0)), scripts=[PlayerMove(5, 0.01, self.width, self.height)]
        #     ),
        #     GameObject(
        #         "cube",
        #         Transform(Vec3(0, 0, 5), Vec3(1, 1, 1,), Vec3(0, 0, 0)),
        #         render_component=RenderComponent("assets/objects/Cube.txt", "assets/images/test.png"),
        #         parent_name="parent"
        #     ),
        #     GameObject(
        #         "parent", Transform(Vec3(0, 0, 1), Vec3(1, 1, 1), Vec3(0, 0, 0))
        #     )
        # ]
        self.load_json("gameobjects.json")
        self.start_game_objects()
    
    def destroy(self):
        self.end_game_objects()
        for obj in self.game_objects:
            obj.destroy()
        pg.quit()

    def start_game_objects(self):
        for game_object in self.game_objects:
            game_object.init_parent(self.game_objects)
            for script in game_object.scripts:
                script.start()

    def update_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.delta_time = self.delta_time
                script.update()
                
    def end_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.end()
    
    def load_json(self, path: str):
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"object_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "parent_name": str, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})
        self.game_objects: list[GameObject] = []
        with open(path) as file:
            json_dict: FileDict = json.load(file)
        for game_object in json_dict["objects"]:
            scripts = []
            for script_dict in game_object["scripts"]:
                class_ = getattr(script_classes, script_dict["name"])
                scripts.append(class_(*script_dict["args"]))
            self.game_objects.append(
                GameObject(game_object["name"],
                Transform(
                    Vec3(
                        game_object["transform"]["pos"]["x"],
                        game_object["transform"]["pos"]["y"],
                        game_object["transform"]["pos"]["z"],
                    ),
                    Vec3(
                        game_object["transform"]["scale"]["x"],
                        game_object["transform"]["scale"]["y"],
                        game_object["transform"]["scale"]["z"],
                    ),
                    Vec3(
                        game_object["transform"]["rot"]["x"],
                        game_object["transform"]["rot"]["y"],
                        game_object["transform"]["rot"]["z"],
                    )
                ),
                game_object["parent_name"],
                RenderComponent(
                    game_object["render_component"]["object_path"],
                    game_object["render_component"]["image_path"]
                ),
                scripts
            ))

if __name__ == "__main__":
    app = App()