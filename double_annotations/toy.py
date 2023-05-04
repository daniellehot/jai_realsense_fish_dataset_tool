import cv2 as cv

class Toy():
    def __init__(self):
        self.img_template = cv.imread("image.png")
        self.get_resized_dimension(scale_percent=50)
        self.color = (0, 0, 255)

        self.start_points = []
        self.end_points = []
        
        self.clicked = False
        self.clicked_idx = None


    def get_resized_dimension(self, scale_percent):
        width = int(2464 * scale_percent / 100)
        height = int(2056 * scale_percent / 100)
        self.resized_dim = (width, height)


    def show(self):
        self.window_title = "jai"
        cv.namedWindow(self.window_title, cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback(self.window_title, self.annotate)
        self.scaled_img = cv.resize(self.img_template, self.resized_dim)
        self.draw_annotations()
        cv.imshow(self.window_title, self.scaled_img)


    def annotate(self, event, x, y, flags, param):
        if not self.clicked and event == cv.EVENT_LBUTTONDOWN:
            self.start_points.append((x, y))
            self.end_points.append((x, y))
            self.clicked = True
            self.clicked_idx = self.end_points.index((x, y))
        elif self.clicked:
            self.end_points[self.clicked_idx] = (x, y)
            if event == cv.EVENT_LBUTTONUP:
                self.clicked = False
                self.clicked_idx = None


    def draw_annotations(self):
        for (start_point, end_point) in zip(self.start_points, self.end_points):
            cv.circle(self.scaled_img, start_point, 10, self.color, 2)
            cv.arrowedLine(self.scaled_img, start_point, end_point, self.color, 2)


if __name__=="__main__":
    toy = Toy()
    while True:
        toy.show()
        k = cv.waitKey(1)
        if k==27:    # Esc key to stop
            break