import cv2
import pytesseract
import matplotlib.pyplot as plt

#fonte: https://medium.com/@siromermer/extracting-text-from-images-ocr-using-opencv-pytesseract-aa5e2f7ad513

# Configuração do Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class ImageTextExtractor:
    def __init__(self, imagem_path, save_dir):
        self.imagem_path = imagem_path
        self.save_dir = save_dir

    def ler_imagem(self):
        return cv2.imread(self.imagem_path)

    def converter_para_cinza(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def aplicar_threshold(self, gray_img):
        return cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]

    def aplicar_dilatacao(self, thresh_img, kernel_size=(25, 25)):
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        return cv2.dilate(thresh_img, rect_kernel, iterations=1)

    def encontrar_contornos(self, dilated_img):
        return cv2.findContours(dilated_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

    def extrair_texto_de_contornos(self, contornos, gray_img):
        cnt_list = []
        for cnt in contornos:
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = gray_img[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped, lang='por')
            cnt_list.append((x, y, text))
        return sorted(cnt_list, key=lambda item: item[1])

    def concatenar_texto(self, sorted_text_list):
        return "".join(text for _, _, text in sorted_text_list)

    def salvar_e_mostrar_imagens(self, imagens):
        for nome, img in imagens.items():
            cv2.imwrite(f"{self.save_dir}\\{nome}.png", img)
            cv2.imshow(nome, img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def extrair_texto(self):
        img = self.ler_imagem()
        gray_img = self.converter_para_cinza(img)
        thresh_img = self.aplicar_threshold(gray_img)
        dilated_img = self.aplicar_dilatacao(thresh_img)
        contornos = self.encontrar_contornos(dilated_img)
        sorted_text_list = self.extrair_texto_de_contornos(contornos, gray_img)
        texto_extraido = self.concatenar_texto(sorted_text_list)
        imagens = {
            'dilation': cv2.resize(dilated_img, (0, 0), fx=0.4, fy=0.4),
            'gray': cv2.resize(gray_img, (0, 0), fx=0.4, fy=0.4)
        }
        self.salvar_e_mostrar_imagens(imagens)
        return texto_extraido