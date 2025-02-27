import numpy as np
from rdflib import RDF, RDFS, URIRef, BNode

from utils import ResourceDictionary


class GraphWordsEncoder:
    def __init__(self, properties_dictionary, properties_groups, classes_resources):
        self.properties_dictionary = properties_dictionary
        self.properties_groups = properties_groups
        self.classes_resources = classes_resources
        self.active_properties = ResourceDictionary()
        self.active_properties.add(RDF.type)
        self.active_classes = ResourceDictionary()
        self.number = 0

    def add_resource(self, local_resources, resource, property_uri):
        self.active_properties.add(property_uri)
        property_group = self.properties_groups[property_uri]
        rdf_type_group = self.properties_groups[RDF.type]
        print(f"Property: {property_uri}, property group: {property_group}, rdf type group: {rdf_type_group}")
        if resource in self.classes_resources:
            self.active_classes.add(resource)
            print(f"Added class {resource} to active classes")
        else:
            if property_group not in local_resources:
                local_resources[property_group] = ResourceDictionary(negative=True)
                print(f"Added property group {property_group} to local resources")
            if rdf_type_group not in local_resources:
                local_resources[rdf_type_group] = ResourceDictionary(negative=True)
                print(f"Added rdf type group {rdf_type_group} to local resources")
            local_resources[property_group].add(resource)
            print(f"Added resource {resource} to local resources")
            if type(resource) == URIRef:
                local_resources[rdf_type_group].add(resource)
                print(f"Added resource {resource} to local resources")

    def resource_to_id(self, local_resources, resource, property_uri):
        property_group = self.properties_groups[property_uri]
        print(f"Looking up resource for property group {property_group}: {resource}")
        if property_group in self.active_classes:
            resource_id = self.active_classes[resource]
            print(f"Resource {resource} is a class and is in active classes, returning {resource_id}")
            return resource_id
        else:
            if resource in self.active_classes:
                resource_id = self.active_classes[resource]
                print(f"Resource {resource} is a class and is in active classes, returning {resource_id}")
                return resource_id
            else:
                resource_id = local_resources[property_group][resource]
                print(f"Resource {resource} is not a class and is in local resources, returning {resource_id}")
                return resource_id

    def encode_graph(self, graph, local_resources={}, inference=False, verbose=True, skip_bnodes=True,
                     skip_type_resource=True, skip_type_class=True):
        if not inference:
            local_resources = {}
        encoding = {}
        triples_list = sorted(list(graph))
        # print(f"GRAPH NUMBER: {self.number}")
        # time.sleep(5)
        for subject, property, object in sorted(triples_list, key=self.properties_order):
            print(f"Subject: {subject},\n "
                  f"property: {property},\n "
                  f"object: {object}")
            if property not in self.properties_dictionary:
                graph.remove((subject, property, object))

                continue

            if skip_bnodes and (type(subject) == BNode or type(object) == BNode):
                graph.remove((subject, property, object))

                continue

            if skip_type_resource and (property, object) == (RDF.type, RDFS.Resource):
                graph.remove((subject, property, object))
                continue

            if skip_type_class and (property, object) == (RDF.type, RDFS.Class):
                graph.remove((subject, property, object))

                continue
            print(f"Adding resource {subject} to local resources")
            if inference and object in self.classes_resources:
                self.active_classes.add(object)
            if not inference:
                self.add_resource(local_resources, subject, property)
                self.add_resource(local_resources, object, property)

            self.active_properties.add(property)
            print(f"\n")
            print(f"Retrieving ids for {subject}, {property}, {object}")
            property_id = self.active_properties[property]
            subject_id = self.resource_to_id(local_resources, subject, property)
            object_id = self.resource_to_id(local_resources, object, property)

            if verbose:
                print(subject, property, object)
                print(subject_id, property_id, object_id)
                print()
            # print(property_id, subject_id, object_id)
            if property_id not in encoding:
                encoding[property_id] = []
            encoding[property_id].append((subject_id, object_id))
        # self.number += 1
        return encoding, local_resources

    def graph_encoding_to_np(self, graph_encoding, offset, size):
        three_d_adjacency_matrix = np.zeros((len(self.active_properties), size, size), dtype=np.bool)
        for property_id in self.active_properties.inverse:
            if property_id not in graph_encoding:
                continue
            for (subject_id, object_id) in graph_encoding[property_id]:
                subject_id = self.offset_id(subject_id, offset)
                object_id = self.offset_id(object_id, offset)
                three_d_adjacency_matrix[property_id - 1][subject_id][object_id] = 1
        return three_d_adjacency_matrix

    def layer_to_np(self, layer, offset, size):
        layer_adjacency_matrix = np.zeros((size, size), dtype=np.bool)
        for (subject_id, oid) in layer:
            subject_id = self.offset_id(subject_id, offset)
            oid = self.offset_id(oid, offset)
            layer_adjacency_matrix[subject_id][oid] = 1
        return layer_adjacency_matrix

    @staticmethod
    def offset_id(resource_id, offset):
        if resource_id < 0:
            resource_id = - resource_id
            resource_id += offset
        return resource_id - 1

    @staticmethod
    def properties_order(triple):
        if triple[1] == RDF.type:
            return ""
        return triple[1]
