# _*_ coding: UTF-8 _*_


class Constant(object):
    """
    自定义常量类
    1.常量Key名称必需大写
    2.常量value定义完成不可修改
    """

    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        if self.__dict__.keys():
            raise self.ConstError('Can not change const {0}'.format(key))
        if not key.isupper():
            raise self.ConstCaseError('Const name {0} is not all uppercase'.format(key))


# sys.modules[__name__] = Constant()
