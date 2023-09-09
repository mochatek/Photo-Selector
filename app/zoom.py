class Zoomscale:
    def __init__(self, min: int, max: int):
        self.__val = 1
        self.__min = min
        self.__max = max
        self.__has_changed = True

    def up(self):
        cur_level = self.__val
        next_level = min(self.__max, cur_level + 1)
        if next_level == 0:
            next_level = 1
        if cur_level != next_level:
            self.__val = next_level
            self.__has_changed = True
        else:
            self.__has_changed = False

    def down(self):
        cur_level = self.__val
        prev_level = max(cur_level - 1, self.__min)
        if prev_level == 0:
            prev_level = -1
        if cur_level != prev_level:
            self.__val = prev_level
            self.__has_changed = True
        else:
            self.__has_changed = False

    def reset(self):
        self.__val = 1

    @property
    def has_changed(self):
        return self.__has_changed

    @property
    def at_base(self):
        return self.__val == 1
