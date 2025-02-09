import cv2
import numpy as np

keypoint_map = {
    "Nose": 0,
    "Neck": 1,
    "RShoulder": 2,
    "RElbow": 3,
    "RWrist": 4,
    "LShoulder": 5,
    "LElbow": 6,
    "LWrist": 7,
    "MidHip": 8,
    "RHip": 9,
    "RKnee": 10,
    "RAnkle": 11,
    "LHip": 12,
    "LKnee": 13,
    "LAnkle": 14,
    "REye": 15,
    "LEye": 16,
    "REar": 17,
    "LEar": 18,
    "LBigToe": 19,
    "LSmallToe": 20,
    "LHeel": 21,
    "RBigToe": 22,
    "RSmallToe": 23,
    "RHeel":24,
    "Background":25
}

def plot_im_keypoints(bodyKeypoints, im_path, title=None):
    im = cv2.cvtColor(cv2.imread(im_path), cv2.COLOR_BGR2RGB)
    height, width, _ = im.shape

    ax = plt.gca()
    plt.imshow(im)
    plt.axis('off')

    for x, y, c in bodyKeypoints:
        circle = plt.Circle((x*width, y*height), radius=2, alpha=c)
        ax.add_patch(circle)

    plt.title(title)
    plt.show()

class Coord:
    def __init__(self, x, y, height=2, width=1):
        self.x = x * width
        self.y = y * height

    def __str__(self):
        return '({},{})'.format(self.x, self.y)

    def isNull(self):
        return (self.x == 0 or self.y == 0)

def distance(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def get_xy(keypoints, name):
    x, y, c = keypoints[0][keypoint_map[name]]
    return Coord(x, y)

def get_pose_score(bodyKeypoints, eps=1e-4):
    RShoulder = get_xy(bodyKeypoints, 'RShoulder')
    LShoulder = get_xy(bodyKeypoints, 'LShoulder')
    RHip = get_xy(bodyKeypoints, 'RHip')
    LHip = get_xy(bodyKeypoints, 'LHip')

    if RShoulder.isNull() or LShoulder.isNull():
        return None
    # if abs(RShoulder.x - LShoulder.x) < 0.01:
    #     print('69>', RShoulder, LShoulder)

    mu = -(RShoulder.x - LShoulder.x) / (eps + abs(RShoulder.x - LShoulder.x))
    torso_width = distance(RShoulder, LShoulder)
    torso_height = 0.5*(distance(RShoulder,RHip)+distance(LShoulder,LHip))+eps

    return (mu + eps) *  torso_width / torso_height

def get_theta(bodyKeypoints):
    pose_score = get_pose_score(bodyKeypoints)
    if not pose_score:
        return None
    cos = min(max(pose_score, -1), 1)
    return np.arccos(cos)

def get_pose(bodyKeypoints, n=3):
    """
    Get pose orientation of image
    Args:
        - name: file name
        - n: number of possible pose orientations (0=front, `n-1`=back)
    """
    theta = get_theta(bodyKeypoints)
    if not theta:
        return -1

    for i in range(n):
        if theta < (i + 1) * np.pi / n:
            return i
    # back
    return n - 1

def get_pose_from_name(keypoint_data, name, n_poses):
    if name in keypoint_data.keys():
        return get_pose(keypoint_data[name], n_poses)
    return -1
