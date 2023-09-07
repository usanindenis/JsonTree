_cls_keys = {}


def update_keys(class_name, key):
    global _cls_keys
    if cls_keys := _cls_keys.get(class_name):
        cls_keys.update({key})
    else:
        _cls_keys[class_name] = {key}


def check_key(class_name, key):
    flag = key in _cls_keys.get(class_name, {})
    return flag


def delete_key(class_name, key):
    global _cls_keys
    if key in _cls_keys.get(class_name, {}):
        _cls_keys[class_name].remove(key)


def delete_class(class_name):
    global _cls_keys
    if class_name in _cls_keys and class_name:
        del _cls_keys[class_name]


def _check_attrs(cls_name, name):
    names = name.split('.')
    if len(names) > 1 and check_key(cls_name, names[0]):
        return names


class JsonTree(dict):
    # __keys__ = {'shape'}

    # def __new__(cls, *args, **kwargs):
    #     new_cls = super(JsonTree, cls).__new__(cls, *args, **kwargs)
    #     new_cls.__keys__ = {'shape'}
    #     return new_cls

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if new_value := self.value_to_jsontree(value):
                kwargs[key] = new_value
            update_keys(id(self), key)
        super().__init__(**kwargs)

    def __del__(self):
        try:
            delete_class(id(self))
        except Exception as e:
            ...

    def __delitem__(self, *args, **kwargs):
        if names := _check_attrs(id(self), args[0]):
            self[names[0]].delitem('.'.join(names[1:]))
        else:
            self.pop(args[0])

    def __getattribute__(self, name):
        if names := _check_attrs(id(self), name):
            return self[names[0]].__getattribute__('.'.join(names[1:]))
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if not check_key(id(self), name) and name != 'shape':
                update_keys(id(self), name)
                self[name] = JsonTree()
            return self[name]

    def __setattr__(self, name, value):
        if '.' in name:
            attrs_names = name.split('.')
            if not check_key(id(self), attrs_names[0]):
                update_keys(id(self), attrs_names[0])
                self[attrs_names[0]] = JsonTree()
            return self[attrs_names[0]].__setattr__('.'.join(attrs_names[1:]), value)
        update_keys(id(self), name)
        self[name] = value
        return value

    def __setitem__(self, name, value):
        if '.' in name:
            attrs_names = name.split('.')
            if not check_key(id(self), attrs_names[0]):
                update_keys(id(self), attrs_names[0])
                super().__setitem__(name, value)
            self[attrs_names[0]].__setitem__('.'.join(attrs_names[1:]), value)
        update_keys(id(self), name)
        super().__setitem__(name, value)

    def pop(self, k, d=None):
        if names := _check_attrs(id(self), k):
            return self[names[0]].pop('.'.join(names[1:]))
        result = super().pop(k, d)
        delete_key(id(self), k)
        return result

    def setattr(self, name, value):
        if isinstance(value, dict):
            value = JsonTree(**value)

        return self.__setattr__(name=name, value=value)

    def getattr(self, name):
        return self.__getattribute__(name=name)

    def getattribute(self, name):
        return self.__getattribute__(name)

    def delitem(self, *args, **kwargs):
        self.__delitem__(*args, **kwargs)

    def get(self, *args, **kwargs):
        name, default = args[0] if len(args) else None, args[1] if len(args) > 1 else None
        if name is None:
            return {k: self[k] for k in _cls_keys[id(self)] if k not in ('shape', id(self))}

        if names := _check_attrs(id(self), name):
            return self.get(names[0], {}).get('.'.join(names[1:])) if self.get(names[0]) else None
        return self[name] if check_key(id(self), name) else default

    def update(self, E=None, **F):
        if F:
            E.update(JsonTree(**F))
        for key, value in E.items():
            if new_value := self.value_to_jsontree(value):
                E[key] = new_value
            self.__setattr__(key, E[key])

    def value_to_jsontree(self, value):
        if isinstance(value, dict):
            return JsonTree(**value)
        elif not value:
            return
        elif isinstance(value, list):
            return [self.value_to_jsontree(i) if isinstance(value[0], dict) else i for i in value]
        else:
            return value

    def to_json(self, json_data=None):
        json_tree_to_dict = {}
        for _key, _value in self.items() if json_data is None else json_data.items():
            new_value = _value
            if isinstance(_value, JsonTree) or isinstance(_value, dict):
                new_value = self.to_json(_value)
            elif isinstance(_value, list):
                new_value = [self.to_json(i) if isinstance(i, JsonTree) or isinstance(i, dict) else i
                             for i in _value]
            json_tree_to_dict[_key] = new_value
        return json_tree_to_dict


# if __name__ == '__main__':
#     a = JsonTree(data=123)
#     a.test.pal.pap = 321
#     c = a.test.pal.pap
#     a.setattr('namet.te', 456)
#     a.update({'name.tt': 321321})
#     b = a.get('test.pal.pap')
#     cb = a.getattribute('test.pal')
#     j = a.get()
#     po = a.pop('test.pal.pap')
#
#     del a['test.pal']
#     ...
