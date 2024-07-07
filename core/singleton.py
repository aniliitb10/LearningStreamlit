from __future__ import annotations


class Singleton:
    instance_attr_str: str = '_instance'

    def __init__(self) -> None:
        class_type = type(self)  # this must be of child class
        if class_type is Singleton:
            raise TypeError('This must be called from Initializer of Child Class')

        if not hasattr(class_type, Singleton.instance_attr_str):
            # Although, this attribute can be set now, but missing this attribute shows logical error
            raise TypeError(f'There is no class level [{Singleton.instance_attr_str}] attribute')

        if getattr(class_type, Singleton.instance_attr_str) is not None:
            raise Exception("Singleton is already initialized")

        setattr(class_type, Singleton.instance_attr_str, self)

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    @classmethod
    def has_instance(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def get_instance(cls, *args, **kwargs) -> Singleton:
        raise NotImplementedError()  # as every class will have its own logic to initialize
