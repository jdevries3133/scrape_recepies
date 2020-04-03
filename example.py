class Simple:
    def __init__(self, name):
        self.name = name


names = [
    'jack',
    'forrest',
    'sam',
    'nick'
]

cls_instances = []
for name in range(1000):
    cls_instance = Simple(name)
    cls_instances.append(cls_instance)
