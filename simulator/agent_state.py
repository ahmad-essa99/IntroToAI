
class AgentState:

    def __init__(self, current_vertex, is_equipped, num_of_people_picked, busy_time=0,
                 in_progress_action=None, traverse_dest=None):
        self._current_vertex = current_vertex
        self._is_equipped = is_equipped
        self._num_of_people_picked = num_of_people_picked
        self._busy_time = busy_time

        self.in_progress_action = in_progress_action
        self.traverse_dest = traverse_dest

    def copy(self):
        return AgentState(
            current_vertex=self._current_vertex,
            is_equipped=self._is_equipped,
            num_of_people_picked=self._num_of_people_picked,
            busy_time=self._busy_time,
            in_progress_action=self.in_progress_action,
            traverse_dest=self.traverse_dest,
        )

    def get_key(self):
        return (
            self._current_vertex,
            self._is_equipped,
            self._num_of_people_picked,
            self._busy_time,
            self.in_progress_action,
            self.traverse_dest
        )


