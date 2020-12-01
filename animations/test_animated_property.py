from pycommon.animated_property import AnimatedProperty
import pytest


@pytest.fixture
def ap():
    ap = AnimatedProperty()
    return ap


def test_static_property(ap):
    # GIVEN a static property
    ap.register_child_property(
        'const', 1, property_type="static")      # a static property
    # WHEN we start the animation for 10 frames
    it = iter(ap)
    for i in range(10):
        property_frame = next(it)
        # THEN we expect the frame number to advance at each frame
        assert property_frame.frame_num == i
        # THEN we expect the property to be available and not changing
        assert property_frame.props['const'] == 1


def test_iterated_property(ap):
    # GIVEN an iterated property
    data = [1, 2, 3]
    ap.register_child_property('iterated', data, property_type="iterated")
    # WHEN we start the animation for 3 frames
    it = iter(ap)
    for i in range(3):
        # THEN we expect the iterated property to advance
        property_frame = next(it)
        assert property_frame.props['iterated'] == data[i]
    # THEN we expect the animation to terminate
    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False


def test_dynamic_property(ap):
    # GIVEN an animation with a dynamic property that adds step to its value
    # every iteration
    step = 1
    value = 5
    ap.register_child_property('step', step, property_type="static")
    ap.register_child_property(
        'value',
        value,
        dynamic_updater=lambda pf: pf.props['step'] +
        pf.props['value'])
    # WHEN we iterate through the animation
    it = iter(ap)
    for i in range(10):
        property_frame = next(it)
        # THEN we expect the dynamic value to be updated
        assert property_frame.props['value'] == value + step * i


def test_dynamic_decorator(ap):
    # GIVEN an animation with a dynamic property that adds step to its value
    # every iteration

    step = 1
    value = 5
    ap.register_child_property('step', step, property_type="static")

    @ap.dynamic_property('value', value)
    def update(pf):
        return pf.props['step'] + pf.props['value']

    # WHEN we iterate through the animation
    it = iter(ap)
    for i in range(10):
        property_frame = next(it)
        # THEN we expect the dynamic value to be updated
        assert property_frame.props['value'] == value + step * i


def test_end_action(ap):
    # GIVEN several iterated properties with different end_action
    ap.register_child_property(
        'terminate', [
            1, 2, 3], property_type="iterated", end_action="terminate")
    ap.register_child_property(
        'keep', [1, 2], property_type="iterated", end_action="keep")
    ap.register_child_property(
        'end_value', [
            1, 2], property_type="iterated", end_action="end_value", end_value=99)
    ap.register_child_property(
        'drop', [1, 2], property_type="iterated", end_action="drop")
    # WHEN we reach the third frame of the animation
    it = iter(ap)
    for _ in range(2):
        next(it)
    property_frame = next(it)
    # THEN we expect the right frame number
    assert property_frame.frame_num == 2
    # THEN we expect the 'terminate' property to keep going
    assert property_frame.props['terminate'] == 3
    # THEN we expect the 'keep' property to keep its last value
    assert property_frame.props['keep'] == 2
    # THEN we expect the 'end_value' property to use the specified end_value
    assert property_frame.props['end_value'] == 99
    # THEN we expect the 'drop' property to be dropped
    assert 'drop' not in property_frame.props


def test_default_frame_data(ap):
    # WHEN we have a nested AnimatedProperty
    ap.register_child_property('value', 1)
    child = AnimatedProperty()
    child.register_child_property('child_value', 2)
    ap.register_child_property('child', child)
    frame_data = next(iter(ap)).get_frame_data()
    # THEN we expect the default frame data to be a nested dictionary
    assert frame_data == {'value': 1, 'child': {'child_value': 2}}


def test_terminator(ap):
    # WHEN we have a terminator registered
    ap.register_child_property('value', 1)
    ap.register_terminator(lambda pf: pf.frame_num >= 3)
    it = iter(ap)
    # THEN we expect the animation to terminate accordingly
    for _ in range(3):
        next(it)
    try:
        next(it)
    except StopIteration:
        pass
    else:
        assert False

def test_append_child_property(ap):
    # WHEN we append to a child property
    ap.register_child_property('iterated', [1,2,3], property_type="iterated")   
    ap.append_child_property('iterated', [4,5,6])   
    # THEN we expect the property to be properly extended
    for pf, i in zip(ap, [1,2,3,4,5,6]):
        assert pf.props['iterated'] == i

