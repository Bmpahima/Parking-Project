# from models.YoloModelManager import ModelManager
# import cv2

# if __name__ == "__main__":
#     model = ModelManager(
#         vehicle_model_path="models/VehiclesModel.pt",
#         lp_model_path="models/LicensePlateModel.pt",
#         numbers_models_path="models/LicensePlateNumModel.pt"
#     )

#     image = cv2.imread("images/motorbikelp.png")

#     number_prediction = model.license_number_prediction(image, is_car=False)

#     print(number_prediction)