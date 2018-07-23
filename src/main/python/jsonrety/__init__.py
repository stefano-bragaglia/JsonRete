"""
json is empty              == {}
json is not empty          {_}  or {...}
json contains key          {"key": _}
json key has type of value {"key": int}
json key contains value    {"key": 5}

assignment {$v = "key": int}
assignment {$v = "key": _}
assignment {$v = "key": 5}

{}
{...}
{"key": _} or more comma separated
{"key": 5} or more comma separated
{$v = "key": _} ore more comma separated
{$v = "key": 5} ore more comma separated

$a = {}
$a = {...}
$a = {"key": _} ore more comma separated
$a = {"key": 5} ore more comma separated
$a = {$v = "key": _} ore more comma separated
$a = {$v = "key": 5} ore more comma separated

{"key": $v} ore more comma separated



{...} @ 5, #$p @ 5
<-
{...},
not {...},
all {...},
exist {...},
{not "key": _}



"""
import json
from collections import namedtuple
from typing import Dict, Union

Value = Union[bool, int, float, str, list]
JSON = Dict[str, Value]
Payload = namedtuple('Payload', 'match table')


class Condition:
    def __repr__(self) -> str:
        raise NotImplementedError

    def is_met(self, left, right=None) -> bool:
        raise NotImplementedError


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        signature = '_'.join([str(part) for part in [cls.__name__, *args, *kwargs]])
        if signature not in cls._instances:
            cls._instances[signature] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[signature]


class IsStarted(Condition, metaclass=Singleton):
    def __repr__(self) -> str:
        return str(None)

    def is_met(self, left, right=None) -> bool:
        return left is None


class IsEmpty(Condition, metaclass=Singleton):
    def __repr__(self) -> str:
        return '{}'

    def is_met(self, left, right=None) -> bool:
        return left == {}


class HasKey(Condition, metaclass=Singleton):
    def __init__(self, key: str):
        self.key = key

    def __repr__(self) -> str:
        return '{%s: _}' % json.dumps(self.key)

    def is_met(self, left, right=None) -> bool:
        return self.key in left


class HasValue(Condition, metaclass=Singleton):
    def __init__(self, key: str, value: Value):
        self.key = key
        self.value = value

    def __repr__(self) -> str:
        return '{%s: %s}' % (json.dumps(self.key), json.dumps(self.value))

    def is_met(self, left, right=None) -> bool:
        return self.key in left and left[self.key] == self.value


class RootNode(metaclass=Singleton):
    def __init__(self):
        self.memory = set()
        self.children = set()

    def notify(self, payload: Payload):
        if payload.match not in self.memory:
            self.memory.add(payload.match)
            for child in self.children:
                child.notify(payload)


class AlphaNode(metaclass=Singleton):
    def __init__(self, condition: Condition, parent: RootNode, name: str = None):
        self.condition = condition
        self.memory = set()
        self.children = set()
        self.parent = parent
        parent.children.add(self)
        self.name = name

    def notify(self, payload: Payload):
        if self.condition.is_met(payload) and payload.match not in self.memory:
            self.memory.add(payload.match)
            for child in self.children:
                child.notify(payload, self)


class BetaNode(metaclass=Singleton):
    def __init__(self,
                 condition: Condition,
                 left_parent: Union[AlphaNode, 'BetaNode'],
                 right_parent: AlphaNode,
                 name: str = None):
        self.condition = condition
        self.memory = set()
        self.children = set()
        self.left_parent = left_parent
        self.right_parent = right_parent
        left_parent.children.add(self)
        right_parent.children.add(self)
        self.name = name

    def notify(self, payload: Payload, source: Union[AlphaNode, 'BetaNode']):
        if source == self.left_parent:
            for right_payload in self.right_parent.memory:
                self._notify(payload, right_payload)

        elif source == self.right_parent:
            for left_payload in self.left_parent.memory:
                self._notify(left_payload, payload)

        else:
            raise ValueError('Unknown source!')

    def _notify(self, left_payload: Payload, right_payload: Payload):
        if self.condition.is_met(left_payload, right_payload):
            payload = left_payload or right_payload
            if payload.match not in self.memory:
                self.memory.add(payload.match)
                for child in self.children:
                    child.notify(payload, self)


class LeafNode(metaclass=Singleton):
    def __init__(self, parent: Union[AlphaNode, BetaNode]):
        self.memory = set()
        self.parent = parent
        parent.children.add(self)

    def notify(self, payload: Payload, source: Union[AlphaNode, BetaNode]):
        pass


class Session:
    @staticmethod
    def build(rules) -> 'Session':
        root = RootNode()
        return Session(root)

    def __init__(self, root: RootNode):
        self.root = root

    def insert(self, item: JSON):
        self.root.notify(item)
        pass


class Rule:
    pass


class RuleBase:

    def get_session(self) -> Session:
        return Session.build(self)


if __name__ == '__main__':
    conditions = set()

    is_started = IsStarted()
    conditions.add(is_started)

    is_empty = IsEmpty()
    conditions.add(is_empty)

    has_key_k1 = HasKey('k1')
    conditions.add(has_key_k1)

    has_key_k2 = HasKey('k2')
    conditions.add(has_key_k2)

    has_value_k1_v1 = HasValue('k1', 'v1')
    conditions.add(has_value_k1_v1)

    has_value_k1_v2 = HasValue('k1', 'v2')
    conditions.add(has_value_k1_v2)

    has_value_k2_v1 = HasValue('k2', 'v1')
    conditions.add(has_value_k2_v1)

    has_value_k2_v2 = HasValue('k2', 'v2')
    conditions.add(has_value_k2_v2)

    is_started = IsStarted()
    conditions.add(is_started)

    is_empty = IsEmpty()
    conditions.add(is_empty)

    has_key_k1 = HasKey('k1')
    conditions.add(has_key_k1)

    has_key_k2 = HasKey('k2')
    conditions.add(has_key_k2)

    has_value_k1_v1 = HasValue('k1', 'v1')
    conditions.add(has_value_k1_v1)

    has_value_k1_v2 = HasValue('k1', 'v2')
    conditions.add(has_value_k1_v2)

    has_value_k2_v1 = HasValue('k2', 'v1')
    conditions.add(has_value_k2_v1)

    has_value_k2_v2 = HasValue('k2', 'v2')
    conditions.add(has_value_k2_v2)

    has_value_k3_v1 = HasValue('k3', 5)
    conditions.add(has_value_k3_v1)

    has_value_k3_v2 = HasValue('k3', -0.123)
    conditions.add(has_value_k3_v2)

    has_value_k3_v3 = HasValue('k3', True)
    conditions.add(has_value_k3_v3)

    conditions.add(RootNode())
    conditions.add(RootNode())
    conditions.add(RootNode())

    for condition in conditions:
        print(condition)
