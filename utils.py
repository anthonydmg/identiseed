# This is a sample Python script.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
import cv2
import os


"""
filenames=['ANC-399-1',
           'ANC-399-2',
           'ANC-526-1',
           'ANC-526-2',
           'APUC-264-1',
           'APUC-264-2',
           'AREQ-155-1',
           'AREQ-155-2',
           'AYAC-118-1',
           'AYAC-118-2',
           'CAJ-63-1',
           'CAJ-63-2',
           'CAJA-54-1',
           'CAJA-54-2',
           'JUN-220-1',
           'JUN-220-2',
           'LBQUE-14',
           'LIM-102-1',
           'LIM-102-2',
           'PUN-16-1',
           'PUN-16-2',
           'SMTI-131-1',
           'SMTI-131-2',
           'UCAY-21']
"""

filenames=['LIB-105-01',
           'LIB-105-02',
           'LIB-175-01',
           'LIB-175-02',
           'AYAC-05-01',
           'AYAC-05-02',
           'AMAZ-46-01',
           'AMAZ-46-02',
           'SMTIN-62-01',
           'SMTIN-62-02',
           'LOR-23-01',
           'LOR-23-02',
           'HVCA-1-01',
           'HVCA-1-02',
           'LIB-54-01',
           'LIB-54-02',
           'CRMOROCHO-III-01',
           'CRMOROCHO-III-02',
           'HCO-188-01',
           'HCO-188-02',
           'APUC-272-01',
           'APUC-272-02',
           'UCAY-7-01',
           'UCAY-7-02',
           'ANC-399-1']

#row_column= [[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[6,9],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[6,9]]
row_column= [[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5],[5,5], [5,5]]
long_onda = [395.62, 397.6728, 399.7256, 401.7784, 403.8312, 405.884, 407.9368, 409.9896, 412.0424, 414.0952, 416.148, 418.2008, 420.2536, 422.3064, 424.3592, 426.412, 428.4648, 430.5176, 432.5704, 434.6232, 436.676, 438.7288, 440.7816, 442.8344, 444.8872, 446.94, 448.9928, 451.0456, 453.0984, 455.1512, 457.204, 459.2568, 461.3096, 463.3624, 465.4152, 467.468, 469.5208, 471.5736, 473.6264, 475.6792, 477.732, 479.7848, 481.8376, 483.8904, 485.9432, 487.996, 490.0488, 492.1016, 494.1544, 496.2072, 498.26, 500.3128, 502.3656, 504.4184, 506.4712, 508.524, 510.5768, 512.6296, 514.6824, 516.7352, 518.788, 520.8408, 522.8936, 524.9464, 526.9992, 529.052, 531.1048, 533.1576, 535.2104, 537.2632, 539.316, 541.3688, 543.4216, 545.4744, 547.5272, 549.58, 551.6328, 553.6856, 555.7384, 557.7912, 559.844, 561.8968, 563.9496, 566.0024, 568.0552, 570.108, 572.1608, 574.2136, 576.2664, 578.3192, 580.372, 582.4248, 584.4776, 586.5304, 588.5832, 590.636, 592.6888, 594.7416, 596.7944, 598.8472, 600.9, 602.9528, 605.0056, 607.0584, 609.1112, 611.164, 613.2168, 615.2696, 617.3224, 619.3752, 621.428, 623.4808, 625.5336, 627.5864, 629.6392, 631.692, 633.7448, 635.7976, 637.8504, 639.9032, 641.956, 644.0088, 646.0616, 648.1144, 650.1672, 652.22, 654.2728, 656.3256, 658.3784, 660.4312, 662.484, 664.5368, 666.5896, 668.6424, 670.6952, 672.748, 674.8008, 676.8536, 678.9064, 680.9592, 683.012, 685.0648, 687.1176, 689.1704, 691.2232, 693.276, 695.3288, 697.3816, 699.4344, 701.4872, 703.54, 705.5928, 707.6456, 709.6984, 711.7512, 713.804, 715.8568, 717.9096, 719.9624, 722.0152, 724.068, 726.1208, 728.1736, 730.2264, 732.2792, 734.332, 736.3848, 738.4376, 740.4904, 742.5432, 744.596, 746.6488, 748.7016, 750.7544, 752.8072, 754.86, 756.9128, 758.9656, 761.0184, 763.0712, 765.124, 767.1768, 769.2296, 771.2824, 773.3352, 775.388, 777.4408, 779.4936, 781.5464, 783.5992, 785.652, 787.7048, 789.7576, 791.8104, 793.8632, 795.916, 797.9688, 800.0216, 802.0744, 804.1272, 806.18, 808.2328, 810.2856, 812.3384, 814.3912, 816.444, 818.4968, 820.5496, 822.6024, 824.6552, 826.708, 828.7608, 830.8136, 832.8664, 834.9192, 836.972, 839.0248, 841.0776, 843.1304, 845.1832, 847.236, 849.2888, 851.3416, 853.3944, 855.4472, 857.5, 859.5528, 861.6056, 863.6584, 865.7112, 867.764, 869.8168, 871.8696, 873.9224, 875.9752, 878.028, 880.0808, 882.1336, 884.1864, 886.2392]

path = '/home/amiranda/Documentos/Proyectos/identiseed/sample_image/'
def show_image_rgb(filename,plot=True):
    frame_BGR = cv2.imread(path+filename+'-RGB.tif')
    frame_RGB = cv2.cvtColor(frame_BGR, cv2.COLOR_BGR2RGB)

    if plot==True:
        plt.figure(1)
        plt.title("Archivo: " + filename)
        plt.imshow(frame_RGB)
        plt.show(block=False)

    return frame_RGB

def seed_detection(frame_RGB, grid_seeds_shape = [5,5], plot=True, hue_range = None, saturation_range = None, value_range = None):

    frame_HSV = cv2.cvtColor(frame_RGB, cv2.COLOR_BGR2HSV)
    
    V = int(frame_HSV[:, :, 2].mean())

    #print(frame_HSV[:, :, 2].mean())
    #print(frame_HSV[:, :, 2].std())
    v=0
    counter = 0
    
    if hue_range == None:
       hue_range = (0,255)
    
    if saturation_range == None:
       saturation_range = (0,255)

    if value_range == None:
       value_range = (V,255)  
    
    num_seeds = grid_seeds_shape[0] * grid_seeds_shape[1]

    while counter < num_seeds:
        centro_x = []
        centro_y = []
        ancho = []
        largo = []
        angulo = []
        counter = 0
        #print(v)

        lower = np.array([hue_range[0], saturation_range[0], value_range[0] - v], np.uint8)
        
        upper = np.array([hue_range[1], saturation_range[1], value_range[1]], np.uint8)
        
        mask = cv2.inRange(frame_HSV, lower, upper)

        mask = cv2.erode(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        frame_detection = frame_RGB.copy()

        if len(cnts) > 0:
            for i in range(len(cnts)):
                (center_x, center_y), (width, height), angle = cv2.minAreaRect(cnts[i])
                if width > 20.0 and height > 20.0:
                    min_rect = np.intp(cv2.boxPoints(((center_x, center_y), (width, height), angle)))
                    cv2.drawContours(frame_detection, [min_rect], 0, (0, 255, 0), 2)
                    centro_x.append(center_x)
                    centro_y.append(center_y)
                    ancho.append(width)
                    largo.append(height)
                    angulo.append(angle)
                    counter = counter + 1
        v = v  + 1


    mask_2 = mask.copy()
    mask_2 = cv2.erode(mask_2, None, iterations=2)
    gauss = cv2.GaussianBlur(mask_2, (5, 5), 0)
    canny = cv2.Canny(gauss, 80, 10)
    (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame_RGB_segmentation=frame_RGB.copy()
    counter_seg = 0
    contornos_2=[]
    if len(cnts) > 0:
        for i in range(len(cnts)):
            area = cv2.contourArea(cnts[i])
            if area > 20:
                contornos_2.append(cnts[i])
                counter_seg = counter_seg + 1
    cv2.drawContours(frame_RGB_segmentation, contornos_2, -1, (0, 0, 255), 1)

    if plot == True:
        plt.figure(2)
        plt.title("Mask of Seed detection")
        plt.imshow(mask)
        plt.show(block=False)
        plt.figure(3)
        plt.title("Seed detection:" + str(counter))
        plt.imshow(frame_detection)
        plt.show(block=False)
        plt.figure(4)
        plt.title("Segmentation:" + str(counter))
        plt.imshow(frame_RGB_segmentation)
        plt.show(block=False)


    return mask,centro_x, centro_y, ancho, largo, angulo, counter

def give_me_the_spreed(row,column,centro_x,centro_y,spreed):
    centro=np.zeros(shape=[len(centro_y),2])
    centro[:,0]=centro_y
    centro[:,1]=centro_x
    centro_sort=np.zeros(shape=[len(centro_y),2])
    centro_sort[:,0]=np.sort(centro[:,0])
    for j in range(len(centro_y)):
        for i in range(len(centro_y)):
            if centro_sort[j,0] == centro[i,0]:
                centro_sort[j,1]=centro[i,1]
                centro=np.delete(centro,i,0)
                break
    centro_sort_2=np.zeros(shape=[column,2])
    centro_sort_3=np.zeros(shape=[row*column,2])

    for k in range(row):
        centro_sort_2[:,1]=np.sort(centro_sort[0:column,1])
        for j in range(column):
            for i in range(column):
                if centro_sort_2[j,1] == centro_sort[i,1]:
                    centro_sort_2[j,0]=centro_sort[i,0]
                    centro_sort=np.delete(centro_sort,i,0)
                    break
        centro_sort_3[column*k:column*(k+1),:]=centro_sort_2
    centro=np.zeros(shape=[len(centro_y),2])
    centro[:,0]=centro_y
    centro[:,1]=centro_x
    maiz_id=np.zeros(shape=[len(centro_y)])

    for j in range(len(centro_y)):
        for i in range(len(centro_y)):
            if (centro_sort_3[j, 0] == centro[i, 0]) and (centro_sort_3[j, 1] == centro[i, 1]):
                maiz_id[j] = i
                break
    return(int(maiz_id[spreed]))

def metadata_hsi_image(path):
    import spectral
    dataset = spectral.open_image(path + ".hdr")
    type_file = dataset.metadata.get("interleave")
    wavelength = dataset.metadata.get("wavelength")
    print(dataset.shape)

    return dataset.shape, type_file, wavelength

def metadata_image_tiff(path):
    from PIL import Image

    # Abre la imagen TIFF
    imagen = Image.open(path)

    # Obtén la información básica de la imagen
    print(f"Formato: {imagen.format}")
    print(f"Tamaño: {imagen.size}")
    return imagen.size, imagen.format

def read_bil_file(path):
    dataset = rasterio.open(path)
    data = dataset.read()
    return data

def black_white(path):
    dataset_white = rasterio.open(path+'white.bil')
    white_bands = dataset_white.read()
    dataset_white.close()
    dataset_black = rasterio.open(path+'black-cap.bil')
    black_bands = dataset_black.read()
    dataset_black.close()
    return white_bands,black_bands

def hyperspectral_images_seeds(filename,correction=False,white_bands=None,black_bands=None):
    dataset = rasterio.open(filename)
    frame_bands = dataset.read()
    dataset.close()
    if correction==True:
        white_bands = np.append(white_bands, white_bands[:,0:frame_bands.shape[1]-white_bands.shape[1],:], axis=1)
        black_bands = np.append(black_bands, black_bands[:,0:frame_bands.shape[1]-black_bands.shape[1],:], axis=1)
        frame_bands_correc=(frame_bands-black_bands)/(white_bands-black_bands)*100
        return frame_bands_correc
    else:
        return frame_bands


def extract_one_seed_hsi_features(frame_bands, dsize, mini_mask_2, traslate_matrix, rotate_matrix, roi_seed):

    x = np.array(long_onda)
    y_mean = np.zeros(x.shape)
    y_std = np.zeros(x.shape)
    
    x_low, x_up, y_low, y_up = roi_seed

    traslated_frame_bands = cv2.warpAffine(src=frame_bands.transpose(1,2,0), M=traslate_matrix,dsize= dsize)

    rotated_frame_bands = cv2.warpAffine(src=traslated_frame_bands, M=rotate_matrix,dsize= dsize)

    mini_frame_bands = rotated_frame_bands[y_low:y_up, x_low:x_up,:]
    
    mini_frame_bands_seg = cv2.bitwise_and(mini_frame_bands, mini_frame_bands, mask= mini_mask_2)

   
    for i in range(len(x)):
    # Seleccionar los valores no cero para la fila actual
        non_zero_values = mini_frame_bands_seg[:,:,i][mini_frame_bands_seg[:,:,i] != 0]
    
    # Calcular y_mean y y_std para la fila actual
        if len(non_zero_values) > 0:
            y_mean[i] = np.mean(non_zero_values)
            y_std[i] = np.std(non_zero_values)

    return y_mean, y_std

def extract_one_seed_hsi(row_column,mask,frame_RGB,frame_bands,centro_x,centro_y,ancho,largo,angulo,id,plot=True):
    row=row_column[0]
    column=row_column[1]
    maiz_id=give_me_the_spreed(row,column,centro_x,centro_y,id-1)
    #maiz_id=int(id-1)

    ancho_x = int(ancho[maiz_id] * 1.5)
    largo_y = int(largo[maiz_id] * 1.5)

    X_centro_image = frame_RGB.shape[1] / 2
    Y_centro_image = frame_RGB.shape[0] / 2
    X_centro = X_centro_image - centro_x[maiz_id]
    Y_centro = Y_centro_image - centro_y[maiz_id]
    traslate_matrix = np.float32([[1, 0, X_centro], [0, 1, Y_centro]])
    rotate_matrix = cv2.getRotationMatrix2D(center=(X_centro_image, Y_centro_image), angle=angulo[maiz_id], scale=1)

    traslated_frame_rgb = cv2.warpAffine(src=frame_RGB, M=traslate_matrix,
                                         dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    traslated_mask = cv2.warpAffine(src=mask, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

    rotated_frame_rgb = cv2.warpAffine(src=traslated_frame_rgb, M=rotate_matrix,
                                       dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    rotated_mask_rgb = cv2.warpAffine(src=traslated_mask, M=rotate_matrix, dsize=(mask.shape[1], mask.shape[0]))

    x_low = int(X_centro_image - ancho_x / 2)
    x_up = int(X_centro_image + ancho_x / 2)
    y_low = int(Y_centro_image - largo_y / 2)
    y_up = int(Y_centro_image + largo_y / 2)

    mini_frame_rgb = rotated_frame_rgb[y_low:y_up, x_low:x_up, :]
    mini_mask = rotated_mask_rgb[y_low:y_up, x_low:x_up]

    mini_mask = cv2.dilate(mini_mask, None, iterations=1)
    mini_mask_0 = cv2.GaussianBlur(mini_mask, (1, 1), 0)

    m = 0

    while True:
        m = m + 1
        mini_mask = mini_mask_0.copy()
        mini_mask = cv2.dilate(mini_mask, None, iterations=m)
        mini_mask = cv2.GaussianBlur(mini_mask, (1, 1), 0)

        #mini_frame_rgb_seg_obs = mini_frame_rgb.copy()

        canny = cv2.Canny(mini_mask, 80, 10)
        (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contornos_2 = []
        area_max = 0
        n = 0
        if len(contornos) > 0:
            for i in range(len(contornos)):
                area = cv2.contourArea(contornos[i])
                if area > 800:
                    if area_max < area:
                        area_max = area
                        n = int(i)
                        print(id, area_max)
            if area_max > 800:
                break

    mini_mask_2 = np.zeros((mini_frame_rgb.shape[0], mini_frame_rgb.shape[1]), 'uint8')
    cv2.drawContours(mini_mask_2, [contornos[n]], -1, 255, -1)
    mini_mask_2 = cv2.erode(mini_mask_2, None, iterations=3)
    mini_mask_2 = cv2.dilate(mini_mask_2, None, iterations=3)
    mini_frame_rgb_seg=cv2.bitwise_and(mini_frame_rgb, mini_frame_rgb, mask=mini_mask_2)

   
    x = np.array(long_onda)
    y_mean = np.zeros(x.shape)
    y_std = np.zeros(x.shape)
    
    

    traslated_frame_bands = cv2.warpAffine(src=frame_bands.transpose(1,2,0), M=traslate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

    rotated_frame_bands = cv2.warpAffine(src=traslated_frame_bands, M=rotate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

    mini_frame_bands = rotated_frame_bands[y_low:y_up, x_low:x_up,:]
    
    mini_frame_bands_seg = cv2.bitwise_and(mini_frame_bands, mini_frame_bands, mask=mini_mask_2)

   
    for i in range(len(x)):
    # Seleccionar los valores no cero para la fila actual
        non_zero_values = mini_frame_bands_seg[:,:,i][mini_frame_bands_seg[:,:,i] != 0]
    
    # Calcular y_mean y y_std para la fila actual
        if len(non_zero_values) > 0:
            y_mean[i] = np.mean(non_zero_values)
            y_std[i] = np.std(non_zero_values)

    """ fig, axs = plt.subplots(2, 3, figsize=(10, 6))
    axs[0][0].imshow(frame_bands.transpose(1,2,0)[:,:,10])
    axs[0][0].set_title("Imagen 10 de la semilla: " + str(id))
    axs[0][1].imshow(traslated_frame_bands[:,:,10])
    axs[0][1].set_title("traslated_frame_bands: " + str(id))

    axs[0][2].imshow(mini_frame_bands_seg[:,:,10])
    axs[0][2].set_title("Imagen 10 de la semilla: " + str(id))
    axs[1][0].imshow(mini_mask_2)
    axs[1][0].set_title("Mascara de la semilla: " + str(id))
    
    axs[1][1].imshow(rotated_frame_bands[:,:,10])
    axs[1][1].set_title("rotated_frame_bands: " + str(id))


    axs[1][2].imshow(mini_frame_bands[:,:,10])
    axs[1][2].set_title("mini_frame_bands: " + str(id))
    plt.show(block=True) """
    

    return y_mean, y_std



def one_seed(row_column,mask,frame_RGB,frame_bands,centro_x,centro_y,ancho,largo,angulo,id,plot=True):
    row=row_column[0]
    column=row_column[1]
    maiz_id=give_me_the_spreed(row,column,centro_x,centro_y,id-1)
    #maiz_id=int(id-1)

    ancho_x = int(ancho[maiz_id] * 1.5)
    largo_y = int(largo[maiz_id] * 1.5)

    X_centro_image = frame_RGB.shape[1] / 2
    Y_centro_image = frame_RGB.shape[0] / 2
    X_centro = X_centro_image - centro_x[maiz_id]
    Y_centro = Y_centro_image - centro_y[maiz_id]
    traslate_matrix = np.float32([[1, 0, X_centro], [0, 1, Y_centro]])
    rotate_matrix = cv2.getRotationMatrix2D(center=(X_centro_image, Y_centro_image), angle=angulo[maiz_id], scale=1)

    traslated_frame_rgb = cv2.warpAffine(src=frame_RGB, M=traslate_matrix,
                                         dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    traslated_mask = cv2.warpAffine(src=mask, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

    rotated_frame_rgb = cv2.warpAffine(src=traslated_frame_rgb, M=rotate_matrix,
                                       dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    rotated_mask_rgb = cv2.warpAffine(src=traslated_mask, M=rotate_matrix, dsize=(mask.shape[1], mask.shape[0]))

    x_low = int(X_centro_image - ancho_x / 2)
    x_up = int(X_centro_image + ancho_x / 2)
    y_low = int(Y_centro_image - largo_y / 2)
    y_up = int(Y_centro_image + largo_y / 2)

    mini_frame_rgb = rotated_frame_rgb[y_low:y_up, x_low:x_up, :]
    mini_mask = rotated_mask_rgb[y_low:y_up, x_low:x_up]

    mini_mask = cv2.dilate(mini_mask, None, iterations=1)
    mini_mask_0 = cv2.GaussianBlur(mini_mask, (1, 1), 0)

    m = 0

    while True:
        m = m + 1
        mini_mask = mini_mask_0.copy()
        mini_mask = cv2.dilate(mini_mask, None, iterations=m)
        mini_mask = cv2.GaussianBlur(mini_mask, (1, 1), 0)

        mini_frame_rgb_seg_obs = mini_frame_rgb.copy()

        canny = cv2.Canny(mini_mask, 80, 10)
        (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contornos_2 = []
        area_max = 0
        n = 0
        if len(contornos) > 0:
            for i in range(len(contornos)):
                area = cv2.contourArea(contornos[i])
                if area > 800:
                    if area_max < area:
                        area_max = area
                        n = int(i)
                        print(id, area_max)
            if area_max > 800:
                break

    mini_mask_2 = np.zeros((mini_frame_rgb.shape[0], mini_frame_rgb.shape[1]), 'uint8')
    cv2.drawContours(mini_mask_2, [contornos[n]], -1, 255, -1)
    mini_mask_2 = cv2.erode(mini_mask_2, None, iterations=3)
    mini_mask_2 = cv2.dilate(mini_mask_2, None, iterations=3)
    mini_frame_rgb_seg=cv2.bitwise_and(mini_frame_rgb, mini_frame_rgb, mask=mini_mask_2)

    """""
    plt.figure(5)
    plt.imshow(mini_mask_2)
    plt.title("Imagen rgb de la semilla: " + str(id))
    plt.show()

    """""
    x = np.array(long_onda)
    y_mean = np.zeros(x.shape)
    y_std = np.zeros(x.shape)
    
    for i in range(len(x)):
        traslated_frame_band = cv2.warpAffine(src=frame_bands[i, :, :], M=traslate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        rotated_frame_band = cv2.warpAffine(src=traslated_frame_band, M=rotate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        mini_frame_band = rotated_frame_band[y_low:y_up, x_low:x_up]
        mini_frame_band_seg = cv2.bitwise_and(mini_frame_band, mini_frame_band, mask=mini_mask_2)

        vector = []
        for n in mini_frame_band_seg.reshape(-1):
            if n != 0:
                vector.append(n)
        y_mean[i] = np.mean(vector)
        y_std[i] = np.std(vector)

    if plot == True:
        fig, axs = plt.subplots(1, 3, figsize=(10, 6))
        axs[0].imshow(mini_frame_rgb_seg)
        axs[0].set_title("Imagen rgb de la semilla: " + str(id))
        axs[1].imshow(mini_mask_2)
        axs[1].set_title("Mascara de la semilla: " + str(id))
        axs[2].plot(x, y_mean, label="mean")
        axs[2].plot(x, y_std, label="std")
        axs[2].legend()
        axs[2].twinx().set_ylabel("desviacion estandar")
        axs[2].set_xlabel('Espectro')
        axs[2].set_ylabel('media aritmetica')
        axs[2].set_title("Longitud de onda vs mean")
        plt.show(block=True)
    return y_mean,y_std

def several_seeds(row_column,mask,frame_RGB,frame_bands,centro_x,centro_y,ancho,largo,angulo,plot=True):
    row=row_column[0]
    column=row_column[1]
    maiz_id=give_me_the_spreed(row,column,centro_x,centro_y,id-1)
    #maiz_id=int(id-1)

    ancho_x = int(ancho[maiz_id] * 1.5)
    largo_y = int(largo[maiz_id] * 1.5)

    X_centro_image = frame_RGB.shape[1] / 2
    Y_centro_image = frame_RGB.shape[0] / 2
    X_centro = X_centro_image - centro_x[maiz_id]
    Y_centro = Y_centro_image - centro_y[maiz_id]
    traslate_matrix = np.float32([[1, 0, X_centro], [0, 1, Y_centro]])
    rotate_matrix = cv2.getRotationMatrix2D(center=(X_centro_image, Y_centro_image), angle=angulo[maiz_id], scale=1)

    traslated_frame_rgb = cv2.warpAffine(src=frame_RGB, M=traslate_matrix,
                                         dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    traslated_mask = cv2.warpAffine(src=mask, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

    rotated_frame_rgb = cv2.warpAffine(src=traslated_frame_rgb, M=rotate_matrix,
                                       dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
    rotated_mask_rgb = cv2.warpAffine(src=traslated_mask, M=rotate_matrix, dsize=(mask.shape[1], mask.shape[0]))

    x_low = int(X_centro_image - ancho_x / 2)
    x_up = int(X_centro_image + ancho_x / 2)
    y_low = int(Y_centro_image - largo_y / 2)
    y_up = int(Y_centro_image + largo_y / 2)

    mini_frame_rgb = rotated_frame_rgb[y_low:y_up, x_low:x_up, :]
    mini_mask = rotated_mask_rgb[y_low:y_up, x_low:x_up]

    mini_mask = cv2.dilate(mini_mask, None, iterations=1)
    mini_mask = cv2.GaussianBlur(mini_mask, (1, 1), 0)

    mini_frame_rgb_seg_obs = mini_frame_rgb.copy()

    canny = cv2.Canny(mini_mask, 80, 10)
    (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contornos))
    contornos_2 = []
    area_max = 0
    if len(contornos) > 0:
        for i in range(len(contornos)):
            area = cv2.contourArea(contornos[i])
            if area > 20:
                if area_max < area:
                    area_max = area
                    # print(id,area_max)

                contornos_2.append(contornos[i])
    # print(cv2.contourArea(contornos_2[0]))
    #cv2.drawContours(mini_frame_rgb_seg_obs, contornos_2, -1, (0, 0, 255), 1)

    mini_mask_2 = np.zeros((mini_frame_rgb.shape[0], mini_frame_rgb.shape[1]), 'uint8')
    cv2.drawContours(mini_mask_2, contornos_2, -1, 255, -1)
    mini_mask_2 = cv2.erode(mini_mask_2, None, iterations=3)
    mini_mask_2 = cv2.dilate(mini_mask_2, None, iterations=3)
    mini_frame_rgb_seg=cv2.bitwise_and(mini_frame_rgb, mini_frame_rgb, mask=mini_mask_2)


    plt.figure(5)
    plt.imshow(mini_mask_2)
    plt.title("Imagen rgb de la semilla: " + str(id))
    plt.show(block=True)
    plt.show()


    x = np.array(long_onda)
    y_mean = np.zeros(x.shape)
    y_std = np.zeros(x.shape)
    for i in range(len(x)):
        traslated_frame_band = cv2.warpAffine(src=frame_bands[i, :, :], M=traslate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        rotated_frame_band = cv2.warpAffine(src=traslated_frame_band, M=rotate_matrix,dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        mini_frame_band = rotated_frame_band[y_low:y_up, x_low:x_up]
        mini_frame_band_seg = cv2.bitwise_and(mini_frame_band, mini_frame_band, mask=mini_mask_2)

        vector = []
        for n in mini_frame_band_seg.reshape(-1):
            if n != 0:
                vector.append(n)
        y_mean[i] = np.mean(vector)
        y_std[i] = np.std(vector)

    if plot == True:
        fig, axs = plt.subplots(1, 3, figsize=(10, 6))
        axs[0].imshow(mini_frame_rgb_seg)
        axs[0].set_title("Imagen rgb de la semilla: " + str(id))
        axs[1].imshow(mini_mask_2)
        axs[1].set_title("Mascara de la semilla: " + str(id))
        axs[2].plot(x, y_mean, label="mean")
        axs[2].plot(x, y_std, label="std")
        axs[2].legend()
        axs[2].twinx().set_ylabel("desviacion estandar")
        axs[2].set_xlabel('Espectro')
        axs[2].set_ylabel('media aritmetica')
        axs[2].set_title("Longitud de onda vs mean")
        plt.show(block=True)
    return y_mean,y_std

def morfo_features_extraction(image_seed, seed_mask):
    contornos, _ = cv2.findContours(seed_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contorno = contornos[0]

    # calcular area
    area = cv2.contourArea(contorno)

    # calcular perimetro
    perimetro = cv2.arcLength(contorno, True)
    
    x, y, w, h = cv2.boundingRect(contorno)
    
    relacion_aspecto = w / h

    morfo_features = {"area": area, "perimetro": perimetro, "relacion_aspecto": relacion_aspecto}
    
    
    return morfo_features



def seeds_extraction(row_column,mask,frame_RGB,centro_x,centro_y,ancho,largo,angulo, plot = False):
    row=row_column[0]
    column=row_column[1]
    OBS = []
    MASK = []
    TRAS_MATRIX = []
    ROT_MATRIX = []
    ROI_SEED = []
    for id in range(len(centro_x)):
        maiz_id=give_me_the_spreed(row,column,centro_x,centro_y,id)
        ancho_x = int(ancho[maiz_id]*1.5)
        largo_y = int(largo[maiz_id]*1.5)

        X_centro_image = frame_RGB.shape[1]/2
        Y_centro_image = frame_RGB.shape[0]/2
        X_centro= X_centro_image-centro_x[maiz_id]
        Y_centro= Y_centro_image-centro_y[maiz_id]
        traslate_matrix = np.float32([[1, 0, X_centro], [0, 1, Y_centro]])
        rotate_matrix = cv2.getRotationMatrix2D(center=(X_centro_image, Y_centro_image), angle=angulo[maiz_id],scale=1)


        traslated_frame_rgb = cv2.warpAffine(src=frame_RGB, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        traslated_mask = cv2.warpAffine(src=mask, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

        rotated_frame_rgb = cv2.warpAffine(src=traslated_frame_rgb, M=rotate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        rotated_mask_rgb = cv2.warpAffine(src=traslated_mask, M=rotate_matrix, dsize=(mask.shape[1], mask.shape[0]))

        x_low = int(X_centro_image - ancho_x/ 2)
        x_up = int(X_centro_image + ancho_x/ 2)
        y_low = int(Y_centro_image - largo_y / 2)
        y_up = int(Y_centro_image + largo_y / 2)

        ROI_SEED.append([x_low, x_up, y_low, y_up])

        mini_frame_rgb = rotated_frame_rgb[y_low:y_up, x_low:x_up, :]
        mini_mask_0 = rotated_mask_rgb[y_low:y_up, x_low:x_up]

        """
        plt.figure(5)
        plt.imshow(mini_frame_rgb)
        plt.show()


        mini_frame_HSV = cv2.cvtColor(mini_frame_rgb, cv2.COLOR_BGR2HSV)
        V = int(mini_frame_HSV[:, :, 2].mean())
        S = int(mini_frame_HSV[:, :, 1].mean())
        H = int(mini_frame_HSV[:, :, 0].mean())
        lower = np.array([H, S, V  ], np.uint8)
        #lower = np.array([0, 0, V ], np.uint8)
        upper = np.array([255, 255, 255], np.uint8)
        mini_mask = cv2.inRange(mini_frame_HSV, lower, upper)
        """
        m= 0

        while True:
            m = m + 1
            mini_mask= mini_mask_0.copy()
            mini_mask = cv2.dilate(mini_mask, None, iterations=m)
            mini_mask = cv2.GaussianBlur(mini_mask, (1, 1), 0)

            mini_frame_rgb_seg_obs=mini_frame_rgb.copy()

            canny = cv2.Canny(mini_mask, 80, 10)
            (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #contornos_2 = []
            area_max=0
            n=0
            if len(contornos) > 0:
                for i in range(len(contornos)):
                    area = cv2.contourArea(contornos[i])
                    if area > 800:
                        if area_max < area:
                            area_max = area
                            n=int(i)
                            print(id,area_max)
                if area_max > 800:
                    break


        #contornos_2.append(contornos[n])
        #print(len(contornos_2))

        print(len([contornos[n]]))
        #print(cv2.contourArea(contornos_2[0]))
        #cv2.drawContours(mini_frame_rgb_seg_obs, [contornos[n]], -1, (0, 0, 255), 1)
        '''
        plt.figure(5)
        plt.imshow(mini_frame_rgb_seg_obs)
        plt.title("Imagen rgb de la semilla: " + str(id))
        plt.show()
        '''
        mini_mask_2 = np.zeros((mini_frame_rgb.shape[0], mini_frame_rgb.shape[1]), 'uint8')
        cv2.drawContours(mini_mask_2, [contornos[n]],-1, 255, -1)
        mini_mask_2 = cv2.erode(mini_mask_2, None, iterations=3)
        mini_mask_2 = cv2.dilate(mini_mask_2, None, iterations=3)
        
        TRAS_MATRIX.append(traslate_matrix)
        ROT_MATRIX.append(rotate_matrix)
        OBS.append(mini_frame_rgb_seg_obs)
        MASK.append( mini_mask_2)


    if plot == True:
        plt.figure(5)
        for j in range(0, row):
            for i in range(0, column):
                plt.subplot(column, column, j * column + i + 1)
                #plt.title('%d/%d' % (Y_test_2[j * 10 + i + 1 + idx], Y_predict_2[j * 10 + i + 1 + idx]))
                plt.imshow(OBS[j * column + i ])
        plt.show(block=False)

        plt.figure(6)
        for j in range(0, row):
            for i in range(0, column):
                plt.subplot(column, column, j * column + i + 1)
                # plt.title('%d/%d' % (Y_test_2[j * 10 + i + 1 + idx], Y_predict_2[j * 10 + i + 1 + idx]))
                plt.imshow(MASK[j * column + i])
        plt.show(block=True)

    return OBS, MASK, TRAS_MATRIX, ROT_MATRIX, ROI_SEED
    
def seeds(row_column,mask,frame_RGB,centro_x,centro_y,ancho,largo,angulo,plot=True):
    row=row_column[0]
    column=row_column[1]
    OBS = []
    MASK = []
    for id in range(len(centro_x)):
        maiz_id=give_me_the_spreed(row,column,centro_x,centro_y,id)
        ancho_x = int(ancho[maiz_id]*1.5)
        largo_y = int(largo[maiz_id]*1.5)

        X_centro_image = frame_RGB.shape[1]/2
        Y_centro_image = frame_RGB.shape[0]/2
        X_centro= X_centro_image-centro_x[maiz_id]
        Y_centro= Y_centro_image-centro_y[maiz_id]
        traslate_matrix = np.float32([[1, 0, X_centro], [0, 1, Y_centro]])
        rotate_matrix = cv2.getRotationMatrix2D(center=(X_centro_image, Y_centro_image), angle=angulo[maiz_id],scale=1)


        traslated_frame_rgb = cv2.warpAffine(src=frame_RGB, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        traslated_mask = cv2.warpAffine(src=mask, M=traslate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))

        rotated_frame_rgb = cv2.warpAffine(src=traslated_frame_rgb, M=rotate_matrix, dsize=(frame_RGB.shape[1], frame_RGB.shape[0]))
        rotated_mask_rgb = cv2.warpAffine(src=traslated_mask, M=rotate_matrix, dsize=(mask.shape[1], mask.shape[0]))

        x_low = int(X_centro_image - ancho_x/ 2)
        x_up = int(X_centro_image + ancho_x/ 2)
        y_low = int(Y_centro_image - largo_y / 2)
        y_up = int(Y_centro_image + largo_y / 2)

        mini_frame_rgb = rotated_frame_rgb[y_low:y_up, x_low:x_up, :]
        mini_mask_0 = rotated_mask_rgb[y_low:y_up, x_low:x_up]

        """
        plt.figure(5)
        plt.imshow(mini_frame_rgb)
        plt.show()


        mini_frame_HSV = cv2.cvtColor(mini_frame_rgb, cv2.COLOR_BGR2HSV)
        V = int(mini_frame_HSV[:, :, 2].mean())
        S = int(mini_frame_HSV[:, :, 1].mean())
        H = int(mini_frame_HSV[:, :, 0].mean())
        lower = np.array([H, S, V  ], np.uint8)
        #lower = np.array([0, 0, V ], np.uint8)
        upper = np.array([255, 255, 255], np.uint8)
        mini_mask = cv2.inRange(mini_frame_HSV, lower, upper)
        """
        m= 0

        while True:
            m = m + 1
            mini_mask= mini_mask_0.copy()
            mini_mask = cv2.dilate(mini_mask, None, iterations=m)
            mini_mask = cv2.GaussianBlur(mini_mask, (1, 1), 0)

            mini_frame_rgb_seg_obs=mini_frame_rgb.copy()

            canny = cv2.Canny(mini_mask, 80, 10)
            (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #contornos_2 = []
            area_max=0
            n=0
            if len(contornos) > 0:
                for i in range(len(contornos)):
                    area = cv2.contourArea(contornos[i])
                    if area > 800:
                        if area_max < area:
                            area_max = area
                            n=int(i)
                            print(id,area_max)
                if area_max > 800:
                    break


        #contornos_2.append(contornos[n])
        #print(len(contornos_2))

        print(len([contornos[n]]))
        #print(cv2.contourArea(contornos_2[0]))
        cv2.drawContours(mini_frame_rgb_seg_obs, [contornos[n]], -1, (0, 0, 255), 1)
        '''
        plt.figure(5)
        plt.imshow(mini_frame_rgb_seg_obs)
        plt.title("Imagen rgb de la semilla: " + str(id))
        plt.show()
        '''
        mini_mask_2 = np.zeros((mini_frame_rgb.shape[0], mini_frame_rgb.shape[1]), 'uint8')
        cv2.drawContours(mini_mask_2, [contornos[n]],-1, 255, -1)
        mini_mask_2 = cv2.erode(mini_mask_2, None, iterations=3)
        mini_mask_2 = cv2.dilate(mini_mask_2, None, iterations=3)

        OBS.append(mini_frame_rgb_seg_obs)
        MASK.append( mini_mask_2)


    if plot == True:
        plt.figure(5)
        for j in range(0, row):
            for i in range(0, column):
                plt.subplot(column, column, j * column + i + 1)
                #plt.title('%d/%d' % (Y_test_2[j * 10 + i + 1 + idx], Y_predict_2[j * 10 + i + 1 + idx]))
                plt.imshow(OBS[j * column + i ])
        plt.show(block=False)

        plt.figure(6)
        for j in range(0, row):
            for i in range(0, column):
                plt.subplot(column, column, j * column + i + 1)
                # plt.title('%d/%d' % (Y_test_2[j * 10 + i + 1 + idx], Y_predict_2[j * 10 + i + 1 + idx]))
                plt.imshow(MASK[j * column + i])
        plt.show(block=True)
    return

def analize_one_seed(filename,id_seed):
    group_of_seeds=filenames.index(filename)
    frame_RGB = show_image_rgb(filename)
    mask,centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(frame_RGB,plot=False)
    white_bands,black_bands = black_white("./sample_image/")
    frame_bands_correc = hyperspectral_images_seeds("./sample_image/" + filename + ".bil",correction=True,white_bands=white_bands,black_bands=black_bands)
    one_seed(row_column[group_of_seeds], mask, frame_RGB, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo,id_seed)
    return

def analize_all_seeds(filename):
    group_of_seeds=filenames.index(filename)
    frame_RGB = show_image_rgb(filename)
    mask,centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(frame_RGB)
    white_bands,black_bands = black_white()
    frame_bands_correc = hyperspectral_images_seeds(filename,correction=True,white_bands=white_bands,black_bands=black_bands)
    several_seeds(row_column[group_of_seeds], mask, frame_RGB, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo)
    return

def view_seeds(filename):
    group_of_seeds=filenames.index(filename)
    frame_RGB = show_image_rgb(filename)
    mask, centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(frame_RGB)
    seeds(row_column[group_of_seeds], mask, frame_RGB, centro_x, centro_y, ancho, largo, angulo)
    return


#def 
def generate_images_bands(name):

    white_bands, black_bands = black_white()
    os.mkdir("images_hyper_2/"+name)
    frame_RGB = show_image_rgb(name,plot=False)
    plt.title("Archivo: " + name)
    plt.imshow(frame_RGB)
    plt.savefig("images_hyper_2/"+name+"/RGB.jpg")
    frame_bands_correc = hyperspectral_images_seeds(filenames[0], correction=True, white_bands=white_bands,black_bands=black_bands)
    for i in range(len(long_onda)):
        plt.figure(figsize=(10, 6))
        im = plt.imshow(frame_bands_correc[i], vmin=0, vmax=frame_bands_correc[i].max(), cmap='viridis')
        plt.title("Longitud de onda: " + str(long_onda[i]) + "nm" + " Max Relativo: " + str(frame_bands_correc[i].max()) + "%")
        plt.colorbar(im)
        plt.savefig("images_hyper/"+name + "/" + str(long_onda[i]) + ".jpg")

    return

def extracting_features(filename,white_bands, black_bands):
    group_of_seeds = filenames.index(filename)
    features = []
    for nm in long_onda:
        features.append("mean_" + str(nm) + "_nm")
    for nm in long_onda:
        features.append("std_" + str(nm) + "_nm")
    keys = ['name', 'seed'] + features
    df=pd.DataFrame(columns=keys)
    frame_RGB = show_image_rgb(filename,plot=False)
    mask,centro_x, centro_y, ancho, largo, angulo, counter = seed_detection(frame_RGB,plot=False)
    frame_bands_correc = hyperspectral_images_seeds(filename, correction=True, white_bands=white_bands,black_bands=black_bands)
    for id_seed in range(counter):
        y_mean,y_std=one_seed(row_column[group_of_seeds], mask, frame_RGB, frame_bands_correc, centro_x, centro_y, ancho, largo, angulo,id_seed+1,plot=False)
        values=[filename]+[id_seed+1]+y_mean.tolist()+y_std.tolist()
        df=pd.concat([df, pd.DataFrame(dict(zip(keys, values)),index=[0])], ignore_index=True)
    return df

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Empezar')

    #view_seeds("AMAZ-46-02")

    analize_one_seed("AMAZ-46-02", 12)

    #analize_all_seeds("AMAZ-46-02")

    #generate_images_bands(filenames[-2])

    """
    white_bands, black_bands = black_white()
    for name in filenames:
        df=extracting_features(name,white_bands, black_bands)
        df.to_csv('features_'+name+'.csv')
        print(df.head())
    """
    print('Finalizar')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

