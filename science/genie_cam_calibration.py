import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

wavelengths = [440, 500, 530, 570, 610, 670, 740, 780, 840, 900, 950, 1000]
relative_spectral_sensitivity = {
    440: 0.78, 500: 0.97, 530: 1.0, 570: 0.96, 610: 0.9,
    670: 0.76, 740: 0.58, 780: 0.44, 840: 0.31, 900: 0.18,
    950: 0.1, 1000: 0.05
}

def load_images(folder):
    # load all images in a folder as greyscale numpy arrays
    images = []
    for fname in sorted(os.listdir(folder)): # sorting alphabetically and looping through each file
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp')):
            img = cv2.imread(os.path.join(folder, fname), cv2.IMREAD_GRAYSCALE) # load and convert to greyscale
            images.append(img.astype(np.float32)) # convert to float32
    return np.stack(images, axis=0)  # shape: (num_images, H, W)

def mean_image(images): 
    return np.mean(images, axis=0)

def get_reflectance(filepath: str) -> dict:
    with open(filepath, "r") as f:
        lines = f.read().splitlines() # use splitlines for better line handling
        d = {w: 0.0 for w in wavelengths}
        for i in wavelengths:
            # d[i] = float(lines[i - 349]) # handle null values
            try:
                val = float(lines[i - 349])
                d[i] = val if val > 0 else 0.0
            except (IndexError, ValueError): # handle files that are too short or malformed
                d[i] = 0.0
        return d

def calibrate_images(
    bias_folder, dark_folder, flat_folder, calibration_folder, sample_folder, wavelengths, roi=None, chalk_roi=None, hematite_roi=None, magnetite_roi=None, serpentine_roi=None, chlorite_roi=None
):
    bias_imgs = load_images(bias_folder)
    dark_imgs = load_images(dark_folder)
    flat_imgs = load_images(flat_folder)
    cal_imgs = load_images(calibration_folder)
    sample_imgs = load_images(sample_folder)

    bias = mean_image(bias_imgs)
    dark_corr = mean_image(dark_imgs) - bias
    flat_corr = mean_image(flat_imgs) - dark_corr
    flat_norm = flat_corr / np.mean(flat_corr)

    dark_corr = cv2.resize(dark_corr, (2064, 1544))
    flat_norm = cv2.resize(flat_norm, (2064, 1544))
    

    cal_corrected = (cal_imgs - dark_corr) / flat_norm
    sample_corrected = (sample_imgs - dark_corr) / flat_norm

    # [Sensitivity code is commented out for duplicated test images]
    # for i in range(len(wavelengths)):
    #     cal_corrected[i] /= relative_spectral_sensitivity[wavelengths[i]]
    #     sample_corrected[i] /= relative_spectral_sensitivity[wavelengths[i]]
    
    # Load mineral reflectance data (standard logic)
    with open("genie_calibration_data/chalk - pigments checker acrylic - GorgiasUV.txt", "r") as fca:
        chalk_reflectance = {w: 1.0 for w in wavelengths}
    
    hematite_reflectance = get_reflectance("genie_calibration_data/s07_ASD_Hematite_GDS69.c_60-104um_BECKb_AREF.txt")
    magnetite_reflectance = get_reflectance("genie_calibration_data/s07_ASD_Magnetite_HS195.3B_BECKb_AREF.txt")
    # serpentine_reflectance = get_reflectance("genie_calibration_data/s07_ASD_Hematite_GDS69.c_60-104um_BECKb_AREF.txt") # wrong file
    serpentine_reflectance = get_reflectance("genie_calibration_data/s07_ASD_Serpentine_HS8.3B_BECKc_AREF.txt")
    # chlorite_reflectance = get_reflectance("genie_calibration_data/s07_ASD_Magnetite_HS195.3B_BECKb_AREF.txt") # wrong file
    chlorite_reflectance = get_reflectance("genie_calibration_data/splib07a_Chlorite_SMR-13.b_60-104um_BECKa_AREF.txt")

    A = [0] * 12
    B = [0] * 12
    for i in range(12):
        # a = [[chalk_reflectance[wavelengths[i]], 1], ... ] # solve for reflectance directly
        a = [[cal_corrected[i, chalk_roi[1]:chalk_roi[3], chalk_roi[0]:chalk_roi[2]].mean(), 1],
             [cal_corrected[i, hematite_roi[1]:hematite_roi[3], hematite_roi[0]:hematite_roi[2]].mean(), 1],
             [cal_corrected[i, magnetite_roi[1]:magnetite_roi[3], magnetite_roi[0]:magnetite_roi[2]].mean(), 1],
             [cal_corrected[i, serpentine_roi[1]:serpentine_roi[3], serpentine_roi[0]:serpentine_roi[2]].mean(), 1],
             [cal_corrected[i, chlorite_roi[1]:chlorite_roi[3], chlorite_roi[0]:chlorite_roi[2]].mean(), 1]]
        A[i] = a
        # B[i] = [0] * 5 ... # solve for reflectance directly
        B[i] = [chalk_reflectance[wavelengths[i]],
                hematite_reflectance[wavelengths[i]],
                magnetite_reflectance[wavelengths[i]],
                serpentine_reflectance[wavelengths[i]],
                chlorite_reflectance[wavelengths[i]]]
        B[i] = np.transpose(B[i])

    # Solve for M and C
    M, C = [0] * 12, [0] * 12
    for i in range(12):
        solutions, _, _, _ = np.linalg.lstsq(A[i], B[i], rcond=None)
        m, c = solutions
        M[i] = m
        C[i] = c

    # Calculate final reflectance
    reflectance = np.zeros_like(sample_corrected)
    for i in range(12):
        reflectance[i] = sample_corrected[i] * M[i] + C[i]
    
    # reflectance_corr = np.divide(reflectance, flat_norm) # avoid double scaling
    reflectance_corr = reflectance

    # ROI Mean Extraction
    if roi is not None:
        x1, y1, x2, y2 = roi
        reflectance_roi = reflectance_corr[:, y1:y2, x1:x2]
    else:
        reflectance_roi = reflectance_corr

    mean_reflectance = np.mean(reflectance_roi, axis=(1, 2))
    
    # Plotting
    plt.figure(figsize=(8, 5))
    plt.plot(wavelengths, mean_reflectance, marker='o')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    plt.title('Spectral Reflectance Curve')
    plt.grid(True)
    plt.show()

    return mean_reflectance

if __name__ == "__main__":

    bias_folder = "genie_calibration_data/bias"
    dark_folder = "genie_calibration_data/dark"
    flat_folder = "genie_calibration_data/flat"
    calibration_folder = "calibration_photos2"
    sample_folder = "calibration_photos2"

    serpentine_roi = (689, 630, 709, 653)
    chalk_roi = (776, 631, 796, 651)
    hematite_roi = (843, 630, 875, 652)
    magnetite_roi = (930, 632, 956, 652)
    chlorite_roi = (1012, 626, 1039, 652)

    test_roi = magnetite_roi

    mean_reflectance = calibrate_images(
        bias_folder, dark_folder, flat_folder, calibration_folder, sample_folder, 
        wavelengths, 
        roi=test_roi, 
        chalk_roi=chalk_roi, 
        hematite_roi=hematite_roi, 
        magnetite_roi=magnetite_roi, 
        serpentine_roi=serpentine_roi, 
        chlorite_roi=chlorite_roi
    )