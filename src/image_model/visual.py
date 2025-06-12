from typing import Union, List, Tuple
from pathlib import Path

from torchvision.models import resnet18, resnet34, resnet50, ResNet18_Weights, ResNet34_Weights, ResNet50_Weights
from torchvision.io import decode_image
from torch import Tensor, nn, topk, stack, unbind

from src.logging import logger


class ImageClassifierModel:
    """
    This class is used for initializing an image classifier model.
    It currently supports resnet18 and resnet34
    """
    def __init__(self, model_name: str = "resnet18"):
        self.model_name = model_name
        self.label_path = "src/image_model/labels/imagenet_labels.txt"
        if self.model_name == "resnet18":
            weights = ResNet18_Weights.DEFAULT
            model = resnet18
        elif self.model_name == "resnet34":
            weights = ResNet34_Weights.DEFAULT
            model = resnet34
        elif self.model_name == "resnet50":
            weights = ResNet50_Weights.DEFAULT
            model = resnet50
        else:
            raise ValueError(f"The model {model_name} is not supported. Currently support resnet18, resnet34 and resnet50")
        self.model = model(weights=weights)
        self.preprocess = weights.transforms()

    def classify_image_batch(self, img_list: List[Union[Tensor, str, Path]]) -> List[str]:
        """
        Classify image received from S3 bucket by batch

        Args:
            img_list (List of Tensor, str or pathlib.Path): Images to be classified

        Returns:
            List of str of classifications of images
        """
        input_batch = stack([self.preprocess(decode_image(img)) for img in img_list])
        outputs = unbind(self.model(input_batch))
        probabilities_list = [nn.functional.softmax(output, dim=0) for output in outputs]
        results = [self._translate_probabilities(probabilities) for probabilities in probabilities_list]
        return [result for result, _ in results]

    def _translate_probabilities(self, probabilities: Tensor) -> tuple:
        """
        Read labels and match them to probabilities, return the most likely lable

        Args:
            probabilities (Tensor): 1D tensor of normalized probabilities

        Returns:
            str of most likely label predicted
        """
        with open(self.label_path, "r") as f:
            categories = [s.strip() for s in f.readlines()]
        top_prob_value, top_prob_index = topk(probabilities, 1)
        return categories[top_prob_index[0]], top_prob_value[0]
