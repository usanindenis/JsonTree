from typing import Union, List

_cls_keys = {}


def update_keys(class_name, key):
    """
    Добавление ключа в карту хэша класса
    :param class_name: хэш класса
    :param key: название ключа
    :return:
    """
    global _cls_keys
    if cls_keys := _cls_keys.get(class_name):
        cls_keys.update({key})
    else:
        _cls_keys[class_name] = {key}


def check_key(class_name, key):
    """
    Проверка наличия ключа в карте хэша класса
    :param class_name: хэш класса
    :param key: название ключа
    :return:
    """
    flag = key in _cls_keys.get(class_name, {})
    return flag


def delete_key(class_name, key):
    """
    Удаление ключа из карты хэша класса
    :param class_name: хэш класса
    :param key: название ключа
    :return:
    """
    global _cls_keys
    if key in _cls_keys.get(class_name, {}):
        _cls_keys[class_name].remove(key)


def delete_class(class_name):
    """
    Очистка карты ключей класса JsonTree при удалении
    :param class_name: хэш класса
    :return:
    """
    global _cls_keys
    if class_name in _cls_keys and class_name:
        del _cls_keys[class_name]


def _check_attrs(cls_name, name):
    """
    Проверка на рекурсивный запрос получения значения в дереве, если есть "." в пути, то нам нужно будет спускаться ниже
    по иерархии структуры JsonTree
    :param cls_name: хэш класса
    :param name: название ключа
    :return:
    """
    names = name.split('.')
    if len(names) > 1 and check_key(cls_name, names[0]):
        return names


class JsonTree(dict):

    def __init__(self, **kwargs):
        """
        Построение дерева с инициализацией карты ключей
        :param kwargs:
        """
        for key, value in kwargs.items():
            if new_value := value_to_jsontree(value):
                kwargs[key] = new_value
            update_keys(id(self), key)
        super().__init__(**kwargs)

    def __del__(self):
        """
        Удаление класса JsonTree
        :return:
        """
        try:
            delete_class(id(self))
        except Exception as e:
            ...

    def __delitem__(self, *args, **kwargs):
        """
        Удаление данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param args:
        :param kwargs:
        :return:
        """
        if names := _check_attrs(id(self), args[0]):
            self[names[0]].delitem('.'.join(names[1:]))
        else:
            self.pop(args[0])

    def __getattribute__(self, name):
        """
        Получение данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        с добавлением ячеек дерева, если таких не было найдено в дереве
        :param name:
        :return:
        """
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
        """
        Установка данных в дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param name:
        :param value:
        :return:
        """
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
        """
        Установка данных в дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param name:
        :param value:
        :return:
        """
        if '.' in name:
            attrs_names = name.split('.')
            if not check_key(id(self), attrs_names[0]):
                update_keys(id(self), attrs_names[0])
                super().__setitem__(name, value)
            self[attrs_names[0]].__setitem__('.'.join(attrs_names[1:]), value)
        update_keys(id(self), name)
        super().__setitem__(name, value)

    def pop(self, _key, default=None):
        """
        Получение данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child 
        с последующим удалением ключа из JsonTree
        :param _key: 
        :param default: 
        :return: 
        """
        if names := _check_attrs(id(self), _key):
            return self[names[0]].pop('.'.join(names[1:]), default)
        result = super().pop(_key, default)
        delete_key(id(self), _key)
        return result

    def setattr(self, name, value):
        """
        Установка данных в дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param name:
        :param value:
        :return:
        """
        if isinstance(value, dict):
            value = JsonTree(**value)

        return self.__setattr__(name=name, value=value)

    def getattr(self, name):
        """
        Получение данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param name:
        :return:
        """
        return self.__getattribute__(name=name)

    def getattribute(self, name):
        """
        Получение данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param name:
        :return:
        """
        return self.__getattribute__(name)

    def delitem(self, *args, **kwargs):
        """
        Удаление ключа из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param args:
        :param kwargs:
        :return:
        """
        self.__delitem__(*args, **kwargs)

    def get(self, *args: list, **kwargs: dict):
        """
        Получение данных из дерева JsonTree, с возможностью указать path до атрибута по примеру path_parent.path_child
        :param args: Если нет, то возвращается все данные, которые были записаны ранее, если указан путь - то значение
        данного ключа
        :param kwargs:
        :return:
        """
        name, default = args[0] if len(args) else None, args[1] if len(args) > 1 else None
        if name is None:
            return {k: self[k] for k in _cls_keys[id(self)] if k not in ('shape', id(self))}

        if names := _check_attrs(id(self), name):
            return self.get(names[0], {}).get('.'.join(names[1:]), default) if self.get(names[0]) else default
        return self[name] if check_key(id(self), name) else default

    def update(self, data_for_update: dict = None, **kwargs):
        """
        Обновление дерева JsonTree
        :param data_for_update: Данные для обновления
        :param kwargs: Дополнительные данные
        :return:
        """
        if kwargs:
            data_for_update.update(JsonTree(**kwargs))
        for key, value in data_for_update.items():
            if new_value := value_to_jsontree(value):
                data_for_update[key] = new_value
            self.__setattr__(key, data_for_update[key])

    def to_json(self, json_data=None) -> dict:
        """
        Метод конвертации класса или передаваемого JsonTree в обычный dict
        :param json_data: JsonTree объект, для перевода его в json
        :return:
        """
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


def value_to_jsontree(value: Union[dict, list]) -> Union[JsonTree, List[JsonTree]]:
    """
    Перевод json or list[json] в JsonTree
    :param value:
    :return: объект JsonTree
    """
    if isinstance(value, dict):
        return JsonTree(**value)
    elif isinstance(value, list):
        return [value_to_jsontree(i) if isinstance(value[0], dict) else i for i in value]
    else:
        return value


if __name__ == '__main__':
    a = JsonTree(data=123)
    a.test.pal.pap = 321
    c = a.test.pal.pap
    a.setattr('name.te', 456)
    a.update({'name.tt': 321321})
    b = a.get('test.pal.pap')
    b = a.get('test.pal.papp', 1231)
#     cb = a.getattribute('test.pal')
    j = a.get()
#     po = a.pop('test.pal.pap')
#
#     del a['test.pal']
    ...
