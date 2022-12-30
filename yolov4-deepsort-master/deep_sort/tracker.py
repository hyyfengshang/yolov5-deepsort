# vim: expandtab:ts=4:sw=4
from __future__ import absolute_import
import numpy as np
from . import kalman_filter
from . import linear_assignment
from . import iou_matching
from .track import Track
from .unites import get_iou, get_metric


class Tracker:
    def __init__(self, feature_model, max_distance=0.7, iou_thres=0.8, max_age=60, n_init=3):
        # self.metric = metric
        self.feature_model = feature_model
        self.max_distance = max_distance
        self.max_age = max_age
        self.iou_thres = iou_thres
        self.n_init = n_init

        # self.kf = kalman_filter.KalmanFilter()
        self.image = None
        self.last_image = None
        self.track_ids = []
        self.tracks = []
        self.confirmed_tracks = []
        self.lost_tracks = []
        self.tentative_tracks = []
        self.next_id = 1

        self.matches = []
        self.match_tracks = []
        self.match_detections = []
        self.unmatched_tracks = []
        self.unmatched_detections = []
        self.detections = []

    def predict(self, image):
        self.last_image = self.image
        self.image = image
        for track in self.tracks:
            track.predict()

    def update(self, detections):
        # Run matching cascade.
        self.detections = detections
        matches, unmatched_tracks, unmatched_detections = self._match()

        # Update track set.
        for track_idx, detection_idx in matches:
            self.tracks[track_idx].update(detections[detection_idx])
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()
        for detection_idx in unmatched_detections:
            self._initiate_track(detections[detection_idx])
        self.tracks = [t for t in self.tracks if not t.is_deleted()]

    def _match(self):
        # step1 使用iou匹配
        self.iou_match()
        # 对剩余目标进行特征匹配
        self.feature_match()
        # 获取为匹配的目标
        self.get_unmatched()
        return self.matches, self.unmatched_tracks, self.unmatched_detections

    def _initiate_track(self, detection):
        class_name = detection.get_class()
        bbox = detection.to_tlbr()
        if self.next_id in self.track_ids:
            self.next_id += 1
        self.tracks.append(Track(self.next_id, self.n_init, self.max_age, class_name, bbox))
        self.track_ids.append(self.next_id)

    def iou_match(self):
        for track_idx, track in enumerate(self.tracks):
            for detection_idx, detection in enumerate(self.detections):
                track_box = track.to_tlbr()
                detection_box = detection.to_tlbr()
                iou = get_iou(track_box, detection_box)
                if iou > self.iou_thres:
                    if track_idx not in self.match_tracks and detection_idx not in self.match_detections:
                        match = [track_idx, detection_idx]
                        self.matches.append(match)
                        self.match_tracks.append(track_idx)
                        self.match_detections.append(detection_idx)
                    else:  # 判断为重叠目标
                        last_detection_idx = self.matches[self.matches[:0] == track_idx][1]
                        metric1 = self.feature_compare(track_box, detection_box)
                        metric2 = self.feature_compare(track_box, last_detection_idx)
                        if metric1 < metric2:
                            if detection_idx not in self.match_detections:
                                self.matches[self.matches[:0] == track_idx] = [track_idx, detection_idx]
                                if last_detection_idx in self.match_detections:
                                    self.match_detections.remove(last_detection_idx)

    def feature_match(self):
        for track_idx, track in enumerate(self.tracks):
            if track_idx in self.match_tracks:
                continue
            for detection_idx, detection in enumerate(self.detections):
                if detection_idx in self.match_detections:
                    continue
                track_box = track.to_tlbr()
                detection_box = detection.to_tlbr()
                metric = self.feature_compare(track_box, detection_box)
                if metric < self.max_distance:
                    if track_idx not in self.match_tracks and detection_idx not in self.match_detections:
                        match = [track_idx, detection_idx]
                        self.matches.append(match)
                        self.match_tracks.append(track_idx)
                        self.match_detections.append(detection_idx)

    def get_unmatched(self):
        for track_idx, track in enumerate(self.tracks):
            if track_idx not in self.match_tracks and track_idx not in self.unmatched_tracks:
                self.unmatched_tracks.append(track_idx)
        for detection_idx, detection in enumerate(self.detections):
            if detection_idx not in self.match_detections and detection_idx not in self.unmatched_detections:
                self.unmatched_detections.append(detection_idx)

    def feature_compare(self, track_box, detection_box):
        track_img = self.last_image[track_box]
        detection_img = self.image[detection_box]
        track_feature = self.feature_model.predict(track_img)
        detection_feature = self.feature_model.predict(detection_img)
        metric = get_metric(track_feature, detection_feature)
        return metric
