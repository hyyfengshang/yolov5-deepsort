# vim: expandtab:ts=4:sw=4


class TrackState:
    Tentative = 1
    Confirmed = 2
    Deleted = 3
    Lost = 4


class Track:
    def __init__(self, track_id, n_init, max_age, class_name=None, bbox=None):
        # self.mean = mean
        # self.covariance = covariance
        self.track_id = track_id
        self.hits = 1
        self.age = 1
        self.time_since_update = 0
        self.state = TrackState.Tentative
        self._n_init = n_init
        self._max_age = max_age
        self.class_name = class_name
        self.bbox = bbox

    def to_tlbr(self):
        return self.bbox

    def get_class(self):
        return self.class_name

    def predict(self):
        self.age += 1
        self.time_since_update += 1

    def update(self):
        self.hits += 1
        self.time_since_update = 0
        if self.state == TrackState.Tentative and self.hits >= self._n_init:
            self.state = TrackState.Confirmed

    def mark_missed(self):
        if self.state == TrackState.Tentative:
            self.state = TrackState.Deleted
        elif self.time_since_update > self._max_age:
            self.state = TrackState.Deleted

    def is_tentative(self):
        return self.state == TrackState.Tentative

    def is_confirmed(self):
        return self.state == TrackState.Confirmed

    def is_deleted(self):
        return self.state == TrackState.Deleted
