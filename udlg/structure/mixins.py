# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.mixins
    :synopsis: Mixins and helpers for internal use
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from itertools import chain
from operator import eq, and_
from functools import reduce, partial


class StructureExtendMixin(object):
    _fields_ = []

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "Wrong type match: `%r`, requested `%r` instead" % (
                    type(other), type(self))
            )

        if self._fields_ != other._fields_:
            return False

        get_self = partial(getattr, self)
        get_other = partial(getattr, other)
        self_fields = map(get_self, (x for x, *_ in self._fields_))
        other_fields = map(get_other, (x for x, *_ in other._fields_))

        def equal(*arguments):
            return reduce(eq, chain(*arguments))

        return reduce(and_, map(equal, zip(self_fields, other_fields)))
