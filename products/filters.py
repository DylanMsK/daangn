from datetime import datetime
from products import models


class ProductFilter:
    def __init__(self, filter_args):
        self.filter_args = filter_args

    def general_filter(self):
        pass

    def car_filter(self):
        min_year = self.filter_args.get("min_year")
        max_year = self.filter_args.get("max_year")
        min_distance = self.filter_args.get("min_driven_distance")
        max_distance = self.filter_args.get("max_driven_distance")
        smoking = self.filter_args.get("smoking")

        filter_args = {}

        if min_year is not None:
            filter_args["year__gte"] = min_year
        else:
            filter_args["year__gte"] = models.Car.MIN_YEAR

        if max_year is not None:
            filter_args["year__lte"] = max_year
        else:
            filter_args["year__lte"] = datetime.now().year

        if min_distance is not None:
            filter_args["driven_distance__gte"] = min_distance
        else:
            filter_args["driven_distance__gte"] = models.Car.MIN_DRIVEN_DISTANCE

        if max_distance is not None:
            filter_args["driven_distance__lte"] = max_distance
        else:
            filter_args["driven_distance__lte"] = models.Car.MAX_DRIVEN_DISTANCE
        if smoking is not None:
            if smoking != "total":
                filter_args["smoking"] = smoking

        return filter_args
