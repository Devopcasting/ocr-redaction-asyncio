import cv2

class ProcessJPEGImages:
    def __init__(self, src_image_path, dest_image_path) -> None:

        # Image path
        self.src_image_path = src_image_path
        self.dest_image_path = dest_image_path
       
        # Open image
        self.image = cv2.imread(self.src_image_path)


        # get key values from config.ini
        self.sigma_x = 1
        self.sigma_y = 1
        self.sig_alpha = 1.5
        self.sig_beta = -0.2
        self.gamma = 0

    
    # func: denoising colored image
    def denoise_image(self):
        return cv2.fastNlMeansDenoisingColored(self.image, None, 10, 10, 7, 21)
    
    # func: convert image to gray
    def gray_image(self):
        return cv2.cvtColor(self.denoise_image(), cv2.COLOR_BGR2GRAY)
    
    # func: optimize Gaussian blurring
    def gaussian_blur(self):
        return cv2.GaussianBlur(self.gray_image(), (5,5), sigmaX=self.sigma_x, sigmaY=self.sigma_y)
    
    # func: optimize sharpeness
    # blend or mix two images together by assigning a weight to each image
    # alpah and beta control the weights of the two images
    # formula = alpha * image1 + beta * image2 +gamma
    def processed_image(self):
        try:
            image1 = self.gray_image()
            image2 = self.gaussian_blur()
            sharpened_image = cv2.addWeighted(image1, self.sig_alpha, image2, self.sig_beta, self.gamma)
            sharpened_image_gray = cv2.cvtColor(sharpened_image, cv2.COLOR_GRAY2BGR)
            cv2.imwrite(self.dest_image_path , sharpened_image_gray)
            return True
        except Exception as error:
            return False