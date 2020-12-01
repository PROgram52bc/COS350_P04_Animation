from itertools import chain
import sys
from .maths import Point


def get_class_name(obj):
    """get the class name of an object

    :obj: the object to be analyzed
    :returns: the class name of object as a string

    """
    return type(obj).__name__


def is_iterator(obj):
    """ check if obj is an iterator """
    return (hasattr(obj, "__iter__") and
            hasattr(obj, "__next__"))


class AnimatedProperty:

    def dynamic_property(self, name, initial_value=0):
        def decorator_func(func):
            self.register_child_property(
                name,
                initial_value,
                property_type="dynamic",
                dynamic_updater=func)
        return decorator_func

    def terminator(self):
        def decorator_func(func):
            self.register_terminator(func)
        return decorator_func

    class PropertyFrame:

        """Represents a single frame in an AnimatedProperty"""

        def __init__(self, props, ap, frame_num=None):
            """
            :props: a dictionary where each key is the property name, and value is the data,
                    either as a PropertyFrame object for 'animated' properties,
                    or as a single serializable for 'dynamic' or 'static' properties.
            :ap: the reference to the original animated property.
            :frame_num: the frame number, None if not available.
            """
            self.props = props
            self.ap = ap
            self.frame_num = frame_num

        def get_frame_data(self):
            return self.ap.get_frame_data(self)

    def _get_snapshot(self, property_states, frame_num=None):
        """returns a PropertyFrame as a snapshot for a property_states object

        :property_states: a dictionary where each key is the name of the property, and the value is a dictionary containing a 'value' property: for static and dynamic, this is the actual value. For animated, it is a PropertyFrame.
        :returns: a PropertyFrame object.

        """
        return self.PropertyFrame(
            props={
                k: v['value'] for k,
                v in property_states.items()},
            ap=self,
            frame_num=frame_num)

    def _advance_animated_and_iterated_property(
            self, property_states, property_name):
        """ advance the specified animated property, set value to the yielded value, handle StopIteration error based on the end_action

        :property_states: a dictionary where each key is the name of the property, and the value is a dictionary containing an 'iterator' property
                {
                    type: animated or iterated
                    iterator: the iterator to be advanced
                    value: the current value as a PropertyFrame
                    end_action: same as in register_child_property
                    end_value: same as in register_child_property
                }
        :returns: the yielded object from the iterator, None if unavailable.
        :raises: a StopIteration error if the specified property terminates and its end_action is 'terminate'

        """
        prop = property_states[property_name]
        iterator = prop['iterator']
        if not is_iterator(iterator):
            raise ValueError(
                f"The 'iterator' slot of [{property_name}] does not have an iterator: {iterator}")
        try:
            next_value = next(iterator)
            prop['value'] = next_value
            return next_value
        except StopIteration:
            if prop['end_action'] == 'terminate':
                raise
            elif prop['end_action'] == 'drop':
                del property_states[property_name]
            elif prop['end_action'] == 'keep':
                pass
            elif prop['end_action'] == 'end_value':
                prop['value'] = prop['end_value']
            else:
                raise ValueError(f"unknown end_action [{prop['end_action']}]")

    def get_frame_data(self, property_frame):
        """ should be defined in subclass, used to generate the frame data in the final animation.

        :property_frame: the PropertyFrame object representing the current state
        :returns: a serializable property representing the current frame data

        """
        def _unpack_pf_or_data(data):
            if isinstance(data, self.PropertyFrame):
                return data.get_frame_data()
            return data
        return { k:_unpack_pf_or_data(v) for k,v in property_frame.props.items() }

    def __init__(self):
        """
        :returns: None

        """
        # { 'prop_name': { 'seed': ..., 'type': "animated|static|dynamic", 'end_action', 'end_value' }, ... }
        self.__prop_map = {}
        self.__terminators = []

    # @property
    # def prop_map(self):
    #     return self.__prop_map

    def register_child_property(
            self,
            name,
            prop,
            *,
            property_type="auto",
            end_action="terminate",
            end_value=0,
            dynamic_updater=None):
        """ to be called by subclass to register an AnimatedProperty to be used in the current AnimatedProperty

        :name: the name of the property
        :prop: An AnimatedProperty object, or any object
        :property_type: auto|animated|dynamic|static.
                If type is auto and property is an AnimatedProperty, it is registered as "animated" type in __prop_map.
                if type is auto and property is iterable, it is registered as "iterated" type in __prop_map.
                if type is auto and property is neither an AnimatedProperty nor an iterable, the value is registered as "dynamic" type
                if type is iterated, a check is performed to make sure property is iterable
                if type is animated, a check is performed to make sure property is an instance of AnimatedProperty
                if type is static, it is registered as "static"
                if type is dynamic, it is registered as "dynamic"
        :end_action: drop|end_value|keep|terminate.
                drop means dropping the current property when it is done;
                end_value means use the value specified by `end_value`;
                keep means using the last frame's value as its value;
                terminate means terminating the parent animation when the child property ends.
        :end_value: the value to be used when the property terminates, only effective when `end_action` is set to 'value'
        :dynamic_updater: a function with the following signature dynamic_updater(property_frame): new_value, used to update dynamic values
        :returns: None

        """
        # make sure property name does not exist
        if name in self.__prop_map:
            raise ValueError(f"Child property [{name}] is already registered")

        # make sure the specified property_type matches the prop provided
        if property_type == "animated" and not isinstance(
                prop, AnimatedProperty):
            raise ValueError(
                f"Failed to register animated property [{name}], "
                f"because object of [{get_class_name(prop)}] is not an instance of AnimatedProperty")
        elif property_type == "iterated":
            try:
                iter(prop)
            except TypeError:
                raise ValueError(
                    f"Failed to register iterated property [{name}], "
                    f"because object of [{get_class_name(prop)}] is not iterable")

        # auto detect property_type
        if property_type == "auto":
            if dynamic_updater is not None:
                property_type = "dynamic"
            elif isinstance(prop, AnimatedProperty):
                property_type = "animated"
            elif hasattr(prop, "__iter__"):
                property_type = "iterated"
            else:
                property_type = "static"

        if property_type == "dynamic":
            if dynamic_updater is None or not callable(dynamic_updater):
                raise ValueError(
                    f"Failed to register iterated property [{name}], "
                    f"because the dynamic_updater is either not specified or not callable")

        self.__prop_map[name] = {
            "type": property_type,
            "seed": prop,
            "end_action": end_action,
            "end_value": end_value,
            "dynamic_updater": dynamic_updater
        }

    def append_child_property(self, name, prop):
        """ append to properties that have iterable or animated type

        :name: the name of the existing property
        :prop: An AnimatedProperty object, or an iterable
        """
        if name not in self.__prop_map:
            raise ValueError(f"Cannot append to non-existing child property [{name}]")
        property_type = self.__prop_map[name]['type']
        if property_type != 'animated' and property_type != 'iterated':
            raise ValueError(f"Cannot append property to non-iterable type [{property_type}]")
        seed = self.__prop_map[name]['seed']
        seed = chain(seed, prop)
        self.__prop_map[name]['seed'] = seed
        

    def remove_child_property(self, name):
        """ reverses the effect of register_child_property

        :name: the name of the property
        :returns: the child property being removed

        """
        if name not in self.__prop_map:
            raise ValueError(
                f"Failed to remove child property [{name}] because it is not registered")
        return self.__prop_map.pop(name)

    def register_terminator(self, terminator):
        if not callable(terminator):
            raise ValueError("terminator must be callable")
        self.__terminators.append(terminator)

    def __iter__(self):
        property_states = {
            k: {
                "type": v['type'],
                "iterator": iter(
                    v['seed']) if v['type'] == 'animated' or v['type'] == 'iterated' else v['seed'],
                "value": None if v['type'] == 'animated' or v['type'] == 'iterated' else v['seed'],
                "end_action": v['end_action'],
                "end_value": v['end_value'],
                "dynamic_updater": v['dynamic_updater']}
            for k, v in self.__prop_map.items()
        }
        frame_num = 0
        while True:
            # update all animated and iterated properties, create a copy because properties
            # might be removed
            for name in property_states.copy():
                if (property_states[name]["type"] != "animated" and
                        property_states[name]["type"] != "iterated"):
                    continue
                try:
                    self._advance_animated_and_iterated_property(
                        property_states, name)
                except StopIteration:
                    return
            # take a snapshot (as a PropertyFrame object)
            snapshot = self._get_snapshot(property_states, frame_num)

            # check whether should terminate
            for terminate in self.__terminators:
                if terminate(snapshot):
                    return
            
            yield snapshot
            # update all dynamic properties
            for name in property_states:
                if property_states[name]["type"] == "dynamic":
                    update = property_states[name]["dynamic_updater"]
                    property_states[name]["value"] = update(snapshot)
            frame_num += 1
