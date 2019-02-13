#!/usr/bin/env python3
# cpython 3.6

import cv2
import numpy as np

import settings
import game_strings

import os
import os.path
import sys
import time
import random
import signal


def show(img):
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyWindow('image')


def iter_contours(contours, orig, path, carry_forward=False):
    orig_bgr = cv2.cvtColor(orig, cv2.COLOR_GRAY2BGR)
    if not carry_forward:
        for (i, cnt) in enumerate(contours):
            contoured = orig_bgr.copy()
            contoured = cv2.drawContours(contoured, [cnt], 0, (0,255,0), 3)     
            cv2.imwrite(os.path.join(os.path.abspath(path), 'contour-{}.png'.format(i)), contoured)
    else:
        contoured = orig_bgr.copy()
        contoured = cv2.drawContours(contoured, contours, -1, (0,255,0), 3)
        cv2.imwrite(os.path.join(os.path.abspath(path), 'contour-all.png'), contoured) 


class Card(object):
    """Wrapper for a playing card"""
    def __init__(self, working_image):
        self.img = working_image
        self.orig = self.img    # image without any preprocessing for later reference
        self.rank = None
        self.suit = None
        self.colour = None  # 'B' (black) or 'R' (red)

    def __str__(self):
        return '{} {} {}'.format(game_strings.COLOURS[self.colour], 
            game_strings.SUITS[self.suit], game_strings.RANKS[self.rank])

    def preprocess(self, preprocessed_image=None):
        """Update the current image of the Card with a preprocessed version of the image."""
        if preprocessed_image is not None:
            self.img = preprocessed_image

    def set_rank(self, rank):
        self.rank = rank

    def set_suit(self, suit):
        """Sets the card's suit and its coloured derived from the suit"""
        self.suit = suit
        if suit == 'C' or suit == 'S':
            self.colour = 'B'
        elif suit == 'H' or suit == 'D':
            self.colour = 'R'


class DetectedCard(Card):
    def __init__(self, working_image, contour, original_image):
        self.contour = contour
        self.orig = original_image
        super().__init__(working_image)

    def get_original(self):
        if self.orig is not None:
            return self.orig
        else:
            return self.img

    def preprocess(self, width_norm, height_norm):
        img = self.img     
        invert = cv2.bitwise_not(img)
        size = cv2.resize(invert, (width_norm, height_norm))
        super().preprocess(size)

    def get_relative_rectangle(self):
        x, y, w, h = cv2.boundingRect(self.contour)
        x1, x2, y1, y2 = x, x+w, y, y+h
        return [(x1, y1), (x2, y2)]

    def get_relative_centroid(self):
        M = cv2.moments(self.contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        return [(cx, cy)]

    def get_relative_vertices(self):
        x, y, w, h = cv2.boundingRect(self.contour)
        return [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]


class TrainingCard(Card):
    def preprocess(self):
        img = self.img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray ,(5,5), 0)
        ret, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        super().preprocess(thresh)


class Trainer(object):
    def __init__(self):
        self.training_cards = []

    def __iter__(self):
        for card in self.training_cards:
            yield card

    def __str__(self):
        b = []
        for card in self:
            b.append(str(card))
        return ', '.join(b)

    def add_card(self, card):
        self.training_cards.append(card)

    def show_cards(self):
        for card in train.training_cards:
            show(card.img)
            input('Press enter to continue')


class LayoutDetector(object):
    """Low-level detector for part of the image"""

    def __init__(self, target_image):
        self.img = target_image
        self.orig = self.img    # original image as a reference for later
        self.cards = None

    def __str__(self):
        b = []
        b.append('{} :'.format(self.__class__))
        for card in self.cards:
            b.append(str(card))
        return ', '.join(b)

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        for card in self.cards:
            yield card

    def get_original(self):
        if self.orig is not None:
            return self.orig
        else:
            return self.img

    def preprocess(self, preprocessed_image=None):
        """Preprocessor for the layout's image"""
        if preprocessed_image is not None:
            self.img = preprocessed_image

    def localise_cards(self, full_card_area, area_margin):
        contours, hierarchy = cv2.findContours(self.img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        matching_cnts = list(filter(lambda cnt: self.filter_contour_noise(cnt, full_card_area, area_margin), contours))
        self.cards = []
        for cnt in matching_cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            x1, x2, y1, y2 = x, x+w, y, y+h # get vetrices of the contour bounding rectangle
            card_img = self.img[y1:y2, x1:x2]
            card_orig = self.orig[y1:y2, x1:x2]
            card = DetectedCard(card_img, cnt, card_orig)
            self.cards.append(card)
        return self.cards

    @staticmethod
    def filter_contour_noise(contour, required_area, area_margin):
        contour_area = cv2.contourArea(contour)
        area_difference = (abs(required_area-contour_area)/required_area) * 100
        return area_difference < area_margin

    def recognise_cards(self, trainer):
        for recog_card in self.cards:
            differences = sorted(trainer, key=lambda training_card: self.compute_card_difference(recog_card, training_card))
            top_match = differences[0]
            recog_card.set_rank(top_match.rank)
            recog_card.set_suit(top_match.suit)
        return self.cards

    @staticmethod
    def compute_card_difference(card1, card2):
        return np.sum(cv2.absdiff(card1.img, card2.img))


class TableauxDetector(LayoutDetector):
    def preprocess(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        ret, thresh = cv2.threshold(blur, 226, 255, cv2.THRESH_BINARY)
        super().preprocess(thresh)


class FoundationDetector(LayoutDetector):
    def preprocess(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        super().preprocess(thresh)


class StockDetector(LayoutDetector):
    def preprocess(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)
        ret, thresh = cv2.threshold(blur, 226, 255, cv2.THRESH_BINARY)
        super().preprocess(thresh)


class CardDetector(object):
    """High level settings/environment for detecting full cards"""

    def __init__(self, training_set_directory_path='', fully_visible_card_area=0, partial_visibility_card_area=0, 
            allowed_area_difference_margin=0, training_image_height=0, training_image_width=0):
        self.FULL_CARD_AREA = fully_visible_card_area
        self.PART_CARD_AREA = partial_visibility_card_area
        self.AREA_MARGIN = allowed_area_difference_margin
        self.TRAIN_W = training_image_width
        self.TRAIN_H = training_image_height
        self.TRAIN_PATH = training_set_directory_path
        self.gameshot = None

    def __str__(self):
        b = []
        for obj, ROI in self.layouts:
            b.append(str(obj))
        return '\n'.join(b)

    def __len__(self):
        total_cards = 0
        for obj, ROI in self.layouts:
            total_cards += len(obj)
        return total_cards

    def set_gameshot(self, image):
        self.gameshot = image

    def partition_layout(self, partition_scheme):
        if self.gameshot is not None:
            layouts = []
            for scheme in partition_scheme:
                cls = scheme[0]         # layout class to use
                ROI = scheme[1:]        # region of interest coordinates, to be re-used later
                x1, y1, x2, y2 = ROI
                crop = self.gameshot[y1:y2, x1:x2]
                layout = cls(crop)
                layouts.append((layout, ROI))
            self.layouts = layouts

    def load_trainer(self):
        training_directory = self.TRAIN_PATH
        training_directory = os.path.abspath(training_directory)
        trainer = Trainer()
        for image_name in os.listdir(training_directory):
            img = cv2.imread(os.path.join(training_directory, image_name))
            training_card = TrainingCard(img)
            training_card.preprocess()
            suit, rank = os.path.splitext(image_name)[0].split('_')
            training_card.set_rank(rank)
            training_card.set_suit(suit)
            trainer.add_card(training_card)
        self.trainer = trainer

    def detect_cards(self):
        all_cards = []
        for obj, ROI in self.layouts:
            obj.preprocess()
            cards = obj.localise_cards(full_card_area=self.FULL_CARD_AREA, area_margin=self.AREA_MARGIN)
            for card in cards:
                card.preprocess(self.TRAIN_W, self.TRAIN_H)
            all_cards += obj.recognise_cards(self.trainer)
        return all_cards

    def draw_detected(self):
        drawable = self.gameshot.copy()
        # drawable = cv2.cvtColor(drawable, cv2.COLOR_GRAY2BGR)
        for layout in self.layouts:
            obj, ROI = layout
            for card in obj:
                coordinates = self.restore_roi(card.get_relative_rectangle(), ROI)
                x1, y1 = coordinates[0]
                x2, y2 = coordinates[1]
                drawable = cv2.rectangle(drawable, (x1, y1), (x2, y2), (0,255,0), 3)
                # margin = 0.1
                # lower_x, upper_x = int(x1+x1*margin), int(x2)
                # lower_y, upper_y = int(y1+y1*margin), int(y2)
                # random_x = random.randint(lower_x, upper_x)
                # random_y = random.randint(lower_y, upper_y)
                cx, cy = self.restore_roi(card.get_relative_centroid(), ROI)[0]
                drawable = cv2.putText(drawable, str(card), (x1, cy), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2, cv2.LINE_8)
        return drawable

    @staticmethod
    def restore_roi(relative_points, ROI):
        absolute_points = []
        for p in relative_points:
            x1, y1 = p
            rx1, ry1, rx2, ry2 = ROI
            absolute_points.append((x1+rx1, y1+ry1))
        return absolute_points

    @staticmethod
    def _get_touchpoint(card, ROI):
        return CardDetector.restore_roi(card.get_relative_centroid(), ROI)[0]

    def get_touchpoints(self):
        touchpoints = []
        for layout in self.layouts:
            obj, ROI = layout
            for card in obj:
                touchpoints.append(self._get_touchpoint(card, ROI))
        return touchpoints


def write_touchpoints(touchpoint_list, path):
    with open(path, 'w') as f:
        for touchpoint in touchpoint_list:
            f.write('{} {}\n'.format(touchpoint[0], touchpoint[1]))


def main():
    print('Starting Image Detector script ...')
    # initialise the detector object
    layout_partition_scheme = [
        [TableauxDetector, 5, 360, 1075, 1600, ],
        [FoundationDetector, 5, 100, 615, 330, ],
        [StockDetector, 650, 100, 920, 330, ],
    ]
    det = CardDetector(training_set_directory_path=settings.TRAINING_DATA_PATH, fully_visible_card_area=29700, allowed_area_difference_margin=10.0, 
        training_image_width=146, training_image_height=226)
    det.load_trainer()

    # begin 'read screenshot - write touchpoints' loop
    while True:
        # block until the Android script has a gameshot (screenshot) available
        # poll for gameshot check file
        while not os.path.isfile(settings.GAMESHOT_CHECK_PATH):
            time.sleep(1)
        os.remove(settings.GAMESHOT_CHECK_PATH) # clean up for next run

        screenshot = cv2.imread(settings.GAMESHOT_PATH)
        print('Press any key when image window is active to close the image / continue')
        print('Original image ...')
        show(screenshot)

        print('Localising and recognising full cards...')
        det.set_gameshot(screenshot)
        det.partition_layout(layout_partition_scheme)
        cards = det.detect_cards()
        print('I see {} cards'.format(len(det)))
        for card in cards:
            print('I see a {}'.format(str(card)))
            show(card.get_original())  # this does not always show the full colour crop, only the preprocessed version

        print('Detected image ...')
        recognised_screenshot = det.draw_detected()
        show(recognised_screenshot)

        print('Getting coordinates to interact with ...')
        touchpoints = det.get_touchpoints()
        print(touchpoints)
        print('Writing coordinates ...')
        write_touchpoints(touchpoints, settings.TOUCHPOINTS_PATH)
        with open(settings.TOUCHPOINTS_CHECK_PATH, 'w') as f:   # create a check file to synchronise with the Android script
            pass
        print('Done writing')


if __name__ == '__main__':
    main()
