"""
Showcase of how to use the SceneGraph class to load a scene graph from a JSON file 
and query its properties.
"""
import torch
import matplotlib
import numpy as np

from src.SceneGraph import SceneGraph

from transformers import Owlv2Processor, Owlv2ForObjectDetection
from PIL import Image

if __name__ == "__main__":
    # Load the scene graph from a JSON file
    scene_graph = SceneGraph()
    scene_graph.load_from_json("material/example.json")

    scene_graph.print_statistics()

    scene_graph.print_graph()

    # Tests
    camera = scene_graph.graph["C1"]
    object1 = scene_graph.graph["O1"]
    object2 = scene_graph.graph["O2"]
    room = scene_graph.graph["R1"]
    building = scene_graph.graph["B1"]

    assert object2 in camera.occlusion[object1]
    assert camera.spatial_order[object1][object2] == (0.8, 0.3, -0.1)

    assert building in room.parent_buildings
    assert room in building.parent_buildings

    assert room in object1.parent_spaces
    assert room in object2.parent_spaces