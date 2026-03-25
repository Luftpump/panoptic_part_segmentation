"""
This module defines the classes for the scene graph, including Node, Building, Room, Object, Camera, and SceneGraph.
The scene graph is a hierarchical structure that organizes the elements of a scene, such as buildings, rooms, objects, and cameras. 
It allows for efficient management and rendering of complex scenes by grouping related elements together.
Each node in the scene graph represents an element of the scene and contains attributes and relationships to other nodes.
"""


class Node:
    """
    A node in the scene graph represents an element of the scene, such as a building, room, object, or camera.
    """
    def __init__(self, attr : dict):
        """
        Initializes a node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the node
        """
        self.attr = attr

    def specify_type(self):
        """
        Specifies the type of the node. This method should be overridden by subclasses to return the appropriate type.
        """
        raise NotImplementedError("Subclasses should implement this method to specify their type.")


class Building(Node):
    """
    A building node represents a building in the scene graph.
    """
    def __init__(self, attr : dict, parent_buildings : list):
        """
        Initializes a building node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the building node.
            parent_buildings (list): A list of room nodes which belong to this building.
        """
        super().__init__(attr)
        self.parent_buildings = parent_buildings
    
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
    def __init__(self, attr : dict, parent_buildings : list, parent_spaces : list, rmv : dict[Room , float]):
        """
        Initializes a room node with its attributes and relationships to other nodes.

        Args:
            attr (dict): A dictionary of attributes for the room node.
            parent_buildings (list): A list of building nodes which this room belongs to.
            parent_spaces (list): A list of object nodes which belong to this room.
            rmv (dict[Room, float]): A dictionary mapping room nodes to their relative magnitude volumes.
        """
        super().__init__(attr)
        self.parent_buildings = parent_buildings
        self.parent_spaces = parent_spaces
        self.relative_magnitude_volume = rmv

    def __hash__(self):
        """
        Returns a hash value for the room node based on its attributes. This allows room nodes to be used as keys in dictionaries or stored in sets.
        """
        return hash(tuple(self.attr.items()))
    
    def __eq__(self, other : Room):
        """
        Checks if this room node is equal to another room node based on their attributes.

        Args:
            other (Room): The other room node to compare with.
        
        Returns:
            bool: True if the room nodes are equal, False otherwise.
        """
        if not isinstance(other, Room):
            return NotImplemented
        return self.attr == other.attr

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
    
    def get_rmv(self, other_room : Room) -> float:
        """
        Retrieves the relative magnitude volume (RMV) between this room and another room.

        Args:
            other_room (Room): The other room for which to retrieve the RMV.

        Returns:
            float: The relative magnitude volume between this room and the other room.
        """
        return self.relative_magnitude_volume[other_room]


class Object(Node):
    """
    An object node represents an object in the scene graph.
    """
    def __init__(self, attr : dict, parent_spaces : list[Room], rmv : dict[Object, float]):
        """
        Initializes an object node with its attributes and relationships to other nodes.
        Args:
            attr (dict): A dictionary of attributes for the object node.
            parent_spaces (list[Room]): A list of room nodes which this object belongs to.
            rmv (dict[Object, float]): A dictionary mapping object nodes to their relative magnitude volumes.
        """
        super().__init__(attr)
        self.parent_spaces = parent_spaces
        self.relative_magnitude_volume = rmv

    def __hash__(self):
        """
        Returns a hash value for the object node based on its attributes. This allows object nodes to be used as keys in dictionaries or stored in sets.
        """
        return hash(tuple(self.attr.items()))
    
    def __eq__(self, other : Object):
        """
        Checks if this object node is equal to another object node based on their attributes.

        Args:
            other (Object): The other object node to compare with.
        
        Returns:
            bool: True if the object nodes are equal, False otherwise.
        """
        if not isinstance(other, Object):
            return NotImplemented
        return self.attr == other.attr

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
    
    def get_rmv(self, other_object : Object) -> float:
        """
        Retrieves the relative magnitude volume (RMV) between this object and another object.

        Args:
            other_object (Object): The other object for which to retrieve the RMV.

        Returns:
            float: The relative magnitude volume between this object and the other object.
        """
        return self.relative_magnitude_volume[other_object]


class Camera(Node):
    """
    A camera node represents a camera in the scene graph.
    """
    def __init__(self, attr: dict, occlusion : dict[Object, list[Object]], 
                 spatial_order : dict[Object | Room, dict[Object | Room, tuple[float, float, float]]]):
        super().__init__(attr)
        self.occlusion = occlusion
        self.spatial_order = spatial_order

    def specify_type(self):
        return "camera"
    
    def is_occluded(self, obj1 : Object, obj2 : Object) -> bool:
        """
        Determines if one object is occluded by another object from the perspective of this camera.

        Args:
            obj1 (Object): The first object to check for occlusion.
            obj2 (Object): The second object to check for occlusion.
        
        Returns:
            bool: True if obj1 is occluded by obj2, False otherwise.
        """
        return obj1 in self.occlusion and obj2 in self.occlusion[obj1]
    
    def get_spatial_order(self, entity1 : Object | Room, entity2 : Object | Room) -> tuple[float, float, float]:
        """
        Retrieves the spatial order between two entities (objects or rooms) from the perspective of this camera.

        Args:
            entity1 (Object | Room): The first entity to check for spatial order.
            entity2 (Object | Room): The second entity to check for spatial order.

        Returns:
            tuple[float, float, float]: A tuple representing the spatial order between the two entities.
        """
        if entity1 not in self.spatial_order or entity2 not in self.spatial_order[entity1]:
            raise ValueError("Spatial order information is missing for the given entities.")
        return self.spatial_order[entity1][entity2] 


class SceneGraph:
    """
    A scene graph is a hierarchical structure that organizes the elements of a scene, such as buildings, rooms, objects, and cameras. It allows for efficient management and rendering of complex scenes by grouping related elements together.
    """
    def __init__(self):
        """
        Initializes the scene graph with empty lists for buildings, rooms, objects, and cameras.
        """
        self.buildings = []
        self.rooms = []
        self.objects = []
        self.cameras = []

    def from_dict(self, data : dict):
        """
        Populates the scene graph from a dictionary representation. 
        The dictionary should contain keys for 'buildings', 'rooms', 'objects', and 'cameras', each mapping to a list of corresponding elements.

        Args:
            data (dict): A dictionary containing the scene graph data.
        """
        self.buildings = data["buildings"]
        self.rooms = data["rooms"]
        self.objects = data["objects"]
        self.cameras = data["cameras"]