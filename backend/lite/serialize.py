from trace import Trace
from env import VentureEnvironment
from node import Node, ConstantNode, LookupNode, RequestNode, OutputNode
from request import Request, ESR
from value import VentureNumber, VentureAtom, VentureBool, VentureSymbol, VentureArray, VentureNil, VenturePair, VentureSimplex, VentureDict, VentureMatrix, SPRef
from sp import VentureSP, SPAux, SPFamilies
from psp import NullRequestPSP, ESRRefOutputPSP
from csp import CSPRequestPSP
from msp import MSPRequestPSP
from smap import SMap

class Placeholder(object):
    """An object that can be instantiated before knowing what type it should be."""
    pass

serializable_types = [
    Trace,
    ConstantNode,
    LookupNode,
    RequestNode,
    OutputNode,
    VentureEnvironment,
    VentureNumber,
    VentureAtom,
    VentureBool,
    VentureSymbol,
    VentureArray,
    VentureNil,
    VenturePair,
    VentureSimplex,
    VentureDict,
    VentureMatrix,
    VentureSP,
    SPRef,
    SPAux,
    SPFamilies,
    Request,
    ESR,
    CSPRequestPSP,
    MSPRequestPSP,
    ESRRefOutputPSP,
    SMap
]

type_to_str = dict((t, t.__name__) for t in serializable_types)
str_to_type = dict((t.__name__, t) for t in serializable_types)

class Serializer(object):
    """Serializer and deserializer for Trace objects."""

    def serialize_trace(self, root):
        """Serialize a Trace object."""

        ## set up data structures for handling reference cycles
        self.obj_data = []
        self.obj_to_id = {}

        ## add built-in SP specially
        for name, node in root.globalEnv.outerEnv.frame.iteritems():
            self.obj_to_id[node.madeSP] = 'builtin:' + name

        ## serialize recursively
        serialized_root = self.serialize(root)
        return {
            'root': serialized_root,
            'objects': self.obj_data,
            'version': '0.1'
        }

    def serialize(self, obj):
        if isinstance(obj, (bool, int, long, float, str, unicode, type(None))):
            return obj
        elif isinstance(obj, list):
            return [self.serialize(o) for o in obj]
        elif isinstance(obj, tuple):
            value = tuple(self.serialize(o) for o in obj)
            return {'_type': 'tuple', '_value': value}
        elif isinstance(obj, set):
            value = [self.serialize(o) for o in obj]
            return {'_type': 'set', '_value': value}
        elif isinstance(obj, dict):
            value = [(self.serialize(k), self.serialize(v)) for (k, v) in obj.iteritems()]
            return {'_type': 'dict', '_value': value}
        else:
            assert type(obj) in type_to_str, "Can't serialize {0}".format(repr(obj))

            ## some objects should be stored by reference, in case of shared objects and cycles
            should_make_ref = isinstance(obj, (Node, VentureEnvironment, VentureSP))
            if should_make_ref:
                ## check if seen already
                if obj in self.obj_to_id:
                    return {'_type': 'ref', '_value': self.obj_to_id[obj]}
                ## generate a new id and append a placeholder to the obj_data array
                i = len(self.obj_data)
                self.obj_to_id[obj] = i
                self.obj_data.append(None)

            ## attempt to use the object's serialize method if available
            ## fallback: just get the __dict__
            if hasattr(obj, 'serialize'):
                serialized = obj.serialize(self)
            else:
                serialized = dict((k, self.serialize(v)) for (k, v) in obj.__dict__.iteritems())
            data = {'_type': type_to_str[type(obj)], '_value': serialized}

            if should_make_ref:
                ## store the actual data in the obj_data array and return the index instead
                self.obj_data[i] = data
                return {'_type': 'ref', '_value': i}
            else:
                return data

    def deserialize_trace(self, data):
        """Deserialize a serialized trace, producing a Trace object."""

        assert data['version'] == '0.1', "Incompatible version or unrecognized object"

        ## create placeholder object references so that we can rebuild cycles
        ## attach to each placeholder object the data dict that goes with it
        self.id_to_obj = {}
        for i, obj_dict in enumerate(data['objects']):
            obj = Placeholder()
            obj._data = obj_dict
            self.id_to_obj[i] = obj

        ## add built-in SP specially
        for name, node in Trace().globalEnv.outerEnv.frame.iteritems():
            self.id_to_obj['builtin:' + name] = node.madeSP

        deserialized_root = self.deserialize(data['root'])
        return deserialized_root

    def deserialize(self, data):
        if isinstance(data, (bool, int, long, float, str, unicode, type(None))):
            return data
        elif isinstance(data, list):
            return [self.deserialize(o) for o in data]
        else:
            assert isinstance(data, dict), "Unrecognized object {0}".format(repr(obj))
            assert '_type' in data, "_type missing from {0}".format(repr(obj))
        if data['_type'] == 'tuple':
            return tuple(self.deserialize(o) for o in data['_value'])
        elif data['_type'] == 'set':
            return set(self.deserialize(o) for o in data['_value'])
        elif data['_type'] == 'dict':
            return dict((self.deserialize(k), self.deserialize(v)) for (k, v) in data['_value'])
        else:
            ## if it's a ref, look up the real object
            if data['_type'] == 'ref':
                obj = self.id_to_obj[data['_value']]
                try:
                    ## get the data dict we attached to the placeholder object earlier
                    data = obj._data
                    del obj._data
                except AttributeError:
                    ## already deserialized, just return the object
                    return obj
            else:
                obj = Placeholder()

            assert data['_type'] in str_to_type, "Can't deserialize {0}".format(repr(obj))
            cls = str_to_type[data['_type']]
            obj.__class__ = cls

            ## attempt to use the object's deserialize method if available
            ## fallback: just set the __dict__
            if hasattr(cls, 'deserialize'):
                obj.deserialize(self)
            else:
                obj.__dict__ = dict((k, self.deserialize(v)) for (k, v) in data['_value'].iteritems())

            return obj

def serialize_trace(trace):
    return Serializer().serialize_trace(trace)

def deserialize_trace(serialized):
    return Serializer().deserialize_trace(serialized)
