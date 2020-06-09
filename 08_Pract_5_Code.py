from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import dicom
from scipy.interpolate import RectBivariateSpline
from scipy import ndimage as ndi
from tqdm import tqdm


class Image:
    def __init__(self, name):
        self.ds = dicom.read_file(name)
        self.bits = self.ds[0x280100].value
        self.data_type = self.image_type()
        self.image_pixels = self.normalize(self.ds.pixel_array)
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.bordered = False

    def image_type(self):
        intercept = self.ds[0x281052].value
        slope = self.ds[0x281053].value
        if intercept != 0 and slope != 1:
            return GL_FLOAT
        else:
            return GL_UNSIGNED_BYTE if self.bits == 8 else GL_UNSIGNED_SHORT

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()

    def draw(self):
        pixels_to_draw = np.copy(self.image_pixels)
        self.drawTexture(pixels_to_draw)
        if self.bordered:
            points = self.activation_border(pixels_to_draw)
            self.drawPoints(points)
        glutSwapBuffers()

    def drawPoints(self, points):
        size = len(points)
        glPointSize(5)
        glBegin(GL_POINTS)
        glColor3f(1, 0, 0)
        for i in range(size):
            glVertex2f(points[i, 1], points[i, 0])
        glEnd()

        glBegin(GL_LINES)
        for i in range(size-1):
            glVertex2f(points[i, 1], points[i, 0])
            glVertex2f(points[i, 1], points[i, 0])
            if (i == size-1):
                glVertex2f(points[size-1, 1], points[size-1, 0])
                glVertex2f(points[0, 1], points[0, 0])
        glEnd()

    def activation_border(self, pixels):
        s = np.linspace(0, 2 * np.pi, 15)
        r = np.linspace(10, 21, len(s))*s
        c = list(np.linspace(10, 35, len(s))*s+10)
        init = np.array([r, c]).T
        snake = self.active_contour(self.gaussian(pixels, 5), init,
                                    alpha=0.015, beta=10, gamma=0.001)
        return snake

    def active_contour(self, image, snake, alpha=100, beta=90, gamma=1001, max_px_move=4.0,
                       max_iterations=10, convergence=0.0001):

        snake_xy = snake[:, ::-1]
        convergence_order = 10
        img = image / image.max()
        intp = RectBivariateSpline(np.arange(img.shape[1]), np.arange(img.shape[0]), img.T, kx=2, ky=2, s=0)

        x, y = snake_xy[:, 0].astype(np.float), snake_xy[:, 1].astype(np.float)
        n = len(x)
        xsave = np.empty((convergence_order, len(x)))
        ysave = np.empty((convergence_order, len(x)))

        a = np.roll(np.eye(n), -1, axis=0) + np.roll(np.eye(n), -1, axis=1) - 2 * np.eye(n)
        b = np.roll(np.eye(n), -2, axis=0) + np.roll(np.eye(n), -2, axis=1) - 4 * np.roll(np.eye(n), -1, axis=0) - \
            4 * np.roll(np.eye(n), -1, axis=1) + 6 * np.eye(n)
        A = -alpha * a + beta * b
        inv = np.linalg.inv(A + gamma * np.eye(n))

        # energy minimization:
        for i in tqdm(range(max_iterations)):
            fx, fy = intp(x, y, dx=1, grid=False), intp(x, y, dy=1, grid=False)
            xn, yn = inv @ (gamma * x + fx), inv @ (gamma * y + fy)
            dx, dy = max_px_move * np.tanh(xn - x), max_px_move * np.tanh(yn - y)
            x += dx
            y += dy
            dist = np.min(np.max(np.abs(xsave - x[None, :]) + np.abs(ysave - y[None, :]), 1))
            if dist < convergence:
                break

        return np.stack([y, x], axis=1)

    def gaussian(self, image, sigma=1):
        image = image / np.iinfo(image.dtype).max
        output = np.empty_like(image)
        ndi.gaussian_filter(image, sigma, output=output)
        return output

    def normalize(self, pixels):
        min, max = pixels.min(), pixels.max()
        new_min, new_max = 0, np.iinfo(pixels.dtype).max
        arr = (pixels - min)/(max - min)*(new_max - new_min)+new_min
        return arr.astype(int)

    def drawTexture(self, data):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, self.data_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(0.0, 0.0)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width, 0.0)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width, self.height)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(0.0, self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == 'b':
            self.bordered = not self.bordered
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_5 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    image = Image("Data-Pract/Lab#2-#6 - DICOM_single_16bits/DICOM_Image_16b.dcm")
    initWindow(image.width, image.height)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutMainLoop()


if __name__ == '__main__':
    main()
