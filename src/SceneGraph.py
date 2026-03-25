"""
This module defines the classes for the scene graph, including Node, Building, Room, Object, Camera, and SceneGraph.
The scene graph is a hierarchical structure that organizes the elements of a scene, such as buildings, rooms, objects, and cameras. 
It allows for efficient management and rendering of complex scenes by grouping related elements together.
Each node in the scene graph represents an element of the scene and contains attributes and relationships to other nodes.
"""

import json


class Node:
    """
    A node in the scene graph represents an element of the scene, such as a building, room, object, or camera.
    """
    def __init__(self, attr = None):
        """
        Initializes a node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the node
        """
        self.attr = attr or dict()

    def specify_type(self):
        """
        Specifies the type of the node. This method should be overridden by subclasses to return the appropriate type.
        """
        raise NotImplementedError("Subclasses should implement this method to specify their type.")


class Building(Node):
    """
    A building node represents a building in the scene graph.
    """
    def __init__(self, attr = None, parent_buildings = None):
        """
        Initializes a building node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the building node.
            parent_buildings (list): A list of room nodes which belong to this building.
        """
        super().__init__(attr)
        self.parent_buildings = parent_buildings or []
    
    def specify_type(self):
        """
        Specifies the type of the building.
        """
        if "function" not in self.attr:
            raise ValueError("Building node must have a 'function' attribute.")
        return self.attr["function"]
    
    def get_rooms(self):
        """
        Retrieves the rooms that are part of this building.
        """
        return self.parent_buildings


class Room(Node):
    """
    A room node represents a room in the scene graph.
    """
    def __init__(self, attr = None, parent_buildings = None, parent_spaces = None, 
                 rmv = None):
        """
        Initializes a room node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the room node.
            parent_buildings (list): A list of building nodes which this room belongs to.
            parent_spaces (list): A list of object nodes which belong to this room.
            rmv (dict[Room, float]): A dictionary mapping room instances to their relative magnitude volumes.
        """
        super().__init__(attr)
        self.parent_buildings = parent_buildings or []
        self.parent_spaces = parent_spaces or []
        self.relative_magnitude_volume = rmv or {}

    def specify_type(self):
        """
        Specifies the type of the room.
        """
        if "class" not in self.attr:
            raise ValueError("Room node must have a 'class' attribute.")
        return self.attr["class"]
    
    def get_building(self):
        """
        Retrieves the building that this room belongs to.
        """
        return self.parent_buildings
    
    def get_objects(self):
        """
        Retrieves the objects that are part of this room.
        """
        return self.parent_spaces
    
    def get_rmv(self, other_room) -> float:
        """
        Retrieves the relative magnitude volume (RMV) between this room and another room.

        Args:
            other_room (Room): The Room instance for which to retrieve the RMV.

        Returns:
            float: The relative magnitude volume between this room and the other room.
        """
        return self.relative_magnitude_volume[other_room]


class Object(Node):
    """
    An object node represents an object in the scene graph.
    """
    def __init__(self, attr = None, parent_spaces = None, 
                 rmv = None):
        """
        Initializes an object node with its attributes and relationships to other nodes.
        Args:
            attr (dict): A dictionary of attributes for the object node.
            parent_spaces (list[Room]): A list of room nodes which this object belongs to.
            rmv (dict[Object, float]): A dictionary mapping object instances to their relative magnitude volumes.
        """
        super().__init__(attr)
        self.parent_spaces = parent_spaces or []
        self.relative_magnitude_volume = rmv or {}

    def specify_type(self):
        """
        Specifies the type of the object.
        """
        if "class" not in self.attr:
            raise ValueError("Object node must have a 'class' attribute.")
        return self.attr["class"]
    
    def get_rooms(self):
        """
        Retrieves the rooms that this object belongs to.
        """
        return self.parent_spaces
    
    def get_rmv(self, other_object) -> float:
        """
        Retrieves the relative magnitude volume (RMV) between this object and another object.

        Args:
            other_object (Object): The Object instance for which to retrieve the RMV.

        Returns:
            float: The relative magnitude volume between this object and the other object.
        """
        return self.relative_magnitude_volume[other_object]


class Camera(Node):
    """
    A camera node represents a camera in the scene graph.
    """
    def __init__(self, attr = None, occlusion = None, spatial_order = None):
        """
        Initializes a camera node with its attributes and relationships to other nodes.
        
        Args:
            attr (dict): A dictionary of attributes for the camera node.
            occlusion (dict[Object | Room, list[Object | Room]]): A dictionary mapping object instances to lists of object instances that occlude them from the perspective of this camera.
            spatial_order (dict[Object | Room, dict[Object | Room, tuple[float, float, float]]]): A nested dictionary mapping pairs of entity instances (objects or rooms) to their spatial order from the perspective of this camera.
        """
        super().__init__(attr)
        self.occlusion = occlusion or {}
        self.spatial_order = spatial_order or {}

    def specify_type(self):
        return "camera"
    
    def is_occluded(self, obj1 : Object | Room, obj2 : Object | Room) -> bool:
        """
        Determines if one object is occluded by another object from the perspective of this camera.

        Args:
            obj1 (Object | Room): The first object to check for occlusion.
            obj2 (Object | Room): The second object to check for occlusion.
        
        Returns:
            bool: True if obj1 is occluded by obj2, False otherwise.
        """
        return obj1 in self.occlusion.keys() and obj2 in self.occlusion[obj1]
    
    def get_spatial_order(self, entity1 : Object | Room, entity2 : Object | Room) -> tuple[float, float, float]:
        """
        Retrieves the spatial order between two entities (objects or rooms) from the perspective of this camera.

        Args:
            entity1 (Object | Room): The first entity to check for spatial order.
            entity2 (Object | Room): The second entity to check for spatial order.

        Returns:
            tuple[float, float, float]: A tuple representing the spatial order between the two entities.
        """
        if entity1 in self.spatial_order.keys() and entity2 in self.spatial_order[entity1]:
            return self.spatial_order[entity1][entity2]
        else:
            raise ValueError(f"Spatial order between {entity1} and {entity2} is not defined for this camera.")


class SceneGraph:
    """
    A scene graph is a hierarchical structure that organizes the elements of a scene, such as buildings, rooms, objects, and cameras. It allows for efficient management and rendering of complex scenes by grouping related elements together.
    """
    def __init__(self):
        """
        Initializes the scene graph with empty lists for buildings, rooms, objects, and cameras.
        """
        self.graph = {}

    def load_from_dict(self, data : dict):
        """
        Populates the scene graph from a dictionary representation. 
        The dictionary should contain keys for 'buildings', 'rooms', 'objects', and 'cameras', each mapping to a list of corresponding elements.

        Args:
            data (dict): A dictionary containing the scene graph data.
        """
        for id, value in data.items():
            if value["type"] == "building":
                self.graph[id] = Building(attr=value.get("attr", {}), 
                                        parent_buildings=value.get("parent_buildings", []))
            elif value["type"] == "room":
                self.graph[id] = Room(attr=value.get("attr", {}), 
                                        parent_buildings=value.get("parent_buildings", []), 
                                        parent_spaces=value.get("parent_spaces", []), 
                                        rmv=value.get("rmv", {}))
            elif value["type"] == "object":
                self.graph[id] = Object(attr=value.get("attr", {}), 
                                        parent_spaces=value.get("parent_spaces", []), 
                                        rmv=value.get("rmv", {}))
            elif value["type"] == "camera":
                self.graph[id] = Camera(attr=value.get("attr", {}), 
                                        occlusion=value.get("occlusion", {}), 
                                        spatial_order=value.get("spatial_order", {}))
                
        for id, node in self.graph.items():
            if isinstance(node, Building):
                node.parent_buildings = [self.graph[room_id] for room_id in node.parent_buildings]
            elif isinstance(node, Room):
                node.parent_buildings = [self.graph[building_id] for building_id in node.parent_buildings]
                node.parent_spaces = [self.graph[object_id] for object_id in node.parent_spaces]
                node.relative_magnitude_volume = {self.graph[other_room_id]: rmv for other_room_id, rmv in node.relative_magnitude_volume.items()}
            elif isinstance(node, Object):
                node.parent_spaces = [self.graph[room_id] for room_id in node.parent_spaces]
                node.relative_magnitude_volume = {self.graph[other_object_id]: rmv for other_object_id, rmv in node.relative_magnitude_volume.items()}
            elif isinstance(node, Camera):
                node.occlusion = {self.graph[obj_id]: [self.graph[occluder_id] for occluder_id in occluders] for obj_id, occluders in node.occlusion.items()}
                node.spatial_order = {self.graph[entity1_id]: {self.graph[entity2_id]: tuple(order) 
                                                               for entity2_id, order in entity2_orders.items()} 
                                                               for entity1_id, entity2_orders in node.spatial_order.items()}

    def load_from_json(self, json_file : str):
        """
        Populates the scene graph from a JSON file. The JSON file should contain a dictionary representation of the scene graph.

        Args:
            json_file (str): The path to the JSON file containing the scene graph data.
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        self.load_from_dict(data)

    def print_statistics(self):
        """
        Prints statistics about the scene graph, including the number of buildings, rooms, objects, and cameras.
        """
        num_buildings = sum(1 for node in self.graph.values() if isinstance(node, Building))
        num_rooms = sum(1 for node in self.graph.values() if isinstance(node, Room))
        num_objects = sum(1 for node in self.graph.values() if isinstance(node, Object))
        num_cameras = sum(1 for node in self.graph.values() if isinstance(node, Camera))
        
        print(f"Scene Graph Statistics:")
        print(f"  Total number of nodes: {len(self.graph)}")
        print(f"    Number of Buildings: {num_buildings}")
        print(f"    Number of Rooms: {num_rooms}")
        print(f"    Number of Objects: {num_objects}")
        print(f"    Number of Cameras: {num_cameras}")

    def print_graph(self):
        """
        Prints the structure of the scene graph, showing the relationships between buildings, rooms, objects, and cameras.
        """
        used = []
        for id, node in self.graph.items():
            if id in used:
                continue
            if isinstance(node, Building):
                print(f"In building {id} (function: {node.specify_type()}):")
                for room in node.get_rooms():
                    room_id = [key for key, value in self.graph.items() if value == room][0]
                    print(f"  In room {room_id} (class: {room.specify_type()}):")
                    used.append(room_id)
                    for obj in room.get_objects():
                        obj_id = [key for key, value in self.graph.items() if value == obj][0]
                        print(f"    Object {obj_id} (class: {obj.specify_type()})")
        for id, node in self.graph.items():
            if id in used:
                continue
            if isinstance(node, Room):
                print(f"In room {id} (class: {node.specify_type()}):")
                for obj in node.get_objects():
                    obj_id = [key for key, value in self.graph.items() if value == obj][0]
                    print(f"  Object {obj_id} (class: {obj.specify_type()})")
        for id, node in self.graph.items():
            if isinstance(node, Camera):
                print(f"Camera {id}:")
                for obj, occluders in node.occlusion.items():
                    obj_id = [key for key, value in self.graph.items() if value == obj][0]
                    print(f"  Object {obj_id} is occluded by:")
                    for occluder in occluders:
                        occluder_id = [key for key, value in self.graph.items() if value == occluder][0]
                        print(f"    {occluder_id}")
                for entity1, entity2_orders in node.spatial_order.items():
                    entity1_id = [key for key, value in self.graph.items() if value == entity1][0]
                    print(f"  Spatial order for {entity1_id}:")
                    for entity2, order in entity2_orders.items():
                        entity2_id = [key for key, value in self.graph.items() if value == entity2][0]
                        print(f"    {entity2_id}: {order}")
