import 'maths.dart';

abstract class AnimatedProperty {
    AnimatedProperty(/* pass various properties and initialize here in subclass */);
    void advance();
    dynamic get current; // returns the current frame
    // void injectJSON(path, json) {
    // }
}

class LinearAnimation extends AnimatedProperty {
    Point start = Point(0,0,0);
    Direction direction = Direction(1,0,0);
    double speed = 1.0;
    Point _currentPosition;

    LinearAnimation({start, direction, speed}) {
        this.start = Point.fromList(start) ?? this.start;
        this.direction = Direction.fromList(direction) ?? this.direction;
        this.speed = speed.toDouble() ?? this.speed;
        this._currentPosition = this.start;
    }
    @override
    void advance() {
        this._currentPosition += this.direction * this.speed;
    }
    @override
    dynamic get current => this._currentPosition.asList();
}

Map AnimationMap = {
    'LinearAnimation': LinearAnimation
};
